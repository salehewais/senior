#!/usr/bin/env python3
"""
19 — Connection / Workload Control
----------------------------------
Semaphore / pool so 50 users cannot open 50 full AML scans at once.
Safety net — not a substitute for good report design.
"""

from __future__ import annotations

import threading
import time

from _demo_data import banner, make_lines

LINES = make_lines(8_000)
DB_SLOTS = threading.Semaphore(3)  # max 3 concurrent heavy queries


def run_user_report(user_id: int, results: list) -> None:
    print(f"  user{user_id} waiting for DB slot…")
    with DB_SLOTS:
        print(f"  user{user_id} acquired connection")
        time.sleep(0.15)
        total = sum(l.balance for l in LINES if l.branch_id == (user_id % 5) + 1)
        results.append((user_id, total))
        print(f"  user{user_id} done")


def main() -> None:
    banner("19 Connection Control — semaphore caps concurrent scans")
    results: list = []
    threads = [
        threading.Thread(target=run_user_report, args=(i, results)) for i in range(1, 9)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"finished {len(results)} reports with max 3 concurrent DB slots")
    print("\nTrade-off: queueing delay under load — combine with async UX.")


if __name__ == "__main__":
    main()
