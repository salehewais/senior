#!/usr/bin/env python3
"""Bridge ETL: copy Phase 2 summary tables from replica into Reporting DB facts."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    import psycopg2
    from psycopg2.extras import execute_batch
except ImportError:
    print("Install psycopg2-binary", file=sys.stderr)
    sys.exit(1)


def load_env() -> None:
    cfg = Path(__file__).resolve().parents[2] / "shared" / "config.env"
    if not cfg.exists():
        return
    for line in cfg.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def sync_aml(replica, reporting) -> int:
    with replica.cursor() as cur:
        cur.execute(
            """
            SELECT move_date, company_id, branch_id, account_id,
                   debit, credit, balance, line_count
            FROM reporting.aml_daily
            """
        )
        rows = cur.fetchall()
    upsert = """
    INSERT INTO reporting.fact_aml_daily (
      date_key, company_id, branch_id, account_id,
      debit, credit, balance, line_count, as_of
    ) VALUES (
      to_char(%s::date, 'YYYYMMDD')::int, %s, %s, %s,
      %s, %s, %s, %s, now()
    )
    ON CONFLICT (date_key, company_id, branch_id, account_id) DO UPDATE SET
      debit = EXCLUDED.debit,
      credit = EXCLUDED.credit,
      balance = EXCLUDED.balance,
      line_count = EXCLUDED.line_count,
      as_of = EXCLUDED.as_of
    """
    with reporting.cursor() as cur:
        execute_batch(cur, upsert, rows, page_size=1000)
        cur.execute(
            """
            UPDATE reporting_meta.refresh_watermark
            SET status = 'ok', as_of = now(), detail = %s, updated_at = now()
            WHERE dataset = 'aml_daily'
            """,
            (f"synced {len(rows)} rows",),
        )
    reporting.commit()
    return len(rows)


def sync_sales(replica, reporting) -> int:
    with replica.cursor() as cur:
        cur.execute(
            """
            SELECT sale_date, company_id, branch_id, product_id,
                   qty, amount_untaxed, amount_total, cost, order_count
            FROM reporting.sales_daily
            """
        )
        rows = cur.fetchall()
    upsert = """
    INSERT INTO reporting.fact_sales_daily (
      date_key, company_id, branch_id, product_id,
      qty, amount_untaxed, amount_total, cost, order_count, as_of
    ) VALUES (
      to_char(%s::date, 'YYYYMMDD')::int, %s, %s, %s,
      %s, %s, %s, %s, %s, now()
    )
    ON CONFLICT (date_key, company_id, branch_id, product_id) DO UPDATE SET
      qty = EXCLUDED.qty,
      amount_untaxed = EXCLUDED.amount_untaxed,
      amount_total = EXCLUDED.amount_total,
      cost = EXCLUDED.cost,
      order_count = EXCLUDED.order_count,
      as_of = EXCLUDED.as_of
    """
    with reporting.cursor() as cur:
        execute_batch(cur, upsert, rows, page_size=1000)
        cur.execute(
            """
            UPDATE reporting_meta.refresh_watermark
            SET status = 'ok', as_of = now(), detail = %s, updated_at = now()
            WHERE dataset = 'sales_daily'
            """,
            (f"synced {len(rows)} rows",),
        )
    reporting.commit()
    return len(rows)


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=("aml_daily", "sales_daily", "all"), default="all")
    args = parser.parse_args()

    replica = psycopg2.connect(os.environ["REPLICA_DSN"])
    reporting = psycopg2.connect(os.environ["REPORTING_DSN"])
    try:
        if args.dataset in ("aml_daily", "all"):
            n = sync_aml(replica, reporting)
            print(f"aml_daily synced rows={n}")
        if args.dataset in ("sales_daily", "all"):
            n = sync_sales(replica, reporting)
            print(f"sales_daily synced rows={n}")
    finally:
        replica.close()
        reporting.close()


if __name__ == "__main__":
    main()
