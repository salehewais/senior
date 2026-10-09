"""Delete old terminal orders from order_db, in committed batches.

    python -m order_service.infrastructure.database.retention

Reads ORDER_RETENTION_DAYS (default 365), ORDER_RETENTION_BATCH_SIZE (default
100), and ORDER_RETENTION_MAX_BATCHES (default 20). Opens DATABASE_URL only.
This process does not connect to reporting_db or odoo_db.

Eligible orders are DELIVERED or CANCELLED with created_at earlier than now
minus the retention window. PENDING, CONFIRMED, PROCESSING, and SHIPPED stay.
Each batch selects a bounded id list, deletes order_items for those ids, then
deletes the orders, then commits. The next batch is a new transaction.

outbox.aggregate_id is not a foreign key to orders. Published rows older than
the same cutoff are deleted in their own batches. So are published rows whose
aggregate_type is order when that order row is already gone. Pending and
failed outbox rows are left, including rows for an order this run deleted.
A pending row has not been confirmed by the broker. A failed row needs an
operator. Dropping either would discard a fact that never reached the broker.

order_db.processed_events rows with processed_at earlier than the cutoff are
deleted in their own batches. That table is the inventory consumer's
event_id ledger, not an order ledger. A redelivery reapplies InventoryUpdated.
An older source_version does not overwrite a newer snapshot, and the handler
does not insert an order, so it cannot resurrect a deleted order. Reporting
keeps its own processed_events in reporting_db. Those rows dedupe order
facts. This command does not delete them: a redelivery would apply
OrderCreated again and put the order back in the report.

inventory_snapshots, customers, products, and accounts are not order history.
They stay.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from sqlalchemy import and_, delete, or_, select
from sqlalchemy.orm import Session, sessionmaker

from order_service.application.outbox import PUBLISHED
from order_service.application.retention import (
    ORDER_AGGREGATE,
    TERMINAL_ORDER_STATUSES,
    RetentionReport,
    run_retention,
)
from order_service.infrastructure.database.engine import make_engine, make_session_factory
from order_service.infrastructure.database.models import (
    OrderItemRow,
    OrderRow,
    OutboxRow,
    ProcessedEventRow,
)
from order_service.infrastructure.settings import Settings, get_settings

logger = logging.getLogger("order_service.retention")


class SqlRetentionStore:
    """One session per batch. Commit ends that batch. A later failure leaves it committed."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def delete_order_batch(self, *, cutoff: datetime, limit: int) -> int:
        session = self._session_factory()
        try:
            ids = list(
                session.scalars(
                    select(OrderRow.id)
                    .where(OrderRow.status.in_(sorted(TERMINAL_ORDER_STATUSES)))
                    .where(OrderRow.created_at < cutoff)
                    .order_by(OrderRow.created_at, OrderRow.id)
                    .limit(limit)
                )
            )
            if not ids:
                session.rollback()
                return 0
            # order_items.order_id references orders.id. Delete the children first.
            session.execute(delete(OrderItemRow).where(OrderItemRow.order_id.in_(ids)))
            session.execute(delete(OrderRow).where(OrderRow.id.in_(ids)))
            session.commit()
            return len(ids)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete_published_outbox_batch(self, *, cutoff: datetime, limit: int) -> int:
        session = self._session_factory()
        try:
            live_orders = select(OrderRow.id)
            ids = list(
                session.scalars(
                    select(OutboxRow.id)
                    .where(OutboxRow.status == PUBLISHED)
                    .where(
                        or_(
                            OutboxRow.created_at < cutoff,
                            and_(
                                OutboxRow.aggregate_type == ORDER_AGGREGATE,
                                OutboxRow.aggregate_id.not_in(live_orders),
                            ),
                        )
                    )
                    .order_by(OutboxRow.created_at, OutboxRow.id)
                    .limit(limit)
                )
            )
            if not ids:
                session.rollback()
                return 0
            session.execute(delete(OutboxRow).where(OutboxRow.id.in_(ids)))
            session.commit()
            return len(ids)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def delete_processed_events_batch(self, *, cutoff: datetime, limit: int) -> int:
        session = self._session_factory()
        try:
            ids = list(
                session.scalars(
                    select(ProcessedEventRow.event_id)
                    .where(ProcessedEventRow.processed_at < cutoff)
                    .order_by(ProcessedEventRow.processed_at, ProcessedEventRow.event_id)
                    .limit(limit)
                )
            )
            if not ids:
                session.rollback()
                return 0
            session.execute(delete(ProcessedEventRow).where(ProcessedEventRow.event_id.in_(ids)))
            session.commit()
            return len(ids)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


def run(settings: Settings, *, now: datetime | None = None) -> RetentionReport:
    engine = make_engine(settings)
    try:
        store = SqlRetentionStore(make_session_factory(engine))
        return run_retention(
            store,
            now=now if now is not None else datetime.now(UTC),
            retention_days=settings.order_retention_days,
            batch_size=settings.order_retention_batch_size,
            max_batches=settings.order_retention_max_batches,
        )
    finally:
        engine.dispose()


def main() -> None:
    from order_service.observability.jsonlog import configure_logging

    configure_logging("order-retention")
    report = run(get_settings())
    logger.info(
        "retention finished orders_deleted=%s order_batches=%s "
        "outbox_deleted=%s outbox_batches=%s "
        "processed_events_deleted=%s processed_event_batches=%s",
        report.orders_deleted,
        report.order_batches,
        report.outbox_deleted,
        report.outbox_batches,
        report.processed_events_deleted,
        report.processed_event_batches,
    )


if __name__ == "__main__":
    main()
