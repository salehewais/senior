"""Money and quantity. Prices are integers. Binary floats are rejected on purpose."""

from __future__ import annotations

import re
from dataclasses import dataclass

from order_service.domain.exceptions import DomainValidationError

_CURRENCY = re.compile(r"^[A-Z]{3}$")


@dataclass(frozen=True, slots=True)
class Money:
    amount_minor: int
    currency: str

    def __post_init__(self) -> None:
        if isinstance(self.amount_minor, bool) or not isinstance(self.amount_minor, int):
            raise DomainValidationError("amount_minor must be an integer number of minor units.")
        if self.amount_minor < 0:
            raise DomainValidationError("amount_minor cannot be negative.")
        if not isinstance(self.currency, str) or _CURRENCY.fullmatch(self.currency) is None:
            raise DomainValidationError("currency must be a three-letter ISO 4217 code.")

    def plus(self, other: Money) -> Money:
        if other.currency != self.currency:
            raise DomainValidationError("Cannot add money in different currencies.")
        return Money(self.amount_minor + other.amount_minor, self.currency)

    def times(self, quantity: int) -> Money:
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 0:
            raise DomainValidationError("A money multiplier must be a non-negative integer.")
        return Money(self.amount_minor * quantity, self.currency)

    def as_dict(self) -> dict[str, int | str]:
        return {"amount_minor": self.amount_minor, "currency": self.currency}


@dataclass(frozen=True, slots=True)
class Quantity:
    """Order lines are at least 1. Stock snapshots may be zero. Negatives are never legal."""

    value: int

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, int):
            raise DomainValidationError("quantity must be an integer.")
        if self.value < 0:
            raise DomainValidationError("quantity cannot be negative.")

    @classmethod
    def of_line(cls, value: int) -> Quantity:
        quantity = cls(value)
        if quantity.value < 1:
            raise DomainValidationError("An order line quantity must be at least 1.")
        return quantity

    @classmethod
    def of_stock(cls, value: int) -> Quantity:
        return cls(value)
