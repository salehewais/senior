"""Facts the aggregate has already accepted.

The application publishes these after the database commit. The domain does not
import a broker. Phase 6 will also store them in the outbox in the same
transaction as the row. Until then a crash after commit can lose the event.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from order_service.domain.ids import CustomerId, ProductId
from order_service.domain.value_objects import Money


@dataclass(frozen=True, slots=True)
class LineSnapshot:
    product_id: ProductId
    sku: str
    quantity: int
    unit_price: Money


@dataclass(frozen=True, slots=True)
class DomainEvent:
    event_id: uuid.UUID
    occurred_at: datetime
    aggregate_id: uuid.UUID
    aggregate_version: int
    correlation_id: uuid.UUID
    causation_id: uuid.UUID

    @property
    def event_type(self) -> str:
        return type(self).__name__


@dataclass(frozen=True, slots=True)
class OrderCreated(DomainEvent):
    customer_id: CustomerId
    items: tuple[LineSnapshot, ...]
    total: Money


@dataclass(frozen=True, slots=True)
class OrderConfirmed(DomainEvent):
    customer_id: CustomerId
    items: tuple[LineSnapshot, ...]
    total: Money


@dataclass(frozen=True, slots=True)
class OrderCancelled(DomainEvent):
    reason: str


@dataclass(frozen=True, slots=True)
class OrderProcessingStarted(DomainEvent):
    pass


@dataclass(frozen=True, slots=True)
class OrderShipped(DomainEvent):
    tracking_reference: str | None


@dataclass(frozen=True, slots=True)
class OrderDelivered(DomainEvent):
    pass


@dataclass(frozen=True, slots=True)
class ProductCreated(DomainEvent):
    sku: str
    name: str
    unit_price: Money
    active: bool


@dataclass(frozen=True, slots=True)
class ProductUpdated(DomainEvent):
    sku: str
    name: str
    unit_price: Money
    active: bool


@dataclass(frozen=True, slots=True)
class CustomerUpdated(DomainEvent):
    email: str
    display_name: str
