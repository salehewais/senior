"""The publisher sends InventoryUpdated to erp.events and refuses order-status events."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from commerce_erp.domain.inventory import build_inventory_updated
from commerce_erp.settings import Settings
from commerce_erp.workers.publisher import PendingOutbox, publish_batch

PRODUCT_ID = "018f1c2a-5555-7c11-8a22-666666666666"
NOW = datetime(2026, 10, 9, tzinfo=UTC)


class MemoryLease:
    def __init__(self, rows: list[PendingOutbox]) -> None:
        self.rows = rows
        self.published: list[uuid.UUID] = []
        self.failed: list[tuple[uuid.UUID, int, str]] = []
        self.finished = False
        self.aborted = False

    def claim(self, limit: int) -> list[PendingOutbox]:
        return self.rows[:limit]

    def mark_published(self, event_id: uuid.UUID, published_at: datetime) -> None:
        self.published.append(event_id)

    def record_attempt_failure(self, event_id: uuid.UUID, *, retry_count: int, status: str) -> None:
        self.failed.append((event_id, retry_count, status))

    def finish(self) -> None:
        self.finished = True

    def abort(self) -> None:
        self.aborted = True


class Broker:
    def __init__(self) -> None:
        self.messages = []

    def publish(self, message) -> None:
        self.messages.append(message)


def _row(event_type: str, payload: dict) -> PendingOutbox:
    event_id = uuid.UUID(str(payload["event_id"]))
    return PendingOutbox(
        id=event_id,
        event_type=event_type,
        aggregate_type="inventory" if event_type == "InventoryUpdated" else "order",
        aggregate_id=uuid.UUID(PRODUCT_ID),
        payload=payload,
        retry_count=0,
        created_at=NOW,
    )


def test_inventory_row_publishes_to_erp_events() -> None:
    envelope = build_inventory_updated(
        product_id=PRODUCT_ID,
        sku="MUG-01",
        on_hand=10,
        reserved=2,
        warehouse_code="WH",
        aggregate_version=1,
    )
    lease = MemoryLease([_row("InventoryUpdated", envelope)])
    broker = Broker()

    claimed = publish_batch(lease, broker, limit=10, max_attempts=5, now=lambda: NOW)

    assert claimed == 1
    assert lease.finished
    assert lease.published == [uuid.UUID(str(envelope["event_id"]))]
    assert broker.messages[0].exchange == "erp.events"
    assert broker.messages[0].routing_key == "inventory.updated"
    assert broker.messages[0].body["payload"]["quantity_on_hand"] == 10
    assert broker.messages[0].body["payload"]["quantity_reserved"] == 2


def test_order_shipped_is_not_published() -> None:
    event_id = "018f1c2a-7b3d-7c11-8a22-111111111111"
    payload = {
        "event_id": event_id,
        "event_type": "OrderShipped",
        "occurred_at": "2026-10-09T00:00:00Z",
        "producer": "odoo",
        "aggregate_id": PRODUCT_ID,
        "correlation_id": PRODUCT_ID,
        "causation_id": event_id,
        "version": 1,
        "payload": {"order_id": PRODUCT_ID, "status": "SHIPPED", "aggregate_version": 1},
    }
    lease = MemoryLease([_row("OrderShipped", payload)])
    broker = Broker()

    publish_batch(lease, broker, limit=10, max_attempts=5, now=lambda: NOW)

    assert broker.messages == []
    assert lease.failed[0][0] == uuid.UUID(event_id)
    assert lease.failed[0][2] == "failed"
    assert lease.finished


def test_publisher_refuses_order_db() -> None:
    settings = Settings(
        rabbitmq_url="amqp://guest:guest@127.0.0.1:5672/%2F",
        rabbitmq_timeout_seconds=5,
        odoo_url="http://127.0.0.1:8069",
        odoo_db="odoo_db",
        odoo_user="admin",
        odoo_password="admin",
        odoo_timeout_seconds=5,
        order_service_url="http://127.0.0.1:8000",
        internal_service_token="",
        order_service_timeout_seconds=5,
        odoo_database_url="postgresql://odoo:odoo@127.0.0.1:5432/order_db",
        db_connect_timeout_seconds=5,
        db_statement_timeout_ms=10000,
        outbox_poll_interval_seconds=1,
        outbox_batch_size=100,
        outbox_max_attempts=5,
    )
    with pytest.raises(RuntimeError, match="order_db"):
        settings.require_odoo_database_url()
