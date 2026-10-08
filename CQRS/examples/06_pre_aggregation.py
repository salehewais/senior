#!/usr/bin/env python3
"""
06 — Pre-Aggregation  (highest ROI for ~200M)
---------------------------------------------
Compute SUM/GROUP BY once into a summary; many reports reuse it.
"""

from __future__ import annotations

import time
from collections import defaultdict

from _demo_data import banner, make_lines


def report_from_raw(lines, branch_id: int) -> float:
    return sum(l.balance for l in lines if l.branch_id == branch_id)


def build_daily_summary(lines):
    """date × company × branch × account"""
    summary: dict[tuple, float] = defaultdict(float)
    for l in lines:
        key = (l.move_date, l.company_id, l.branch_id, l.account_id)
        summary[key] += l.balance
    return summary


def report_from_summary(summary, branch_id: int) -> float:
    return sum(bal for (_d, _c, b, _a), bal in summary.items() if b == branch_id)


def main() -> None:
    banner("06 Pre-Aggregation — pay once, read many times")
    lines = make_lines(80_000)

    t0 = time.perf_counter()
    # 10 accountants each run the same heavy report from raw AML
    totals_raw = [report_from_raw(lines, branch_id=1) for _ in range(10)]
    raw_s = time.perf_counter() - t0

    t0 = time.perf_counter()
    summary = build_daily_summary(lines)
    build_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    totals_sum = [report_from_summary(summary, branch_id=1) for _ in range(10)]
    read_s = time.perf_counter() - t0

    print(f"10× report from raw AML:     {raw_s:.3f}s  result={totals_raw[0]:,.2f}")
    print(f"build summary once:          {build_s:.3f}s  keys={len(summary):,}")
    print(f"10× report from summary:     {read_s:.3f}s  result={totals_sum[0]:,.2f}")
    print("\nTrade-off: Analytical freshness depends on refresh schedule (as-of).")


if __name__ == "__main__":
    main()
