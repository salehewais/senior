-- Run on PRIMARY (replicates) or directly on replica if roles not replicated.
-- Tighten table grants to what Exact/Analytical workers need.

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'odoo_reporting') THEN
    CREATE ROLE odoo_reporting LOGIN PASSWORD 'CHANGE_ME';
  END IF;
END $$;

GRANT CONNECT ON DATABASE odoo TO odoo_reporting;
GRANT USAGE ON SCHEMA public TO odoo_reporting;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO odoo_reporting;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO odoo_reporting;

-- Optional: force timeouts for this role
ALTER ROLE odoo_reporting SET statement_timeout = '180s';
ALTER ROLE odoo_reporting SET idle_in_transaction_session_timeout = '60s';
