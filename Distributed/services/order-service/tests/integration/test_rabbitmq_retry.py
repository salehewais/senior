"""Retry twice, then apply once. A second publish of the same event_id does not apply again.

Skipped when RabbitMQ or Postgres is down. The first retry waits 5 seconds and
the second waits 30 seconds, which is the backoff in docs/rabbitmq.md.
"""

from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from order_service.application.consuming import INVENTORY_EVENT_TYPES, DeliveryOutcome, DeliveryResult
from order_service.infrastructure.database.engine import make_engine, make_session_factory
from order_service.infrastructure.messaging.connection import broker_deadline, close_connection, open_connection
from order_service.infrastructure.messaging.consumer import run_consumer
from order_service.infrastructure.messaging.inventory_handler import InventoryUpdatedHandler
from order_service.infrastructure.messaging.topology import (
    EXCHANGE_ERP_EVENTS,
    QUEUE_INVENTORY,
    declare_topology,
)
from order_service.infrastructure.settings import Settings

_ROOT = Path(__file__).resolve().parents[2]


def _settings() -> Settings:
    return Settings()


def _broker_up(settings: Settings) -> bool:
    try:
        connection = open_connection(settings, timeout_seconds=2)
    except Exception:
        return False
    close_connection(connection)
    return True


def _postgres_up(settings: Settings):
    engine = make_engine(settings)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError:
        engine.dispose()
        return None
    return engine


def _migrate() -> None:
    # A subprocess so Alembic's fileConfig does not detach pytest's log capture.
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=_ROOT,
        check=True,
    )


def _publish(settings: Settings, body: bytes) -> None:
    connection = open_connection(settings, timeout_seconds=5)
    try:
        with broker_deadline(connection, 5):
            channel = connection.channel()
            declare_topology(channel)
            channel.confirm_delivery()
            channel.basic_publish(
                exchange=EXCHANGE_ERP_EVENTS,
                routing_key="inventory.updated",
                body=body,
                properties=_properties(),
                mandatory=True,
            )
    finally:
        close_connection(connection)


def _properties():
    import pika

    return pika.BasicProperties(
        content_type="application/json",
        delivery_mode=pika.DeliveryMode.Persistent,
        # Disagree with the body on purpose. The consumer must follow the body.
        message_id="not-the-body-event-id",
        type="OrderCreated",
    )


def _ready_count(settings: Settings, queue_name: str) -> int:
    connection = open_connection(settings, timeout_seconds=5)
    try:
        channel = connection.channel()
        declared = channel.queue_declare(queue=queue_name, passive=True)
        return int(declared.method.message_count)
    finally:
        close_connection(connection)


def _purge(settings: Settings) -> None:
    connection = open_connection(settings, timeout_seconds=5)
    try:
        channel = connection.channel()
        declare_topology(channel)
        channel.queue_purge(QUEUE_INVENTORY)
        channel.queue_purge(f"{QUEUE_INVENTORY}.dlq")
        for attempt in range(1, 6):
            channel.queue_purge(f"{QUEUE_INVENTORY}.retry.{attempt}")
    finally:
        close_connection(connection)


class _FailTwice:
    def __init__(self, inner: InventoryUpdatedHandler) -> None:
        self.inner = inner
        self.calls = 0

    def __call__(self, envelope: dict) -> DeliveryResult | DeliveryOutcome:
        self.calls += 1
        if self.calls <= 2:
            return DeliveryOutcome.TRANSIENT
        return self.inner(envelope)


def test_retry_then_duplicate_does_not_apply_twice() -> None:
    settings = _settings()
    if not _broker_up(settings):
        pytest.skip("RabbitMQ is not running. Start services/order-service/compose.yaml.")
    engine = _postgres_up(settings)
    if engine is None:
        pytest.skip("order_db is not running. Start services/order-service/compose.yaml.")
    _migrate()
    _purge(settings)

    event_id = uuid.uuid4()
    product_id = uuid.uuid4()
    body = json.dumps(
        {
            "event_id": str(event_id),
            "event_type": "InventoryUpdated",
            "occurred_at": "2026-10-08T12:00:00Z",
            "producer": "odoo",
            "aggregate_id": str(product_id),
            "correlation_id": str(uuid.uuid4()),
            "causation_id": str(uuid.uuid4()),
            "version": 1,
            "payload": {
                "product_id": str(product_id),
                "sku": "MUG-01",
                "quantity_on_hand": 10,
                "quantity_reserved": 2,
                "warehouse_code": "MAIN",
                "aggregate_version": 4,
            },
        }
    ).encode()
    handler = _FailTwice(InventoryUpdatedHandler(make_session_factory(engine)))
    stop = threading.Event()
    ready = threading.Event()
    errors: list[BaseException] = []

    def _run() -> None:
        try:
            run_consumer(
                settings,
                handler,
                stop,
                queue_name=QUEUE_INVENTORY,
                ready=ready,
                accepted_event_types=INVENTORY_EVENT_TYPES,
            )
        except Exception as exc:
            errors.append(exc)
            ready.set()

    worker = threading.Thread(target=_run, name="rabbitmq-retry-test")
    worker.start()
    try:
        assert ready.wait(10), errors or "consumer did not start"
        _publish(settings, body)
        deadline = time.monotonic() + 70
        while time.monotonic() < deadline and handler.calls < 3:
            time.sleep(0.2)
        assert handler.calls >= 3, f"handler ran {handler.calls} times; errors={errors}"
        _publish(settings, body)
        duplicate_deadline = time.monotonic() + 10
        while time.monotonic() < duplicate_deadline and handler.calls < 4:
            time.sleep(0.1)
    finally:
        stop.set()
        worker.join(10)
        engine.dispose()
    assert not worker.is_alive()
    assert errors == []
    assert handler.calls == 4
    assert _ready_count(settings, QUEUE_INVENTORY) == 0
    assert _ready_count(settings, f"{QUEUE_INVENTORY}.dlq") == 0

    check = make_engine(settings)
    try:
        with check.connect() as connection:
            processed = connection.execute(
                text("SELECT count(*) FROM processed_events WHERE event_id = :event_id"),
                {"event_id": event_id},
            ).scalar_one()
            snapshot = connection.execute(
                text(
                    "SELECT quantity_on_hand, source_version FROM inventory_snapshots WHERE product_id = :product_id"
                ),
                {"product_id": product_id},
            ).one()
    finally:
        check.dispose()
    assert processed == 1
    assert snapshot.quantity_on_hand == 10
    assert snapshot.source_version == 4
