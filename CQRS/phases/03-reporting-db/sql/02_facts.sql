CREATE TABLE IF NOT EXISTS reporting.fact_aml_daily (
  date_key     int NOT NULL REFERENCES reporting.dim_date (date_key),
  company_id   int NOT NULL,
  branch_id    int NOT NULL,
  account_id   int NOT NULL,
  debit        numeric NOT NULL DEFAULT 0,
  credit       numeric NOT NULL DEFAULT 0,
  balance      numeric NOT NULL DEFAULT 0,
  line_count   int NOT NULL DEFAULT 0,
  as_of        timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (date_key, company_id, branch_id, account_id)
);

CREATE INDEX IF NOT EXISTS fact_aml_daily_company_date_idx
  ON reporting.fact_aml_daily (company_id, date_key);

CREATE TABLE IF NOT EXISTS reporting.fact_sales_daily (
  date_key         int NOT NULL REFERENCES reporting.dim_date (date_key),
  company_id       int NOT NULL,
  branch_id        int NOT NULL,
  product_id       int NOT NULL,
  qty              numeric NOT NULL DEFAULT 0,
  amount_untaxed   numeric NOT NULL DEFAULT 0,
  amount_total     numeric NOT NULL DEFAULT 0,
  cost             numeric NOT NULL DEFAULT 0,
  order_count      int NOT NULL DEFAULT 0,
  as_of            timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (date_key, company_id, branch_id, product_id)
);

CREATE INDEX IF NOT EXISTS fact_sales_daily_company_date_idx
  ON reporting.fact_sales_daily (company_id, date_key);
