-- Phase 2: AML daily summary table + refresh helpers

CREATE TABLE IF NOT EXISTS reporting.aml_daily (
  move_date   date NOT NULL,
  company_id  int  NOT NULL,
  branch_id   int  NOT NULL,
  account_id  int  NOT NULL,
  debit       numeric NOT NULL DEFAULT 0,
  credit      numeric NOT NULL DEFAULT 0,
  balance     numeric NOT NULL DEFAULT 0,
  line_count  int NOT NULL DEFAULT 0,
  updated_at  timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (move_date, company_id, branch_id, account_id)
);

CREATE INDEX IF NOT EXISTS aml_daily_company_date_idx
  ON reporting.aml_daily (company_id, move_date);

-- Nightly / window rebuild for [:window_start, :window_end)
CREATE OR REPLACE FUNCTION reporting.refresh_aml_daily_window(
  p_window_start date,
  p_window_end   date
) RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  UPDATE reporting.refresh_watermark
  SET status = 'running', detail = format('window %s .. %s', p_window_start, p_window_end),
      updated_at = now()
  WHERE dataset = 'aml_daily';

  DELETE FROM reporting.aml_daily
  WHERE move_date >= p_window_start
    AND move_date < p_window_end;

  INSERT INTO reporting.aml_daily (
    move_date, company_id, branch_id, account_id,
    debit, credit, balance, line_count, updated_at
  )
  SELECT
    am.date::date AS move_date,
    aml.company_id,
    reporting.branch_id(am) AS branch_id,
    aml.account_id,
    sum(aml.debit),
    sum(aml.credit),
    sum(aml.debit - aml.credit),
    count(*)::int,
    now()
  FROM account_move_line aml
  JOIN account_move am ON am.id = aml.move_id
  WHERE am.state = 'posted'
    AND am.date >= p_window_start
    AND am.date < p_window_end
  GROUP BY 1, 2, 3, 4;

  UPDATE reporting.refresh_watermark
  SET status = 'ok',
      as_of = now(),
      detail = format('window refresh ok %s .. %s', p_window_start, p_window_end),
      updated_at = now()
  WHERE dataset = 'aml_daily';
EXCEPTION WHEN OTHERS THEN
  UPDATE reporting.refresh_watermark
  SET status = 'failed', detail = SQLERRM, updated_at = now()
  WHERE dataset = 'aml_daily';
  RAISE;
END;
$$;

-- Incremental: re-aggregate keys touched since high water (by move write_date)
CREATE OR REPLACE FUNCTION reporting.refresh_aml_daily_incremental(
  p_since timestamptz DEFAULT NULL
) RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
  v_since timestamptz;
BEGIN
  SELECT COALESCE(p_since, source_high_water, now() - interval '1 day')
  INTO v_since
  FROM reporting.refresh_watermark
  WHERE dataset = 'aml_daily';

  UPDATE reporting.refresh_watermark
  SET status = 'running', detail = format('incremental since %s', v_since), updated_at = now()
  WHERE dataset = 'aml_daily';

  CREATE TEMPORARY TABLE _aml_touch ON COMMIT DROP AS
  SELECT DISTINCT
    am.date::date AS move_date,
    aml.company_id,
    reporting.branch_id(am) AS branch_id,
    aml.account_id
  FROM account_move am
  JOIN account_move_line aml ON aml.move_id = am.id
  WHERE am.write_date >= v_since
     OR aml.write_date >= v_since;

  DELETE FROM reporting.aml_daily d
  USING _aml_touch t
  WHERE d.move_date = t.move_date
    AND d.company_id = t.company_id
    AND d.branch_id = t.branch_id
    AND d.account_id = t.account_id;

  INSERT INTO reporting.aml_daily (
    move_date, company_id, branch_id, account_id,
    debit, credit, balance, line_count, updated_at
  )
  SELECT
    am.date::date,
    aml.company_id,
    reporting.branch_id(am),
    aml.account_id,
    sum(aml.debit),
    sum(aml.credit),
    sum(aml.debit - aml.credit),
    count(*)::int,
    now()
  FROM account_move_line aml
  JOIN account_move am ON am.id = aml.move_id
  JOIN _aml_touch t
    ON t.move_date = am.date::date
   AND t.company_id = aml.company_id
   AND t.branch_id = reporting.branch_id(am)
   AND t.account_id = aml.account_id
  WHERE am.state = 'posted'
  GROUP BY 1, 2, 3, 4;

  UPDATE reporting.refresh_watermark
  SET status = 'ok',
      as_of = now(),
      source_high_water = now(),
      detail = 'incremental ok',
      updated_at = now()
  WHERE dataset = 'aml_daily';
EXCEPTION WHEN OTHERS THEN
  UPDATE reporting.refresh_watermark
  SET status = 'failed', detail = SQLERRM, updated_at = now()
  WHERE dataset = 'aml_daily';
  RAISE;
END;
$$;
