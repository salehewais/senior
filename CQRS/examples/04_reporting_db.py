#!/usr/bin/env python3
"""
04 — Reporting Database
-----------------------
Idea: a separate analytical store with facts/dims. Reports query fact_sales_daily
instead of raw account.move.line.
"""

from __future__ import annotations

import sqlite3
from collections import defaultdict

from _demo_data import banner, make_lines


def build_reporting_db(lines) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE dim_branch(branch_id INT PRIMARY KEY, name TEXT);
        CREATE TABLE fact_aml_daily(
          move_date TEXT, company_id INT, branch_id INT, account_id INT,
          balance REAL,
          PRIMARY KEY(move_date, company_id, branch_id, account_id)
        );
        """
    )
    for b in range(1, 6):
        conn.execute("INSERT INTO dim_branch VALUES (?, ?)", (b, f"Branch {b}"))

    agg: dict[tuple, float] = defaultdict(float)
    for l in lines:
        key = (l.move_date.isoformat(), l.company_id, l.branch_id, l.account_id)
        agg[key] += l.balance

    conn.executemany(
        "INSERT INTO fact_aml_daily VALUES (?,?,?,?,?)",
        [(k[0], k[1], k[2], k[3], v) for k, v in agg.items()],
    )
    conn.commit()
    return conn


def main() -> None:
    banner("04 Reporting DB — facts/dims instead of raw AML")
    lines = make_lines(30_000)
    conn = build_reporting_db(lines)

    raw = len(lines)
    facts = conn.execute("SELECT count(*) FROM fact_aml_daily").fetchone()[0]
    print(f"raw AML rows:     {raw:,}")
    print(f"fact_aml_daily:   {facts:,}")

    rows = conn.execute(
        """
        SELECT b.name, round(sum(f.balance), 2)
        FROM fact_aml_daily f
        JOIN dim_branch b ON b.branch_id = f.branch_id
        WHERE f.move_date LIKE '2025-06%'
        GROUP BY b.name
        ORDER BY 1
        """
    ).fetchall()
    print("Branch P&L Jun 2025 from Reporting DB:")
    for name, bal in rows:
        print(f"  {name}: {bal}")

    print("\nTrade-off: need sync/ETL; Exact statutory reports stay on Odoo schema.")


if __name__ == "__main__":
    main()
