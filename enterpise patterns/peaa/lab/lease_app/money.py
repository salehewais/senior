"""Money value object. قيمة نقدية بالمليم/السنت من غير float."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    cents: int
    currency: str = "USD"

    def __post_init__(self) -> None:
        if self.currency != "USD":
            raise ValueError(f"unsupported currency {self.currency}")

    def __add__(self, other: Money) -> Money:
        self._same(other)
        return Money(self.cents + other.cents, self.currency)

    def __sub__(self, other: Money) -> Money:
        self._same(other)
        return Money(self.cents - other.cents, self.currency)

    def __mul__(self, factor: int) -> Money:
        return Money(self.cents * factor, self.currency)

    def _same(self, other: Money) -> None:
        if not isinstance(other, Money) or other.currency != self.currency:
            raise ValueError("currency mismatch")

    def __str__(self) -> str:
        sign = "-" if self.cents < 0 else ""
        cents = abs(self.cents)
        return f"{sign}{self.currency} {cents // 100}.{cents % 100:02d}"
