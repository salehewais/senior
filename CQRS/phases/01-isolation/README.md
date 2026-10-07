# Phase 1 — Isolation package

Replica routing + pooling/concurrency + async report jobs on a separate reporting host.

## Deliverables

| Path | Purpose |
|------|---------|
| `config/pgbouncer.ini.example` | Pooler in front of replica |
| `config/reporting_role.sql` | SELECT-only role for report workers |
| `sql/01_report_jobs.sql` | Job queue table (can live on primary or reporting DB) |
| `worker/async_report_worker.py` | Cap concurrency, lag-gate Exact, run query, store artifact |

## Deploy order

1. Stand up streaming replica; verify lag SQL from Phase 0.
2. Create `odoo_reporting` role on replica (`config/reporting_role.sql`).
3. Place PgBouncer on reporting host → replica (`config/pgbouncer.ini.example`).
4. Install job table (`sql/01_report_jobs.sql`) — typically on primary (Odoo-visible) or Reporting DB.
5. Run workers on **reporting host** with `REPLICA_DSN` only for report SQL.
6. Point Odoo “Generate report” at enqueue API (thin), not sync SQL.

## Exit

POS/write p95 stable under concurrent report load; report HTTP returns `job_id` quickly.
