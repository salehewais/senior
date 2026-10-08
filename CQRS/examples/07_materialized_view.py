#!/usr/bin/env python3
"""
07 — Materialized View
----------------------
A view whose result is stored and refreshed on a schedule (not on every read).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from _demo_data import banner, make_lines


@dataclass
class MaterializedView:
    name: str
    data: dict = field(default_factory=dict)
    refreshed_at: str | None = None

    def refresh(self, lines, clock: str) -> None:
        agg: dict[tuple[int, int], float] = defaultdict(float)
        for l in lines:
            agg[(l.branch_id, l.move_date.month)] += l.balance
        self.data = dict(agg)
        self.refreshed_at = clock
        print(f"REFRESH MATERIALIZED VIEW {self.name} at {clock} → {len(self.data)} groups")

    def select_branch(self, branch_id: int) -> float:
        return sum(v for (b, _m), v in self.data.items() if b == branch_id)


def main() -> None:
    banner("07 Materialized View — store query result, refresh later")
    lines = make_lines(25_000)
    mv = MaterializedView("branch_month_balance")

    mv.refresh(lines, clock="10:00")
    print(f"  report reads MV branch=1 → {mv.select_branch(1):,.2f} (as_of={mv.refreshed_at})")

    # new postings land in write model; MV is stale until refresh
    lines.extend(make_lines(1_000)[:100])
    print("  100 new lines written to AML… MV still shows old total until REFRESH")
    print(f"  stale read → {mv.select_branch(1):,.2f} as_of={mv.refreshed_at}")

    mv.refresh(lines, clock="10:15")
    print(f"  after refresh → {mv.select_branch(1):,.2f} as_of={mv.refreshed_at}")
    print("\nTrade-off: great when minutes of lag are OK; full refresh can be costly.")


if __name__ == "__main__":
    main()
