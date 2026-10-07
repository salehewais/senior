-- Phase 2: reporting schema + watermark + branch helper (on REPLICA)

CREATE SCHEMA IF NOT EXISTS reporting;

CREATE TABLE IF NOT EXISTS reporting.refresh_watermark (
  dataset              text PRIMARY KEY,
  as_of                timestamptz NOT NULL DEFAULT to_timestamp(0),
  source_high_water    timestamptz,
  status               text NOT NULL DEFAULT 'idle'
                         CHECK (status IN ('idle', 'running', 'ok', 'failed')),
  detail               text,
  updated_at           timestamptz NOT NULL DEFAULT now()
);

INSERT INTO reporting.refresh_watermark (dataset, status)
VALUES ('aml_daily', 'idle'), ('sales_daily', 'idle')
ON CONFLICT (dataset) DO NOTHING;

-- Adapt body per phases/shared/branch_mapping.md
CREATE OR REPLACE FUNCTION reporting.branch_id(am account_move)
RETURNS integer
LANGUAGE sql
STABLE
AS $$
  SELECT COALESCE(
    -- am.branch_id,
    0
  );
$$;

COMMENT ON FUNCTION reporting.branch_id(account_move) IS
  'Map account_move → branch_id integer; default 0 until customized';
