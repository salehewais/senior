# Phase checklists

Exit criteria and work items per phase. Complete in order; skip ahead only with an explicit risk acceptance.

---

## Phase 0 — Measure and classify (1–2 weeks)

**Goal:** Know which reports hurt, which lane they belong to, and what “good” means.

**Design detail:** [`phase-0-baseline.md`](phase-0-baseline.md) · [`report-classification.md`](report-classification.md)

### Do

- [ ] Inventory top reports (frequency, runtime, rows touched, tables)
- [ ] Assign each: **Exact** vs **Analytical** (see [`report-classification.md`](report-classification.md))
- [ ] Capture contention during POS peaks (`pg_stat_activity`, locks, IO, slow queries)
- [ ] Define SLAs (analytical freshness; exact replica lag ceiling)
- [ ] Record baseline p50/p95 timings for top N reports and POS checkout latency

### Exit

- [ ] Prioritized report list
- [ ] Lane assignment for every high-impact report
- [ ] Written SLAs + baselines for before/after comparison

---

## Phase 1 — Protect Odoo writes (quick wins)

**Goal:** Reports must not choke POS/writes—even if heavy queries still take 30–60s on a replica.

**Design detail:** [`phase-1-isolation.md`](phase-1-isolation.md)

### Do

- [ ] PostgreSQL **read replica** for reporting traffic only
- [ ] Lag monitoring + alert at Exact SLA threshold
- [ ] **Separate reporting app/worker host** (CPU/RAM/connections off Odoo web tier)
- [ ] Connection pooling for report DB access
- [ ] Worker / query **concurrency caps** (prevent N users × full AML scan)
- [ ] **Async report generation**: queue → workers → PDF/Excel/store → notify
- [ ] Route Exact reports to replica (or primary only per policy)

### Exit

- [ ] Write latency / POS checkout stable under concurrent report load
- [ ] Report HTTP no longer holds long-lived request threads for heavy jobs

**Opinion:** This phase often restores POS stability without making 200M scans cheap.

---

## Phase 2 — Shrink analytical reads (biggest performance win)

**Goal:** Top analytical reports read thousands–millions of summary rows, not 200M AML.

**Design detail:** [`phase-2-preaggregation.md`](phase-2-preaggregation.md)

### Do

- [ ] Pick top N **Analytical** reports only
- [ ] Design summary grain (e.g. `date × company × branch × account` and/or product)
- [ ] Implement matviews **or** scheduled SQL aggregation (nightly + incremental daytime if needed)
- [ ] Point management reports at summaries—not raw `account.move.line`
- [ ] Add cache only for repeated identical parameter sets
- [ ] Expose refresh “as of” on analytical UI
- [ ] Monitor refresh job success/duration

### Defer

- [ ] Partitioning AML
- [ ] Full CQRS
- [ ] Warehouse

### Exit

- [ ] Top N analytical reports no longer full-scan AML
- [ ] Analytical runtime meets agreed targets under concurrent use

**Opinion:** Pre-aggregation is the highest-impact technique for the 200M problem. Replica without aggregation still scans 200M.

---

## Phase 3 — Reporting DB + read model (CQRS light)

**Goal:** Analytical workload fully off Odoo primary; reports independent of AML shape.

**Design detail:** [`phase-3-reporting-db.md`](phase-3-reporting-db.md)

### Do

- [ ] Provision dedicated **Reporting DB**
- [ ] Model facts/dims (`fact_*_daily`, `dim_branch`, etc.) from classified reports
- [ ] Sync path: ETL and/or CDC from primary or replica
- [ ] Move analytical reports to Reporting DB
- [ ] Keep Exact Accounting on primary/replica Odoo schema
- [ ] Document ownership of sync jobs and schema

### Exit

- [ ] Analytical queries do not hit Odoo primary
- [ ] Reports no longer depend on AML table shape
- [ ] Exact lane still ledger-correct under SLA

**Opinion:** Right “CQRS” for Odoo in practice—data separation without rewriting Odoo writes on day one.

---

## Phase 4 — Event-driven incremental refresh

**Goal:** Meet analytical freshness SLA without re-scanning 200M every refresh.

**Design detail:** [`phase-4-events-and-beyond.md`](phase-4-events-and-beyond.md)

### Do

- [ ] Identify high-value events (invoice posted, payment posted, POS order done)
- [ ] Emit → queue → worker → update summary / Reporting DB
- [ ] Surface “as of” from last successful apply / watermark
- [ ] Nightly **reconciliation** (source aggregates vs read model)
- [ ] Alert on missed events / drift beyond tolerance
- [ ] Keep batch backfill path for rebuilds

### Exit

- [ ] Analytical freshness meets SLA via incremental updates
- [ ] Nightly reconcile green (or drift within tolerance)

**Opinion:** Events maintain an existing read model; they are not the first step.

---

## Phase 5 — Explicit CQRS architecture

**Goal:** Formalize ownership when complexity (multiple consumers/read models/teams) demands it.

**Design detail:** [`phase-4-events-and-beyond.md`](phase-4-events-and-beyond.md) (Phase 5 section)

### Do

- [ ] Document: Commands → Odoo write model / primary
- [ ] Document: Queries → reporting read models only
- [ ] Document: Sync via events + batch + reconcile
- [ ] Assign team ownership per read model
- [ ] Avoid dual write paths outside Odoo for accounting facts

### Exit

- [ ] Clear command/query boundaries and owners
- [ ] No accidental Exact reports on unverified projections

**Trigger:** Multiple report consumers, multiple read models, or team boundaries—not “we need performance.”

---

## Phase 6 — Warehouse / OLAP

**Goal:** Enterprise analytics when management BI becomes its own product.

**Design detail:** [`phase-4-events-and-beyond.md`](phase-4-events-and-beyond.md) (Phase 6 section)

### Do

- [ ] Confirm Phase 2–4 cannot meet cross-domain / history / tool needs
- [ ] ETL/ELT from Odoo (+ Reporting DB) → Data Warehouse
- [ ] Optional OLAP / semantic layer for heavy multidimensional analysis
- [ ] Keep Exact statutory path out of warehouse-only delivery

### Exit

- [ ] BI tools (Metabase/Power BI/etc.) served without hammering Odoo
- [ ] Cost/ops model accepted

**Opinion:** Skip until summaries + Reporting DB stop being enough. Warehouse is expensive to operate.

---

## Late / special (not early levers)

### Partitioning AML

- [ ] Study Odoo FK/ORM/upgrade impact
- [ ] Prove partition pruning benefit for remaining Exact range queries
- [ ] Plan migration/rollback before any production cutover

### Archiving

- [ ] Legal / audit / ZATCA retention reviewed
- [ ] Hot window defined
- [ ] Cold storage / reporting history—**not** naive `DELETE` on AML
- [ ] Exact reconstructibility verified

---

## Suggested sequence reminder

```text
0 Classify → 1 Isolate → 2 Pre-agg → 3 Reporting DB → 4 Events → 5 CQRS formalize → 6 Warehouse
```
