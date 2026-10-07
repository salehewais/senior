-- Phase 0: account_move_line footprint
SELECT
  pg_size_pretty(pg_total_relation_size('account_move_line')) AS total,
  pg_size_pretty(pg_relation_size('account_move_line')) AS heap,
  pg_size_pretty(pg_indexes_size('account_move_line')) AS indexes;

SELECT reltuples::bigint AS estimated_rows
FROM pg_class
WHERE relname = 'account_move_line';
