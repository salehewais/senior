# Solutions catalog (22)

Every solution discussed for the Odoo 200M AML reporting problem, mapped to phase, role, and risk. Do **not** treat these as peers—implement in roadmap order.

## Capability legend

| Capability | Meaning |
|------------|---------|
| Isolation | Protects primary writes / POS from reporting load |
| Reduction | Shrinks rows scanned for analytical queries |
| UX | Improves wait time / UI without necessarily cheaper SQL |
| Architecture | Makes the analytical lane maintainable at scale |

---

## Catalog

### 1. Partitioning (`account.move.line`)

| | |
|--|--|
| **Phase** | Late / special (after Phase 2–3; study first) |
| **Role** | Data reduction for range queries; storage/pruning |
| **When** | Proven need for prune-by-date or partition elimination; ops ready for Odoo upgrades |
| **Why** | Large tables can benefit from partition pruning on date ranges |
| **Risk** | High for Odoo: FK constraints, ORM assumptions, module upgrades, migrations. Not the first lever after indexes. |
| **Lane** | Exact (careful) or storage hygiene—never a substitute for analytical pre-agg |

### 2. Read replica

| | |
|--|--|
| **Phase** | 1 |
| **Role** | Workload isolation |
| **When** | Reports compete with POS/writes on primary |
| **Why** | Moves read load off primary; exact reports can stay ledger-shaped |
| **Risk** | Replica lag; exact reports must define max lag + alert |
| **Lane** | Both (exact prefers low-lag; analytical can tolerate more) |

### 3. Separate reporting server

| | |
|--|--|
| **Phase** | 1 |
| **Role** | App / CPU / RAM / connection isolation |
| **When** | Report workers share Odoo web tier and starve POS |
| **Why** | Report generation should not sit on the transactional app host |
| **Risk** | Operational overhead (deploy, auth, DB credentials) |
| **Lane** | Both |

### 4. Reporting DB

| | |
|--|--|
| **Phase** | 3 |
| **Role** | Dedicated analytical store |
| **When** | Matviews on replica are not enough; many consumers; want schema freedom |
| **Why** | Facts/dims optimized for queries without AML shape |
| **Risk** | Sync lag, dual sources of truth if exact reports wrongly point here |
| **Lane** | Analytical only (unless parity proven) |

### 5. Read model

| | |
|--|--|
| **Phase** | 3–5 |
| **Role** | Query-optimized projections |
| **When** | Reports need denormalized, stable shapes independent of Odoo tables |
| **Why** | CQRS-as-data-separation without rewriting Odoo writes |
| **Risk** | Drift from ledger; needs reconcile + “as of” UX |
| **Lane** | Analytical |

### 6. Pre-aggregation

| | |
|--|--|
| **Phase** | 2 |
| **Role** | Primary data reduction (highest ROI for 200M) |
| **When** | Management reports scan AML repeatedly |
| **Why** | Daily `date × company × branch × account` (or product) turns hundreds of millions into thousands–millions |
| **Risk** | Wrong grain; missing dimensions force fall-back to AML |
| **Lane** | Analytical |

### 7. Materialized view

| | |
|--|--|
| **Phase** | 2 |
| **Role** | Fast path to pre-aggregation |
| **When** | Early summaries on replica/primary before a full reporting DB |
| **Why** | Low ceremony; SQL-owned refresh |
| **Risk** | Full refresh cost; concurrent refresh locks; still on same DB family |
| **Lane** | Analytical |

### 8. Cache (Redis / app)

| | |
|--|--|
| **Phase** | 2 |
| **Role** | Same-query fan-out relief |
| **When** | Many users hit identical params (same branch/month) |
| **Why** | Avoids repeating the same expensive query |
| **Risk** | Stale results; does not help unique heavy queries; not a substitute for pre-agg |
| **Lane** | Analytical (exact only with strict TTL / invalidate rules) |

### 9. Async processing

| | |
|--|--|
| **Phase** | 1 |
| **Role** | UX / HTTP isolation |
| **When** | Users wait on long-running report HTTP requests |
| **Why** | Queue → worker → store PDF/Excel → notify; exact can still be correct |
| **Risk** | Misread as “faster query”—query cost unchanged without aggregation |
| **Lane** | Both |

### 10. Background workers

| | |
|--|--|
| **Phase** | 1–4 |
| **Role** | Run reports, aggregations, sync, event consumers |
| **When** | Any async or incremental pipeline |
| **Why** | Decouples user request from long work |
| **Risk** | Unbounded queues; need concurrency caps and poison handling |
| **Lane** | Both |

### 11. CQRS

| | |
|--|--|
| **Phase** | 3–5 |
| **Role** | Separation pattern (commands vs queries) |
| **When** | Multiple read models/consumers or clear team boundaries |
| **Why** | Formalizes write model (Odoo) vs read models (reporting) |
| **Risk** | Starting here before isolation + pre-agg wastes effort |
| **Lane** | Analytical shape; exact stays on ledger schema |

