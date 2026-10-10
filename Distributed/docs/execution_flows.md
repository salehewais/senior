# Execution flows

Primary page: `STRUCTURE.html`, section "Request and message lifecycles".

## Order create

1. Client calls the gateway `POST /api/v1/orders`.
2. `edgeheaders` prepare strips identity headers and sets `X-Correlation-Id` when the incoming value is not a UUID.
3. Traefik in-memory limit: average 30/s, burst 60, per gateway process.
4. `jwt-check` `GET /verify` (`deploy/gateway/jwt_check.py`).
5. Router `order-api` forwards to `order-service:8000` in the full stack (`deploy/compose/dynamic.yaml`).
6. The order service checks the token again, applies Redis limits (fail closed), and takes the short create lock.
7. The use case commits the order and the outbox row in one `order_db` transaction.
8. HTTP returns. `order-outbox-publisher` later claims rows with `FOR UPDATE SKIP LOCKED` and waits for a broker confirm.

## Confirm

`confirm_order` in `services/order-service/src/order_service/presentation/routes/orders.py` runs `ConfirmOrder` and increments `orders_confirmed_total`. It does not call `advance()`. The saga worker does, one step at a time, and that worker is not in Compose. `deploy/compose/up.sh` says a live confirm does not reach saga `COMPLETED` against Odoo.

Legal statuses: `services/order-service/src/order_service/domain/entities/order_status.py`.

## Inventory and ERP

- `CreateErpOrder` creates one sales order (`services/odoo/src/commerce_erp/commands.py`).
- `OrderConfirmed` is recorded and does not create a second sales order (`services/odoo/src/commerce_erp/confirmed.py`).
- Odoo publishes `InventoryUpdated` only (`services/odoo/src/commerce_erp/publisher.py`).
- The order inventory consumer applies `inventory_snapshots` and dedupes `event_id`.
- Warehouse status changes are HTTP to `/api/v1/internal` with `X-Internal-Token`.

## Reporting and notifications

Both are consumers. Stopping `reporting-consumer` leaves existing report rows readable and delays new ones. Notification queue bindings are in `services/notification-service/src/notification_service/topology.py`.
