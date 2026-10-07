-- Optional MVP: materialized view instead of (or before) summary tables.
-- Prefer 01_aml_daily.sql for incremental control.

DROP MATERIALIZED VIEW IF EXISTS reporting.aml_daily_mv;

CREATE MATERIALIZED VIEW reporting.aml_daily_mv AS
SELECT
  am.date::date AS move_date,
  aml.company_id,
  reporting.branch_id(am) AS branch_id,
  aml.account_id,
  sum(aml.debit) AS debit,
  sum(aml.credit) AS credit,
  sum(aml.debit - aml.credit) AS balance,
  count(*)::int AS line_count
FROM account_move_line aml
JOIN account_move am ON am.id = aml.move_id
WHERE am.state = 'posted'
GROUP BY 1, 2, 3, 4
WITH NO DATA;

CREATE UNIQUE INDEX aml_daily_mv_pk
  ON reporting.aml_daily_mv (move_date, company_id, branch_id, account_id);

-- REFRESH MATERIALIZED VIEW CONCURRENTLY reporting.aml_daily_mv;
