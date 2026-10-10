"""Build an InventoryUpdated envelope. The payload is a full snapshot.

The order-service handler reads product_id, sku, quantity_on_hand,
quantity_reserved, warehouse_code, and aggregate_version. aggregate_id on
the envelope is that product_id. A delta is not representable here: both
quantities are required absolute integers.

Products that never arrived on OrderConfirmed have no commerce product id.
The module does not invent one. The order service keys its snapshot by the
catalog product id, so a random id would be a snapshot nothing reads.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from commerce_erp.domain.ids import uuid7

EVENT_INVENTORY_UPDATED = "InventoryUpdated"
PRODUCER = "odoo"
SCHEMA_VERSION = 1
EXCHANGE_ERP_EVENTS = "erp.events"
ROUTING_KEY_INVENTORY = "inventory.updated"
AGGREGATE_TYPE = "inventory"

# Same columns as order_db.outbox. id is the envelope event_id.
OUTBOX_COLUMNS = (
    "id",
    "event_type",
    "aggregate_type",
    "aggregate_id",
    "payload",
    "created_at",
    "published_at",
    "retry_count",
    "status",
)

OUTBOX_STATEMENTS = (
    """
    CREATE TABLE IF NOT EXISTS commerce_event_outbox (
        id uuid PRIMARY KEY,
        event_type varchar(64) NOT NULL,
        aggregate_type varchar(32) NOT NULL,
        aggregate_id uuid NOT NULL,
        payload jsonb NOT NULL,
        created_at timestamptz NOT NULL,
        published_at timestamptz NULL,
        retry_count integer NOT NULL DEFAULT 0,
        status varchar(16) NOT NULL,
        CONSTRAINT ck_commerce_event_outbox_status CHECK (status IN ('pending', 'published', 'failed'))
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS ix_commerce_event_outbox_pending
        ON commerce_event_outbox (created_at, id)
        WHERE status = 'pending'
    """,
)


def quantity_for_catalog(raw: float) -> int:
    """Round a warehouse float to the non-negative integer the catalog stores.

    The order-service snapshot rejects a negative quantity. A negative Odoo
    sum is published as zero so the event stays a full snapshot the handler
    can apply. The next non-negative count replaces it.
    """

    whole = int(round(float(raw)))
    if whole < 0:
        return 0
    return whole


def build_inventory_updated(
    *,
    product_id: str,
    sku: str,
    on_hand: int,
    reserved: int,
    warehouse_code: str,
    aggregate_version: int,
    correlation_id: str | None = None,
    causation_id: str | None = None,
    occurred_at: datetime | None = None,
    event_id: uuid.UUID | None = None,
) -> dict[str, object]:
    """Return the catalog envelope. Both quantities are the current totals."""

    product = _uuid(product_id)
    if product is None:
        raise ValueError("product_id must be a UUID")
    if not isinstance(sku, str) or not sku.strip() or len(sku) > 64:
        raise ValueError("sku is required")
    if not isinstance(warehouse_code, str) or not warehouse_code.strip() or len(warehouse_code) > 64:
        raise ValueError("warehouse_code is required")
    on_hand_i = _whole(on_hand)
    reserved_i = _whole(reserved)
    version = _whole(aggregate_version)
    if version < 1:
        raise ValueError("aggregate_version starts at 1")
    fact_id = event_id or uuid7()
    thread = _uuid(correlation_id) if correlation_id else str(uuid7())
    cause = _uuid(causation_id) if causation_id else str(uuid7())
    if thread is None or cause is None:
        raise ValueError("correlation_id and causation_id must be UUIDs when set")
    return {
        "event_id": str(fact_id),
        "event_type": EVENT_INVENTORY_UPDATED,
        "occurred_at": _occurred_at(occurred_at or datetime.now(UTC)),
        "producer": PRODUCER,
        "aggregate_id": product,
        "correlation_id": thread,
        "causation_id": cause,
        "version": SCHEMA_VERSION,
        "payload": {
            "product_id": product,
            "sku": sku,
            "quantity_on_hand": on_hand_i,
            "quantity_reserved": reserved_i,
            "warehouse_code": warehouse_code,
            "aggregate_version": version,
        },
    }


def _whole(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("stock counts must be non-negative integers")
    return value


def _uuid(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        return str(uuid.UUID(value))
    except ValueError:
        return None


def _occurred_at(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    text = value.astimezone(UTC).isoformat()
    if text.endswith("+00:00"):
        return text[:-6] + "Z"
    return text
