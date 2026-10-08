"""Shapes returned to the presentation layer. They carry data, not behavior."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from order_service.domain.entities.catalog import Customer, Product
from order_service.domain.entities.order import Order


@dataclass(frozen=True, slots=True)
class MoneyView:
    amount_minor: int
    currency: str


@dataclass(frozen=True, slots=True)
class OrderItemView:
    product_id: uuid.UUID
    sku: str
    quantity: int
    unit_price: MoneyView


@dataclass(frozen=True, slots=True)
class OrderView:
    id: uuid.UUID
    customer_id: uuid.UUID
    status: str
    saga_status: str | None
    items: tuple[OrderItemView, ...]
    total: MoneyView
    version: int
    tracking_reference: str | None
    cancel_reason: str | None
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ProductView:
    id: uuid.UUID
    sku: str
    name: str
    unit_price: MoneyView
    active: bool
    version: int


@dataclass(frozen=True, slots=True)
class CustomerView:
    id: uuid.UUID
    email: str
    display_name: str
    version: int
    created_at: datetime


@dataclass(frozen=True, slots=True)
class PageView:
    items: tuple[object, ...]
    next_cursor: str | None


def order_view(order: Order) -> OrderView:
    return OrderView(
        id=order.id.value,
        customer_id=order.customer_id.value,
        status=order.status.value,
        saga_status=order.saga_status,
        items=tuple(
            OrderItemView(
                product_id=item.product_id.value,
                sku=item.sku,
                quantity=item.quantity.value,
                unit_price=MoneyView(item.unit_price.amount_minor, item.unit_price.currency),
            )
            for item in order.items
        ),
        total=MoneyView(order.total.amount_minor, order.total.currency),
        version=order.version,
        tracking_reference=order.tracking_reference,
        cancel_reason=order.cancel_reason,
        created_at=order.created_at,
    )


def product_view(product: Product) -> ProductView:
    return ProductView(
        id=product.id.value,
        sku=product.sku,
        name=product.name,
        unit_price=MoneyView(product.unit_price.amount_minor, product.unit_price.currency),
        active=product.active,
        version=product.version,
    )


def customer_view(customer: Customer) -> CustomerView:
    return CustomerView(
        id=customer.id.value,
        email=customer.email,
        display_name=customer.display_name,
        version=customer.version,
        created_at=customer.created_at,
    )
