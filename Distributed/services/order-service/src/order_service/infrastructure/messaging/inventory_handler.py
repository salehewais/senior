"""Idempotent InventoryUpdated handler for q.order.inventory.

The processed_events insert and the snapshot write share one transaction.
A duplicate event_id acks and does not change the snapshot. A stale
source_version is stored as processed and does not overwrite a newer row.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from order_service.application.consuming import (
    CONSUMER_ORDER_INVENTORY,
    DeliveryResult,
    ProcessedEvent,
    apply_once,
)
from order_service.application.inventory_update import apply_inventory_payload
from order_service.infrastructure.database.consumer_store import SqlConsumerStore

Clock = Callable[[], datetime]


def _now() -> datetime:
    return datetime.now(UTC)


class InventoryUpdatedHandler:
    def __init__(
        self,
        session_factory: Callable[[], Session],
        *,
        clock: Clock | None = None,
        consumer_name: str = CONSUMER_ORDER_INVENTORY,
    ) -> None:
        self._session_factory = session_factory
        self._clock = clock or _now
        self._consumer_name = consumer_name

    def __call__(self, envelope: dict[str, object]) -> DeliveryResult:
        session = self._session_factory()
        store = SqlConsumerStore(session)
        try:
            record = ProcessedEvent(
                event_id=_uuid(envelope["event_id"]),
                event_type=str(envelope["event_type"]),
                aggregate_id=_uuid(envelope["aggregate_id"]),
                processed_at=self._clock(),
                consumer_name=self._consumer_name,
            )
            updated_at = record.processed_at
            return apply_once(
                store,
                record,
                lambda: apply_inventory_payload(envelope, store, updated_at=updated_at),
            )
        finally:
            session.close()


def _uuid(value: object) -> uuid.UUID:
    if isinstance(value, uuid.UUID):
        return value
    return uuid.UUID(str(value))
