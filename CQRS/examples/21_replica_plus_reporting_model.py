#!/usr/bin/env python3
"""
21 — Read Replica + Reporting Model (Hybrid)
--------------------------------------------
Exact reports → replica (ledger shape, lag-gated).
Analytical reports → pre-aggregated read model (cheap).
"""

from __future__ import annotations

from collections import defaultdict

from _demo_data import banner, make_lines


def main() -> None:
    banner("21 Hybrid — Exact on replica, Analytical on read model")
    primary = make_lines(12_000)
    replica = list(primary)  # same rows

    # build reporting model from replica (ETL source)
    model: dict[int, float] = defaultdict(float)
    for l in replica:
        model[l.branch_id] += l.balance

    def exact_trial_balance_stub():
        # still ledger-shaped scan on replica (correctness first)
        return sum(l.balance for l in replica)

    def analytical_branch_kpi(branch_id: int):
        return model[branch_id]

    print(f"EXACT trial balance on replica: {exact_trial_balance_stub():,.2f}")
    print(f"ANALYTICAL KPI branch 2 on model: {analytical_branch_kpi(2):,.2f}")
    print("routing: exact→REPLICA_DSN  analytical→REPORTING_DSN/summary")
    print("\nTrade-off: never serve statutory Exact from unverified reporting model.")


if __name__ == "__main__":
    main()
