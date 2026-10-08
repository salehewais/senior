from order_service.domain.entities.catalog import Customer, Product
from order_service.domain.entities.inventory_snapshot import InventorySnapshot
from order_service.domain.entities.order import Order
from order_service.domain.entities.order_item import OrderItem
from order_service.domain.entities.order_status import ALLOWED_TRANSITIONS, OrderStatus

__all__ = [
    "ALLOWED_TRANSITIONS",
    "Customer",
    "InventorySnapshot",
    "Order",
    "OrderItem",
    "OrderStatus",
    "Product",
]
