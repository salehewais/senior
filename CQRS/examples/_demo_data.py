"""Tiny fake accounting dataset shared by the examples (stdlib only)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable


@dataclass(frozen=True)
class MoveLine:
    id: int
    move_date: date
    company_id: int
    branch_id: int
    account_id: int
    debit: float
    credit: float
    product_id: int | None = None

    @property
    def balance(self) -> float:
        return self.debit - self.credit


def make_lines(n: int = 50_000, seed: int = 7) -> list[MoveLine]:
    """Generate n fake posted AML-like rows across ~3 years / 5 branches."""
    lines: list[MoveLine] = []
    start = date(2024, 1, 1)
    for i in range(1, n + 1):
        d = start + timedelta(days=(i * seed) % 900)
        branch = (i % 5) + 1
        account = 1000 + (i % 40)
        debit = float((i * 13) % 500)
        credit = float((i * 7) % 300)
        product = (i % 20) + 1 if i % 3 == 0 else None
        lines.append(
            MoveLine(
                id=i,
                move_date=d,
                company_id=1,
                branch_id=branch,
                account_id=account,
                debit=debit,
                credit=credit,
                product_id=product,
            )
        )
    return lines


def filter_month(lines: Iterable[MoveLine], year: int, month: int) -> list[MoveLine]:
    return [l for l in lines if l.move_date.year == year and l.move_date.month == month]


def banner(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
