"""Publish pending outbox rows to commerce.events.

Run next to the API, not inside it:

    python -m order_service.infrastructure.messaging.outbox_publisher

The API has already committed the business row and this outbox row in one
order_db transaction. This process claims pending rows with
SELECT ... FOR UPDATE SKIP LOCKED, ordered by created_at, id. It publishes
the stored envelope and waits for a broker confirm, with an explicit timeout.
On confirm it sets status=published and published_at. On failure it increments
retry_count and leaves the row pending. It does not change the order.

After outbox_max_attempts failed confirms the row becomes status=failed and
later polls skip it. That is an operator problem: the broker never accepted
the publish. It is not the consumer dead-letter queue. A DLQ message was
delivered to a consumer, which could not apply it. The outbox row for that
fact can already be published. Consumers dedupe on event_id, and the outbox
id is that event_id, so a republish after a crash is the same fact.

Shutdown finishes the batch already claimed, does not claim another, and
closes the broker connection.
"""

from __future__ import annotations

import logging
import os
import signal
import threading
import time
import uuid
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy import select, text
from sqlalchemy.orm import Session, sessionmaker

from order_service.application.outbox import FAILED, PENDING, PUBLISHED
from order_service.application.publishing import EventPublisher, outbound_from_envelope
from order_service.infrastructure.database.engine import make_engine, make_session_factory
from order_service.infrastructure.database.models import OutboxRow
from order_service.infrastructure.messaging.publisher import ConfirmingBroker
from order_service.infrastructure.settings import Settings, get_settings
from order_service.observability.context import correlation_id_var, event_id_var, event_type_var
from order_service.observability.metrics import record_outbox_attempt_failed, record_outbox_published

logger = logging.getLogger("order_service.outbox")


@dataclass(frozen=True, slots=True)
class PendingOutbox:
    id: uuid.UUID
    event_type: str
    aggregate_type: str
    aggregate_id: uuid.UUID
    payload: object
    retry_count: int
    created_at: datetime


class OutboxLease(Protocol):
    def claim(self, limit: int) -> Sequence[PendingOutbox]:
        """Lock up to ``limit`` pending rows. Locked rows are invisible to other claims."""

    def mark_published(self, event_id: uuid.UUID, published_at: datetime) -> None:
        """Record a broker confirm. ``retry_count`` stays as it was."""

    def record_attempt_failure(self, event_id: uuid.UUID, *, retry_count: int, status: str) -> None:
        """Count one failed confirm. ``status`` is pending or failed."""

    def finish(self) -> None:
        """Commit the status updates and release the locks."""

    def abort(self) -> None:
        """Roll back status updates and release the locks. Do not touch business rows."""


def publish_batch(
    lease: OutboxLease,
    broker: EventPublisher,
    *,
    limit: int,
    max_attempts: int,
    now: Callable[[], datetime],
) -> int:
    """Publish one claimed batch. Returns how many rows were claimed.

    A row stays pending until ``broker.publish`` returns. That return is the
    broker confirm. A raise leaves the row pending, or failed once
    ``retry_count`` reaches ``max_attempts``.
    """

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
            event_id, event_type, correlation_id = _log_ids(row)
            event_token = event_id_var.set(event_id)
            type_token = event_type_var.set(event_type)
            correlation_token = correlation_id_var.set(correlation_id if correlation_id != "missing" else "")
            started = time.perf_counter()
            try:
                try:
                    broker.publish(outbound_from_envelope(row.payload, column_event_type=row.event_type))
                except Exception as exc:
                    retry_count = row.retry_count + 1
                    status = FAILED if retry_count >= max_attempts else PENDING
                    lease.record_attempt_failure(row.id, retry_count=retry_count, status=status)
                    record_outbox_attempt_failed(
                        event_type,
                        terminal=status == FAILED,
                        seconds=time.perf_counter() - started,
                    )
                    _log_failure(row, exc, retry_count=retry_count, status=status)
                    continue
                lease.mark_published(row.id, now())
                record_outbox_published(event_type, time.perf_counter() - started)
            finally:
                event_id_var.reset(event_token)
                event_type_var.reset(type_token)
                correlation_id_var.reset(correlation_token)
        lease.finish()
        return len(rows)
    except Exception:
        lease.abort()
        raise


def publish_once(
    session_factory: sessionmaker[Session],
    broker: EventPublisher,
    settings: Settings,
    *,
    now: Callable[[], datetime] | None = None,
) -> int:
    """Claim one batch, publish it, and commit. Holds the row locks across the confirms."""

    session = session_factory()
    lease = SqlOutboxLease(session)
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
        session.close()


