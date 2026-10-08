#!/usr/bin/env python3
"""
14 — Eventual Consistency
-------------------------
Write DB is immediately correct; read model catches up after event processing.
Business must accept lag for analytical reports (show as_of).
"""

from __future__ import annotations

import threading
import time

from _demo_data import banner


def main() -> None:
    banner("14 Eventual Consistency — write now, read model later")
    write_balance = 0.0
    read_balance = 0.0
    as_of = "10:00:00"

    def process_event(amount: float, delay: float) -> None:
        nonlocal read_balance, as_of
        time.sleep(delay)
        read_balance += amount
        as_of = time.strftime("%H:%M:%S")
        print(f"  [{as_of}] read model caught up → {read_balance}")

    amount = 500.0
    write_balance += amount
    print(f"[10:00:00] WRITE Odoo balance={write_balance} (real-time)")
    print(f"[10:00:00] READ  dashboard={read_balance} as_of={as_of} (stale)")

    t = threading.Thread(target=process_event, args=(amount, 0.35))
    t.start()
    time.sleep(0.1)
    print(f"[10:00:00+] READ still {read_balance} — eventual consistency window")
    t.join()
    print(f"final READ={read_balance} as_of={as_of} (matches write)")
    print("\nTrade-off: OK for KPIs; NOT OK for ZATCA/statutory without lag policy.")


if __name__ == "__main__":
    main()
