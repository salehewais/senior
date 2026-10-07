CREATE TABLE IF NOT EXISTS reporting.dim_date (
  date_key     int PRIMARY KEY,  -- YYYYMMDD
  date         date NOT NULL UNIQUE,
  year         int NOT NULL,
  month        int NOT NULL,
  day          int NOT NULL,
  week         int NOT NULL,
  is_month_end boolean NOT NULL
);

CREATE TABLE IF NOT EXISTS reporting.dim_company (
  company_id   int PRIMARY KEY,
  name         text NOT NULL,
  currency     text,
  updated_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS reporting.dim_branch (
  branch_id    int PRIMARY KEY,
  company_id   int,
  name         text NOT NULL,
  updated_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS reporting.dim_account (
  account_id   int PRIMARY KEY,
  code         text,
  name         text NOT NULL,
  account_type text,
  updated_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS reporting.dim_product (
  product_id   int PRIMARY KEY,
  default_code text,
  name         text NOT NULL,
  categ        text,
  updated_at   timestamptz NOT NULL DEFAULT now()
);

-- Seed dim_date for a wide range (adjust as needed)
INSERT INTO reporting.dim_date (date_key, date, year, month, day, week, is_month_end)
SELECT
  to_char(d, 'YYYYMMDD')::int,
  d::date,
  extract(year FROM d)::int,
  extract(month FROM d)::int,
  extract(day FROM d)::int,
  extract(week FROM d)::int,
  (d::date = (date_trunc('month', d) + interval '1 month - 1 day')::date)
FROM generate_series(date '2018-01-01', date '2035-12-31', interval '1 day') AS g(d)
ON CONFLICT (date_key) DO NOTHING;