def run_publisher(
    settings: Settings,
    session_factory: sessionmaker[Session],
    broker: ConfirmingBroker,
    stop: threading.Event,
    *,
    publish_pending: Callable[[sessionmaker[Session], EventPublisher, Settings], int] = publish_once,
) -> None:
    """Poll until ``stop`` is set. The batch in progress finishes before the process exits."""

    logger.info(
        "outbox publisher started poll_interval_seconds=%s batch_size=%s max_attempts=%s",
        settings.outbox_poll_interval_seconds,
        settings.outbox_batch_size,
        settings.outbox_max_attempts,
    )
    while not stop.is_set():
        try:
            publish_pending(session_factory, broker, settings)
        except Exception as exc:
            logger.error("outbox batch aborted error_type=%s", type(exc).__name__)
        if stop.wait(settings.outbox_poll_interval_seconds):
            break
    logger.info("outbox publisher stopping")


class SqlOutboxLease:
    """SELECT ... FOR UPDATE SKIP LOCKED, then update those rows in the same transaction."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._claimed: dict[uuid.UUID, OutboxRow] = {}
        self._closed = False

    def claim(self, limit: int) -> Sequence[PendingOutbox]:
        rows = self._session.scalars(
            select(OutboxRow)
            .where(OutboxRow.status == PENDING)
            .order_by(OutboxRow.created_at, OutboxRow.id)
            .limit(limit)
            .with_for_update(skip_locked=True)
        ).all()
        self._claimed = {row.id: row for row in rows}
        return [
            PendingOutbox(
                id=row.id,
                event_type=row.event_type,
                aggregate_type=row.aggregate_type,
                aggregate_id=row.aggregate_id,
                payload=row.payload,
                retry_count=row.retry_count,
                created_at=row.created_at,
            )
            for row in rows
        ]

    def mark_published(self, event_id: uuid.UUID, published_at: datetime) -> None:
        row = self._claimed[event_id]
        row.status = PUBLISHED
        row.published_at = published_at

    def record_attempt_failure(self, event_id: uuid.UUID, *, retry_count: int, status: str) -> None:
        row = self._claimed[event_id]
        row.retry_count = retry_count
        row.status = status

    def finish(self) -> None:
        if self._closed:
            return
        self._session.commit()
        self._closed = True

    def abort(self) -> None:
        if self._closed:
            return
        self._session.rollback()
        self._closed = True


def main() -> None:
    from order_service.observability.jsonlog import configure_logging
    from order_service.observability.metrics import bind_database_engine, serve_metrics
    from order_service.observability.tracing import configure_tracing

    configure_logging("order-outbox-publisher")
    settings = get_settings()
    engine = make_engine(settings)
    configure_tracing(os.environ.get("OTEL_SERVICE_NAME", "order-outbox-publisher"), engine)
    bind_database_engine(engine)
    serve_metrics()
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    sessions = make_session_factory(engine)
    stop = threading.Event()

    def _request_stop(signum: int, _frame: object) -> None:
        logger.info("shutdown requested signal=%s", signum)
        stop.set()

    signal.signal(signal.SIGINT, _request_stop)
    signal.signal(signal.SIGTERM, _request_stop)
    broker = ConfirmingBroker(settings)
    try:
        run_publisher(settings, sessions, broker, stop)
    finally:
        broker.close()
        engine.dispose()
        logger.info("outbox publisher stopped")


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _log_failure(row: PendingOutbox, exc: BaseException, *, retry_count: int, status: str) -> None:
    event_id, event_type, correlation_id = _log_ids(row)
    if status == FAILED:
        logger.error(
            "outbox row failed; the business row is unchanged; this is not the consumer DLQ "
            "event_id=%s event_type=%s correlation_id=%s retry_count=%s error_type=%s",
            event_id,
            event_type,
            correlation_id,
            retry_count,
            type(exc).__name__,
        )
        return
    logger.warning(
        "outbox publish failed; row stays pending "
        "event_id=%s event_type=%s correlation_id=%s retry_count=%s error_type=%s",
        event_id,
        event_type,
        correlation_id,
        retry_count,
        type(exc).__name__,
    )


def _log_ids(row: PendingOutbox) -> tuple[str, str, str]:
    correlation_id = "missing"
    event_type = row.event_type
    if isinstance(row.payload, dict):
        raw_correlation = row.payload.get("correlation_id")
        if raw_correlation is not None:
            correlation_id = str(raw_correlation)
        raw_type = row.payload.get("event_type")
        if isinstance(raw_type, str) and raw_type:
            event_type = raw_type
    return str(row.id), event_type, correlation_id


if __name__ == "__main__":
    main()
