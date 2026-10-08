"""processed_events and inventory_snapshots in one order_db transaction.

A crash before commit leaves neither row. The redelivery tries again.
A crash after commit and before ack redelivers; the insert conflicts; the
consumer acks. The snapshot write cannot commit without the event_id row.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from order_service.application.consuming import ProcessedEvent
from order_service.domain.entities.inventory_snapshot import InventorySnapshot
from order_service.domain.ids import ProductId
from order_service.domain.value_objects import Quantity
from order_service.infrastructure.database.models import InventorySnapshotRow, ProcessedEventRow


class SqlConsumerStore:
    def __init__(self, session: Session) -> None:
        self._session = session

    def insert_if_new(self, record: ProcessedEvent) -> bool:
        statement = (
            pg_insert(ProcessedEventRow)
            .values(
                event_id=record.event_id,
                event_type=record.event_type,
                aggregate_id=record.aggregate_id,
                processed_at=record.processed_at,
                consumer_name=record.consumer_name,
            )
            .on_conflict_do_nothing(index_elements=["event_id"])
            .returning(ProcessedEventRow.event_id)
        )
        inserted = self._session.execute(statement).first()
        return inserted is not None

    def get_snapshot(self, product_id: ProductId) -> InventorySnapshot | None:
        row = self._session.get(InventorySnapshotRow, product_id.value)
        if row is None:
            return None
        return InventorySnapshot(
            product_id=ProductId(row.product_id),
            sku=row.sku,
            on_hand=Quantity.of_stock(row.quantity_on_hand),
            reserved=Quantity.of_stock(row.quantity_reserved),
            warehouse_code=row.warehouse_code,
            source_version=row.source_version,
        )

    def save_snapshot(self, snapshot: InventorySnapshot, updated_at: datetime) -> None:
        row = self._session.get(InventorySnapshotRow, snapshot.product_id.value)
        if row is None:
            self._session.add(
                InventorySnapshotRow(
                    product_id=snapshot.product_id.value,
                    sku=snapshot.sku,
                    quantity_on_hand=snapshot.on_hand.value,
                    quantity_reserved=snapshot.reserved.value,
                    warehouse_code=snapshot.warehouse_code,
                    source_version=snapshot.source_version,
                    updated_at=updated_at,
                )
            )
            return
        row.sku = snapshot.sku
        row.quantity_on_hand = snapshot.on_hand.value
        row.quantity_reserved = snapshot.reserved.value
        row.warehouse_code = snapshot.warehouse_code
        row.source_version = snapshot.source_version
        row.updated_at = updated_at

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
