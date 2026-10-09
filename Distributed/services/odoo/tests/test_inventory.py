"""InventoryUpdated is a full snapshot with the fields the order service reads."""

from __future__ import annotations

from commerce_erp.inventory import (
    OUTBOX_COLUMNS,
    OUTBOX_STATEMENTS,
    build_inventory_updated,
    quantity_for_catalog,
)

PRODUCT_ID = "018f1c2a-5555-7c11-8a22-666666666666"
CORRELATION_ID = "018f1c2a-3333-7c11-8a22-444444444444"
CAUSATION_ID = "018f1c2a-7b3d-7c11-8a22-111111111111"


def test_inventory_payload_is_a_full_snapshot() -> None:
    first = build_inventory_updated(
        product_id=PRODUCT_ID,
        sku="MUG-01",
        on_hand=10,
        reserved=2,
        warehouse_code="WH",
        aggregate_version=4,
        correlation_id=CORRELATION_ID,
        causation_id=CAUSATION_ID,
    )
    later = build_inventory_updated(
        product_id=PRODUCT_ID,
        sku="MUG-01",
        on_hand=7,
        reserved=0,
        warehouse_code="WH",
        aggregate_version=5,
        correlation_id=CORRELATION_ID,
        causation_id=CAUSATION_ID,
    )

    assert first["event_type"] == "InventoryUpdated"
    assert first["producer"] == "odoo"
    assert first["version"] == 1
    assert first["aggregate_id"] == PRODUCT_ID
    payload = first["payload"]
    assert isinstance(payload, dict)
    assert payload == {
        "product_id": PRODUCT_ID,
        "sku": "MUG-01",
        "quantity_on_hand": 10,
        "quantity_reserved": 2,
        "warehouse_code": "WH",
        "aggregate_version": 4,
    }
    assert "quantity_delta" not in payload
    later_payload = later["payload"]
    assert isinstance(later_payload, dict)
    assert later_payload["quantity_on_hand"] == 7
    assert later_payload["quantity_reserved"] == 0
    assert set(later_payload) == set(payload)


def test_negative_warehouse_float_becomes_zero() -> None:
    assert quantity_for_catalog(-2.2) == 0
    assert quantity_for_catalog(10.4) == 10


def test_outbox_columns_match_the_order_service_outbox() -> None:
    ddl = "\n".join(OUTBOX_STATEMENTS)
    for column in OUTBOX_COLUMNS:
        assert column in ddl
    assert "commerce_event_outbox" in ddl
    assert "pending" in ddl and "published" in ddl and "failed" in ddl
