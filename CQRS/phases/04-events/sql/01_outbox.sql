-- Optional transactional outbox on Odoo PRIMARY.
-- Writers insert in same TX as business change; poller publishes to queue.

CREATE SCHEMA IF NOT EXISTS reporting;

CREATE TABLE IF NOT EXISTS reporting.event_outbox (
  id            bigserial PRIMARY KEY,
  event_id      uuid NOT NULL UNIQUE,
  event_type    text NOT NULL,
  occurred_at   timestamptz NOT NULL DEFAULT now(),
  company_id    int NOT NULL,
  record_model  text NOT NULL,
  record_id     int NOT NULL,
  business_date date,
  payload       jsonb NOT NULL DEFAULT '{}',
  published_at  timestamptz,
  created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS event_outbox_unpublished_idx
  ON reporting.event_outbox (id)
  WHERE published_at IS NULL;
