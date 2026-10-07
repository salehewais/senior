# Phase 0 — Baseline

Read-only measurement against primary (and replica if present). Produces evidence for Exact vs Analytical classification.

## Steps

1. Fill [`report_inventory.csv`](report_inventory.csv) for top reports.
2. Run SQL under `sql/` during POS peak and report peak; save outputs with timestamps.
3. Set SLAs in [`../shared/config.example.env`](../shared/config.example.env) (`EXACT_MAX_REPLICA_LAG_SECONDS`, `ANALYTICAL_FRESHNESS_MINUTES`).
4. Exit when prioritized list + lanes + baselines exist (see [`../../docs/phase-0-baseline.md`](../../docs/phase-0-baseline.md)).

```bash
set -a; source ../shared/config.env; set +a
mkdir -p ./out
psql "$PRIMARY_DSN" -f sql/01_session_snapshot.sql  | tee out/sessions_$(date +%F_%H%M).txt
psql "$PRIMARY_DSN" -f sql/02_long_queries.sql       | tee out/long_$(date +%F_%H%M).txt
psql "$PRIMARY_DSN" -f sql/03_aml_size.sql            | tee out/aml_size_$(date +%F_%H%M).txt
psql "$PRIMARY_DSN" -f sql/04_pg_stat_statements_aml.sql | tee out/aml_queries_$(date +%F_%H%M).txt
# if replica exists:
psql "$PRIMARY_DSN" -f sql/05_replication_lag.sql    | tee out/repl_$(date +%F_%H%M).txt
```
