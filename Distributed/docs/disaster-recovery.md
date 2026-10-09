# Disaster recovery

**Status: Phase 19 backup and restore for the three Compose databases. The RPO and RTO below are learning targets. RTO was not measured.**

This page says what must be restorable and in what order. It does not claim an RPO or RTO that anyone has measured. The numbers below are **exercise targets for the learning project**, so Phase 19 has something to aim at. They are not a customer promise.

| Store | Exercise target | Why this number |
| --- | --- | --- |
| `order_db` | Recover to within 24 hours of data (RPO), service back the same day (RTO 8 hours) | A laptop backup rhythm, not a payments license |
| `odoo_db` and Odoo filestore | Same exercise targets | ERP documents are not rebuildable from our events alone if Odoo has local edits |
| `reporting_db` | Rebuild from events when the broker or outbox still has them; otherwise same backup target | The read model is a projection, but only if the facts still exist |
| RabbitMQ | Topology reapplied from code in minutes; in-flight messages may be lost on a single node | The outbox is the real copy of unpublished work |
| Redis | No restore | It is a cache |
| Prometheus | No restore required for business correctness | A metrics gap is acceptable in this project |

> **Learning simplification.** A documented `pg_dump` per database, taken by hand in Phase 19 (`deploy/backup/dump.sh`), stored outside the database container. Restore is `deploy/backup/restore.sh` with `--yes`, and it replaces only that database.
> **Production would require.** Scheduled backups, an off-site copy, encryption, restore tests on a calendar, and targets agreed with the people who lose money when checkout is down. Point-in-time recovery for `order_db` is the usual production bar. We have not built it.

## What is authoritative

- An order's status is whatever `order_db` committed, with the outbox as the record of facts that must leave the service.
- A report is allowed to be behind. Rebuilding it is success, not data loss, if events still exist.
- Odoo stock is authoritative for the warehouse. `InventorySnapshot` is rebuilt from `InventoryUpdated` or from a new snapshot after Odoo returns.
- Redis is never restored from a dump onto a new primary and treated as truth.

## Backup contents

| Artifact | Includes |
| --- | --- |
| `order_db` dump | Accounts, orders, outbox, processed events, refresh-token hashes |
| `reporting_db` dump | Projections and processed events |
| `odoo_db` dump plus filestore | ERP data and attachments |
| Topology definition | The `commerce-platform-topology` exchanges and queues, from git, not from a live UI export as the only copy |
| Key material | JWT keys stored with the secrets, not in git. A restore without the public key pair invalidates every session, which is acceptable if you rotate on purpose and painful if you lose the key by accident. |

Do not back up Redis. Do not put dumps in the git repository.

## Restore order

1. Decide the time you are restoring to. Write it down. A quiet restore of three databases taken at different hours will look like a corruption bug.
2. Restore `order_db` first. Checkout is the system of record for orders.
3. Restore `odoo_db` and the filestore together. One without the other is a broken ERP.
4. Reapply RabbitMQ topology before starting publishers.
5. Start the order service and the publisher. Pending outbox rows drain. Already-published rows must not be sent again unless you have decided to replay; consumers will dedupe if you do replay.
6. Restore or rebuild `reporting_db`. If you restored `order_db` to an earlier time than consumers had applied, stop consumers, rebuild projections, or accept duplicates only where dedup still has the old `event_id`s. If the restored outbox is missing events consumers already applied, do not delete those consumer rows to "match." You would re-apply nothing and also forget that the fact happened. This case needs a human.
7. Start reporting and Odoo consumers.
8. Discard Redis contents.
9. Run one create-and-confirm journey and one report read before calling the exercise done.

What happens without a written order: the team restores reporting first, serves confident wrong totals, and then overwrites `order_db` underneath a publisher that is already sending stale envelopes.

## Detection

Backups that have never been restored are rumors. Phase 19's restore is the detection. A failed restore is the finding. Metrics will not tell you that a dump is truncated; only a restore will.

## What we will not recover

- A message that was never in the outbox and never in a queue, because the bug dropped it. Fix the bug. The backup cannot contain a fact that was not committed.
- Card data. We should not have it.
- Grafana's ad-hoc panels that were never exported. Another reason to keep dashboard definitions in git once they exist.

## Related documents

- [database.md](database.md)
- [deployment.md](deployment.md)
- [failure-scenarios.md](failure-scenarios.md)
