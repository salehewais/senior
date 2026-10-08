# Event catalog

**Status: Phase 6 stores this envelope in `order_db.outbox` in the same transaction as the aggregate write. A separate publisher sends that stored body. Phase 5's inventory worker consumes `InventoryUpdated` from `q.order.inventory`. Phase 7's reporting worker consumes the catalog on `q.reporting.projection` into `reporting_db`. If an AMQP property disagrees with the body, the body wins. The Odoo client is a later phase.**

Events are facts that have already been committed in the producer's database. They are not requests. A consumer that disagrees with a fact does not rewrite the producer's tables. It records the consequence in its own database, or it raises a command through an API that the producer validates.

Saga commands are not in this catalog. They are specified in [rabbitmq.md](rabbitmq.md) so Phase 15 has a shape, and they must not be projected into reports as if they were order status.

## Envelope

Every event uses the same JSON object. The RabbitMQ body is this object. AMQP properties may repeat `message_id`, `correlation_id`, `type`, and `app_id` for operators; if they ever disagree with the body, the body wins.

| Field | Type | Meaning |
| --- | --- | --- |
| `event_id` | UUID | Unique fact. Consumers dedupe on this. Generated as UUID v7 in application code when practical. |
| `event_type` | string | One of the catalog names below, exact spelling. |
| `occurred_at` | ISO-8601 timestamp | When the fact was committed, not when a consumer woke up. UTC. |
| `producer` | string | `order-service` or `odoo`. |
| `aggregate_id` | UUID | The stream this fact belongs to. |
| `correlation_id` | UUID | The business thread, usually the edge request that started the work. |
| `causation_id` | UUID | `event_id` of the fact that caused this one, or the request id when a human request caused it. |
| `version` | integer | Schema version of this `event_type`, starting at 1. |
| `payload` | object | Type-specific body. |

Example shell:

```json
{
  "event_id": "018f1c2a-7b3d-7c11-8a22-111111111111",
  "event_type": "OrderConfirmed",
  "occurred_at": "2026-10-08T12:00:00Z",
  "producer": "order-service",
  "aggregate_id": "018f1c2a-1111-7c11-8a22-222222222222",
  "correlation_id": "018f1c2a-3333-7c11-8a22-444444444444",
  "causation_id": "018f1c2a-5555-7c11-8a22-666666666666",
  "version": 1,
  "payload": {}
}
```

Unknown envelope fields are ignored. Unknown `event_type` values are dead-lettered after a log line, not applied. An unknown `version` greater than what the consumer understands is dead-lettered the same way. A consumer that silently skips those will look healthy while dropping money.

`version` here is the schema version. Several payloads also carry `aggregate_version`, which is the aggregate's own counter. They are different numbers. Schema version 1 can carry aggregate version 14.

Money inside payloads is always:

```json
{"amount_minor": 1999, "currency": "USD"}
```

Integer minor units. Never a JSON float.

## Who produces and who consumes

| Event | Producer | Consumers | Aggregate |
| --- | --- | --- | --- |
| `OrderCreated` | `order-service` | reporting | order |
| `OrderConfirmed` | `order-service` | reporting, Odoo | order |
| `OrderCancelled` | `order-service` | reporting | order |
| `OrderProcessingStarted` | `order-service` | reporting | order |
| `OrderShipped` | `order-service` | reporting | order |
| `OrderDelivered` | `order-service` | reporting | order |
| `ProductCreated` | `order-service` | reporting | product |
| `ProductUpdated` | `order-service` | reporting | product |
| `CustomerUpdated` | `order-service` | reporting | customer |
| `PaymentConfirmed` | `order-service` | reporting | order |
| `PaymentFailed` | `order-service` | reporting | order |
| `InventoryUpdated` | `odoo` | order-service, reporting | product |

Odoo consumes **only** `OrderConfirmed` from this catalog. `OrderCancelled` is not delivered to Odoo: cancellation exists only from `PENDING`, and Odoo never saw the pending order. Stopping an ERP document after confirmation is a saga command, not this event.

The order service does not consume its own order events. It already applied them in the transaction that wrote the outbox. It consumes `InventoryUpdated` only.

Reporting consumes the full catalog, including inventory.

Password hashes, refresh tokens, and card numbers are never placed in a payload. `PaymentConfirmed` carries the provider's reference, not a PAN.

## Ordering notes

RabbitMQ preserves order per queue only while a single consumer reads that queue and messages were published in order. Competing consumers remove that guarantee. Design rules:

- **Order, including payment facts on that order.** Transition and payment events for one `aggregate_id` carry contiguous `aggregate_version` values starting at 1. The consumer applies version N+1 only after N. If N+1 arrives first, the consumer rejects the message so it is retried, not dead-lettered on the first miss. After the retry budget, a true gap lands in the DLQ and an alert fires.
- **Product and customer.** `ProductCreated`, `ProductUpdated`, and `CustomerUpdated` carry a full public snapshot and `aggregate_version`. A consumer may apply a higher version and ignore a lower one. Lost intermediates are acceptable because the next snapshot replaces the public fields. History of names is not a goal.
- **Inventory.** `InventoryUpdated` is a full snapshot, not a delta. The order service and reporting store it when `aggregate_version` is newer than the stored snapshot. An older message is acknowledged and ignored. Deltas were rejected because a lost delta silently corrupts stock, while a lost snapshot heals on the next update.
- **Single publisher at first.** The outbox publisher sends in `created_at, id` order so one reporting consumer with modest prefetch sees a natural order. That is an implementation aid, not a guarantee once more publishers or consumers appear. Version checks are the guarantee.

