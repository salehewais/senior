#!/usr/bin/env python3
"""
03 — Separate Reporting Server
------------------------------
Idea: report CPU/RAM/connections live on another host/process so Odoo web/POS
workers are not starved.
"""

from __future__ import annotations

import multiprocessing as mp
import os
import time

from _demo_data import banner, make_lines


def odoo_web_tick(stop: mp.Event) -> None:
    """Simulates POS/web staying responsive."""
    n = 0
    while not stop.is_set():
        n += 1
        time.sleep(0.05)
    print(f"[odoo-web pid={os.getpid()}] handled ~{n} ticks, never ran report SQL")


def reporting_worker(rows: int) -> None:
    lines = make_lines(rows)
    t0 = time.time()
    total = sum(l.balance for l in lines)
    print(
        f"[report-host pid={os.getpid()}] scanned {rows:,} "
        f"balance={total:,.2f} in {time.time()-t0:.3f}s"
    )


def main() -> None:
    banner("03 Separate Reporting Server — different process/host for reports")
    stop = mp.Event()
    web = mp.Process(target=odoo_web_tick, args=(stop,), name="odoo-web")
    web.start()

    # Report runs elsewhere (another process ≈ another server)
    report = mp.Process(target=reporting_worker, args=(20_000,), name="report")
    report.start()
    report.join()

    time.sleep(0.2)
    stop.set()
    web.join()
    print("\nTrade-off: ops overhead (deploy/auth), but POS CPU stays free.")


if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    main()
