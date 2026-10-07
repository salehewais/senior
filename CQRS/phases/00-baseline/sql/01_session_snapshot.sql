-- Phase 0: who is on the DB right now?
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
