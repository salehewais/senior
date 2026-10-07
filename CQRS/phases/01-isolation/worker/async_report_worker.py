#!/usr/bin/env python3
"""Phase 1 async report worker: concurrency cap + Exact lag gate + artifact write.

Enqueue rows into reporting.report_job; this process claims queued jobs.
Report SQL must use REPLICA_DSN — never PRIMARY_DSN.
"""

from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    print("Install psycopg2-binary to run this worker", file=sys.stderr)
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


def connect(dsn: str):
    return psycopg2.connect(dsn)


def replica_lag_seconds(conn) -> float | None:
    with conn.cursor() as cur:
        cur.execute("SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))")
        row = cur.fetchone()
        if row is None or row[0] is None:
            return None
        return float(row[0])


def claim_jobs(control_dsn: str, limit: int) -> list[dict]:
    sql = """
    UPDATE reporting.report_job j
    SET status = 'running', started_at = now()
    WHERE id IN (
      SELECT id FROM reporting.report_job
      WHERE status = 'queued'
      ORDER BY created_at
      FOR UPDATE SKIP LOCKED
      LIMIT %s
    )
    RETURNING id, report_code, lane, params_json, company_ids;
    """
    with connect(control_dsn) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (limit,))
            rows = [dict(r) for r in cur.fetchall()]
        conn.commit()
    return rows


def finish_job(control_dsn: str, job_id: int, **fields) -> None:
    cols = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [job_id]
    with connect(control_dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE reporting.report_job SET {cols}, finished_at = now() WHERE id = %s",
                values,
            )
        conn.commit()


def run_report_sql(replica_dsn: str, timeout_ms: int, sql: str, params: dict):
    with connect(replica_dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SET statement_timeout = %s", (timeout_ms,))
            cur.execute(sql, params)
            if cur.description:
                return cur.fetchall()
            return []


# Map report_code → SQL. Replace with real Exact/Analytical queries.
REPORT_SQL = {
    "exact.trial_balance_stub": """
        SELECT 1 WHERE false;  -- replace with real Exact SQL against Odoo schema
    """,
    "analytical.branch_kpi_stub": """
        SELECT move_date, company_id, branch_id, sum(balance) AS balance
        FROM reporting.aml_daily
        WHERE company_id = %(company_id)s
          AND move_date BETWEEN %(date_from)s AND %(date_to)s
        GROUP BY 1, 2, 3
        ORDER BY 1;
    """,
}


def process_job(job: dict) -> None:
    control = os.environ["PRIMARY_DSN"]  # or REPORTING_DSN if jobs live there
    replica = os.environ["REPLICA_DSN"]
    max_lag = float(os.environ.get("EXACT_MAX_REPLICA_LAG_SECONDS", "5"))
    timeout_ms = int(os.environ.get("REPORT_STATEMENT_TIMEOUT_MS", "180000"))
    artifact_dir = Path(os.environ.get("ARTIFACT_DIR", "/tmp/reporting-artifacts"))
    artifact_dir.mkdir(parents=True, exist_ok=True)

    lag = None
    try:
        with connect(replica) as rconn:
            lag = replica_lag_seconds(rconn)
        if job["lane"] == "exact" and lag is not None and lag > max_lag:
            finish_job(
                control,
                job["id"],
                status="failed",
                error=f"replica lag {lag:.1f}s exceeds {max_lag}s",
                replica_lag_at_start=f"{int(lag)} seconds",
            )
            return

        sql = REPORT_SQL.get(job["report_code"])
        if not sql:
            raise KeyError(f"unknown report_code={job['report_code']}")

        params = job["params_json"] or {}
        if isinstance(params, str):
            params = json.loads(params)
        rows = run_report_sql(replica, timeout_ms, sql, params)

        out = artifact_dir / f"job_{job['id']}.json"
        out.write_text(json.dumps({"rows": rows}, default=str))
        finish_job(
            control,
            job["id"],
            status="done",
            artifact_uri=str(out),
            as_of_timestamp=datetime.now(timezone.utc),
            replica_lag_at_start=f"{int(lag)} seconds" if lag is not None else None,
        )
    except Exception as exc:  # noqa: BLE001 — worker boundary
        finish_job(control, job["id"], status="failed", error=str(exc))


def main() -> None:
    load_env()
    concurrency = int(os.environ.get("REPORT_WORKER_CONCURRENCY", "6"))
    control = os.environ["PRIMARY_DSN"]
    print(f"worker starting concurrency={concurrency}")
    while True:
        jobs = claim_jobs(control, concurrency)
        if not jobs:
            time.sleep(2)
            continue
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            futs = [pool.submit(process_job, j) for j in jobs]
            for f in as_completed(futs):
                f.result()


if __name__ == "__main__":
    main()
