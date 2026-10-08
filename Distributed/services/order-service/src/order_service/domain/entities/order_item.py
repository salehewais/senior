"""Order lines belong to the order aggregate. They are not a separate consistency boundary."""

from __future__ import annotations

from dataclasses import dataclass

from order_service.domain.events import LineSnapshot
from order_service.domain.ids import ProductId
from order_service.domain.value_objects import Money, Quantity


@dataclass(frozen=True, slots=True)
class OrderItem:
    product_id: ProductId
    sku: str
    quantity: Quantity
    unit_price: Money

    def line_total(self) -> Money:
        return self.unit_price.times(self.quantity.value)

    def snapshot(self) -> LineSnapshot:
        return LineSnapshot(
            product_id=self.product_id,
            sku=self.sku,
            quantity=self.quantity.value,
            unit_price=self.unit_price,
        )
