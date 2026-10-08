#!/usr/bin/env python3
"""
20 — Async + Pre-Aggregation
----------------------------
Best operational combo for summaries: workers update aggregates; reports read cheap tables.
"""

from __future__ import annotations

import queue
import threading
from collections import defaultdict

from _demo_data import banner


def main() -> None:
    banner("20 Async + Pre-Aggregation — event worker maintains summary")
    summary: dict[tuple[str, int], float] = defaultdict(float)
    q: queue.Queue = queue.Queue()

    def worker() -> None:
        while True:
            ev = q.get()
            if ev is None:
                break
            key = (ev["date"], ev["branch_id"])
            summary[key] += ev["amount"]
            print(f"  agg worker: {key} → {summary[key]}")
            q.task_done()

    threading.Thread(target=worker, daemon=True).start()

    # many invoices posted
    for i, amount in enumerate((100, 250, 50), start=1):
        q.put({"date": "2026-10-07", "branch_id": 1, "amount": amount, "id": i})
    q.join()

    # report is a cheap read
    print(f"REPORT select summary: {dict(summary)}")
    q.put(None)
    print("\nTrade-off: monitor worker failures; nightly reconcile still required.")


if __name__ == "__main__":
    main()
