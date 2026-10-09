# Failure scenarios

**Status: The services implement the results below. Phase 18 adds stop/start scripts in `deploy/failure-lab`. Those scripts were not run live (Docker was down). This page is the expected result, not a measured drill.**

These are the failures a drill should cause on purpose. Each one states the user-visible result, what must stay up, how you notice, and how you recover. If a drill produces a different result, the implementation drifted from the architecture.

Phase 18 is the failure lab. Phase 19 is backup and restore, not this lab. Do not "fix" a drill by weakening the expected result.

## Order database unavailable

**Cause.** Stop Postgres, or revoke the `order_service` role.

**Expected.** Create and confirm return 503 or 500. The gateway is up. Reporting still serves the last projections. Odoo still has documents it already stored. No half-written order appears after Postgres returns, because a transaction that did not commit left no row and no outbox message.

**Detection.** Readiness fails, `OrderServiceDown`, gateway 5xx.

**Recovery.** Restore the database process. In-flight client retries with the same idempotency key must not duplicate orders once the write path works again.

## Kill the process after commit and before publish

**Cause.** Commit an order, stop the publisher, or crash it after insert and before the broker confirm. Easiest drill: stop the publisher process only.

**Expected.** The HTTP call has already succeeded. `outbox` holds a `pending` row. Reporting and Odoo do not move yet. Restarting the publisher sends the message. Consumers apply it once.

**Detection.** `OutboxStale`.

**Recovery.** Start the publisher. Do not re-confirm the order in the UI; that should 409.

## Duplicate delivery

**Cause.** Ack fails after the consumer commits. Republish the same `event_id`, or run the handler twice in a test.

**Expected.** One sales order in Odoo, one projection row, `consumer_messages_total` result `duplicate` on the second delivery.

**Detection.** Duplicate counter. Absence of doubled revenue is the real assertion.

**Recovery.** None, if the processed-event transaction is correct. If revenue doubled, the consumer committed the business write outside the dedup transaction. Fix that before adding features.

## RabbitMQ down

**Cause.** Stop the broker.

**Expected.** Confirm still commits in `order_db`. Publish attempts fail and rows stay `pending`. Queues do not grow. When the broker returns, the publisher drains. Messages are not invented for rows already `published`.

**Detection.** `RabbitDown`, then `OutboxStale`.

**Recovery.** Start RabbitMQ. If the volume was wiped, the topology must be reapplied from code before the drain, or publishes will be unroutable and rows will become `failed`.

## Poison payload

**Cause.** A message whose `event_type` is unknown, or whose order version skips in a way that never fills in.

**Expected.** Retries follow the backoff in [rabbitmq.md](rabbitmq.md), then the message sits in the consumer's DLQ. Later messages on that queue continue if the consumer does not stop the world. With one consumer and prefetch 1, a retrying message delays others; that is a reason to keep poison messages moving to the DLQ rather than requeue forever.

**Detection.** `DeadLetterBacklog`.

**Recovery.** Fix the producer or the handler. Replay from the DLQ with a recorded reason. Do not ack the DLQ to make the alert green.

## Odoo down

**Cause.** Stop Odoo after the platform is otherwise healthy.

**Expected.** Create and confirm still succeed. `q.odoo.order-confirmed` grows. Saga steps that need Odoo retry. Inventory snapshots stop updating, so the "nothing in stock" guard becomes stale. Reports that do not need new stock events still work.

**Detection.** Queue depth, snapshot age, saga stuck in `STARTED` or `PAYMENT_CONFIRMED`.

**Recovery.** Start Odoo. The queue drains. Idempotency on commerce `order_id` prevents two ERP orders.

## Reporting down

**Cause.** Stop Django or `reporting_db`.

**Expected.** Checkout and confirm work. Report routes fail. The reporting queue grows or the consumer errors. Order status in the order service stays authoritative.

**Detection.** Report 5xx, `ReportingLagHigh`.

**Recovery.** Restore the read side. Drain the queue. Do not point Django at `order_db` to "catch up."

## Redis down

**Cause.** Stop Redis.

**Expected.** Product reads still return from Postgres, slower. Login and order-create limits fail closed with 503 `DEPENDENCY_UNAVAILABLE`. Existing sessions whose access tokens are still valid keep working. No order disappears, because orders were never in Redis.

**Detection.** Redis connection errors, 503s on login.

**Recovery.** Start Redis. Cache refills. Limits apply again.

## Simulated payment fails

**Cause.** The simulated adapter declines, times out, or opens its circuit after consecutive declines.

**Expected.** A decline or `circuit_open` records `PaymentFailed` and releases the reservation when release succeeds. Order status stays `CONFIRMED`. `saga_status` becomes `COMPENSATED`. If release or the simulated refund fails, `saga_status` becomes `MANUAL_INTERVENTION_REQUIRED`. The order does not become `CANCELLED`. A recorded refund is not a guaranteed movement of money.

**Detection.** `payment_circuit_state` and the saga row. Stuck `STARTED` or `PAYMENT_CONFIRMED` means an Odoo command outcome is still unknown.

**Recovery.** A half-open trial can close the circuit. Already compensated orders do not silently restart payment. `MANUAL_INTERVENTION_REQUIRED` waits for a person.

## Illegal transition through the API

**Cause.** Cancel a `CONFIRMED` order. Post `delivered` before `shipped`.

**Expected.** HTTP 409 `INVALID_STATE_TRANSITION`. No outbox row. No consumer activity. Domain tests and API tests both catch this. A passing controller test that never calls the domain is not evidence.

**Detection.** 409 rate is normal traffic. A spike can mean a bad client retrying forever.

**Recovery.** None on the server. The client stops. If a bug wrote the illegal status anyway, that is a severity-one defect: restore the row from the last valid event and fix the bypass.

## Gateway down

**Cause.** Stop Traefik.

**Expected.** The browser cannot reach APIs. Direct calls to internal service DNS still work inside the network, which is why services must verify JWTs themselves. Data is unchanged.

**Detection.** External probe fails while process probes for API containers stay green.

**Recovery.** Start Traefik. No replay.

## Clock and order of drills

Run database and broker drills before the payment drill so you know the outbox works before you interpret saga behavior. Record the actual result next to the expected result. A mismatch is a documentation update only when the architecture was wrong; otherwise it is a bug.

## Related documents

- [architecture.md](architecture.md)
- [alerting.md](alerting.md)
- [disaster-recovery.md](disaster-recovery.md)
