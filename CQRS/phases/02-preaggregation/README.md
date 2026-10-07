# Phase 2 — Pre-aggregation

Create summary tables on the **replica**, refresh nightly + optional daytime incremental, reconcile vs AML.

## Install

```bash
set -a; source ../shared/config.env; set +a
psql "$REPLICA_DSN" -f sql/00_schema.sql
psql "$REPLICA_DSN" -f sql/01_aml_daily.sql
psql "$REPLICA_DSN" -f sql/02_sales_daily.sql   # skip if no POS
psql "$REPLICA_DSN" -f sql/03_matview_optional.sql  # optional MVP path
```

Edit `reporting.branch_id` (see [`../shared/branch_mapping.md`](../shared/branch_mapping.md)) **before** first backfill.

## Refresh

```bash
# Nightly window rebuild (cron 01:00)
python jobs/refresh_runner.py --dataset aml_daily --mode nightly
python jobs/refresh_runner.py --dataset sales_daily --mode nightly

# Daytime incremental (cron every 10–15 min)
python jobs/refresh_runner.py --dataset aml_daily --mode incremental

# Reconcile yesterday
psql "$REPLICA_DSN" -v company_id=1 -v d="'2026-10-06'" -f sql/04_reconcile_aml_daily.sql
```

## Wire analytical reports

Point Analytical reports at `reporting.aml_daily` / `reporting.sales_daily` and show `reporting.refresh_watermark.as_of`. Keep Exact on live Odoo schema via Phase 1 workers.
