# Saga pattern

Extension Phase 1. The saga lives in the order service. There is no saga service. State is a row in `saga_instances` in `order_db`, committed with the order and the outbox in one transaction. Process memory is not the record. The React Native client at `mobile/react-native-app` calls the order HTTP API. It does not own saga state.

`COMPLETED` means reserve, simulated payment, and ERP create finished. It does not mean the parcel was delivered. Delivery stays on the order status machine: `PENDING` → `CONFIRMED` → `PROCESSING` → `SHIPPED` → `DELIVERED`. Cancel is legal only from `PENDING`. A payment failure does not cancel the order. The order stays `CONFIRMED`, and `orders.saga_status` mirrors the saga row.

Broker, outbox, retry, Kubernetes, observability, tests, and auth are not copied here:

- [rabbitmq.md](rabbitmq.md)
- [outbox.md](outbox.md)
- [kubernetes.md](kubernetes.md)
- [observability.md](observability.md)
- [testing.md](testing.md)
- [security.md](security.md)

## What a saga is

A saga is a sequence of local commits plus compensations. A database transaction in `order_db` cannot commit a reservation in `odoo_db` or a charge at a payment provider. Those are other processes. The orchestrator records how far this order has gone, sends the next command, and undoes what it can when a later step fails for certain.

Rollback and compensation are different. `ROLLBACK` undoes writes that have not committed. Compensation is a new local commit that asks a system to undo a side effect it already accepted. A simulated refund is that kind of commit. It is not a guaranteed movement of money.

Orchestration keeps the steps and the legal transitions in one place, the order service. Choreography would let each service decide the next step from events. This phase uses an orchestrator because the workflow and its failures are easier to read in one row.

## Workflow

```text
confirm order
     |
     v
STARTED
     |
     v
ReserveInventory
     |
     v
INVENTORY_RESERVED
     |
     v
simulated charge
     |
     v
PAYMENT_CONFIRMED
     |
     v
CreateErpOrder
     |
     v
ODOO_ORDER_CREATED
     |
     v
COMPLETED
```

Confirm returns when `order_db` commits. It does not call Odoo or the payment adapter. The row starts at `STARTED`. The worker `python -m order_service.infrastructure.saga.worker` loads non-terminal rows and applies one step per transaction.

Odoo is the stock authority. `inventory_snapshots` stays a projection of `InventoryUpdated`. Reservation is `ReserveInventory` and `ReleaseInventory` on the direct exchange `commerce.commands`. A timeout is an unknown outcome. The next step looks the reservation or the sales order up before it sends the command again. The Odoo consumer does the same lookup before it inserts, so a late duplicate does not reserve twice or create a second sales order.

`OrderConfirmed` is still published for reporting. The Odoo consumer records that delivery and does not create a sales order from it. `CreateErpOrder` creates the sales order. `CancelErpOrder` cancels it. Reporting does not bind to `commerce.commands`.

## States

| Status | Meaning |
| --- | --- |
| `STARTED` | Confirm committed. Reserve has not succeeded. |
| `INVENTORY_RESERVED` | Odoo holds stock for this order, or a lookup found that hold. |
| `PAYMENT_CONFIRMED` | The simulated charge succeeded. The order status is still `CONFIRMED`. |
| `ODOO_ORDER_CREATED` | `CreateErpOrder` succeeded, or a lookup found the sales order. |
| `COMPLETED` | Reserve, simulated payment, and ERP create finished. The parcel is not delivered. |
| `COMPENSATING` | A later step failed. Release, simulated refund, or ERP cancel is in progress. |
| `COMPENSATED` | Those compensations finished. The order status is still `CONFIRMED`. |
| `FAILED` | Reserve was rejected. Nothing was held, so there is nothing to release. |
| `MANUAL_INTERVENTION_REQUIRED` | A compensation step failed. The saga is not `COMPENSATED`. |

Legal transitions are `ALLOWED_SAGA_TRANSITIONS` in `services/order-service/src/order_service/domain/entities/saga_status.py`. An unknown outcome does not change status. The pending step stays on the row until lookup or a retry resolves it.

## Payment

`SimulatedPayment` is an adapter in the order service. It is not a new service and not a card processor. `PaymentConfirmed` and `PaymentFailed` go through the existing outbox onto `commerce.events` (`payment.confirmed`, `payment.failed`). The order version moves. The order status does not.

A succeeded refund is a local record. It is not a guaranteed refund. If the refund or the inventory release fails, the saga becomes `MANUAL_INTERVENTION_REQUIRED`.

The adapter opens a small circuit after repeated declines. While it is open, a new charge fails with `circuit_open` and the saga compensates. The gauge `payment_circuit_state` is 0 closed, 1 half-open, 2 open. The worker copies the adapter's state into that gauge. The default is closed.

## Commands

The envelope is the same shape as a catalog event. `event_type` is the command name. The payload carries `idempotency_key`. Retries reuse that key.

Commands go out on `commerce.commands`. Routing keys, retry, and dead-letter are [rabbitmq.md](rabbitmq.md).

The worker that ships with this phase treats an Odoo call as unknown and writes the command to the outbox. It does not pretend the reservation succeeded. The eight scenarios below drive the same orchestrator with ports so the outcomes are visible without a live broker. The Odoo tests apply the same command bodies.

## Eight scenarios

Expected order status is `CONFIRMED` in every row. The saga status is the column that changes.

| # | Scenario | Saga status | Side effects |
| --- | --- | --- | --- |
| 1 | Every step succeeds | `COMPLETED` | One `ReserveInventory`, one simulated charge, one `PaymentConfirmed`, one `CreateErpOrder`. No release. Order is not `DELIVERED`. |
| 2 | Inventory reservation fails | `FAILED` | The reserve command was attempted and rejected. No charge, no ERP order, no release. |
| 3 | Payment fails after inventory reservation | `COMPENSATED` | `PaymentFailed` with `declined`. `ReleaseInventory` runs. No `CreateErpOrder`. The hold is released. |
| 4 | Odoo is unavailable | `STARTED` | The reserve command is unknown. The next step looks the reservation up and does not send a second reserve while the lookup is still unknown. |
| 5 | An event arrives twice | unchanged after the first apply | The orchestrator does not reserve or charge a second time for the same step. Odoo keeps one reservation and one sales order for a repeated command with the same idempotency key. |
| 6 | A process crashes halfway through the saga | `PAYMENT_CONFIRMED` after restart from `INVENTORY_RESERVED` | The new process reads the row. It does not reserve again. It charges once. |
| 7 | Compensation fails | `MANUAL_INTERVENTION_REQUIRED` | Release failed after a declined charge. The saga is not `COMPENSATED`. The hold is still there. |
| 8 | The workflow resumes after restart | `INVENTORY_RESERVED` | The first process timed out after the hold existed. The restarted process looks the reservation up and continues. It does not reserve again. |

A simulated refund that fails after `CreateErpOrder` was rejected is the same rule as scenario 7: `MANUAL_INTERVENTION_REQUIRED`, not `COMPENSATED`. The refund record, when it succeeds, is still not a guaranteed refund.

## Saga and outbox

The saga chooses the next business step and stores the command or the payment fact in the same `order_db` transaction. The publisher is [outbox.md](outbox.md). Which readers can lag that commit is [consistency-models.md](consistency-models.md).

## Tests

`services/order-service/tests/unit/test_saga_scenarios.py` covers the eight scenarios. `services/odoo/tests/test_commands.py` covers duplicate reserve, create, release, and cancel. `services/odoo/tests/test_confirmed.py` covers `OrderConfirmed` no longer creating a sales order. Commands and what a skip means are [testing.md](testing.md).
