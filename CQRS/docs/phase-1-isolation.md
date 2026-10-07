# Phase 1 — Protect Odoo writes (isolation package)

Treat these as **one package**, not optional peers: replica + separate reporting host + pooling/concurrency caps + async generation.

**Exit:** POS/write latency stable under concurrent report load. Heavy queries may still take 30–60s on the replica.

## Architecture (Phase 1)

```text
                    ┌─────────────────────────────┐
  POS / Odoo UI ──► │ Odoo web tier (primary host) │──writes──► Primary PostgreSQL
                    └─────────────────────────────┘                 │
                                                                   │ streaming
                    ┌─────────────────────────────┐                 ▼
  User clicks     │ Reporting host                │          Read replica
  "Generate" ───► │  - API enqueue only           │────────► Exact + Analytical
                    │  - Worker pool (capped)      │          report queries
                    │  - PgBouncer / pooler        │
                    │  - Artifact store + notify   │
                    └─────────────────────────────┘
```

Web requests must **enqueue** and return; workers do SQL + PDF/Excel.

## 1. Read replica

### Intent

- All heavy report SQL goes to the replica.
- Primary reserved for Odoo writes / POS / interactive transactional reads.

### Requirements

| Item | Guidance |
|------|----------|
| Type | Physical streaming replica (same major PG version) |
| Routing | Reporting DB DSN ≠ primary DSN |
| Lag SLA | Exact: alert if lag > **N** seconds (default start: 5s) |
| Fail policy | If lag > N: delay Exact job, fail with clear message, or controlled primary fallback with tight concurrency |
| Monitoring | `pg_stat_replication` on primary; `pg_last_xact_replay_timestamp()` on replica |

### Do not

- Point Odoo’s main `db_host` at the replica (breaks writes).
- Run unrestricted ad-hoc SQL from accountants on primary.

## 2. Separate reporting host

### Intent

Report CPU, RAM, and DB connections must not sit on the Odoo web/POS tier.

### Minimum split

| Process | Where |
|---------|--------|
| Odoo HTTP / longpolling / POS | Primary app host(s) |
| Report workers + queue consumer | Reporting host(s) |
| Optional: report enqueue API | Reporting host or thin route on Odoo that only enqueues |

Scale workers horizontally later; start with **one reporting host** and hard concurrency caps.

## 3. Connection pooling & concurrency caps

### Why

50 users × one AML scan each can exhaust connections and IO even on a replica.

### Suggested controls

| Control | Starting point (tune from Phase 0 baselines) |
|---------|-----------------------------------------------|
| Pooler | PgBouncer (transaction or session mode as required by report lib) in front of replica |
| Max replica connections for reporting role | e.g. 20–40 (below replica `max_connections` headroom) |
| Max concurrent report workers | e.g. 4–8 heavy AML jobs |
| Per-user / per-company queue fairness | Optional: limit 1–2 active jobs per user |
| Statement timeout (replica) | e.g. 120–300s for report role; fail and retry with narrower filters |
| Primary report fallback concurrency | 1–2 max if ever used |

### Pooling rules of thumb

- Dedicated DB role: `odoo_reporting` (SELECT-only on needed schemas).
- Separate pool from Odoo ORM pool.
- Cap `max_client_conn` high, `default_pool_size` low relative to worker count.

## 4. Async report generation

### Flow

```text
1. User requests report (params + lane)
2. API validates ACL + enqueues job (idempotent key optional)
3. Returns job_id immediately
4. Worker:
   - acquires concurrency slot
   - checks replica lag if Exact
   - runs query on replica
   - writes PDF/Excel to object store / filestore
   - marks job done + notifies (bus / email / in-app)
5. User downloads artifact
```

### Job record (minimal fields)

```text
id, report_code, lane (exact|analytical),
requested_by, company_ids, params_json,
status (queued|running|done|failed|cancelled),
replica_lag_at_start, as_of_timestamp,
artifact_uri, error, created_at, started_at, finished_at
```

### Exact vs Analytical in Phase 1

| | Exact | Analytical |
|--|-------|------------|
| DB target | Replica (lag-gated) | Replica (lag can be higher until Phase 2) |
| Query | Still Odoo/AML-shaped | Still AML until Phase 2 summaries exist |
| Win | POS isolation + UX | Same; real speed comes in Phase 2 |

Async alone does **not** make queries cheaper—only safer for the write path.

## 5. Odoo integration patterns (choose one)

| Pattern | Pros | Cons |
|---------|------|------|
| Odoo `queue_job` / similar on reporting workers | Fits Odoo ACL/models | Careful: workers must use replica DSN for report SQL |
| External queue (Redis/RQ, Rabbit, SQS) + small service | Clear isolation | Extra service to operate |
| Hybrid: Odoo enqueues, external workers execute | Good separation | Need shared auth for “who can run this report” |

Prefer **workers that never open a primary connection** for report SQL.

## 6. Acceptance tests

- [ ] Under load: N concurrent report jobs do not move POS p95 beyond agreed budget
- [ ] Primary `pg_stat_activity` during report storm shows no pile of report SELECTs
- [ ] Exact job refuses or waits when replica lag > N
- [ ] User receives artifact without holding HTTP > ~1–2s for enqueue
- [ ] Worker kill/restart does not corrupt job state (at-least-once with safe overwrite)

## 7. Exit → Phase 2

When Phase 1 exit is met, start [`phase-2-preaggregation.md`](phase-2-preaggregation.md) for Analytical reports only. Keep Exact on replica + async.
