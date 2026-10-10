"""Publish pending inventory outbox rows to erp.events.

Run beside Odoo, not inside the order service:

    python -m commerce_erp.workers.publisher

The stock write and the outbox row commit together inside Odoo. This process
claims pending rows with SELECT ... FOR UPDATE SKIP LOCKED, ordered by
created_at, id. It publishes the stored envelope to erp.events and waits for
a broker confirm, with an explicit timeout. On confirm it sets
status=published. On failure it increments retry_count. After
outbox_max_attempts the row becomes failed.

A row whose event_type is not InventoryUpdated is marked failed and is not
published. Odoo does not emit OrderShipped or any other order-status event.

The row lock is held across the confirm, same as the order-service outbox.
The broker call has a timeout, so the lock is not held forever. A crash after
the confirm and before this commit sends the same event_id again. Consumers
dedupe on event_id, and an older aggregate_version is ignored.

This process opens odoo_db only. It refuses order_db and reporting_db.
"""

from __future__ import annotations

import json
import logging
import signal
import threading
import uuid
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from math import ceil
from typing import Protocol

import pika
import psycopg
from pika.adapters.blocking_connection import BlockingChannel
from psycopg.rows import dict_row

from commerce_erp.domain.inventory import EVENT_INVENTORY_UPDATED, EXCHANGE_ERP_EVENTS, ROUTING_KEY_INVENTORY
from commerce_erp.messaging.broker import broker_deadline, close_connection, open_connection
from commerce_erp.messaging.topology import declare_topology
from commerce_erp.settings import Settings

logger = logging.getLogger("commerce_erp.publisher")

PENDING = "pending"
PUBLISHED = "published"
FAILED = "failed"


class NotInventoryEvent(Exception):
    """The outbox row is not InventoryUpdated. Do not publish it."""


@dataclass(frozen=True, slots=True)
class PendingOutbox:
    id: uuid.UUID
    event_type: str
    aggregate_type: str
    aggregate_id: uuid.UUID
    payload: object
    retry_count: int
    created_at: datetime


@dataclass(frozen=True, slots=True)
class OutboundMessage:
    event_id: uuid.UUID
    event_type: str
    exchange: str
    routing_key: str
    correlation_id: uuid.UUID
    body: dict[str, object]


class OutboxLease(Protocol):
    def claim(self, limit: int) -> Sequence[PendingOutbox]: ...

    def mark_published(self, event_id: uuid.UUID, published_at: datetime) -> None: ...

    def record_attempt_failure(self, event_id: uuid.UUID, *, retry_count: int, status: str) -> None: ...

    def finish(self) -> None: ...

    def abort(self) -> None: ...


class EventPublisher(Protocol):
    def publish(self, message: OutboundMessage) -> None: ...


def prepare_outbound(payload: object, *, column_event_type: str) -> OutboundMessage:
    """Build the broker message from the stored envelope. Only InventoryUpdated leaves Odoo."""

    if not isinstance(payload, dict):
        raise NotInventoryEvent("outbox payload is not a JSON object")
    payload_type = payload.get("event_type")
    if payload_type != column_event_type:
        logger.error(
            "outbox event_type column disagrees with payload; sending the payload "
            "event_id=%s column_event_type=%s payload_event_type=%s correlation_id=%s",
            payload.get("event_id"),
            column_event_type,
            payload_type,
            payload.get("correlation_id"),
        )
    if payload_type != EVENT_INVENTORY_UPDATED:
        raise NotInventoryEvent("refusing to publish a non-inventory event")
    try:
        event_id = uuid.UUID(str(payload.get("event_id")))
        correlation_id = uuid.UUID(str(payload.get("correlation_id")))
    except ValueError as exc:
        raise NotInventoryEvent("event_id or correlation_id is not a UUID") from exc
    return OutboundMessage(
        event_id=event_id,
        event_type=EVENT_INVENTORY_UPDATED,
        exchange=EXCHANGE_ERP_EVENTS,
        routing_key=ROUTING_KEY_INVENTORY,
        correlation_id=correlation_id,
        body=payload,
    )


def publish_batch(
    lease: OutboxLease,
    broker: EventPublisher,
    *,
    limit: int,
    max_attempts: int,
    now: Callable[[], datetime],
) -> int:
    if limit < 1:
        raise ValueError("outbox batch size must be at least 1")
    if max_attempts < 1:
        raise ValueError("outbox max attempts must be at least 1")
    try:
        rows = list(lease.claim(limit))
        if not rows:
            lease.abort()
            return 0
        for row in rows:
            try:
                broker.publish(prepare_outbound(row.payload, column_event_type=row.event_type))
            except NotInventoryEvent as exc:
                lease.record_attempt_failure(row.id, retry_count=row.retry_count, status=FAILED)
                logger.error(
                    "outbox row failed without publishing event_id=%s event_type=%s reason=%s",
                    row.id,
                    row.event_type,
                    exc,
                )
                continue
            except Exception as exc:
                retry_count = row.retry_count + 1
                status = FAILED if retry_count >= max_attempts else PENDING
                lease.record_attempt_failure(row.id, retry_count=retry_count, status=status)
                logger.error(
                    "outbox publish failed; row stays %s event_id=%s event_type=%s retry_count=%s error_type=%s",
                    status,
                    row.id,
                    row.event_type,
                    retry_count,
                    type(exc).__name__,
                )
                continue
            lease.mark_published(row.id, now())
        lease.finish()
        return len(rows)
    except Exception:
        lease.abort()
        raise


