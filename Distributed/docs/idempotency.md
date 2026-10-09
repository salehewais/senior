# Idempotency

**Status: Phase 5 stores consumer dedup for the order-service inventory worker in `order_db.processed_events`, in the same transaction as `inventory_snapshots`. Phase 7 does the same for reporting projections in `reporting_db.processed_events`. HTTP idempotency keys are not implemented. Phase 9 adds an expiring Redis lock around order create. That lock is not a store of record.**

At-least-once delivery means every consumer and every unsafe HTTP endpoint will see duplicates. The duplicates are not a broker bug. They are what happens when a process is killed after it has done the work and before it has recorded that it is done.

There are two different stores. Do not merge them into Redis.

| Kind | Store | Key | Protects |
| --- | --- | --- | --- |
| Consumer dedup | `processed_events` in the consumer's own database | `event_id` | Redelivered messages |
| HTTP dedup | `http_idempotency_keys` in `order_db` | Client `Idempotency-Key` plus the route and account | Retried POST requests |

Redis is the wrong home for both. Eviction or a restart would forget that an order already exists and the next retry would create another one.

Phase 9 does not change that. `POST /api/v1/orders` takes a Redis lock keyed by the account and the line items, with a 15-second TTL, and releases it when the request finishes. A second in-flight create with the same body gets 409 `IDEMPOTENCY_IN_PROGRESS` and writes nothing. Two requests in sequence still insert two orders. If the process dies, the key expires and a retry can insert another order. That is not exactly-once. `http_idempotency_keys` is still not in `order_db`, so a lost response is not replayed.

## Processed-event store

Each consuming database has a table:

| Column | Meaning |
| --- | --- |
| `event_id` | Primary key. The envelope id. |
| `event_type` | For operators. |
| `aggregate_id` | For operators and rebuilds. |
| `processed_at` | When this database applied it. |

Where it lives:

| Consumer | Database |
| --- | --- |
| Reporting projections | `reporting_db` |
| Inventory snapshot worker | `order_db` |
| Odoo connector | `odoo_db` (custom model) |

### How a consumer handles one message

1. Begin a local transaction.
2. Insert the `event_id` into `processed_events`.
3. If the insert conflicts, this event was already applied. Commit nothing else, ack the message, and increment a duplicate counter. Stop.
4. If the insert succeeds, apply the projection or the ERP write in the **same** transaction.
5. Commit.
6. Ack the RabbitMQ delivery.

The insert and the business write commit together. A crash before commit leaves no row and no partial apply; the redelivery tries again. A crash after commit and before ack redelivers; the insert conflicts; the consumer acks. A crash that applied the write and then failed the insert cannot happen if they are one transaction.

What happens without the table: the second delivery creates a second Odoo sales order, or adds the revenue twice. What happens if you ack first and write second: a crash drops the message forever. Ack after commit, always.

What happens if you dedupe in memory: the next deploy forgets, and the backlog is delivered again.

Detection: `consumer_duplicates_total`, handler errors, DLQ depth. A sudden climb in duplicates usually means the publisher crashed mid-batch or a consumer is restarting, which is noisy and not by itself a data bug. A climb in DLQ depth is a data bug or a poison payload.

Recovery: duplicates need no repair when the transaction rule is kept. If a consumer was buggy and committed a bad projection **and** the processed row, a replay will skip the event. Repair is then a deliberate delete of that `event_id` from `processed_events` (and a fix of the bad row) followed by a republish. That is an operator action, not the default path.

Version conflicts are not duplicates. An older `InventoryUpdated` is acked and ignored without treating it as an error. A future order version is not inserted into `processed_events` before it is applied; the handler fails so the retry can run. If you mark it processed and then fail the apply, you have swallowed the fact.

## HTTP idempotency

Phase 9 does not enforce `Idempotency-Key`. The paragraphs below are the durable design. The table is not migrated yet.

`POST /api/v1/orders`, `POST /api/v1/orders/{id}/confirm`, and `POST /api/v1/orders/{id}/cancel` require an `Idempotency-Key` header (UUID, client-generated). The server stores the key, the account id, the request hash, and the response status and body.

Rules:

- Same key, same account, same request hash, still in progress: return 409 with code `IDEMPOTENCY_IN_PROGRESS` so the client waits and retries.
- Same key, same account, same request hash, completed: return the stored response. Do not run the use case again.
- Same key, different request hash: return 409 with code `IDEMPOTENCY_KEY_REUSE`.
- Keys are kept long enough for client retries (design value: 24 hours), then deleted by a janitor. After expiry a retry can double-submit. Twenty-four hours covers a human with a bad connection. It does not cover a client that reuses keys next month.

The row is written in the same transaction as the order change. A retry after a lost response sees the stored response and does not create a second order.

Client-supplied keys are untrusted as identity. They are scoped to the authenticated account. One customer cannot replay another customer's key.

GET requests are not stored. They are safe.

What happens without HTTP idempotency: the storefront times out, retries, and the customer has two pending orders. The state machine does not save you, because both creates are legal.

Detection: duplicate-create attempts in logs (same key returning the stored body), and orders-per-customer spikes. Recovery: cancel the extra pending order if one slipped through before this was implemented. After implementation, recovery is "return the stored response."

## How this relates to the outbox

The publisher may send the same `event_id` more than once. That is success, not a bug, as long as consumers dedupe. Do not add a second dedup cache in the publisher that can disagree with `published_at`. The outbox status is the publisher's memory. The processed-event table is the consumer's memory.

## Learning versus production

> **Learning simplification.** One dedup table per database, primary key on `event_id`, no TTL on processed events (the table grows with history). HTTP keys expire in 24 hours.
> **Production would require.** A growth plan for `processed_events` (partition by month, or retain only after consumers no longer replay that far), the same transactional rule, and load tests that kill the worker between commit and ack.

## Related documents

- [outbox.md](outbox.md)
- [rabbitmq.md](rabbitmq.md)
- [api.md](api.md)
