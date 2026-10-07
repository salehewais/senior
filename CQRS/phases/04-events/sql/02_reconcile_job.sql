-- Run on REPORTING_DSN after dims/facts loaded.
-- Compares Reporting fact totals to a staging copy of source aggregates if present,
-- or use Phase 2 reconcile against replica and compare both to facts.

CREATE TABLE IF NOT EXISTS reporting_meta.reconcile_result (
  id           bigserial PRIMARY KEY,
  dataset      text NOT NULL,
  company_id   int NOT NULL,
  move_date    date NOT NULL,
  source_balance numeric,
  fact_balance   numeric,
  drift          numeric,
  checked_at   timestamptz NOT NULL DEFAULT now()
);

-- Example when you also keep a linked FDW / dblink to replica.
-- Prefer application-side compare (consumer/reconcile.py pattern) in production.
