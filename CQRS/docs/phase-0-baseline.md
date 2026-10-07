# Phase 0 — Baseline & measurement

Concrete queries and worksheets to finish classification before changing infra. Pair with [`report-classification.md`](report-classification.md).

## 1. Report inventory worksheet

Fill for the top 15–25 reports (or export to a spreadsheet). Score impact = `frequency × p95_runtime_sec × concurrent_users_peak`.

| Report | Lane | Freq/day | p50s | p95s | Conc. peak | AML? | During POS peak? | Freshness need | Priority |
|--------|------|----------|------|------|------------|------|------------------|----------------|----------|
| e.g. Trial balance | Exact | 40 | 12 | 45 | 8 | Y | Y | ≤5s lag | 1 |
| e.g. Branch sales KPI | Analytical | 200 | 8 | 30 | 20 | Y | Y | ≤15 min | 1 |

Lane rule of thumb: statutory / tax / ZATCA / close → **Exact**. KPI / dashboard / trend → **Analytical**.

## 2. SLA defaults (edit after measurement)

```text
Exact:
  - Serve from replica when lag <= 5 seconds (adjust N)
  - Alert if lag > 5s for > 60s
  - Fall back policy: queue Exact on primary only for period close, with concurrency=1–2

Analytical:
  - Freshness SLA: <= 15 minutes
  - UI must show as_of timestamp
  - Drift tolerance after reconcile: document per metric (e.g. abs(diff) < 0.01 currency unit or 0.1%)
```

## 3. Database contention snapshots

Run during a **POS peak** and again during a **report peak**. Save outputs with timestamps.

### Active sessions by state / application

```sql
-- Who is on the DB right now?
SELECT
  state,
  wait_event_type,
  wait_event,
  application_name,
  usename,
  count(*) AS sessions,
  count(*) FILTER (WHERE state = 'active') AS active
FROM pg_stat_activity
WHERE datname = current_database()
  AND pid <> pg_backend_pid()
GROUP BY 1, 2, 3, 4, 5
ORDER BY active DESC, sessions DESC;
```

### Blocking / lock waits

```sql
SELECT
  blocked.pid AS blocked_pid,
  blocked.usename AS blocked_user,
  left(blocked.query, 120) AS blocked_query,
  blocking.pid AS blocking_pid,
  left(blocking.query, 120) AS blocking_query
FROM pg_stat_activity blocked
JOIN pg_locks bl ON bl.pid = blocked.pid AND NOT bl.granted
JOIN pg_locks kl ON kl.locktype = bl.locktype
  AND kl.database IS NOT DISTINCT FROM bl.database
  AND kl.relation IS NOT DISTINCT FROM bl.relation
  AND kl.page IS NOT DISTINCT FROM bl.page
  AND kl.tuple IS NOT DISTINCT FROM bl.tuple
  AND kl.virtualxid IS NOT DISTINCT FROM bl.virtualxid
  AND kl.transactionid IS NOT DISTINCT FROM bl.transactionid
  AND kl.classid IS NOT DISTINCT FROM bl.classid
  AND kl.objid IS NOT DISTINCT FROM bl.objid
  AND kl.objsubid IS NOT DISTINCT FROM bl.objsubid
  AND kl.granted
JOIN pg_stat_activity blocking ON blocking.pid = kl.pid
WHERE blocked.pid <> blocking.pid;
```

### Long-running queries

```sql
SELECT
  pid,
  usename,
  application_name,
  now() - query_start AS runtime,
  wait_event_type,
  wait_event,
  left(query, 200) AS query
FROM pg_stat_activity
WHERE datname = current_database()
  AND state = 'active'
  AND pid <> pg_backend_pid()
  AND query_start < now() - interval '5 seconds'
ORDER BY query_start;
```

### `account.move.line` access patterns (if `pg_stat_statements` enabled)

```sql
SELECT
  calls,
  round(total_exec_time::numeric, 1) AS total_ms,
  round(mean_exec_time::numeric, 1) AS mean_ms,
  rows,
  left(query, 200) AS query
FROM pg_stat_statements
WHERE query ILIKE '%account_move_line%'
ORDER BY total_exec_time DESC
LIMIT 30;
```

### Table size / bloat awareness

```sql
SELECT
  pg_size_pretty(pg_total_relation_size('account_move_line')) AS total,
  pg_size_pretty(pg_relation_size('account_move_line')) AS heap,
  pg_size_pretty(pg_indexes_size('account_move_line')) AS indexes;
```

### Replica lag (once replica exists)

```sql
-- On primary: see replica apply lag
SELECT
  client_addr,
  state,
  sent_lsn,
  write_lsn,
  flush_lsn,
  replay_lsn,
  pg_wal_lsn_diff(sent_lsn, replay_lsn) AS replay_bytes_behind
FROM pg_stat_replication;

-- On replica:
SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;
```

## 4. Application / POS baselines

Capture for one peak week:

| Metric | How | Baseline |
|--------|-----|----------|
| POS checkout p95 latency | APM / Odoo logs / proxy | |
| Report request p95 (sync) | App timings | |
| Concurrent report DB connections | `pg_stat_activity` | |
| Primary CPU / IO during dual peak | Host metrics | |

## 5. Phase 0 exit pack

Produce a short note (even one page) containing:

1. Top 10 reports by impact score, with lane
2. Chosen Exact lag N and Analytical freshness SLA
3. Evidence that reports and POS contend (or do not) on primary
4. Go / no-go for Phase 1 package (replica + async + caps)

## 6. What not to optimize yet

- Partitioning AML
- Warehouse design
- Event bus
- Rewriting Exact reports onto summaries
