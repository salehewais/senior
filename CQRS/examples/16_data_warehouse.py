#!/usr/bin/env python3
"""
16 — Data Warehouse
-------------------
ETL from OLTP (or Reporting DB) into a star schema for BI / history / cross-domain.
"""

from __future__ import annotations

import sqlite3
from collections import defaultdict

from _demo_data import banner, make_lines


def etl_to_warehouse(lines) -> sqlite3.Connection:
    wh = sqlite3.connect(":memory:")
    wh.executescript(
        """
        CREATE TABLE dim_branch(branch_sk INTEGER PRIMARY KEY, branch_id INT UNIQUE, name TEXT);
        CREATE TABLE fact_sales_daily(
          date TEXT, branch_sk INT, amount REAL,
          PRIMARY KEY(date, branch_sk)
        );
        """
    )
    for b in range(1, 6):
        wh.execute("INSERT INTO dim_branch(branch_id, name) VALUES (?, ?)", (b, f"B{b}"))

    agg: dict[tuple[str, int], float] = defaultdict(float)
    for l in lines:
        if l.product_id is None:
            continue
        agg[(l.move_date.isoformat(), l.branch_id)] += l.debit

    for (day, branch_id), amount in agg.items():
        sk = wh.execute(
            "SELECT branch_sk FROM dim_branch WHERE branch_id=?", (branch_id,)
        ).fetchone()[0]
        wh.execute(
            "INSERT INTO fact_sales_daily VALUES (?,?,?) "
            "ON CONFLICT(date, branch_sk) DO UPDATE SET amount=excluded.amount",
            (day, sk, amount),
        )
    wh.commit()
    return wh


def main() -> None:
    banner("16 Data Warehouse — star schema for BI")
    wh = etl_to_warehouse(make_lines(15_000))
    rows = wh.execute(
        """
        SELECT d.name, round(sum(f.amount),1)
        FROM fact_sales_daily f
        JOIN dim_branch d ON d.branch_sk = f.branch_sk
        GROUP BY d.name
        ORDER BY 1
        """
    ).fetchall()
    print("BI query on warehouse facts:")
    for name, amt in rows:
        print(f"  {name}: {amt}")
    print("\nTrade-off: expensive to operate; use after summaries/reporting DB aren't enough.")


if __name__ == "__main__":
    main()
