"""The only legal order transitions. Controllers do not get a copy of this table."""

from __future__ import annotations

from enum import StrEnum

from order_service.domain.exceptions import InvalidStateTransition


class OrderStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


ALLOWED_TRANSITIONS: frozenset[tuple[OrderStatus, OrderStatus]] = frozenset(
    {
        (OrderStatus.PENDING, OrderStatus.CONFIRMED),
        (OrderStatus.PENDING, OrderStatus.CANCELLED),
        (OrderStatus.CONFIRMED, OrderStatus.PROCESSING),
        (OrderStatus.PROCESSING, OrderStatus.SHIPPED),
        (OrderStatus.SHIPPED, OrderStatus.DELIVERED),
    }
)


def require_transition(current: OrderStatus, target: OrderStatus) -> None:
    if (current, target) not in ALLOWED_TRANSITIONS:
        raise InvalidStateTransition(
            f"An order in {current.value} cannot move to {target.value}."
        )
