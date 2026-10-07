# Phase 4 — Event-driven incremental refresh

After Reporting DB / summaries exist: emit domain events → queue → recompute affected grain keys → nightly reconcile.

## Components

| Path | Purpose |
|------|---------|
| `contracts/reporting_events.schema.json` | Event envelope schema |
| `sql/01_outbox.sql` | Optional transactional outbox on primary |
| `sql/02_reconcile_job.sql` | Drift check helper on Reporting DB |
| `consumer/event_consumer.py` | Applies events by recomputing keys |

## Flow

1. Odoo (or DB trigger/outbox poller) writes events for move posted/cancelled, POS done.
2. Consumer reads queue/outbox, recomputes `fact_aml_daily` / Phase 2 keys from **replica source**.
3. Nightly reconcile compares source vs facts; window rebuild on drift.

Prefer **recompute-from-source** over blind deltas until thoroughly tested.
