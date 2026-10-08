#!/usr/bin/env python3
"""
12 — Event-Driven
-----------------
After a business fact is committed, emit an event; a worker updates the read model.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable

from _demo_data import banner


@dataclass
class EventBus:
    subscribers: dict[str, list[Callable]] = field(default_factory=lambda: defaultdict(list))

    def on(self, event_type: str, handler: Callable) -> None:
        self.subscribers[event_type].append(handler)

    def emit(self, event_type: str, payload: dict) -> None:
        print(f"  emit {event_type}: {payload}")
        for h in self.subscribers[event_type]:
            h(payload)


def main() -> None:
    banner("12 Event-Driven — InvoicePosted updates summary asynchronously")
    bus = EventBus()
    daily_sales: dict[tuple[str, int], float] = defaultdict(float)

    def on_invoice_posted(p: dict) -> None:
        key = (p["date"], p["branch_id"])
        daily_sales[key] += p["amount"]
        print(f"  worker updated daily_sales_summary {key} → {daily_sales[key]}")

    bus.on("InvoicePosted", on_invoice_posted)

    # Odoo commit path
    print("Odoo posts invoice #1001…")
    bus.emit(
        "InvoicePosted",
        {"invoice_id": 1001, "date": "2026-10-07", "branch_id": 3, "amount": 1200.0},
    )
    print(f"report reads summary: {dict(daily_sales)}")
    print("\nTrade-off: missed events need nightly reconcile; ordering matters.")


if __name__ == "__main__":
    main()
