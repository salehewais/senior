-- Compare source AML vs summary for one company/day.
-- Usage: psql -v company_id=1 -v d="'2026-10-06'" -f 04_reconcile_aml_daily.sql

SELECT origin, balance
FROM (
  SELECT
    'source'::text AS origin,
    coalesce(sum(aml.debit - aml.credit), 0) AS balance
  FROM account_move_line aml
  JOIN account_move am ON am.id = aml.move_id
  WHERE am.state = 'posted'
    AND aml.company_id = :company_id
    AND am.date = :d::date

  UNION ALL

  SELECT
    'summary'::text,
    coalesce(sum(balance), 0)
  FROM reporting.aml_daily
  WHERE company_id = :company_id
    AND move_date = :d::date
) s;

SELECT
  (SELECT balance FROM (
     SELECT coalesce(sum(aml.debit - aml.credit), 0) AS balance
     FROM account_move_line aml
     JOIN account_move am ON am.id = aml.move_id
     WHERE am.state = 'posted'
       AND aml.company_id = :company_id
       AND am.date = :d::date
  ) x)
  -
  (SELECT coalesce(sum(balance), 0)
   FROM reporting.aml_daily
   WHERE company_id = :company_id AND move_date = :d::date)
  AS drift;
