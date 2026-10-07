-- Warehouse star (WAREHOUSE_DSN). Prefer loading from Reporting DB facts.

CREATE SCHEMA IF NOT EXISTS wh;

CREATE TABLE IF NOT EXISTS wh.dim_date (
  date_key int PRIMARY KEY,
  date date NOT NULL UNIQUE,
  year int NOT NULL,
  month int NOT NULL,
  day int NOT NULL,
  week int NOT NULL,
  is_month_end boolean NOT NULL
);

CREATE TABLE IF NOT EXISTS wh.dim_company (
  company_sk serial PRIMARY KEY,
  company_id int NOT NULL UNIQUE,
  name text NOT NULL,
  currency text
);

CREATE TABLE IF NOT EXISTS wh.dim_branch (
  branch_sk serial PRIMARY KEY,
  branch_id int NOT NULL UNIQUE,
  company_id int,
  name text NOT NULL
);

CREATE TABLE IF NOT EXISTS wh.dim_account (
  account_sk serial PRIMARY KEY,
  account_id int NOT NULL UNIQUE,
  code text,
  name text NOT NULL,
  account_type text
);

CREATE TABLE IF NOT EXISTS wh.dim_product (
  product_sk serial PRIMARY KEY,
  product_id int NOT NULL UNIQUE,
  default_code text,
  name text NOT NULL,
  categ text
);

CREATE TABLE IF NOT EXISTS wh.fact_aml_daily (
  date_key int NOT NULL REFERENCES wh.dim_date (date_key),
  company_sk int NOT NULL REFERENCES wh.dim_company (company_sk),
  branch_sk int NOT NULL REFERENCES wh.dim_branch (branch_sk),
  account_sk int NOT NULL REFERENCES wh.dim_account (account_sk),
  debit numeric NOT NULL DEFAULT 0,
  credit numeric NOT NULL DEFAULT 0,
  balance numeric NOT NULL DEFAULT 0,
  line_count int NOT NULL DEFAULT 0,
  loaded_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (date_key, company_sk, branch_sk, account_sk)
);

CREATE TABLE IF NOT EXISTS wh.fact_sales_daily (
  date_key int NOT NULL REFERENCES wh.dim_date (date_key),
  company_sk int NOT NULL REFERENCES wh.dim_company (company_sk),
  branch_sk int NOT NULL REFERENCES wh.dim_branch (branch_sk),
  product_sk int NOT NULL REFERENCES wh.dim_product (product_sk),
  qty numeric NOT NULL DEFAULT 0,
  amount_untaxed numeric NOT NULL DEFAULT 0,
  amount_total numeric NOT NULL DEFAULT 0,
  cost numeric NOT NULL DEFAULT 0,
  order_count int NOT NULL DEFAULT 0,
  loaded_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (date_key, company_sk, branch_sk, product_sk)
);

CREATE TABLE IF NOT EXISTS wh.elt_watermark (
  dataset text PRIMARY KEY,
  as_of timestamptz NOT NULL DEFAULT to_timestamp(0),
  detail text,
  updated_at timestamptz NOT NULL DEFAULT now()
);
