#!/usr/bin/env python3
"""
18 — Database / Resource Isolation
----------------------------------
Give OLTP and reporting separate resource budgets (processes/pools),
so a heavy report cannot consume all CPU for POS.
"""

from __future__ import annotations

import concurrent.futures
import os
import time

from _demo_data import banner, make_lines


def pos_checkout(_: int) -> str:
    time.sleep(0.02)
    return f"pos-ok@{os.getpid()}"


def heavy_report(_: int) -> str:
    lines = make_lines(25_000)
    total = sum(l.balance for l in lines)
    return f"report={total:.0f}@{os.getpid()}"


def main() -> None:
    banner("18 Resource Isolation — separate executor pools")
    # Two pools ≈ two machines / cgroups
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pos_pool, \
         concurrent.futures.ProcessPoolExecutor(max_workers=1) as report_pool:
        pos_futs = [pos_pool.submit(pos_checkout, i) for i in range(6)]
        rep_fut = report_pool.submit(heavy_report, 0)
        print("POS results:", [f.result() for f in pos_futs])
        print("Report result:", rep_fut.result())
    print("\nTrade-off: infra cost; still need caps + aggregation for scale.")


if __name__ == "__main__":
    main()
