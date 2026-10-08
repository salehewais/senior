"""Apply one InventoryUpdated envelope onto the local snapshot.

Odoo remains the warehouse authority. This write is the order service's copy.
An older source_version is ignored: the payload is a full snapshot, and the
next newer one heals a gap. That decision is an ack, not a retry.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Protocol

from order_service.application.consuming import PermanentMessageError
from order_service.domain.entities.inventory_snapshot import InventorySnapshot
from order_service.domain.exceptions import DomainValidationError
from order_service.domain.ids import ProductId
from order_service.domain.value_objects import Quantity

REASON_INVALID_INVENTORY = "invalid-inventory-payload"


class SnapshotWriter(Protocol):
    def get_snapshot(self, product_id: ProductId) -> InventorySnapshot | None: ...

    def save_snapshot(self, snapshot: InventorySnapshot, updated_at: datetime) -> None: ...


def apply_inventory_payload(envelope: dict[str, object], snapshots: SnapshotWriter, *, updated_at: datetime) -> None:
    """Upsert when the incoming source_version is newer. Raise when it can never apply."""

    incoming = snapshot_from_envelope(envelope)
    current = snapshots.get_snapshot(incoming.product_id)
    if current is None:
        snapshots.save_snapshot(incoming, updated_at)
        return
    if current.apply(incoming):
        snapshots.save_snapshot(current, updated_at)


def snapshot_from_envelope(envelope: dict[str, object]) -> InventorySnapshot:
    payload = envelope.get("payload")
    if not isinstance(payload, dict):
        raise PermanentMessageError(REASON_INVALID_INVENTORY)
    aggregate_id = _uuid(envelope.get("aggregate_id"))
    product_raw = payload.get("product_id")
    product_id = _uuid(product_raw)
    if aggregate_id is None or product_id is None or aggregate_id != product_id:
        raise PermanentMessageError(REASON_INVALID_INVENTORY)
    try:
        return InventorySnapshot(
            product_id=ProductId(product_id),
            sku=_text(payload.get("sku")),
            on_hand=Quantity.of_stock(_whole(payload.get("quantity_on_hand"))),
            reserved=Quantity.of_stock(_whole(payload.get("quantity_reserved"))),
            warehouse_code=_text(payload.get("warehouse_code")),
            source_version=_whole(payload.get("aggregate_version")),
        )
    except (PermanentMessageError, DomainValidationError, ValueError) as exc:
        if isinstance(exc, PermanentMessageError):
            raise
        raise PermanentMessageError(REASON_INVALID_INVENTORY) from exc


def _uuid(value: object) -> uuid.UUID | None:
    if not isinstance(value, str):
        return None
    try:
        return uuid.UUID(value)
    except ValueError:
        return None


def _text(value: object) -> str:
    if not isinstance(value, str):
        raise PermanentMessageError(REASON_INVALID_INVENTORY)
    return value


def _whole(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise PermanentMessageError(REASON_INVALID_INVENTORY)
    return value
