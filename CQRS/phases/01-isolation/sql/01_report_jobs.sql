-- Async report job ledger. Install where the enqueue API can write
-- (Odoo primary DB or a small control DB). Workers update status.

CREATE SCHEMA IF NOT EXISTS reporting;

CREATE TABLE IF NOT EXISTS reporting.report_job (
  id                bigserial PRIMARY KEY,
  report_code       text NOT NULL,
  lane              text NOT NULL CHECK (lane IN ('exact', 'analytical')),
  requested_by      text,
  company_ids       int[] NOT NULL DEFAULT '{}',
  params_json       jsonb NOT NULL DEFAULT '{}',
  status            text NOT NULL DEFAULT 'queued'
                      CHECK (status IN ('queued', 'running', 'done', 'failed', 'cancelled')),
  replica_lag_at_start interval,
  as_of_timestamp   timestamptz,
  artifact_uri      text,
  error             text,
  created_at        timestamptz NOT NULL DEFAULT now(),
  started_at        timestamptz,
  finished_at       timestamptz
);

CREATE INDEX IF NOT EXISTS report_job_status_created_idx
  ON reporting.report_job (status, created_at);

CREATE INDEX IF NOT EXISTS report_job_requested_by_idx
  ON reporting.report_job (requested_by, created_at DESC);
