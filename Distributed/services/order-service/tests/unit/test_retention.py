"""Retention keeps in-flight orders and deletes terminal ones in bounded batches."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import pytest

from order_service.application.outbox import FAILED, PENDING, PUBLISHED
from order_service.application.retention import (
    order_is_eligible,
    processed_event_is_eligible,
    published_outbox_is_eligible,
    run_retention,
)

NOW = datetime(2026, 10, 9, tzinfo=UTC)
OLD = NOW - timedelta(days=400)
RECENT = NOW - timedelta(days=10)


@dataclass
class _Order:
    id: uuid.UUID
    status: str
    created_at: datetime


@dataclass
class _Outbox:
    id: uuid.UUID
    status: str
    created_at: datetime
    aggregate_type: str
    aggregate_id: uuid.UUID


@dataclass
class _Processed:
    event_id: uuid.UUID
    processed_at: datetime


class MemoryRetentionStore:
    """Applies the same eligibility rules the SQL adapter translates into statements.

    Each method is one committed batch. It never deletes more rows than ``limit``.
    """

    def __init__(self) -> None:
        self.orders: dict[uuid.UUID, _Order] = {}
        self.items: dict[uuid.UUID, list[uuid.UUID]] = {}
        self.outbox: dict[uuid.UUID, _Outbox] = {}
        self.processed: dict[uuid.UUID, _Processed] = {}
        self.order_batches: list[int] = []
        self.outbox_batches: list[int] = []
        self.processed_batches: list[int] = []

    def add_order(self, status: str, created_at: datetime, *, items: int = 1) -> uuid.UUID:
        order_id = uuid.uuid4()
        self.orders[order_id] = _Order(order_id, status, created_at)
        self.items[order_id] = [uuid.uuid4() for _ in range(items)]
        return order_id

    def add_outbox(
        self,
        status: str,
        created_at: datetime,
        *,
        aggregate_type: str = "order",
        aggregate_id: uuid.UUID | None = None,
    ) -> uuid.UUID:
        row_id = uuid.uuid4()
        self.outbox[row_id] = _Outbox(
            row_id,
            status,
            created_at,
            aggregate_type,
            aggregate_id if aggregate_id is not None else uuid.uuid4(),
        )
        return row_id

    def add_processed(self, processed_at: datetime) -> uuid.UUID:
        event_id = uuid.uuid4()
        self.processed[event_id] = _Processed(event_id, processed_at)
        return event_id

    def delete_order_batch(self, *, cutoff: datetime, limit: int) -> int:
        eligible = sorted(
            (
                order
                for order in self.orders.values()
                if order_is_eligible(order.status, order.created_at, cutoff)
            ),
            key=lambda order: (order.created_at, order.id),
        )[:limit]
        for order in eligible:
            self.items.pop(order.id, None)
            del self.orders[order.id]
        self.order_batches.append(len(eligible))
        return len(eligible)

    def delete_published_outbox_batch(self, *, cutoff: datetime, limit: int) -> int:
        live = set(self.orders)
        eligible = sorted(
            (
                row
                for row in self.outbox.values()
                if published_outbox_is_eligible(
                    status=row.status,
                    created_at=row.created_at,
                    aggregate_type=row.aggregate_type,
                    aggregate_id=row.aggregate_id,
                    cutoff=cutoff,
                    live_order_ids=live,
                )
            ),
            key=lambda row: (row.created_at, row.id),
        )[:limit]
        for row in eligible:
            del self.outbox[row.id]
        self.outbox_batches.append(len(eligible))
        return len(eligible)

    def delete_processed_events_batch(self, *, cutoff: datetime, limit: int) -> int:
        eligible = sorted(
            (
                row
                for row in self.processed.values()
                if processed_event_is_eligible(row.processed_at, cutoff)
            ),
            key=lambda row: (row.processed_at, row.event_id),
        )[:limit]
        for row in eligible:
            del self.processed[row.event_id]
        self.processed_batches.append(len(eligible))
        return len(eligible)


def test_old_terminal_orders_go_and_in_flight_and_recent_orders_stay() -> None:
    store = MemoryRetentionStore()
    delivered = store.add_order("DELIVERED", OLD, items=2)
    cancelled = store.add_order("CANCELLED", OLD, items=1)
    pending = store.add_order("PENDING", OLD, items=3)
    processing = store.add_order("PROCESSING", OLD, items=1)
    confirmed = store.add_order("CONFIRMED", OLD)
    shipped = store.add_order("SHIPPED", OLD)
    recent = store.add_order("DELIVERED", RECENT, items=2)

    report = run_retention(store, now=NOW, retention_days=365, batch_size=100, max_batches=10)

    assert delivered not in store.orders
    assert cancelled not in store.orders
    assert delivered not in store.items
    assert cancelled not in store.items
    assert store.orders[pending].status == "PENDING"
    assert len(store.items[pending]) == 3
    assert processing in store.orders
    assert confirmed in store.orders
    assert shipped in store.orders
    assert recent in store.orders
    assert len(store.items[recent]) == 2
    assert report.orders_deleted == 2


def test_more_orders_than_one_batch_take_several_commits() -> None:
    store = MemoryRetentionStore()
    for _ in range(5):
        store.add_order("DELIVERED", OLD)
    store.add_order("PENDING", OLD)
    store.add_order("DELIVERED", RECENT)

    report = run_retention(store, now=NOW, retention_days=365, batch_size=2, max_batches=10)

    assert store.order_batches == [2, 2, 1]
    assert report.orders_deleted == 5
    assert report.order_batches == 3
    assert all(count <= 2 for count in store.order_batches)
    assert {order.status for order in store.orders.values()} == {"PENDING", "DELIVERED"}
    assert all(order.created_at == RECENT or order.status == "PENDING" for order in store.orders.values())


def test_max_batches_stops_before_the_backlog_is_gone() -> None:
    store = MemoryRetentionStore()
    for _ in range(5):
        store.add_order("CANCELLED", OLD)

    report = run_retention(store, now=NOW, retention_days=365, batch_size=2, max_batches=2)

    assert store.order_batches == [2, 2]
    assert report.orders_deleted == 4
    assert len(store.orders) == 1


def test_published_outbox_and_old_processed_events_are_batched_pending_and_failed_stay() -> None:
    store = MemoryRetentionStore()
    kept = store.add_order("PENDING", OLD)
    store.add_outbox(PENDING, OLD, aggregate_id=kept)
    store.add_outbox(FAILED, OLD, aggregate_id=kept)
    old_published = store.add_outbox(PUBLISHED, OLD, aggregate_id=kept)
    recent_published = store.add_outbox(PUBLISHED, RECENT, aggregate_id=kept)
    gone = store.add_order("DELIVERED", OLD)
    orphan_recent = store.add_outbox(PUBLISHED, RECENT, aggregate_id=gone)
    orphan_pending = store.add_outbox(PENDING, RECENT, aggregate_id=gone)
    catalog = store.add_outbox(PUBLISHED, RECENT, aggregate_type="product")
    old_event = store.add_processed(OLD)
    recent_event = store.add_processed(RECENT)

    report = run_retention(store, now=NOW, retention_days=365, batch_size=1, max_batches=10)

    assert old_published not in store.outbox
    assert orphan_recent not in store.outbox
    assert recent_published in store.outbox
    assert catalog in store.outbox
    assert store.outbox[orphan_pending].status == PENDING
    assert any(row.status == FAILED for row in store.outbox.values())
    assert any(row.status == PENDING and row.aggregate_id == kept for row in store.outbox.values())
    assert old_event not in store.processed
    assert recent_event in store.processed
    assert report.outbox_deleted == 2
    assert report.outbox_batches > 1
    assert store.outbox_batches[0] == 1
    assert report.processed_events_deleted == 1


def test_cutoff_is_exclusive_and_bad_settings_do_not_delete() -> None:
    cutoff = NOW - timedelta(days=365)
    assert order_is_eligible("DELIVERED", cutoff, cutoff) is False
    assert order_is_eligible("DELIVERED", cutoff - timedelta(seconds=1), cutoff) is True
    assert order_is_eligible("SHIPPED", OLD, cutoff) is False
    assert processed_event_is_eligible(cutoff, cutoff) is False
    store = MemoryRetentionStore()
    store.add_order("DELIVERED", OLD)
    with pytest.raises(ValueError):
        run_retention(store, now=NOW, retention_days=0, batch_size=10, max_batches=1)
    assert len(store.orders) == 1
    with pytest.raises(ValueError):
        run_retention(store, now=NOW.replace(tzinfo=None), retention_days=365, batch_size=10, max_batches=1)
    assert store.order_batches == []
