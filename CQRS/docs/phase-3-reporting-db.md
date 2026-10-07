# Phase 3 — Reporting DB + read model (CQRS light)

When summaries outgrow “matview on replica”: move analytical storage to a dedicated DB with fact/dim shapes. Keep Exact Accounting on Odoo primary/replica schema.

**Exit:** Analytical workload fully off Odoo primary; reports no longer depend on AML shape.

**Prerequisite:** Phase 2 grains and refresh logic work; you are copying a known-good model, not inventing a new one.

## Target shape

```text
Odoo Primary (write model / AML)
        │
   sync / ETL / CDC  (from primary or replica)
        ▼
Reporting DB (facts + dims + daily summaries)
        ▼
Management reports / light BI
```

This is **CQRS as data separation**: Odoo remains the write model; Reporting DB is the analytical read model.

## 1. When to start Phase 3

Move off replica-local summaries when any of these are true:

- Analytical refresh/query load still hurts the replica (Exact lag risk)
- Multiple consumers need the same facts (Odoo reports + Metabase/etc.)
- You need denormalized columns / indexes AML-shaped tables fight
- Clear ownership: analytics team owns Reporting DB schema

If none apply, stay on Phase 2 longer.

## 2. Database & schemas

| Object | Guidance |
|--------|----------|
| Instance | Separate PostgreSQL (or at least separate database + roles) |
| Schema | e.g. `reporting` for facts; `reporting_meta` for watermarks |
| Role | `reporting_writer` (ETL only), `reporting_reader` (apps/BI) |
| Source DSN | Prefer **replica** as ETL source to protect primary |

## 3. Dimensions (slowly changing as needed)

Minimal set driven by Phase 2 grains:

```text
dim_date        (date_key, date, year, month, week, is_month_end, …)
dim_company     (company_id, name, currency, …)
dim_branch      (branch_id, company_id, name, …)
dim_account     (account_id, code, name, account_type, …)
dim_product     (product_id, default_code, name, categ, …)  -- if sales grain exists
```

Load strategy: nightly full upsert from Odoo tables is usually enough at this scale of dimensions.

## 4. Facts (carry Phase 2 grains forward)

```text
fact_aml_daily
  date_key, company_id, branch_id, account_id,
  debit, credit, balance, line_count,
  as_of

fact_sales_daily
  date_key, company_id, branch_id, product_id,
  qty, amount_untaxed, amount_total, cost, order_count,
  as_of
```

Keys and measures should match [`phase-2-preaggregation.md`](phase-2-preaggregation.md). Avoid introducing new grain until a classified report requires it.

## 5. Sync options

| Method | Pros | Cons | Fit |
|--------|------|------|-----|
| Scheduled ETL (SQL dump of summary or re-aggregate from replica) | Simple, debuggable | Coarser lag | Default start |
| Copy Phase 2 summary tables → Reporting DB | Reuses tested aggregate | Two hops | Good bridge |
| CDC (logical replication / Debezium) on moves | Near-real-time | Complexity; still need aggregate step | Later / Phase 4 prep |
| Domain events | Incremental | Needs app instrumentation | Phase 4 |

**Recommended bridge:** keep aggregating on replica (Phase 2 jobs) → `COPY`/upsert facts into Reporting DB every N minutes. Then relocate aggregation workers to read replica and write **only** Reporting DB.

## 6. Consistency rules

| Lane | Rule |
|------|------|
| Exact | Still primary/replica Odoo schema—**not** Reporting DB—unless parity proven for that report |
| Analytical | Query facts; show `as_of`; nightly reconcile vs Odoo aggregates |
| Drill to lines | Enqueue Exact async report; do not join back to 200M AML from BI by default |

## 7. Cutover steps

1. Provision Reporting DB + roles + dims
2. Backfill facts for required history window
3. Dual-run: analytical reports still on Phase 2 summaries; compare totals to Reporting DB
4. Flip analytical DSN to Reporting DB
5. Stop serving analytical queries from Odoo primary/replica (Exact remains on replica)
6. Monitor ETL lag vs Analytical SLA

## 8. Acceptance

- [ ] No analytical report sessions on primary
- [ ] Fact row counts and spot totals match Phase 2 summaries
- [ ] Exact lag/POS unaffected by analytical refresh
- [ ] Reader credentials cannot write facts

## 9. Handoff → Phase 4

When batch ETL cannot meet freshness SLA without expensive re-aggregation, add event-driven incremental updates ([`phase-4-events-and-beyond.md`](phase-4-events-and-beyond.md)).
