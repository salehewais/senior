CREATE SCHEMA IF NOT EXISTS reporting;
CREATE SCHEMA IF NOT EXISTS reporting_meta;

CREATE TABLE IF NOT EXISTS reporting_meta.refresh_watermark (
  dataset              text PRIMARY KEY,
  as_of                timestamptz NOT NULL DEFAULT to_timestamp(0),
  source_high_water    timestamptz,
  status               text NOT NULL DEFAULT 'idle',
  detail               text,
  updated_at           timestamptz NOT NULL DEFAULT now()
);

INSERT INTO reporting_meta.refresh_watermark (dataset)
VALUES ('aml_daily'), ('sales_daily'), ('dims')
ON CONFLICT DO NOTHING;
