# Phases — implementation pack

Runnable artifacts for every phase of the Odoo heavy-reporting roadmap. Design rationale lives in [`../docs/`](../docs/).

| Phase | Directory | What you get |
|-------|-----------|--------------|
| 0 | [`00-baseline/`](00-baseline/) | Measurement SQL + report inventory CSV |
| 1 | [`01-isolation/`](01-isolation/) | Replica/pool config, async job DDL, worker stub |
| 2 | [`02-preaggregation/`](02-preaggregation/) | Summary DDL, nightly/incremental/reconcile SQL + runner |
| 3 | [`03-reporting-db/`](03-reporting-db/) | Facts/dims DDL + ETL sync scripts |
| 4 | [`04-events/`](04-events/) | Event contract, outbox DDL, consumer stub, reconcile |
| 5 | [`05-cqrs/`](05-cqrs/) | Command/query routing contracts + config |
| 6 | [`06-warehouse/`](06-warehouse/) | Warehouse star DDL + ELT stubs |

## Conventions

1. **Execute in order.** Do not run Phase 4 against primary AML without Phase 2 grains.
2. **Adapt branch mapping** before production — see [`shared/branch_mapping.md`](shared/branch_mapping.md).
3. Copy [`shared/config.example.env`](shared/config.example.env) → `shared/config.env` (never commit secrets).
4. SQL uses schema `reporting` on the Odoo replica (Phases 1–2) and a dedicated Reporting DB (Phase 3+).
5. Exact Accounting jobs must use `REPLICA_DSN` with lag checks; Analytical may use summaries / Reporting DB.

## Quick start

```bash
cp phases/shared/config.example.env phases/shared/config.env
# edit DSNs, then:

# Phase 0 — capture baselines (read-only on primary or replica)
psql "$PRIMARY_DSN" -f phases/00-baseline/sql/01_session_snapshot.sql

# Phase 2 — create summaries on replica
psql "$REPLICA_DSN" -f phases/02-preaggregation/sql/00_schema.sql
psql "$REPLICA_DSN" -f phases/02-preaggregation/sql/01_aml_daily.sql
python phases/02-preaggregation/jobs/refresh_runner.py --dataset aml_daily --mode nightly
```

## Odoo column caveats

Scripts assume standard Odoo accounting table names (`account_move`, `account_move_line`). Branch is abstracted as `reporting.branch_id(am)` — implement that function for your localization (see shared doc). Sales facts assume `pos_order` / `pos_order_line` when present; disable if unused.