What happens without version checks: two reporting workers apply `OrderShipped` before `OrderProcessingStarted`, the projection grows a private state machine, and totals disagree with `order_db`.

Detection: `projection_versions` gaps, DLQ depth, and a metric of events acked as stale. Recovery: replay the gap from the outbox if the row is still `published` and the payload is intact, or rebuild the projection for that aggregate from a later snapshot event where the catalog allows it. Order transitions cannot be rebuilt from the latest row alone if intermediate payloads mattered; the outbox payload is the record of the fact.

## Catalog schemas

`aggregate_version` in the payload is required on every event below.

### `OrderCreated`

Emitted when an order is first stored as `PENDING`.

```json
{
  "order_id": "uuid",
  "customer_id": "uuid",
  "status": "PENDING",
  "items": [
    {
      "product_id": "uuid",
      "sku": "MUG-01",
      "quantity": 2,
      "unit_price": {"amount_minor": 1500, "currency": "USD"}
    }
  ],
  "total": {"amount_minor": 3000, "currency": "USD"},
  "aggregate_version": 1
}
```

`order_id` equals the envelope `aggregate_id`. Item prices are the copies taken at creation. A later `ProductUpdated` must not change this payload's meaning.

### `OrderConfirmed`

`PENDING` to `CONFIRMED` succeeded.

```json
{
  "order_id": "uuid",
  "customer_id": "uuid",
  "status": "CONFIRMED",
  "items": [],
  "total": {"amount_minor": 3000, "currency": "USD"},
  "aggregate_version": 2
}
```

Items and total are repeated so Odoo can create a sales order from this message alone. Odoo must not call back to `order_db` to fill in the lines. The item array uses the same element shape as `OrderCreated`.

### `OrderCancelled`

`PENDING` to `CANCELLED` succeeded.

```json
{
  "order_id": "uuid",
  "status": "CANCELLED",
  "reason": "customer_request",
  "aggregate_version": 2
}
```

`reason` is a short code from the server (`customer_request`, `staff_request`). Free-text notes, if added later, are a new schema version.

### `OrderProcessingStarted`

`CONFIRMED` to `PROCESSING`.

```json
{
  "order_id": "uuid",
  "status": "PROCESSING",
  "aggregate_version": 5
}
```

### `OrderShipped`

`PROCESSING` to `SHIPPED`.

```json
{
  "order_id": "uuid",
  "status": "SHIPPED",
  "tracking_reference": "TRK-100",
  "aggregate_version": 6
}
```

`tracking_reference` may be null when the warehouse has no carrier code yet. Status has still changed.

### `OrderDelivered`

`SHIPPED` to `DELIVERED`.

```json
{
  "order_id": "uuid",
  "status": "DELIVERED",
  "aggregate_version": 7
}
```

### `ProductCreated` and `ProductUpdated`

```json
{
  "product_id": "uuid",
  "sku": "MUG-01",
  "name": "Mug",
  "unit_price": {"amount_minor": 1500, "currency": "USD"},
  "active": true,
  "aggregate_version": 1
}
```

`ProductCreated` is the first version. `ProductUpdated` is every later snapshot. Consumers upsert.

### `CustomerUpdated`

```json
{
  "customer_id": "uuid",
  "email": "a@example.com",
  "display_name": "Ada",
  "aggregate_version": 3
}
```

Emitted when a public profile field changes, including registration. There is no separate `CustomerCreated` in this catalog; the first update is version 1. That keeps one schema. Email is personal data: reporting may store it for the operational screens this project includes, and logs must not dump the payload wholesale.

### `PaymentConfirmed`

Recorded by the order service after the provider approves a charge. Order status is unchanged by this fact alone.

```json
{
  "order_id": "uuid",
  "payment_reference": "pay_123",
  "amount": {"amount_minor": 3000, "currency": "USD"},
  "aggregate_version": 3
}
```

`payment_reference` is the provider's id, safe to store, and not a card number.

### `PaymentFailed`

Recorded when the provider declines, times out, or the circuit is open and the saga will compensate.

```json
{
  "order_id": "uuid",
  "reason_code": "declined",
  "aggregate_version": 3
}
```

Allowed `reason_code` values for schema version 1: `declined`, `timeout`, `circuit_open`, `provider_error`. Status of the order remains `CONFIRMED`.

### `InventoryUpdated`

Published by Odoo after a stock change commits. Full snapshot.

```json
{
  "product_id": "uuid",
  "sku": "MUG-01",
  "quantity_on_hand": 10,
  "quantity_reserved": 2,
  "warehouse_code": "MAIN",
  "aggregate_version": 4
}
```

Envelope `aggregate_id` is `product_id`. `quantity_on_hand` and `quantity_reserved` are integers. The order service upserts `InventorySnapshot` when the version is newer. A confirm request may refuse to confirm when the snapshot shows nothing available. That check is a user-experience guard. Two confirms can still race on the last unit because the snapshot is stale and the real reservation happens in Odoo afterward. The reserve step is the authority; if it fails, the saga compensates.

> **Learning simplification.** Reservation success and failure are represented by this snapshot plus the saga command result, not by extra catalog events such as `InventoryReserved`.
> **Production would require.** Explicit reservation outcomes if more than one warehouse or more than one channel can reserve the same SKU. Those events would be a conscious catalog change, not a quiet addition inside `InventoryUpdated`.

## What is not in the catalog

- Commands: reserve inventory, release inventory, create ERP order, cancel ERP order.
- HTTP requests and responses.
- Logs and traces.
- Rejected transitions. A rejected confirm produces no event. Nothing happened.

## Related documents

- [rabbitmq.md](rabbitmq.md)
- [outbox.md](outbox.md)
- [idempotency.md](idempotency.md)
