-- Phase 0 / 1: run on PRIMARY
SELECT
  client_addr,
  state,
  sent_lsn,
  write_lsn,
  flush_lsn,
  replay_lsn,
  pg_wal_lsn_diff(sent_lsn, replay_lsn) AS replay_bytes_behind
FROM pg_stat_replication;

-- On REPLICA, also run:
-- SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;