### 12. Event-driven

| | |
|--|--|
| **Phase** | 4 |
| **Role** | Incremental read-model updates |
| **When** | Batch refresh lag hurts analytical SLAs |
| **Why** | Avoid re-scanning 200M on every refresh |
| **Risk** | Missed events; ordering; needs nightly reconcile |
| **Lane** | Analytical |

### 13. CQRS + events

| | |
|--|--|
| **Phase** | 4–5 |
| **Role** | Full advanced analytical combo |
| **When** | Read models exist and freshness SLAs require incremental updates |
| **Why** | Commands → Odoo; events → update projections; queries → reporting |
| **Risk** | Complexity tax; ops and reconcile discipline required |
| **Lane** | Analytical |

### 14. Eventual consistency

| | |
|--|--|
| **Phase** | 4+ (contract from Phase 0) |
| **Role** | Explicit business contract for analytical lane |
| **When** | Dashboards/KPIs can tolerate minutes–hours lag |
| **Why** | Unlocks pre-agg, reporting DB, events without pretending ledger parity |
| **Risk** | Users confuse analytical with statutory; UI must show “as of” |
| **Lane** | Analytical only |

### 15. Archiving

| | |
|--|--|
| **Phase** | After 2–3 |
| **Role** | Hot/cold separation; storage and scan reduction |
| **When** | Legal retention allows cold history; hot window is well defined |
| **Why** | Shrinks hot working set |
| **Risk** | **Never naive DELETE on AML.** Legal, audit, ZATCA first. Prefer cold storage / reporting history with retention policy. |
| **Lane** | Both (policy-driven); exact must remain reconstructible |

### 16. Data warehouse

| | |
|--|--|
| **Phase** | 6 |
| **Role** | Cross-domain historical BI |
| **When** | BI product needs (many domains, long history, forecasting, external tools) beyond Odoo reports |
| **Why** | Purpose-built analytics platform |
| **Risk** | Expensive to operate; often unnecessary if Phase 2–4 suffice |
| **Lane** | Analytical / enterprise BI |

### 17. OLAP

| | |
|--|--|
| **Phase** | 6 |
| **Role** | Heavy multidimensional analysis |
| **When** | Cube/semantic layer needed after warehouse (or equivalent) |
| **Why** | Fast slice/dice across many dimensions |
| **Risk** | Overkill for a few Odoo management reports |
| **Lane** | Analytical / enterprise BI |

### 18. DB / resource isolation

| | |
|--|--|
| **Phase** | 1 |
| **Role** | Infra separation (CPU, IOPS, memory, instances) |
| **When** | Shared DB host saturates under mixed load |
| **Why** | Complements replica/reporting DB with hard resource boundaries |
| **Risk** | Cost; mis-sized instances |
| **Lane** | Both |

### 19. Connection / workload control

| | |
|--|--|
| **Phase** | 1 |
| **Role** | Concurrency safety net |
| **When** | 50 users can fire 50 full AML scans at once |
| **Why** | Pooling + worker/query caps protect primary and replica |
| **Risk** | Queue backlog; need fair scheduling and user feedback |
| **Lane** | Both |

### 20. Async + pre-aggregation

| | |
|--|--|
| **Phase** | 2–4 |
| **Role** | Best operational combo for summaries |
| **When** | Analytical reports must be both cheap and non-blocking |
| **Why** | Aggregation reduces work; async protects UX and concurrency |
| **Risk** | Stale summaries if refresh jobs fail unnoticed |
| **Lane** | Analytical |

### 21. Replica + reporting model

| | |
|--|--|
| **Phase** | 3 |
| **Role** | Hybrid: protect primary + cheap reports |
| **When** | Exact stays on replica; analytical moves to reporting model |
| **Why** | Matches the two-lane strategy at steady state |
| **Risk** | Routing mistakes (exact hitting reporting DB) |
| **Lane** | Exact → replica; Analytical → reporting model |

### 22. Reporting DB + CQRS + events + async

| | |
|--|--|
| **Phase** | 4–5 |
| **Role** | Target steady-state for analytical lane |
| **When** | After Phase 1–3 foundations exist |
| **Why** | Isolation + reduction + incremental refresh + clear query path |
| **Risk** | Jumping here first skips cheaper wins and increases failure surface |
| **Lane** | Analytical |

---

## Quick phase map

| Phase | Solutions |
|-------|-----------|
| 1 | 2, 3, 9, 10, 18, 19 |
| 2 | 6, 7, 8, 20 |
| 3 | 4, 5, 21 |
| 4–5 | 11, 12, 13, 14, 22 |
| 6 | 16, 17 |
| Late / special | 1, 15 |

## Planning rule

1. Classify reports (Exact vs Analytical).
2. Isolate (Phase 1).
3. Reduce analytical reads (Phase 2).
4. Then invest in reporting DB / events / CQRS / warehouse as needed.
