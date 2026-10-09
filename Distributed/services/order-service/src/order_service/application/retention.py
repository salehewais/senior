"""Decide which order_db rows a retention run may delete, and how many batches it takes.

No SQLAlchemy and no Kubernetes. The database adapter commits one batch at a time.
A single DELETE of every old row is the failure this module refuses to issue:
it holds locks for the whole pass, it asks replicas to apply one huge change,
and a crash in the middle of that statement rolls the entire delete back.
"""

from __future__ import annotations

import uuid
from collections.abc import Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from order_service.application.outbox import PUBLISHED
from order_service.domain.entities.order_status import OrderStatus

# In-flight orders are an operator problem. Age does not make them garbage.
TERMINAL_ORDER_STATUSES = frozenset({OrderStatus.DELIVERED.value, OrderStatus.CANCELLED.value})
ORDER_AGGREGATE = "order"


class RetentionStore(Protocol):
    def delete_order_batch(self, *, cutoff: datetime, limit: int) -> int:
        """Delete at most ``limit`` eligible orders and their items. One transaction.

        Return how many orders were deleted. Fewer than ``limit`` means the run is done.
        """

    def delete_published_outbox_batch(self, *, cutoff: datetime, limit: int) -> int:
        """Delete at most ``limit`` published outbox rows that retention may drop.

        Pending and failed rows stay. One transaction.
        """

    def delete_processed_events_batch(self, *, cutoff: datetime, limit: int) -> int:
        """Delete at most ``limit`` processed_events older than ``cutoff``. One transaction."""


@dataclass(frozen=True, slots=True)
class RetentionReport:
    orders_deleted: int
    order_batches: int
    outbox_deleted: int
    outbox_batches: int
    processed_events_deleted: int
    processed_event_batches: int


def order_is_eligible(status: str, created_at: datetime, cutoff: datetime) -> bool:
    """True when this order row is terminal and older than the cutoff.

    ``created_at`` equal to the cutoff stays. "Older" means strictly earlier.
    """

    return status in TERMINAL_ORDER_STATUSES and created_at < cutoff


def published_outbox_is_eligible(
    *,
    status: str,
    created_at: datetime,
    aggregate_type: str,
    aggregate_id: uuid.UUID,
    cutoff: datetime,
    live_order_ids: Set[uuid.UUID],
) -> bool:
    """Published rows only. Pending and failed are never eligible.

    ``outbox.aggregate_id`` is not a foreign key. A published row goes when it
    is older than the cutoff, or when it is an order event whose order row is
    already gone. A recent published row for an order that is still in the
    table stays.
    """

    if status != PUBLISHED:
        return False
    if created_at < cutoff:
        return True
    return aggregate_type == ORDER_AGGREGATE and aggregate_id not in live_order_ids


def processed_event_is_eligible(processed_at: datetime, cutoff: datetime) -> bool:
    """``order_db.processed_events`` ages on ``processed_at``.

    Those rows record InventoryUpdated deliveries. A redelivery after the row
    is gone applies the snapshot again. An older source_version does not
    overwrite a newer snapshot, and that handler does not insert orders, so
    the redelivery cannot bring a deleted order back. Rows newer than the
    cutoff stay so a recent duplicate is still recognized.
    """

    return processed_at < cutoff


def retention_cutoff(now: datetime, retention_days: int) -> datetime:
    return now - timedelta(days=retention_days)


def run_retention(
    store: RetentionStore,
    *,
    now: datetime,
    retention_days: int,
    batch_size: int,
    max_batches: int,
) -> RetentionReport:
    """Run order, published-outbox, and processed_events cleanup.

    Each table gets at most ``max_batches`` commits. A short batch ends that
    table's loop. The next scheduled run continues anything left over.
    """

    if now.tzinfo is None:
        raise ValueError("retention clock must be timezone-aware")
    if retention_days < 1:
        raise ValueError("ORDER_RETENTION_DAYS must be at least 1")
    if batch_size < 1:
        raise ValueError("ORDER_RETENTION_BATCH_SIZE must be at least 1")
    if max_batches < 1:
        raise ValueError("ORDER_RETENTION_MAX_BATCHES must be at least 1")
    cutoff = retention_cutoff(now, retention_days)
    orders_deleted, order_batches = _run_batches(
        lambda: store.delete_order_batch(cutoff=cutoff, limit=batch_size),
        batch_size=batch_size,
        max_batches=max_batches,
    )
    outbox_deleted, outbox_batches = _run_batches(
        lambda: store.delete_published_outbox_batch(cutoff=cutoff, limit=batch_size),
        batch_size=batch_size,
        max_batches=max_batches,
    )
    processed_deleted, processed_batches = _run_batches(
        lambda: store.delete_processed_events_batch(cutoff=cutoff, limit=batch_size),
        batch_size=batch_size,
        max_batches=max_batches,
    )
    return RetentionReport(
        orders_deleted=orders_deleted,
        order_batches=order_batches,
        outbox_deleted=outbox_deleted,
        outbox_batches=outbox_batches,
        processed_events_deleted=processed_deleted,
        processed_event_batches=processed_batches,
    )


def _run_batches(delete_batch, *, batch_size: int, max_batches: int) -> tuple[int, int]:
    deleted = 0
    batches = 0
    while batches < max_batches:
        count = delete_batch()
        batches += 1
        deleted += count
        if count < batch_size:
            break
    return deleted, batches
