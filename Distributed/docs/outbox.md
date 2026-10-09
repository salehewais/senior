# Transactional outbox

**Status: Phase 6 implements this in `order_db`. The API inserts the outbox row in the business transaction. `python -m order_service.infrastructure.messaging.outbox_publisher` publishes it. A `failed` outbox row is not a consumer dead-letter.**

## The inconsistency problem

The order service must do two things that are not one system: commit an order in Postgres, and tell RabbitMQ. They do not share a transaction.

Two naive orders both lose or duplicate work:

1. **Commit, then publish.** The process dies after the commit. The order is `CONFIRMED`. No message exists. Odoo never invoices it. Reporting never shows it. Retrying the HTTP request hits the state machine and refuses a second confirm. The event is gone.
2. **Publish, then commit.** The broker accepts `OrderConfirmed`, then the database rolls back. Odoo creates a sales order for an order that does not exist. There is no local row to repair from.

A distributed transaction across Postgres and RabbitMQ would make the user wait on both, and it would couple their availability. We do not do that. [ADR-005](adr/ADR-005-why-outbox.md) records the choice. [ADR-006](adr/ADR-006-why-eventual-consistency.md) records the consequence: other services see the fact slightly later.

## The pattern

In the **same database transaction** as the business write, insert a row in `outbox`. Commit. A separate publisher reads rows that are still pending and publishes them. Consumers may see the order only after that delay. The HTTP response does not wait for the broker.

The row is the source of the message. The publisher sends the stored envelope. It does not read the order again and build a new payload. If it did, a later update would rewrite history, and a `PENDING` create followed quickly by confirm could publish two different stories depending on timing.

Columns, also listed in [database.md](database.md):

| Column | Meaning |
| --- | --- |
| `id` | Primary key. Equals `event_id` in the envelope. |
| `event_type` | Catalog name, duplicated so operators can query without parsing JSON. |
| `aggregate_type` | `order`, `product`, `customer`. Inventory outbox rows, when Odoo grows one, use `inventory`. |
| `aggregate_id` | Aggregate UUID. |
| `payload` | Full envelope JSON. |
| `created_at` | Insert time inside the business transaction. |
| `published_at` | Null until the broker confirm is in hand. |
| `retry_count` | Failed publish attempts. |
| `status` | `pending`, `published`, or `failed`. |

`event_type` and the envelope can theoretically drift if a bug writes them separately. The publisher treats `payload` as authoritative and logs a mismatch if `payload.event_type` differs from the column.

Odoo has the same problem when it emits `InventoryUpdated`. Phase 14 should put an outbox table in `odoo_db` rather than calling the broker inside the stock transaction. Same columns, same publisher rules.

## Publisher

One process, separate from the API workers, so a slow broker does not occupy request threads.

Loop, conceptually:

1. Begin a database transaction.
2. Select a batch of pending rows (on the order of 100) ordered by `created_at`, then `id`, using `FOR UPDATE SKIP LOCKED`.
3. For each row, publish `payload` to the correct exchange with confirms and `mandatory`.
4. On confirm, set `status = published`, set `published_at`, leave `retry_count` as it is.
5. On failure, increment `retry_count`. If it has reached the max (5, same budget as consumer retries), set `status = failed`. Otherwise leave it `pending`.
6. Commit the database transaction.

The broker publish happens while the row lock is held. If the process dies after the broker accepts and before the commit, the row stays `pending` and will be sent again. That is at least once, and it is correct. Holding the lock across the confirm round-trip is acceptable at learning volume because it keeps the crash story to one paragraph.

What happens without the publisher: outbox rows pile up and no other service ever learns anything. Checkout looks fine. This is why outbox age is an alert, not a log line someone might read.

What happens when publish fails: the user already has their HTTP success. The row remains `pending`. The publisher retries. If the message is unroutable, `mandatory` surfaces it, `retry_count` climbs, and the row becomes `failed` instead of hot-looping forever.

A `failed` outbox row means this publisher never got a broker confirm. The message may not be on any queue. That is an operator problem. A consumer dead-letter message is different: the broker accepted the publish, a consumer received it, and the consumer could not apply it (or exhausted its retry ladder). The outbox row for that fact can already be `published`. Do not treat `outbox.status = failed` as the inventory DLQ, and do not treat a DLQ message as a missing outbox row.

Detection:

| Metric (later) | Why it matters |
| --- | --- |
| `outbox_unpublished_count` | How many committed facts are stuck |
| `outbox_oldest_pending_age_seconds` | How late the rest of the system is. Alert when this stays high. |
| `outbox_publish_failures_total` | Broker rejects, timeouts, unroutable messages |
| `outbox_publish_latency_seconds` | Confirm round-trip. Growing latency predicts a stuck publisher. |
| `outbox_failed_count` | Rows that will not move without a human |

Recovery: if the broker was down, restore it and leave the rows `pending`; the publisher drains them. If a row is `failed` because of a bad payload, fix the publisher or the payload with a deliberate rewrite, set the row back to `pending`, and record why. Do not delete a `failed` row to silence the metric. If `order_db` is restored from a backup that is older than messages consumers already applied, you can republish events consumers must treat as duplicates. Idempotency makes that safe. Restoring a backup that is missing events consumers never saw is a gap; see [disaster-recovery.md](disaster-recovery.md).

## Concurrent publishing

**Learning default:** run one publisher. Combined with `ORDER BY created_at, id`, one worker preserves outbox order, which makes early report projections easier to debug. Phase 14 keeps the kind Deployment `order-outbox-publisher` at 1 replica for that reason. `SKIP LOCKED` is already in `SqlOutboxLease`. It is not enough, by itself, to make a second replica preserve order.

**Design the table for more than one anyway.** `SKIP LOCKED` means a second publisher takes a different batch instead of blocking or double-reading the same row. Without `SKIP LOCKED`, two publishers can grab the same pending rows, send duplicates (consumers must still tolerate those), and deadlock on row locks.

`SKIP LOCKED` does not preserve a global order across publishers. Two workers can publish aggregate A's version 2 before version 1 if they pick rows out of order. That is why consumers use `aggregate_version` ([events.md](events.md)), and why a scaled publisher should partition by `aggregate_id` so one worker owns a given aggregate.

> **Learning simplification.** One publisher, lock held across the broker confirm, batch size around 100, poll interval around one second. No claim step with a visibility timeout.
> **Production would require.** The partition-by-aggregate scheme before you run many publishers, a visibility timeout if you refuse to hold database connections during broker confirms, and the metrics above on a dashboard with an alert on oldest age.

A claim-then-publish design (set `publishing`, commit, send, then mark `published`) shortens locks and adds a new failure: a crash leaves rows stuck in `publishing`. You then need a timeout to reclaim them. That is more moving parts. We leave it as the documented scale-up, not the first implementation.

## What the API must not do

The request handler does not publish to RabbitMQ. It writes the outbox row and commits. If the handler also publishes, you have two paths and they will disagree under partial failure.

The request handler does not wait for `published_at`. Waiting would put the broker on the checkout critical path, which is the coupling this pattern removes.

## Related documents

- [database.md](database.md)
- [rabbitmq.md](rabbitmq.md)
- [idempotency.md](idempotency.md)
- [ADR-005](adr/ADR-005-why-outbox.md)
