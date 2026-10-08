#!/usr/bin/env python3
"""
01 — Partitioning
-----------------
Idea: split one huge table into date (or other) partitions so a range query
only scans relevant chunks (partition pruning).

Python analogy: instead of one list of 200M rows, keep a dict of monthly lists
and only touch the months in the WHERE clause.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date

from _demo_data import MoveLine, banner, make_lines


def build_partitions(lines: list[MoveLine]) -> dict[tuple[int, int], list[MoveLine]]:
    parts: dict[tuple[int, int], list[MoveLine]] = defaultdict(list)
    for line in lines:
        key = (line.move_date.year, line.move_date.month)
        parts[key].append(line)
    return parts


def query_without_partition(lines: list[MoveLine], start: date, end: date) -> float:
    """Naive: scan everything (like unpartitioned AML)."""
    scanned = 0
    total = 0.0
    for line in lines:
        scanned += 1
        if start <= line.move_date < end:
            total += line.balance
    print(f"  unpartitioned scan: {scanned:,} rows → balance={total:,.2f}")
    return total


def query_with_partition(
    parts: dict[tuple[int, int], list[MoveLine]], start: date, end: date
) -> float:
    """Prune: only iterate months overlapping [start, end)."""
    scanned = 0
    total = 0.0
    y, m = start.year, start.month
    while date(y, m, 1) < end:
        chunk = parts.get((y, m), [])
        for line in chunk:
            scanned += 1
            if start <= line.move_date < end:
                total += line.balance
        m += 1
        if m == 13:
            m, y = 1, y + 1
    print(f"  partitioned scan:   {scanned:,} rows → balance={total:,.2f}")
    return total


def main() -> None:
    banner("01 Partitioning — prune months instead of scanning all rows")
    lines = make_lines(40_000)
    parts = build_partitions(lines)
    print(f"partitions created: {len(parts)} months")

    start, end = date(2025, 6, 1), date(2025, 7, 1)
    a = query_without_partition(lines, start, end)
    b = query_with_partition(parts, start, end)
    assert abs(a - b) < 1e-6
    print("\nTrade-off: fewer rows scanned, but Odoo FK/ORM/upgrades make real"
          " AML partitioning hard — study before production.")


if __name__ == "__main__":
    main()
