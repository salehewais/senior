"""The Odoo inventory envelope is the snapshot the order-service handler applies."""

from __future__ import annotations

import sys
from pathlib import Path

from order_service.application.inventory_update import snapshot_from_envelope
from order_service.domain.entities.inventory_snapshot import InventorySnapshot

PRODUCT_ID = "018f1c2a-5555-7c11-8a22-666666666666"


def test_odoo_snapshot_matches_the_inventory_handler() -> None:
    odoo_src = Path(__file__).resolve().parents[3] / "odoo" / "src"
    if str(odoo_src) not in sys.path:
        sys.path.insert(0, str(odoo_src))
    from commerce_erp.inventory import build_inventory_updated

    current = snapshot_from_envelope(
        build_inventory_updated(
            product_id=PRODUCT_ID,
            sku="MUG-01",
            on_hand=10,
            reserved=2,
            warehouse_code="WH",
            aggregate_version=4,
        )
    )
    incoming = snapshot_from_envelope(
        build_inventory_updated(
            product_id=PRODUCT_ID,
            sku="MUG-01",
            on_hand=7,
            reserved=1,
            warehouse_code="WH",
            aggregate_version=5,
        )
    )

    assert isinstance(current, InventorySnapshot)
    assert str(current.product_id.value) == PRODUCT_ID
    assert current.on_hand.value == 10
    assert current.reserved.value == 2
    assert current.warehouse_code == "WH"
    assert current.apply(incoming)
    assert current.on_hand.value == 7
    assert current.reserved.value == 1
    assert current.source_version == 5