class PsycopgOutboxLease:
    """SELECT ... FOR UPDATE SKIP LOCKED on commerce_event_outbox in odoo_db."""

    def __init__(self, connection: psycopg.Connection) -> None:
        self._connection = connection
        self._closed = False

    def claim(self, limit: int) -> Sequence[PendingOutbox]:
        rows = self._connection.execute(
            """
            SELECT id, event_type, aggregate_type, aggregate_id, payload, retry_count, created_at
            FROM commerce_event_outbox
            WHERE status = %s
            ORDER BY created_at, id
            LIMIT %s
            FOR UPDATE SKIP LOCKED
            """,
            (PENDING, limit),
        ).fetchall()
        return [
            PendingOutbox(
                id=_uuid(row["id"]),
                event_type=row["event_type"],
                aggregate_type=row["aggregate_type"],
                aggregate_id=_uuid(row["aggregate_id"]),
                payload=_payload(row["payload"]),
                retry_count=row["retry_count"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def mark_published(self, event_id: uuid.UUID, published_at: datetime) -> None:
        self._connection.execute(
            """
            UPDATE commerce_event_outbox
            SET status = %s, published_at = %s
            WHERE id = %s
            """,
            (PUBLISHED, published_at, event_id),
        )

    def record_attempt_failure(self, event_id: uuid.UUID, *, retry_count: int, status: str) -> None:
        self._connection.execute(
            """
            UPDATE commerce_event_outbox
            SET retry_count = %s, status = %s
            WHERE id = %s
            """,
            (retry_count, status, event_id),
        )

    def finish(self) -> None:
        if not self._closed:
            self._connection.commit()
            self._closed = True

    def abort(self) -> None:
        if not self._closed:
            self._connection.rollback()
            self._closed = True


class ConfirmingBroker:
    """One connection. publish returns after the broker confirms on erp.events."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._connection: pika.BlockingConnection | None = None
        self._channel: BlockingChannel | None = None

    def publish(self, message: OutboundMessage) -> None:
        timeout = self._settings.rabbitmq_timeout_seconds
        try:
            channel = self._ensure_channel(timeout)
            connection = self._connection
            if connection is None:
                raise RuntimeError("RabbitMQ connection is not open.")
            with broker_deadline(connection, timeout):
                channel.basic_publish(
                    exchange=message.exchange,
                    routing_key=message.routing_key,
                    body=json.dumps(message.body, separators=(",", ":")).encode("utf-8"),
                    properties=pika.BasicProperties(
                        content_type="application/json",
                        content_encoding="utf-8",
                        delivery_mode=pika.DeliveryMode.Persistent,
                        message_id=str(message.event_id),
                        correlation_id=str(message.correlation_id),
                        type=message.event_type,
                        app_id="odoo",
                    ),
                    mandatory=True,
                )
        except Exception:
            self.close()
            raise

    def close(self) -> None:
        connection = self._connection
        self._connection = None
        self._channel = None
        if connection is not None:
            close_connection(connection, timeout_seconds=self._settings.rabbitmq_timeout_seconds)

    def _ensure_channel(self, timeout: float) -> BlockingChannel:
        connection = self._connection
        channel = self._channel
        if connection is not None and connection.is_open and channel is not None and channel.is_open:
            return channel
        self.close()
        connection = open_connection(self._settings.rabbitmq_url, timeout)
        self._connection = connection
        try:
            with broker_deadline(connection, timeout):
                opened = connection.channel()
                declare_topology(opened)
                opened.confirm_delivery()
                self._channel = opened
                return opened
        except Exception:
            self.close()
            raise


def publish_once(settings: Settings, broker: EventPublisher, *, now: Callable[[], datetime] | None = None) -> int:
    timeout = max(1, ceil(settings.db_connect_timeout_seconds))
    connection = psycopg.connect(
        settings.require_odoo_database_url(),
        connect_timeout=timeout,
        autocommit=False,
        row_factory=dict_row,
        options=(
            f"-c statement_timeout={settings.db_statement_timeout_ms} "
            f"-c lock_timeout={settings.db_statement_timeout_ms}"
        ),
    )
    lease = PsycopgOutboxLease(connection)
    clock = now or _utc_now
    try:
        return publish_batch(
            lease,
            broker,
            limit=settings.outbox_batch_size,
            max_attempts=settings.outbox_max_attempts,
            now=clock,
        )
    finally:
        connection.close()


def run_publisher(settings: Settings, broker: ConfirmingBroker, stop: threading.Event) -> None:
    logger.info(
        "inventory outbox publisher started poll_interval_seconds=%s batch_size=%s max_attempts=%s",
        settings.outbox_poll_interval_seconds,
        settings.outbox_batch_size,
        settings.outbox_max_attempts,
    )
    while not stop.is_set():
        try:
            publish_once(settings, broker)
        except Exception as exc:
            logger.error("outbox batch aborted error_type=%s", type(exc).__name__)
        if stop.wait(settings.outbox_poll_interval_seconds):
            break
    broker.close()
    logger.info("inventory outbox publisher stopping")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    settings = Settings.from_environ()
    settings.require_odoo_database_url()
    broker = ConfirmingBroker(settings)
    stop = threading.Event()

    def _request_stop(signum: int, _frame: object) -> None:
        logger.info("shutdown requested signal=%s", signum)
        stop.set()

    signal.signal(signal.SIGINT, _request_stop)
    signal.signal(signal.SIGTERM, _request_stop)
    run_publisher(settings, broker, stop)


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _uuid(value: object) -> uuid.UUID:
    if isinstance(value, uuid.UUID):
        return value
    return uuid.UUID(str(value))


def _payload(value: object) -> object:
    if isinstance(value, str):
        return json.loads(value)
    return value


if __name__ == "__main__":
    main()
