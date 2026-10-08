#!/usr/bin/env python3
"""
13 — CQRS + Event-Driven
------------------------
Commands → write model → commit → event → queue → worker → read model → reports.
"""

from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass, field

from _demo_data import banner


@dataclass
class WriteModel:
    invoices: list[dict] = field(default_factory=list)

    def post(self, inv: dict) -> dict:
        inv = {**inv, "state": "posted"}
        self.invoices.append(inv)
        return inv


@dataclass
class ReadModel:
    revenue_by_branch: dict[int, float] = field(default_factory=dict)

    def apply_invoice_posted(self, inv: dict) -> None:
        b = inv["branch_id"]
        self.revenue_by_branch[b] = self.revenue_by_branch.get(b, 0.0) + inv["amount"]


def main() -> None:
    banner("13 CQRS + Events — full write/read separation with async projection")
    write = WriteModel()
    read = ReadModel()
    q: queue.Queue = queue.Queue()

    def worker() -> None:
        while True:
            ev = q.get()
            if ev is None:
                break
            assert ev["type"] == "InvoicePosted"
            time.sleep(0.05)  # async lag
            read.apply_invoice_posted(ev["payload"])
            print(f"  read model updated: {read.revenue_by_branch}")
            q.task_done()

    threading.Thread(target=worker, daemon=True).start()

    inv = write.post({"id": 42, "branch_id": 1, "amount": 999.0})
    print(f"WRITE committed: {inv}")
    q.put({"type": "InvoicePosted", "payload": inv})

    q.join()
    print(f"QUERY reporting DB/read model branch1={read.revenue_by_branch.get(1)}")
    q.put(None)
    print("\nResult: OLTP write path ≠ reporting read path.")


if __name__ == "__main__":
    main()
