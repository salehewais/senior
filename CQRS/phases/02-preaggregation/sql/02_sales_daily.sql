-- Phase 2: POS sales daily summary (skip install if no pos_order tables)

CREATE TABLE IF NOT EXISTS reporting.sales_daily (
  sale_date        date NOT NULL,
  company_id       int  NOT NULL,
  branch_id        int  NOT NULL,
  product_id       int  NOT NULL,
  qty              numeric NOT NULL DEFAULT 0,
  amount_untaxed   numeric NOT NULL DEFAULT 0,
  amount_total     numeric NOT NULL DEFAULT 0,
  cost             numeric NOT NULL DEFAULT 0,
  order_count      int NOT NULL DEFAULT 0,
  updated_at       timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (sale_date, company_id, branch_id, product_id)
);

CREATE INDEX IF NOT EXISTS sales_daily_company_date_idx
  ON reporting.sales_daily (company_id, sale_date);

-- Assumes standard Odoo POS table names; adapt config/branch fields.
CREATE OR REPLACE FUNCTION reporting.refresh_sales_daily_window(
  p_window_start date,
  p_window_end   date
) RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  IF to_regclass('public.pos_order') IS NULL THEN
    UPDATE reporting.refresh_watermark
    SET status = 'ok', detail = 'pos_order missing — skipped', as_of = now(), updated_at = now()
    WHERE dataset = 'sales_daily';
    RETURN;
  END IF;

  UPDATE reporting.refresh_watermark
  SET status = 'running', detail = format('window %s .. %s', p_window_start, p_window_end),
      updated_at = now()
  WHERE dataset = 'sales_daily';

  DELETE FROM reporting.sales_daily
  WHERE sale_date >= p_window_start
    AND sale_date < p_window_end;

  INSERT INTO reporting.sales_daily (
    sale_date, company_id, branch_id, product_id,
    qty, amount_untaxed, amount_total, cost, order_count, updated_at
  )
  SELECT
    (po.date_order AT TIME ZONE 'UTC')::date AS sale_date,
    po.company_id,
    COALESCE(po.config_id, 0) AS branch_id, -- replace with real branch map
    pol.product_id,
    sum(pol.qty),
    sum(pol.price_subtotal),
    sum(pol.price_subtotal_incl),
    sum(COALESCE(pol.total_cost, 0)),
    count(DISTINCT po.id)::int,
    now()
  FROM pos_order_line pol
  JOIN pos_order po ON po.id = pol.order_id
  WHERE po.state IN ('paid', 'done', 'invoiced')
    AND (po.date_order AT TIME ZONE 'UTC')::date >= p_window_start
    AND (po.date_order AT TIME ZONE 'UTC')::date < p_window_end
  GROUP BY 1, 2, 3, 4;

  UPDATE reporting.refresh_watermark
  SET status = 'ok', as_of = now(),
      detail = format('window refresh ok %s .. %s', p_window_start, p_window_end),
      updated_at = now()
  WHERE dataset = 'sales_daily';
EXCEPTION WHEN OTHERS THEN
  UPDATE reporting.refresh_watermark
  SET status = 'failed', detail = SQLERRM, updated_at = now()
  WHERE dataset = 'sales_daily';
  RAISE;
END;
$$;
