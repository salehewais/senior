# Flask notification service

**Status: Extension Phase 3.** This page describes `services/notification-service` as it is in the tree. Broker retry, the outbox, metrics labels, tests, and JWT rules stay in the pages linked below. This page does not copy them.

The Extension Phase 0 plan and [extension-gap-analysis.md](extension-gap-analysis.md) say this service consumes notification events. They do not name event types, tables, or HTTP paths. Nothing under the repository or `/home/asm/.cursor/plans` names a `NotificationRequested` event or a device-token route. This phase follows the gap-analysis decisions: a new Flask process, its own database, mock adapters, and the existing commerce broker. It does not add a new event type to the order service, because that would be a second contract the spec never wrote down.

## What it owns

| Piece | Where |
| --- | --- |
| Process | `services/notification-service` |
| Database | `notification_db` on `notification-postgres` |
| Queue | `q.notification.delivery` |
| HTTP | port 8002 |
| Consumer metrics | port 9100 |

The DSN is `NOTIFICATION_DATABASE_URL`. `require_notification_database` in `services/notification-service/src/notification_service/settings.py` raises before SQLAlchemy builds an engine when the database name is `order_db`, `reporting_db`, or `odoo_db`. The only accepted name is `notification_db`.

Compose runs that database as its own Postgres container (`deploy/compose/docker-compose.yml`). The host-only file `services/notification-service/compose.yaml` publishes it on `127.0.0.1:5435`. kind uses the Service `notification-postgres`.

## Tables

Alembic revision `20261009_0001` creates these tables in `notification_db`:

| Table | Role |
| --- | --- |
| `device_tokens` | `id`, `account_id`, `token`, `platform` (`android` or `ios`), `created_at`. Unique on `(account_id, token)`. |
| `processed_events` | Primary key `event_id`. A second delivery of the same id is acked as a duplicate and does not call the adapters again. |
| `order_contacts` | `order_id` to `account_id`, copied from an event payload that already carries `customer_id`. |
| `notification_deliveries` | One row per mock email or mock push: `event_id`, `channel` (`email` or `push`), `account_id`, `destination`, `summary`. |

`order_contacts` is not a query against `order_db`. Payloads that omit `customer_id` (`OrderShipped`, `OrderDelivered`, `OrderCancelled`, `PaymentConfirmed`, `PaymentFailed`) use a contact learned from an earlier `OrderConfirmed` for that `order_id`. If none is stored yet, the handler returns a retry and does not mark the event processed. `OrderCancelled` from `PENDING` never has a contact in this database, so those deliveries use the retry ladder and then the dead-letter queue. Adding `customer_id` to that payload would be a change to the order service, which this phase does not make.

## Events consumed

The consumer binds `q.notification.delivery` to `commerce.events` with these keys, which are the keys in `services/order-service/src/order_service/application/publishing.py`:

| Routing key | Event |
| --- | --- |
| `order.confirmed` | `OrderConfirmed` |
| `order.cancelled` | `OrderCancelled` |
| `order.shipped` | `OrderShipped` |
| `order.delivered` | `OrderDelivered` |
| `payment.confirmed` | `PaymentConfirmed` |
| `payment.failed` | `PaymentFailed` |

The envelope is the one in [events.md](events.md). Schema version 1 only. An unknown type, an unknown version, or a body that is not that envelope is published to `commerce.dlx` and acked. The consumer does not use `requeue=true`.

`q.notification.delivery` is declared by this service (`services/notification-service/src/notification_service/topology.py`), the same way the reporting consumer declares `q.reporting.projection`. The order-service `declare_topology` function is unchanged. Shared exchanges are redeclared with the same durable topic arguments, which is idempotent.

Retry and dead-letter for `q.notification.delivery` are [rabbitmq.md](rabbitmq.md). kind runs two consumer replicas ([kubernetes.md](kubernetes.md)). `processed_events.event_id` is what makes that safe. The outbox that produces these events is still the order service's; see [outbox.md](outbox.md). This service does not write that outbox and does not answer saga commands.

## HTTP routes

| Method and path | Who |
| --- | --- |
| `GET /health/live` | Process is up. Does not open a database. |
| `GET /health/ready` | `notification_db` accepted `SELECT 1`. Otherwise 503 `DEPENDENCY_UNAVAILABLE`. |
| `GET /metrics` | Prometheus text. Not on the public gateway. |
| `POST /api/v1/device-tokens` | Bearer access token. Body `{"token", "platform"}`. 201, or 200 when that account already stored the same token. |
| `GET /api/v1/device-tokens` | Tokens whose `account_id` is the token subject. |
| `DELETE /api/v1/device-tokens/<id>` | Removes that row when it belongs to the caller. Another account's id is 404. |

The caller is the JWT `sub`. This service verifies RS256 with the public key only. It does not issue tokens and it does not read `X-User-Id`. Rules for that key are [security.md](security.md).

The existing Traefik files route `/api/v1/device-tokens` to this service and exclude that prefix from the order-service router (`deploy/compose/dynamic.yaml` and `deploy/gateway/dynamic.yaml`). `DELETE` was added to the gateway CORS allow list so that removal is not rejected at the edge. There is no second gateway.

## Mock adapters

`MockEmail` and `MockPush` in `services/notification-service/src/notification_service/adapters.py` append `notification_deliveries` rows. They do not open a socket to an SMTP server or to FCM.

Email has no address to send to: the catalog payloads this queue accepts do not include an email except `CustomerUpdated`, which this queue does not bind, and this service does not look one up in `order_db`. The mock records `destination` as `account:<account_id>` and `summary` as the event type.

Push records one row per device token for that account. The destination is the stored token. When the account has no token, one row is stored with destination `no-device`. FCM credentials are not read and are not in this service. A real provider is later work, after the React Native app exists.

A raised adapter failure rolls the transaction back, so `processed_events` does not keep the id, and the broker retry path runs.

## Health and metrics

`GET /metrics` on the HTTP process and port 9100 on the consumer export the same series the other consumers use (`http_requests_total`, `messages_consumed_total`, `messages_processed_total`, `messages_failed_total`, `message_retry_total`, `message_dlq_total`, and the duration histograms). Labels are `service`, `event_type`, `route`, `status`, `queue`, and `result`. They are not an account id, an order id, or a token.

The existing Prometheus file `deploy/observability/prometheus/prometheus.yml` scrapes `notification-service:8002`, `notification-consumer:9100`, and `postgres-exporter-notification:9187`. kind mounts that same file. No second Prometheus and no second Grafana were added. The current dashboards do not yet graph these series.

How to read a scrape, a log line, or a trace stays in [observability.md](observability.md). This service does not export traces.

## Tests

Unit tests do not need Docker. They are `services/notification-service/tests/`. Two live tests in `tests/integration/test_live.py` skip when `127.0.0.1:5435` or `127.0.0.1:5672` is closed. What the suite is expected to prove, and what a skip means, is [testing.md](testing.md).

Commands that run on this machine are in `services/notification-service/README.md`.
