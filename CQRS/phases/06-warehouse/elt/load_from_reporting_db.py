#!/usr/bin/env python3
"""Phase 6 ELT: copy Reporting DB dims/facts into warehouse star (surrogate keys)."""

from __future__ import annotations

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


def sync_dims(src, wh) -> None:
    with src.cursor() as cur:
        cur.execute("SELECT date_key, date, year, month, day, week, is_month_end FROM reporting.dim_date")
        dates = cur.fetchall()
    with wh.cursor() as cur:
        execute_batch(
            cur,
            """
            INSERT INTO wh.dim_date (date_key, date, year, month, day, week, is_month_end)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (date_key) DO NOTHING
            """,
            dates,
            page_size=1000,
        )

    with src.cursor() as cur:
        cur.execute("SELECT company_id, name, currency FROM reporting.dim_company")
        rows = cur.fetchall()
    with wh.cursor() as cur:
        execute_batch(
            cur,
            """
            INSERT INTO wh.dim_company (company_id, name, currency)
            VALUES (%s,%s,%s)
            ON CONFLICT (company_id) DO UPDATE SET name = EXCLUDED.name, currency = EXCLUDED.currency
            """,
            rows,
        )

    with src.cursor() as cur:
        cur.execute("SELECT branch_id, company_id, name FROM reporting.dim_branch")
        rows = cur.fetchall()
    with wh.cursor() as cur:
        execute_batch(
            cur,
            """
            INSERT INTO wh.dim_branch (branch_id, company_id, name)
            VALUES (%s,%s,%s)
            ON CONFLICT (branch_id) DO UPDATE SET company_id = EXCLUDED.company_id, name = EXCLUDED.name
            """,
            rows,
        )

    with src.cursor() as cur:
        cur.execute("SELECT account_id, code, name, account_type FROM reporting.dim_account")
        rows = cur.fetchall()
    with wh.cursor() as cur:
        execute_batch(
            cur,
            """
            INSERT INTO wh.dim_account (account_id, code, name, account_type)
            VALUES (%s,%s,%s,%s)
            ON CONFLICT (account_id) DO UPDATE SET
              code = EXCLUDED.code, name = EXCLUDED.name, account_type = EXCLUDED.account_type
            """,
            rows,
        )

    with src.cursor() as cur:
        cur.execute("SELECT product_id, default_code, name, categ FROM reporting.dim_product")
        rows = cur.fetchall()
    with wh.cursor() as cur:
        execute_batch(
            cur,
            """
            INSERT INTO wh.dim_product (product_id, default_code, name, categ)
            VALUES (%s,%s,%s,%s)
            ON CONFLICT (product_id) DO UPDATE SET
              default_code = EXCLUDED.default_code, name = EXCLUDED.name, categ = EXCLUDED.categ
            """,
            rows,
        )
    wh.commit()


def sync_fact_aml(src, wh) -> int:
    with src.cursor() as cur:
        cur.execute(
            """
            SELECT date_key, company_id, branch_id, account_id,
                   debit, credit, balance, line_count
            FROM reporting.fact_aml_daily
            """
        )
        rows = cur.fetchall()

    mapped = []
    with wh.cursor() as cur:
        for date_key, company_id, branch_id, account_id, debit, credit, balance, line_count in rows:
            cur.execute("SELECT company_sk FROM wh.dim_company WHERE company_id = %s", (company_id,))
            company_sk = cur.fetchone()
            cur.execute("SELECT branch_sk FROM wh.dim_branch WHERE branch_id = %s", (branch_id,))
            branch_sk = cur.fetchone()
            cur.execute("SELECT account_sk FROM wh.dim_account WHERE account_id = %s", (account_id,))
            account_sk = cur.fetchone()
            if not (company_sk and branch_sk and account_sk):
                continue
            mapped.append(
                (date_key, company_sk[0], branch_sk[0], account_sk[0], debit, credit, balance, line_count)
            )
        execute_batch(
            cur,
            """
            INSERT INTO wh.fact_aml_daily (
              date_key, company_sk, branch_sk, account_sk,
              debit, credit, balance, line_count, loaded_at
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s, now())
            ON CONFLICT (date_key, company_sk, branch_sk, account_sk) DO UPDATE SET
              debit = EXCLUDED.debit, credit = EXCLUDED.credit,
              balance = EXCLUDED.balance, line_count = EXCLUDED.line_count,
              loaded_at = now()
            """,
            mapped,
            page_size=500,
        )
        cur.execute(
            """
            INSERT INTO wh.elt_watermark (dataset, as_of, detail, updated_at)
            VALUES ('fact_aml_daily', now(), %s, now())
            ON CONFLICT (dataset) DO UPDATE SET
              as_of = now(), detail = EXCLUDED.detail, updated_at = now()
            """,
            (f"loaded {len(mapped)} rows",),
        )
    wh.commit()
    return len(mapped)


def main() -> None:
    load_env()
    src = psycopg2.connect(os.environ["REPORTING_DSN"])
    wh = psycopg2.connect(os.environ["WAREHOUSE_DSN"])
    try:
        sync_dims(src, wh)
        n = sync_fact_aml(src, wh)
        print(f"warehouse fact_aml_daily rows={n}")
    finally:
        src.close()
        wh.close()


if __name__ == "__main__":
    main()
