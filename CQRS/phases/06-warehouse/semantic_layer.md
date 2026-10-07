# Semantic layer notes (Phase 6)

Use after warehouse facts are stable. Tools: Looker, Power BI datasets, Metabase models, Cube.dev, etc.

## Suggested metrics

| Metric | Base | Grain |
|--------|------|-------|
| Net movement | `sum(balance)` on `wh.fact_aml_daily` | date, company, branch, account |
| Sales amount | `sum(amount_total)` on `wh.fact_sales_daily` | date, company, branch, product |
| Margin | `sum(amount_untaxed - cost)` | same as sales |

## Suggested dimensions

Join facts to `wh.dim_*` on surrogate keys. Expose business keys (`company_id`, `account.code`) for analysts.

## Guardrails

- Label every dashboard with warehouse `elt_watermark.as_of`.
- Do not publish ZATCA / statutory Exact reports from warehouse-only paths.
- Row-level security by `company_id` / branch for multi-tenant BI.
