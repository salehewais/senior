# Phases 4–6 — Events, CQRS formalization, warehouse

Build these only after Phase 2–3 read models exist. Events maintain summaries; they do not replace designing the grain.

---

## Phase 4 — Event-driven incremental refresh

**Goal:** Meet Analytical freshness SLA without re-scanning ~200M rows every refresh.

**Exit:** Incremental updates + nightly reconcile keep freshness within SLA.

### Flow

```text
Invoice posted / Payment posted / POS order done
        → domain event (payload: ids + company + date keys)
        → queue
        → worker re-aggregates affected grain keys from source (or applies verified deltas)
        → upsert Reporting DB / summary tables
        → watermark / as_of advances

Nightly: reconcile source aggregates vs read model → alert on drift → window rebuild if needed
```

### Start with few high-value events

| Event | Typical trigger in Odoo | Affects |
|-------|-------------------------|---------|
| Invoice / move posted | `account.move` → `posted` | `fact_aml_daily` keys for move date/accounts |
| Move cancelled / reset | state leave `posted` | Same keys (must recompute, not ignore) |
| Payment posted | payment move posted | AML daily (and cash KPIs if any) |
| POS order done | POS order paid/posted | `fact_sales_daily` |

### Implementation rules

1. **Recompute keys from source** for affected `date × company × branch × account` (or product). Prefer this over fragile +/- deltas until you have strong tests.
2. **Idempotent consumers** (at-least-once queue is fine if upsert is key-based).
3. **Ordering:** late events for old dates must still recompute that date’s keys.
4. **Backfill path retained:** nightly/window rebuild remains the source of recovery.
5. **UI:** always show `as_of`; if consumer lag > SLA, banner.

### Minimal event envelope

```text
event_id, event_type, occurred_at,
company_id, record_model, record_id,
business_date,  -- accounting/sale date when known
trace_id
```

### Acceptance

- [ ] Daytime freshness meets SLA under normal posting volume
- [ ] Killing a worker does not permanently desync (replay + nightly reconcile)
- [ ] Cancelled moves correct summaries within SLA
- [ ] Nightly reconcile alert fires on intentional fault injection

---

## Phase 5 — Explicit CQRS architecture

**Goal:** Formalize ownership when multiple consumers, read models, or teams need clear boundaries—not as a first performance lever.

### Boundaries

| Side | System | Owner |
|------|--------|-------|
| Commands (writes) | Odoo / POS → primary PostgreSQL | ERP team |
| Queries (reads) | Reporting DB / summaries / BI | Reporting / analytics |
| Sync | Events + batch ETL + reconcile | Shared contract + on-call |

### Do

- Document which reports are Allowed on which read models
- Forbid Exact statutory reports on unverified projections
- One write path for accounting facts: Odoo only (no dual-write from workers into primary AML)
- Version event contracts; consumers tolerate additive fields

### Trigger to invest

- Second/third read model (e.g. ops dashboard vs finance KPI store)
- Team split between ERP and BI
- Need explicit SLAs per consumer

If still one summary DB and one team, Phase 3–4 naming is enough—do not create ceremony.

---

## Phase 6 — Warehouse / OLAP

**Goal:** Cross-domain historical BI when management analytics become a product of their own.

**Skip until** Phase 2–4 cannot meet: long history, many domains, forecasting, or tool requirements (Power BI / Looker / etc.) beyond Odoo reports.

### Shape

```text
Odoo (+ Reporting DB) ──ETL/ELT──► Data Warehouse
                                      │
                                      ├── BI tools
                                      └── optional OLAP / semantic layer
```

### Rules

- Warehouse feeds **Analytical / enterprise BI**, not ZATCA/statutory Exact delivery
- Prefer ELT from Reporting DB facts (already cleaned) plus selective Odoo dims
- Cost/ops model approved before build

### OLAP

Add cubes/semantic layer only for heavy multidimensional analysis after warehouse facts are stable.

---

## Late special topics (still not early levers)

### Partitioning `account.move.line`

- Study Odoo FK, ORM, upgrade, and backup/restore impact first
- Useful later for prune-by-date / partition elimination on Exact range queries
- Never a substitute for Analytical pre-aggregation

### Archiving

- Legal / audit / ZATCA retention first
- Prefer hot/cold / cold storage / reporting history
- **Never** equate archive with naive `DELETE` from AML
- Exact reconstructibility must remain possible per policy

---

## Sequence lock

```text
2 Summaries exist
  → 3 Reporting DB (optional unload)
    → 4 Events (fresher increments)
      → 5 CQRS formalize (if org complexity)
        → 6 Warehouse (if BI product)
```

Jumping to 4–6 without 2 is the failure mode this pack exists to prevent.
