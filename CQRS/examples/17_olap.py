#!/usr/bin/env python3
"""
17 — OLAP (cube-style aggregations)
-----------------------------------
Roll up / slice / dice across dimensions (branch × month × account).
"""

from __future__ import annotations

from collections import defaultdict

from _demo_data import banner, make_lines


def build_cube(lines):
    """cell key: (branch, month, account) → balance"""
    cube: dict[tuple[int, int, int], float] = defaultdict(float)
    for l in lines:
        cube[(l.branch_id, l.move_date.month, l.account_id)] += l.balance
    return cube


def rollup_by_branch(cube) -> dict[int, float]:
    out: dict[int, float] = defaultdict(float)
    for (branch, _month, _account), bal in cube.items():
        out[branch] += bal
    return dict(out)


def slice_month(cube, month: int) -> dict[int, float]:
    out: dict[int, float] = defaultdict(float)
    for (branch, m, _account), bal in cube.items():
        if m == month:
            out[branch] += bal
    return dict(out)


def main() -> None:
    banner("17 OLAP — slice/dice multidimensional aggregates")
    cube = build_cube(make_lines(30_000))
    print(f"cube cells: {len(cube):,}")
    print("rollup by branch:", {k: round(v, 1) for k, v in rollup_by_branch(cube).items()})
    print("slice month=6:", {k: round(v, 1) for k, v in slice_month(cube, 6).items()})
    print("\nTrade-off: overkill for a few Odoo reports; belongs with warehouse/BI.")


if __name__ == "__main__":
    main()
