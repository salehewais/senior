-- Phase 0: active queries older than 5 seconds
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
