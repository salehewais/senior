# Phase 2 — Shrink analytical reads (pre-aggregation)

Highest-impact performance lever for ~200M `account.move.line`. Replica without aggregation still scans 200M.

**Scope:** Analytical / management reports only. Exact Accounting stays on ledger schema (replica + async from Phase 1).

**Exit:** Top N analytical reports read summary rows (thousands–millions), not raw AML.

## Design principles

1. Choose grain from classified reports—not from AML’s natural key.
2. Prefer **scheduled tables** you control; matviews are fine as a first step.
3. Always expose **`as_of`** (last successful refresh watermark).
4. Incremental daytime refresh + nightly full/window rebuild.
5. Cache only identical parameter fan-out; cache does not replace aggregation.

---

## 1. Summary grains

Start with one or two grains that cover the top Analytical reports.

### A. Account movement daily (P&L / branch rollups)

Grain: `date × company_id × branch_id × account_id`

| Column | Type | Notes |
|--------|------|--------|
| `move_date` | date | Accounting date (not create_date) |
| `company_id` | int | |
| `branch_id` | int | Analytic/branch dimension used in your Odoo (adapt name) |
| `account_id` | int | |
| `debit` | numeric | Sum |
| `credit` | numeric | Sum |
| `balance` | numeric | `debit - credit` (or store signed amount only) |
| `line_count` | int | Optional; debug / reconcile |
| `updated_at` | timestamptz | Row maintenance |

**Primary key:** `(move_date, company_id, branch_id, account_id)`

### B. Sales daily (POS / product KPIs)

Grain: `date × company_id × branch_id × product_id`

| Column | Type | Notes |
|--------|------|--------|
| `sale_date` | date | |
| `company_id` | int | |
| `branch_id` | int | |
| `product_id` | int | |
| `qty` | numeric | |
| `amount_untaxed` | numeric | |
| `amount_total` | numeric | |
| `cost` | numeric | If available; else omit |
| `order_count` | int | Optional |
| `updated_at` | timestamptz | |

Add dimensions only when a top report requires them (e.g. `partner_id` usually explodes cardinality—avoid in daily grain).

### Optional: hourly “today” tables

For wallboards: same grain + `hour` for **current date only**, truncated nightly into daily.

---

## 2. Physical design options

### Option A — Materialized view (fastest to stand up)

```sql
-- Illustrative; map to your Odoo column names / branch field
CREATE MATERIALIZED VIEW reporting.aml_daily AS
SELECT
  am.date::date AS move_date,
  aml.company_id,
  /* branch expression */ AS branch_id,
  aml.account_id,
  sum(aml.debit) AS debit,
  sum(aml.credit) AS credit,
  sum(aml.debit - aml.credit) AS balance,
  count(*) AS line_count
FROM account_move_line aml
JOIN account_move am ON am.id = aml.move_id
WHERE am.state = 'posted'
GROUP BY 1, 2, 3, 4
WITH NO DATA;

CREATE UNIQUE INDEX aml_daily_pk
  ON reporting.aml_daily (move_date, company_id, branch_id, account_id);

-- Refresh (concurrent requires unique index)
REFRESH MATERIALIZED VIEW CONCURRENTLY reporting.aml_daily;
```

**Pros:** Simple. **Cons:** Full rebuild cost grows; harder incremental; still on replica DB.

### Option B — Summary tables + SQL jobs (recommended soon after MVP)

```sql
CREATE TABLE reporting.aml_daily (
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

CREATE TABLE reporting.refresh_watermark (
  dataset     text PRIMARY KEY,
  as_of       timestamptz NOT NULL,
  source_high_water timestamptz,
  status      text NOT NULL,
  detail      text,
  updated_at  timestamptz NOT NULL DEFAULT now()
);
```

Build on the **replica** first (Phase 1). Move to Reporting DB in Phase 3 without changing grain.

---

## 3. Refresh job design

### Nightly window rebuild (mandatory)

Rebuild last **D** days (e.g. 3–7) plus any open period your business can still post into.

```text
For dataset aml_daily:
  1. Lock soft: set watermark status=running
  2. DELETE FROM reporting.aml_daily WHERE move_date >= :window_start
  3. INSERT ... SELECT aggregate FROM AML/moves WHERE date >= :window_start AND posted
  4. Set as_of = now(), status=ok
  5. On failure: status=failed, keep previous rows outside failed transaction
```

Prefer one transaction per dataset window, or swap via shadow table:

```text
reporting.aml_daily_staging → aggregate → ANALYZE → rename swap with aml_daily
```

### Incremental daytime (optional, for ≤15 min SLA)

