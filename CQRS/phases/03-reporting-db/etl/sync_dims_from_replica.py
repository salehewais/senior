#!/usr/bin/env python3
"""Load dimension tables from Odoo replica into Reporting DB."""

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


def upsert(reporting, sql: str, rows) -> None:
    with reporting.cursor() as cur:
        execute_batch(cur, sql, rows, page_size=500)
    reporting.commit()


def main() -> None:
    load_env()
    replica = psycopg2.connect(os.environ["REPLICA_DSN"])
    reporting = psycopg2.connect(os.environ["REPORTING_DSN"])
    try:
        with replica.cursor() as cur:
            cur.execute("SELECT id, name, NULLIF(currency_id::text, '') FROM res_company")
            companies = cur.fetchall()
        upsert(
            reporting,
            """
            INSERT INTO reporting.dim_company (company_id, name, currency, updated_at)
            VALUES (%s, %s, %s, now())
            ON CONFLICT (company_id) DO UPDATE SET
              name = EXCLUDED.name, currency = EXCLUDED.currency, updated_at = now()
            """,
            companies,
        )

        with replica.cursor() as cur:
            cur.execute(
                """
                SELECT id, code, name, account_type
                FROM account_account
                """
            )
            accounts = cur.fetchall()
        upsert(
            reporting,
            """
            INSERT INTO reporting.dim_account (account_id, code, name, account_type, updated_at)
            VALUES (%s, %s, %s, %s, now())
            ON CONFLICT (account_id) DO UPDATE SET
              code = EXCLUDED.code, name = EXCLUDED.name,
              account_type = EXCLUDED.account_type, updated_at = now()
            """,
            accounts,
        )

        with replica.cursor() as cur:
            cur.execute(
                """
                SELECT pp.id, pt.default_code, pt.name::text, NULL
                FROM product_product pp
                JOIN product_template pt ON pt.id = pp.product_tmpl_id
                """
            )
            products = cur.fetchall()
        upsert(
            reporting,
            """
            INSERT INTO reporting.dim_product (product_id, default_code, name, categ, updated_at)
            VALUES (%s, %s, %s, %s, now())
            ON CONFLICT (product_id) DO UPDATE SET
              default_code = EXCLUDED.default_code, name = EXCLUDED.name,
              categ = EXCLUDED.categ, updated_at = now()
            """,
            products,
        )

        # Placeholder branch dim: at least id 0
        upsert(
            reporting,
            """
            INSERT INTO reporting.dim_branch (branch_id, company_id, name, updated_at)
            VALUES (%s, %s, %s, now())
            ON CONFLICT (branch_id) DO NOTHING
            """,
            [(0, None, "Unspecified")],
        )

        with reporting.cursor() as cur:
            cur.execute(
                """
                UPDATE reporting_meta.refresh_watermark
                SET status = 'ok', as_of = now(), detail = 'dims synced', updated_at = now()
                WHERE dataset = 'dims'
                """
            )
        reporting.commit()
        print("dims synced")
    finally:
        replica.close()
        reporting.close()


if __name__ == "__main__":
    main()
