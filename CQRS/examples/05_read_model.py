#!/usr/bin/env python3
"""
05 — Read Model
---------------
Idea: keep a write model (transactional lines) and a separate read model shaped
exactly for queries (CQRS light).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from _demo_data import MoveLine, banner, make_lines


@dataclass
class DailyBalanceReadModel:
    """Optimized for: balance by date × branch × account."""

    rows: dict[tuple[str, int, int], float]

    @classmethod
    def from_write_model(cls, lines: list[MoveLine]) -> "DailyBalanceReadModel":
        agg: dict[tuple[str, int, int], float] = defaultdict(float)
        for l in lines:
            key = (l.move_date.isoformat(), l.branch_id, l.account_id)
            agg[key] += l.balance
        return cls(dict(agg))

    def branch_total(self, branch_id: int, day: str) -> float:
        return sum(
            bal
            for (d, b, _acc), bal in self.rows.items()
            if d == day and b == branch_id
        )


def main() -> None:
    banner("05 Read Model — report reads a projection, not AML")
    write_model = make_lines(20_000)
    read_model = DailyBalanceReadModel.from_write_model(write_model)

    day = "2025-03-15"
    # Slow path: scan write model
    slow = sum(l.balance for l in write_model if l.move_date.isoformat() == day and l.branch_id == 2)
    # Fast path: read model
    fast = read_model.branch_total(2, day)
    print(f"write-model scan branch=2 day={day}: {slow:,.2f} (touched {len(write_model):,} rows)")
    print(f"read-model lookup:                 {fast:,.2f} (keys={len(read_model.rows):,})")
    assert abs(slow - fast) < 1e-6
    print("\nTrade-off: must refresh/rebuild read model; eventual consistency.")


if __name__ == "__main__":
    main()
