# Report classification (Exact vs Analytical)

Use this template in **Phase 0** to inventory reports, assign lanes, and set SLAs before choosing tech.

## Why this matters

| If you treat… | You tend to… |
|---------------|--------------|
| Analytical reports as Exact | Overspend on near-real-time ledger parity |
| Exact reports as Analytical | Risk wrong books, tax, ZATCA, statutory closes |

One architecture for all reports is a non-goal.

---

## Lane definitions

### Exact Accounting

- Must match Odoo ledger (primary or controlled as-of on low-lag replica).
- Typical: trial balance, general ledger, partner ledger, tax reports, ZATCA-related, statutory period close.
- Allowed early levers: replica, async export, connection/concurrency limits.
- Disallowed for “speed”: pre-agg that cannot prove parity; reporting DB without reconciliation.

### Analytical / Management

- Eventual consistency OK (minutes–hours), with visible **as-of** timestamp.
- Typical: branch KPIs, daily sales, dashboards, trends, cross-branch P&L rollups.
- Preferred levers: pre-aggregation, matviews, read models, reporting DB, events, cache.

---

## Suggested SLAs (customize)

| Metric | Exact | Analytical |
|--------|-------|------------|
| Freshness | Replica lag ≤ **N** seconds (alert if exceeded); or run on primary for closes | ≤ **15 minutes** (or hourly if business accepts) |
| Delivery | Async OK; user notified when ready | Async OK; dashboards show “as of” |
| Correctness | Ledger parity required | Reconcile nightly vs source; drift alert |
| Concurrency | Hard caps so POS stays healthy | Caps + shared cache/summaries |

Document your chosen **N** and analytical freshness after measuring replica lag and business needs.

---

## Inventory template

Copy per report (or maintain in a sheet). Sort by impact: `frequency × runtime × rows_touched`.

```text
Report name:
Owner / team:
Primary users (roles):
Peak concurrent users:
Typical parameters (company, branch, date range, …):

Lane:            [ Exact | Analytical | Mixed* ]
Freshness need:  [ real-time | ≤N sec | ≤15 min | hourly | daily ]
Statutory / tax / ZATCA relevant: [ yes | no ]

Current runtime (p50 / p95):
Rows touched (estimate):
Tables hit (AML? others?):
Runs during POS peak: [ yes | no ]

Current path:    [ sync HTTP | queue | other ]
Target path:     [ replica exact | summary | reporting DB | warehouse ]

Priority (1–5):
Notes / blockers:
```

\*Mixed = split into two deliverables (exact extract + analytical dashboard), do not keep one hybrid query path.

---

## Classification checklist

For each report, answer:

1. If numbers differ from Odoo GL by a few minutes, is that a **business failure** or **acceptable lag**?
2. Is this used for **filing, audit, or close**—or for **management decisions**?
3. Does it need **line-level AML detail**, or would **daily (or hourly) grain** suffice?
4. Can many users share the **same parameter set** (cache candidate)?
5. Should generation be **async** even if the data path stays Exact?

If (1) = failure → Exact. If (3) = summary grain OK → Analytical + pre-agg.

---

## Baseline metrics to capture (Phase 0)

### Application / report

- Top reports by frequency and wall time
- Concurrent report sessions during POS peak
- Export formats and average payload size

### Database (during POS peaks)

- `pg_stat_activity` — active report queries vs write sessions
- Lock waits / blocked queries
- IO saturation, buffer hit ratio for AML
- Slow query log samples for AML scans
- Replica lag (if replica already exists)

### Exit for Phase 0

- [ ] Prioritized report list
- [ ] Every top report assigned Exact or Analytical
- [ ] SLAs written and agreed
- [ ] Baseline timings recorded for before/after comparison

---

## Example assignments (illustrative)

| Report | Lane | Rationale |
|--------|------|-----------|
| Trial balance / GL | Exact | Must match ledger |
| Partner ledger | Exact | Statement / reconciliation |
| Tax / ZATCA extracts | Exact | Statutory |
| Branch daily sales KPI | Analytical | Minutes lag OK; pre-agg |
| Cross-branch P&L dashboard | Analytical | Summaries + reporting DB |
| “Sales today” wallboard | Analytical | Eventual + as-of |

---

## Routing rule (after Phase 1–3)

```text
Exact      → Primary or low-lag replica + async export + concurrency caps
Analytical → Summaries / read model / reporting DB (+ optional events)
Never     → Exact statutory report served only from unverified reporting DB
```
