#!/usr/bin/env python3
"""Phase 4 consumer: for each event, recompute affected aml_daily keys on replica
and upsert into Reporting DB facts.

Input: JSON lines on stdin (or poll outbox — extend as needed).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    import psycopg2
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


RECOMPUTE_KEYS = """
SELECT DISTINCT
  am.date::date AS move_date,
  aml.company_id,
  reporting.branch_id(am) AS branch_id,
  aml.account_id
FROM account_move am
JOIN account_move_line aml ON aml.move_id = am.id
WHERE am.id = %s
"""

AGG_ONE = """
SELECT
  am.date::date,
  aml.company_id,
  reporting.branch_id(am),
  aml.account_id,
  sum(aml.debit),
  sum(aml.credit),
  sum(aml.debit - aml.credit),
  count(*)::int
FROM account_move_line aml
JOIN account_move am ON am.id = aml.move_id
WHERE am.state = 'posted'
  AND am.date = %s
  AND aml.company_id = %s
  AND reporting.branch_id(am) = %s
  AND aml.account_id = %s
GROUP BY 1, 2, 3, 4
"""

UPSERT_FACT = """
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

DELETE_FACT = """
DELETE FROM reporting.fact_aml_daily
WHERE date_key = to_char(%s::date, 'YYYYMMDD')::int
  AND company_id = %s AND branch_id = %s AND account_id = %s
"""


def apply_move_event(replica, reporting, move_id: int) -> int:
    with replica.cursor() as cur:
        cur.execute(RECOMPUTE_KEYS, (move_id,))
        keys = cur.fetchall()
    updated = 0
    with reporting.cursor() as wcur:
        for move_date, company_id, branch_id, account_id in keys:
            with replica.cursor() as cur:
                cur.execute(AGG_ONE, (move_date, company_id, branch_id, account_id))
                agg = cur.fetchone()
            if agg is None:
                wcur.execute(DELETE_FACT, (move_date, company_id, branch_id, account_id))
            else:
                wcur.execute(UPSERT_FACT, agg)
                updated += 1
    reporting.commit()
    return updated


def handle(event: dict) -> None:
    et = event["event_type"]
    if et not in ("account.move.posted", "account.move.cancelled", "account.payment.posted"):
        print(f"skip event_type={et}")
        return
    if event.get("record_model") not in ("account.move", "account.payment"):
        # payments often create moves — pass move id in payload when possible
        move_id = event.get("payload", {}).get("move_id") or event["record_id"]
    else:
        move_id = event["record_id"]

    replica = psycopg2.connect(os.environ["REPLICA_DSN"])
    reporting = psycopg2.connect(os.environ["REPORTING_DSN"])
    try:
        n = apply_move_event(replica, reporting, move_id)
        print(f"applied event_id={event.get('event_id')} keys_updated={n}")
    finally:
        replica.close()
        reporting.close()


def main() -> None:
    load_env()
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        handle(json.loads(line))


if __name__ == "__main__":
    main()
