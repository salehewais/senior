#!/usr/bin/env python3
"""
22 — Reporting DB + CQRS + Event-Driven + Async (steady state)
-------------------------------------------------------------
Mini end-to-end: command → write → event → worker → reporting DB → query.
"""

from __future__ import annotations

import queue
import sqlite3
import threading

from _demo_data import banner


def main() -> None:
    banner("22 Full analytical stack (mini)")
    # Write model (Odoo primary)
    write_db = sqlite3.connect(":memory:", check_same_thread=False)
    write_db.execute("CREATE TABLE aml(id INT, branch_id INT, amount REAL)")

    # Reporting DB (read model)
    report_db = sqlite3.connect(":memory:", check_same_thread=False)
    report_db.execute(
        "CREATE TABLE fact_aml_daily(day TEXT, branch_id INT, balance REAL, "
        "PRIMARY KEY(day, branch_id))"
    )

    q: queue.Queue = queue.Queue()

    def worker() -> None:
        while True:
            ev = q.get()
            if ev is None:
                break
            day, branch, amount = ev["day"], ev["branch_id"], ev["amount"]
            report_db.execute(
                """
                INSERT INTO fact_aml_daily(day, branch_id, balance) VALUES (?,?,?)
                ON CONFLICT(day, branch_id) DO UPDATE SET
                  balance = fact_aml_daily.balance + excluded.balance
                """,
                (day, branch, amount),
            )
            report_db.commit()
            print(f"  async worker projected event {ev}")
            q.task_done()

    threading.Thread(target=worker, daemon=True).start()

    def command_post(invoice_id: int, branch_id: int, amount: float, day: str) -> None:
        write_db.execute("INSERT INTO aml VALUES (?,?,?)", (invoice_id, branch_id, amount))
        write_db.commit()
        print(f"COMMAND posted invoice={invoice_id} on PRIMARY")
        q.put({"type": "InvoicePosted", "day": day, "branch_id": branch_id, "amount": amount})

    def query_kpi(day: str, branch_id: int) -> float:
        row = report_db.execute(
            "SELECT balance FROM fact_aml_daily WHERE day=? AND branch_id=?",
            (day, branch_id),
        ).fetchone()
        return row[0] if row else 0.0

    command_post(1, 1, 100, "2026-10-07")
    command_post(2, 1, 40, "2026-10-07")
    q.join()
    print(f"QUERY analytical KPI from Reporting DB: {query_kpi('2026-10-07', 1)}")
    q.put(None)
    print("\nThis is the mature analytical shape — build after Phase 1–2 foundations.")


if __name__ == "__main__":
    main()
