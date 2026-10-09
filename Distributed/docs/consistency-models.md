# Consistency models

**Status: Extension Phase 2.** Strong consistency is one `order_db` transaction. Django `reporting_db` and Odoo `odoo_db` catch up from events and commands. This page describes the code that is in the tree. It does not record a Compose, kind, Locust, or restore run.

The decision is [docs/adr/ADR-006-why-eventual-consistency.md](adr/ADR-006-why-eventual-consistency.md). The saga states and the command names are [docs/saga-pattern.md](saga-pattern.md). Broker, outbox, Kubernetes, observability, tests, and auth are not copied here:

- [docs/rabbitmq.md](rabbitmq.md)
- [docs/outbox.md](outbox.md)
- [docs/kubernetes.md](kubernetes.md)
- [docs/observability.md](observability.md)
- [docs/testing.md](testing.md)
- [docs/security.md](security.md)
- [docs/saga-pattern.md](saga-pattern.md)

## Where the guarantee stops

A successful confirm commits three things in one `order_db` transaction: the order row (`CONFIRMED`, `saga_status` `STARTED`), the `saga_instances` row, and the `OrderConfirmed` outbox row. `ConfirmOrder` in `services/order-service/src/order_service/application/use_cases/orders.py` does that through the unit of work. Process memory is not a second record. If that transaction rolls back, the caller does not see `CONFIRMED` and the outbox does not contain the event.

`OrderCreated` was committed in the earlier create transaction, with the order still `PENDING`. Create and confirm are not one transaction.

Nothing in that confirm transaction writes `reporting_db` or `odoo_db`. The outbox publisher sends the stored body later. Django applies it in its own transaction (`projections/apply.py`: the projection row and `processed_events` commit together). Odoo applies `CreateErpOrder` and `ReserveInventory` in `odoo_db`. Those databases do not join `order_db`.

`COMPLETED` on the saga means reserve, simulated payment, and ERP create finished. The order status machine is what says the parcel was delivered.

## Consistency matrix

| Operation | Source of truth | Reader | When the reader can still be stale |
| --- | --- | --- | --- |
| Create an order | `order_db` `orders`, `order_items`, and the `OrderCreated` outbox row | `GET` on the order service | After the create response, that `GET` returns `PENDING`. The report does not have the row until `OrderCreated` is applied. |
| Confirm an order | `order_db` `orders`, `saga_instances`, and the `OrderConfirmed` outbox row, one transaction | `GET` on the order service | After the confirm response, that `GET` returns `CONFIRMED` and `saga_status` `STARTED`. |
| Same confirm | The order row above | Django `order_projections` and `GET /api/v1/reports/orders/summary` | Missing until `OrderCreated` is applied. `PENDING` at version 1 after only that event, while the order row is already `CONFIRMED` at version 2. Matches after `OrderConfirmed` is applied. `as_of` is the newest projection timestamp, not the order-service clock. |
| Simulated payment | The saga row and the `PaymentConfirmed` or `PaymentFailed` outbox row in `order_db` | Django `payment_projections` | Until the reporting consumer applies `payment.*`. The order status stays `CONFIRMED`. A recorded refund is not a guaranteed movement of money. |
| `ReserveInventory` / `ReleaseInventory` | `odoo_db` `commerce.reservation` | The next saga step, via lookup | A timeout is an unknown outcome. The orchestrator looks the reservation up before it sends the command again. A second command with the same order keeps one row. |
| `CreateErpOrder` | `odoo_db` `sale.order` | Saga status `ODOO_ORDER_CREATED`, then `COMPLETED` | Until the command consumer applies `CreateErpOrder`. `OrderConfirmed` is recorded and does not create the sales order. Reporting still consumes `OrderConfirmed`. |
| Stock on the product page | Odoo stock | `inventory_snapshots` in `order_db` | Until `InventoryUpdated` is applied by `apply_inventory_payload`. The snapshot is a projection. Reservation in Odoo is the authority. |
| Stock on a report | Odoo stock, via `InventoryUpdated` | Django `inventory_projections` | Until the reporting consumer applies that event. It can lag both Odoo and `inventory_snapshots`. |
| Fulfillment milestone | `order_db` order status (`PROCESSING`, `SHIPPED`, `DELIVERED`) | Django `order_projections` | Until that status event is applied. Saga `COMPLETED` does not mean `DELIVERED`. |
| Product `GET` | `products` in `order_db` | Redis product cache | A catalog write deletes the key after commit. A reader can still hold a previous value until that delete is visible. Cache failure tests are Extension Phase 5. |

Compensation that fails stays `MANUAL_INTERVENTION_REQUIRED`. It is not `COMPENSATED`. That pair is stored on the saga row in `order_db`. The report learns it only if a later catalog event says so. Saga commands are not projected as order status.

## Reading the order row and the projection

The walkthrough uses the order-service in-memory unit of work and the reporting suite's SQLite database. It does not start Compose or kind.

1. `export_confirmed_order` confirms an order. The returned order is `CONFIRMED` at version 2, with saga status `STARTED`. The `OrderConfirmed` envelope is in that snapshot. No reporting process has applied it.
2. The reporting test reads `order_projections` for that id and finds no row. `as_of` is null.
3. Applying only `OrderCreated` leaves the projection at `PENDING` version 1. The exported order row is still `CONFIRMED` version 2.
4. Applying `OrderConfirmed` makes the projection `CONFIRMED` at version 2, with the same total. Applying that envelope again is a duplicate and does not add a second row.

```bash
cd services/order-service && .venv/bin/python -m pytest tests/unit/test_consistency_export.py tests/unit/test_saga_scenarios.py
cd services/reporting-service && .venv/bin/python -m pytest projections/tests/test_consistency_lag.py
cd services/odoo && python -m pytest tests/test_commands.py
```

## Idempotent reservation

Odoo looks up `commerce.reservation` by order id before it inserts (`services/odoo/src/commerce_erp/commands.py`). The table has one row per commerce order id. A second `ReserveInventory` with the same idempotency key is a duplicate. A second command with a new key and the same order id returns `already-reserved` and keeps the same reservation id.

`services/odoo/tests/test_commands.py` `test_unknown_timeout_looks_up_before_a_second_reserve` applies the command, looks it up, replays it, and retries with a new key. The saga side of the timeout is already in `test_odoo_is_unavailable` and `test_workflow_resumes_after_restart`: the next step looks up and does not call reserve again while the outcome is unknown, and a restarted process that finds the hold does not reserve again.

The live saga worker still has no command-result reply, so it does not reach `COMPLETED` against a running Odoo. This phase does not add that reply. The lookup used above is the one Phase 1 already calls before a retry.
