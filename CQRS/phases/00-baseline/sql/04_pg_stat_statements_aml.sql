-- Phase 0: top AML-related statements (requires pg_stat_statements)
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
