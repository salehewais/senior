"""Local stock picture. Odoo remains the warehouse authority.

The inventory consumer persists this when a newer InventoryUpdated arrives.
An older source_version is ignored, because the payload is a full snapshot
and the next newer one heals a gap. Odoo writes that snapshot through
the inventory outbox in odoo_db.
"""

from __future__ import annotations

from dataclasses import dataclass

from order_service.domain.exceptions import DomainValidationError
from order_service.domain.ids import ProductId
from order_service.domain.value_objects import Quantity


@dataclass
class InventorySnapshot:
    product_id: ProductId
    sku: str
    on_hand: Quantity
    reserved: Quantity
    warehouse_code: str
    source_version: int

    def __post_init__(self) -> None:
        if not isinstance(self.source_version, int) or isinstance(self.source_version, bool):
            raise DomainValidationError("source_version must be an integer.")
        if self.source_version < 1:
            raise DomainValidationError("source_version starts at 1.")
        if not self.warehouse_code.strip():
            raise DomainValidationError("warehouse_code is required.")
        if not self.sku.strip():
            raise DomainValidationError("sku is required.")

    def apply(self, newer: InventorySnapshot) -> bool:
        if newer.product_id != self.product_id:
            raise DomainValidationError("A snapshot can only be applied to the same product.")
        if newer.source_version <= self.source_version:
            return False
        self.sku = newer.sku
        self.on_hand = newer.on_hand
        self.reserved = newer.reserved
        self.warehouse_code = newer.warehouse_code
        self.source_version = newer.source_version
        return True
