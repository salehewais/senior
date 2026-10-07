# Phase 3 — Reporting DB + read model

Dedicated analytical PostgreSQL with dims/facts. ETL from replica summaries (Phase 2) or re-aggregate from replica.

## Install on REPORTING_DSN

```bash
set -a; source ../shared/config.env; set +a
psql "$REPORTING_DSN" -f sql/00_schema.sql
psql "$REPORTING_DSN" -f sql/01_dims.sql
psql "$REPORTING_DSN" -f sql/02_facts.sql
```

## Sync

```bash
# Copy Phase 2 summaries → Reporting DB (bridge)
python etl/sync_facts_from_replica.py --dataset aml_daily
python etl/sync_dims_from_replica.py
```

## Cutover

1. Dual-run Analytical totals vs Phase 2 tables.
2. Point Analytical DSN / reports at `REPORTING_DSN`.
3. Keep Exact on replica Odoo schema.
