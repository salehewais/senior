"""Order aggregate. Status changes only through the methods below."""

from __future__ import annotations

import uuid
from datetime import datetime

from order_service.domain.entities.order_item import OrderItem
from order_service.domain.entities.order_status import OrderStatus, require_transition
from order_service.domain.events import (
    DomainEvent,
    OrderCancelled,
    OrderConfirmed,
    OrderCreated,
    OrderDelivered,
    OrderProcessingStarted,
    OrderShipped,
    PaymentConfirmed,
    PaymentFailed,
)
from order_service.domain.exceptions import DomainValidationError, InvalidStateTransition
from order_service.domain.ids import CustomerId, OrderId, uuid7
from order_service.domain.value_objects import Money

CANCEL_REASONS = frozenset({"customer_request", "staff_request"})
PAYMENT_REASON_CODES = frozenset({"declined", "timeout", "circuit_open", "provider_error"})


class Order:
    def __init__(
        self,
        *,
        order_id: OrderId,
        customer_id: CustomerId,
        status: OrderStatus,
        items: tuple[OrderItem, ...],
        total: Money,
        version: int,
        created_at: datetime,
        updated_at: datetime,
        tracking_reference: str | None = None,
        cancel_reason: str | None = None,
        saga_status: str | None = None,
        loaded_version: int | None = None,
    ) -> None:
        self.id = order_id
        self.customer_id = customer_id
        self.status = status
        self.items = items
        self.total = total
        self.version = version
        self.created_at = created_at
        self.updated_at = updated_at
        self.tracking_reference = tracking_reference
        self.cancel_reason = cancel_reason
        # Null until confirm starts a saga. The saga row is the record; this field mirrors it.
        self.saga_status = saga_status
        self._loaded_version = loaded_version
        self._events: list[DomainEvent] = []

    @property
    def loaded_version(self) -> int | None:
        return self._loaded_version

    def acknowledge_persisted(self) -> None:
        self._loaded_version = self.version

    def collect_events(self) -> list[DomainEvent]:
        events = list(self._events)
        self._events.clear()
        return events

    def pending_events(self) -> tuple[DomainEvent, ...]:
        return tuple(self._events)

    @classmethod
    def create(
        cls,
        *,
        customer_id: CustomerId,
        items: tuple[OrderItem, ...],
        now: datetime,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
        order_id: OrderId | None = None,
    ) -> Order:
        if not items:
            raise DomainValidationError("An order needs at least one item.")
        currencies = {item.unit_price.currency for item in items}
        if len(currencies) != 1:
            raise DomainValidationError("Every line on an order must use the same currency.")
        total = items[0].line_total()
        for item in items[1:]:
            total = total.plus(item.line_total())
        order = cls(
            order_id=order_id or OrderId.generate(),
            customer_id=customer_id,
            status=OrderStatus.PENDING,
            items=items,
            total=total,
            version=1,
            created_at=now,
            updated_at=now,
        )
        order._record(
            OrderCreated(
                event_id=uuid7(),
                occurred_at=now,
                aggregate_id=order.id.value,
                aggregate_version=order.version,
                correlation_id=correlation_id,
                causation_id=causation_id,
                customer_id=customer_id,
                items=tuple(item.snapshot() for item in items),
                total=total,
            )
        )
        return order

    @classmethod
    def reconstitute(
        cls,
        *,
        order_id: OrderId,
        customer_id: CustomerId,
        status: OrderStatus,
        items: tuple[OrderItem, ...],
        total: Money,
        version: int,
        created_at: datetime,
        updated_at: datetime,
        tracking_reference: str | None,
        cancel_reason: str | None,
        saga_status: str | None,
    ) -> Order:
        return cls(
            order_id=order_id,
            customer_id=customer_id,
            status=status,
            items=items,
            total=total,
            version=version,
            created_at=created_at,
            updated_at=updated_at,
            tracking_reference=tracking_reference,
            cancel_reason=cancel_reason,
            saga_status=saga_status,
            loaded_version=version,
        )

    def confirm(
        self,
        *,
        now: datetime,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> None:
        self._move(OrderStatus.CONFIRMED, now)
        self._record(
            OrderConfirmed(
                event_id=uuid7(),
                occurred_at=now,
                aggregate_id=self.id.value,
                aggregate_version=self.version,
                correlation_id=correlation_id,
                causation_id=causation_id,
                customer_id=self.customer_id,
                items=tuple(item.snapshot() for item in self.items),
                total=self.total,
            )
        )

    def cancel(
        self,
        *,
        reason: str,
        now: datetime,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> None:
        if reason not in CANCEL_REASONS:
            raise DomainValidationError("reason must be customer_request or staff_request.")
        self._move(OrderStatus.CANCELLED, now)
        self.cancel_reason = reason
        self._record(
            OrderCancelled(
                event_id=uuid7(),
                occurred_at=now,
                aggregate_id=self.id.value,
                aggregate_version=self.version,
                correlation_id=correlation_id,
                causation_id=causation_id,
                reason=reason,
            )
        )

    def start_processing(
        self,
        *,
        now: datetime,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> None:
        self._move(OrderStatus.PROCESSING, now)
        self._record(
            OrderProcessingStarted(
                event_id=uuid7(),
                occurred_at=now,
                aggregate_id=self.id.value,
                aggregate_version=self.version,
                correlation_id=correlation_id,
                causation_id=causation_id,
            )
        )

    def ship(
        self,
        *,
        tracking_reference: str | None,
        now: datetime,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> None:
        cleaned = _clean_tracking_reference(tracking_reference)
        self._move(OrderStatus.SHIPPED, now)
        self.tracking_reference = cleaned
        self._record(
            OrderShipped(
                event_id=uuid7(),
                occurred_at=now,
                aggregate_id=self.id.value,
                aggregate_version=self.version,
                correlation_id=correlation_id,
                causation_id=causation_id,
                tracking_reference=cleaned,
            )
        )

    def set_saga_status(self, status: str | None) -> None:
        self.saga_status = status

    def record_payment_confirmed(
        self,
        *,
        payment_reference: str,
        now: datetime,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> None:
        if self.status is not OrderStatus.CONFIRMED:
            raise InvalidStateTransition(
                f"An order in {self.status.value} cannot record a payment."
            )
        self.version += 1
        self.updated_at = now
        self._record(
            PaymentConfirmed(
                event_id=uuid7(),
                occurred_at=now,
                aggregate_id=self.id.value,
                aggregate_version=self.version,
                correlation_id=correlation_id,
                causation_id=causation_id,
                payment_reference=payment_reference,
                amount=self.total,
            )
        )

    def record_payment_failed(
        self,
        *,
        reason_code: str,
        now: datetime,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> None:
        if reason_code not in PAYMENT_REASON_CODES:
            raise DomainValidationError("reason_code is not a version-1 payment failure.")
        if self.status is not OrderStatus.CONFIRMED:
            raise InvalidStateTransition(
                f"An order in {self.status.value} cannot record a payment."
            )
        self.version += 1
        self.updated_at = now
        self._record(
            PaymentFailed(
                event_id=uuid7(),
                occurred_at=now,
                aggregate_id=self.id.value,
                aggregate_version=self.version,
                correlation_id=correlation_id,
                causation_id=causation_id,
                reason_code=reason_code,
            )
        )

    def deliver(
        self,
        *,
        now: datetime,
        correlation_id: uuid.UUID,
        causation_id: uuid.UUID,
    ) -> None:
        self._move(OrderStatus.DELIVERED, now)
        self._record(
            OrderDelivered(
                event_id=uuid7(),
                occurred_at=now,
                aggregate_id=self.id.value,
                aggregate_version=self.version,
                correlation_id=correlation_id,
                causation_id=causation_id,
            )
        )

    def _move(self, target: OrderStatus, now: datetime) -> None:
        require_transition(self.status, target)
        self.status = target
        self.version += 1
        self.updated_at = now

    def _record(self, event: DomainEvent) -> None:
        self._events.append(event)


def _clean_tracking_reference(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    if len(cleaned) > 128:
        raise DomainValidationError("tracking_reference cannot be longer than 128 characters.")
    return cleaned
