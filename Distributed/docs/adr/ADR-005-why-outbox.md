# ADR-005: Why the transactional outbox

**Status: Accepted. Implemented in Phase 6** in `order_db`. The Odoo inventory outbox is Phase 8. This is a learning project.

## Context

The order service commits facts in Postgres and must publish them to RabbitMQ. Those systems do not share a transaction. [../outbox.md](../outbox.md) describes the two failure orders: commit-then-publish loses the message; publish-then-commit can emit a fact that rolled back.

Checkout latency must not include Odoo. A two-phase commit across the database and the broker would put both on the critical path and is a poor fit for RabbitMQ.

## Decision

In the same database transaction as the business write, insert an `outbox` row whose `payload` is the full event envelope. A publisher process sends pending rows after commit, with publisher confirms, then marks them `published`. The HTTP handler does not publish and does not wait for the broker.

Odoo's inventory events should use the same pattern inside `odoo_db` when they are implemented. One pattern, two databases, no shared table.

## Alternatives

| Alternative | Why it lost |
| --- | --- |
| Publish inside the request after commit | Lost messages on crash. The state machine then blocks a naive retry. |
| Publish before commit | Ghost events for rolled-back orders. |
| Two-phase commit | Availability of checkout becomes availability of the broker, plus operational complexity we would be using to imitate a row insert. |
| Polling "orders updated since" from other services | Requires cross-database reads, and misses intermediate states if the poller only sees the latest row. |
| A log-based CDC tool (Debezium or similar) | A valid production outbox implementation: read the Postgres log, publish, don't write a custom poller. It adds a connector service to run and understand. A table the application writes is visible in SQL and easier to teach. CDC remains a legitimate replacement for the poller later if the custom publisher becomes the bottleneck. The transactional insert of the fact still wants to be in the business commit; CDC often reads that same outbox table. |

## Consequences

- There is a delay between "the user saw success" and "Django updated." The API must return the strong read from `order_db`, and reports must show `as_of`.
- At least once is mandatory. Idempotent consumers are part of this decision, not a follow-up nice-to-have. See [../idempotency.md](../idempotency.md).
- A silent publisher failure looks like a healthy API. Oldest-pending-age has to be an alert or the pattern fails in practice.
- The stored payload can be wrong if the use case builds a bad envelope. The publisher will faithfully send the bug. Contract tests on the envelope matter.
- One publisher is the first deployment. `SKIP LOCKED` is still the locking rule so a second process cannot corrupt the scheme by accident.
- Outbox rows are retained after publish so a consumer can be rebuilt. Disk growth is the cost. A retention job is a later decision and must not delete rows that were never published.

## What happens without this decision

The first crash after confirm loses an ERP order, or the first rollback creates one. Both show up as "the services disagree" with no row to replay.
