#!/usr/bin/env python3
"""
08 — Cache
----------
If many users request the same parameters, serve from cache (Redis/app).
Does not help when every query is unique.
"""

from __future__ import annotations

import time
from functools import lru_cache

from _demo_data import banner, make_lines

LINES = make_lines(40_000)


def expensive_report(branch_id: int, year: int, month: int) -> float:
    time.sleep(0.05)  # stand-in for heavy SQL
    return sum(
        l.balance
        for l in LINES
        if l.branch_id == branch_id
        and l.move_date.year == year
        and l.move_date.month == month
    )


@lru_cache(maxsize=128)
def cached_report(branch_id: int, year: int, month: int) -> float:
    return expensive_report(branch_id, year, month)


def main() -> None:
    banner("08 Cache — identical params hit memory, not DB")
    t0 = time.perf_counter()
    for _ in range(8):
        expensive_report(1, 2025, 6)
    no_cache = time.perf_counter() - t0

    t0 = time.perf_counter()
    for _ in range(8):
        cached_report(1, 2025, 6)
    with_cache = time.perf_counter() - t0

    print(f"8 identical reports without cache: {no_cache:.3f}s")
    print(f"8 identical reports with cache:    {with_cache:.3f}s")
    print(f"cache info: {cached_report.cache_info()}")
    print("\nTrade-off: useless if every user has different filters; not a substitute for pre-agg.")


if __name__ == "__main__":
    main()
