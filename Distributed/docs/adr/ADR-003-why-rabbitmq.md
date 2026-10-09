# ADR-003: Why RabbitMQ

**Status: Accepted. Implemented in Phase 4**, with the retry ladder in Phase 5 and the outbox publisher in Phase 6. This is a learning project.

## Context

When an order is confirmed, reporting and Odoo need to hear about it without joining the checkout transaction. Odoo may be down. The message must wait. When it is delivered twice, consumers must tolerate that. We also need routing (Odoo sees only `order.confirmed`), retries, and a dead-letter queue a human can see.

The producers are a single order service and an Odoo module. The consumers are few. The volume is a learning project, not a market data feed.

## Decision

Use RabbitMQ with the topology in [../rabbitmq.md](../rabbitmq.md), named `commerce-platform-topology`. Publish to topic exchanges. Consume from durable queues. At least once, with publisher confirms and manual acks. Retry with TTL backoff, then DLQ. Idempotent consumers are required, not optional.

## Alternatives

| Alternative | Why it lost |
| --- | --- |
| Kafka | Excellent when you need a long, replayable log and many independent consumer groups at high throughput. It costs more to operate (partitions, retention, consumer groups) than this project has services. We would be learning the log before we had a single projection. RabbitMQ's queues, routing keys, and DLQs match the teaching goals directly. |
| Redis streams or lists | Redis is already in the design as a cache. Using it as the bus makes the "not source of truth" rule muddy, and a flush would drop the integration path. |
| Direct HTTP callbacks only | Simple until Odoo is down during confirm. Then checkout fails or the caller builds a private retry queue. That private queue is a worse broker. |
| Database polling of each other's tables | Cross-service reads, which [ADR-004](ADR-004-why-database-per-service.md) forbids. |

Kafka's replay story is the real feature we give up. Our substitute is the outbox row plus the projection rebuild described in [../disaster-recovery.md](../disaster-recovery.md). That substitute is weaker if the outbox is truncated. We accept that at this scope and keep the payloads in `outbox` rather than deleting them immediately on publish. A later retention policy can archive them. It should not delete them on the same second as the ack.

## Consequences

- Global ordering does not exist. Per-aggregate versions exist. Implementers who assume "the queue is ordered" will pass tests with one consumer and fail with two.
- The broker can lose acknowledged messages if we run one classic node and the disk dies. The outbox covers republish for anything not yet marked `published`. Anything marked `published` and not yet applied is at risk on a violent broker disk loss. Quorum queues are the production upgrade and are intentionally later.
- Topology is code. A queue created by hand in the management UI will be missing the day someone recreates the container.
- Odoo needs a small module that speaks AMQP or an internal client. That is custom code inside the ERP boundary, not a new microservice.
- Operators must watch DLQ depth. A retry loop without a max is worse than an alert.

## What happens without this decision

Confirm either calls Odoo and Django in the request, and their outages become checkout outages, or it writes a row and hopes a cron job in each database can see it. The first couples availability. The second couples schemas.