Use a **high-water mark** on `account_move.write_date` / `account_move_line.write_date` (confirm which updates on post/cancel in your Odoo version).

```text
1. Read source_high_water from watermark
2. Find move_ids touched since watermark (posted/cancelled/date changes)
3. Collect distinct move_date × company × branch × account affected
4. Re-aggregate only those keys from source
5. UPSERT into reporting.aml_daily
6. Advance watermark
```

**Cancel / date-change hazard:** always re-aggregate keys from source truth; never “subtract” blindly from events until Phase 4.

### Schedule sketch

| Job | Cadence | Scope |
|-----|---------|--------|
| `aml_daily_nightly` | 01:00 | Rolling D-day rebuild |
| `aml_daily_daytime` | every 10–15 min | Incremental upsert |
| `sales_daily_nightly` | 01:30 | Rolling D-day rebuild |
| `sales_daily_daytime` | every 10–15 min | Incremental upsert |
| `reconcile_sample` | nightly after rebuild | Compare totals vs AML for yesterday |

Run jobs on the **reporting worker host**, querying the **replica**.

---

## 4. Illustrative aggregate SQL (AML daily)

Adapt column names (`branch_id`, analytic distribution, multi-company) to your schema.

```sql
INSERT INTO reporting.aml_daily (
  move_date, company_id, branch_id, account_id,
  debit, credit, balance, line_count, updated_at
)
SELECT
  am.date::date AS move_date,
  aml.company_id,
  COALESCE(am.branch_id, 0) AS branch_id,  -- replace with real branch mapping
  aml.account_id,
  sum(aml.debit),
  sum(aml.credit),
  sum(aml.debit - aml.credit),
  count(*),
  now()
FROM account_move_line aml
JOIN account_move am ON am.id = aml.move_id
WHERE am.state = 'posted'
  AND am.date >= :window_start
  AND am.date <  :window_end
GROUP BY 1, 2, 3, 4
ON CONFLICT (move_date, company_id, branch_id, account_id)
DO UPDATE SET
  debit = EXCLUDED.debit,
  credit = EXCLUDED.credit,
  balance = EXCLUDED.balance,
  line_count = EXCLUDED.line_count,
  updated_at = EXCLUDED.updated_at;
```

---

## 5. Pointing reports at summaries

| Before | After |
|--------|--------|
| `account.move.line` search + read_group over wide dates | SQL/ORM against `reporting.aml_daily` filtered by date/company/branch |
| Odoo QWeb/PDF building totals in Python loops | Pre-summed rows; PDF only formats |

### Report adapter checklist

- [ ] Report marked Analytical in inventory
- [ ] Required dimensions ⊆ summary grain
- [ ] Line-level drill-down: optional link to Exact async report, not live AML scan in UI
- [ ] Header shows `as_of` from `reporting.refresh_watermark`
- [ ] If refresh `failed`, show banner; do not silently serve stale without label

---

## 6. Cache policy

Use Redis/app cache **only** when many users share identical params.

| Key | Example |
|-----|---------|
| Key | `an:branch_pnl:{company}:{branch}:{date_from}:{date_to}:{as_of}` |
| TTL | 60–300s, or invalidate when watermark advances |
| Bypass | If params unique per user, skip cache |

Never cache Exact statutory outputs as a correctness shortcut.

---

## 7. Reconciliation (nightly)

For yesterday (and sample of older days):

```sql
-- Source total vs summary total for one day/company
SELECT
  'source' AS origin,
  sum(aml.debit - aml.credit) AS balance
FROM account_move_line aml
JOIN account_move am ON am.id = aml.move_id
WHERE am.state = 'posted'
  AND am.company_id = :company_id
  AND am.date = :d
UNION ALL
SELECT
  'summary',
  sum(balance)
FROM reporting.aml_daily
WHERE company_id = :company_id
  AND move_date = :d;
```

Alert if abs(diff) > tolerance. Fix by window rebuild before adding events (Phase 4).

---

## 8. Acceptance tests

- [ ] Top N Analytical reports no longer issue wide AML scans (verify via `pg_stat_statements` / logs)
- [ ] Summary row count << AML (order-of-magnitude check)
- [ ] Daytime incremental keeps freshness ≤ SLA under normal posting volume
- [ ] Nightly reconcile green for sampled companies/branches
- [ ] Exact reports untouched (still replica/AML)

## 9. Handoff → Phase 3

When matview/summary-on-replica works but you need schema freedom, more consumers, or to unload the replica:

- Keep the **same grains**
- Copy into Reporting DB facts/dims
- See roadmap Phase 3 in [`phase-checklists.md`](phase-checklists.md) and [`target-architecture.md`](target-architecture.md)
