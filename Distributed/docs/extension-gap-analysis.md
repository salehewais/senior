# Extension gap analysis

**Status: Extension Phase 0, with Extension Phases 1, 2, 3, 4, 5, 6, 7, 8, 9, and 10 since added.** This page classifies the platform that Phases 0–20 left in the tree. Extension Phase 1 added the saga described in [saga-pattern.md](saga-pattern.md). Extension Phase 2 added [consistency-models.md](consistency-models.md). Extension Phase 3 added the Flask service in [flask-notification-service.md](flask-notification-service.md). Extension Phase 4 added [load-balancing.md](load-balancing.md) for the gateway and kind Service already in the manifests. Extension Phase 5 added [caching-strategy.md](caching-strategy.md) for the existing cache-aside path, including hit, miss, error, and duration series on the current Grafana dashboards. Extension Phase 6 added the React Native client at `mobile/react-native-app`. It did not add FCM, a second gateway, a second monitoring stack, or a second cache. The Phase 0 sentences below that say the saga, the consistency matrix, or the notification service is missing describe the tree before those phases.

This audit read the repository. It did not re-run pytest, Docker Compose, or kind. It did not start Locust, the failure lab, or a restore. No pass/fail result from a run that did not happen is recorded here.

[docs/testing.md](testing.md) records the Extension Phase 9 unit run. That same page states the remaining limit: live Compose, kind, Locust, the failure lab, and a timed restore were not run on this machine. [docs/architecture-review.md](architecture-review.md) says the Phase 20 review read the code and the manifests, did not execute the test suite, and did not start Docker or a cluster. `deploy/load/RESULTS.md` says the load run did not happen. Those statements still stand. This page does not replace them.

## Phase numbers

The checklist in [README.md](../README.md) is the authoritative order for the work that already shipped.

**README Phase 15 is the retention CronJob** (`deploy/kind/retention.yaml`, schedule `30 3 * * *`). It is not the saga.

Design notes used to schedule the saga as “Phase 15.” That numbering was stale. [docs/architecture.md](architecture.md), [docs/rabbitmq.md](rabbitmq.md), [docs/database.md](database.md), and [docs/services.md](services.md) now point that work at Extension Phase 1. README Phase 15 stays the retention CronJob.

## Already implemented

These pieces exist in the tree and are covered by tests under `services/*/tests` and `deploy/*/test_*.py`. Later extension phases should not rebuild them. The tests are in the repository. This audit did not re-run them, so this section does not claim a fresh green suite.

| Area | Where it lives | Tests that already cover it |
| --- | --- | --- |
| FastAPI Clean Architecture and the order state machine | `services/order-service`. Legal edges are `ALLOWED_TRANSITIONS` in `services/order-service/src/order_service/domain/entities/order_status.py`: `PENDING` → `CONFIRMED`, `PENDING` → `CANCELLED`, `CONFIRMED` → `PROCESSING`, `PROCESSING` → `SHIPPED`, `SHIPPED` → `DELIVERED`. | `services/order-service/tests/unit/test_order_state.py` |
| JWT auth | Register, login, refresh, logout in `services/order-service/src/order_service/presentation/routes/auth.py`. Refresh-token hashes are `refresh_tokens` in `order_db`. | `services/order-service/tests/unit/test_auth.py`, `services/order-service/tests/api/test_auth_api.py` |
| React storefront | `services/frontend` (React, Vite, TypeScript). Routes are in `services/frontend/src/App.tsx`. | Vitest script in `services/frontend/package.json` |
| RabbitMQ topology that Python actually declares | Topic exchanges `commerce.events`, `erp.events`, `commerce.retry`, and `commerce.dlx`, plus `q.reporting.projection`, `q.odoo.order-confirmed`, `q.order.inventory`, the retry ladders, and the DLQs. Declared in `services/order-service/src/order_service/infrastructure/messaging/topology.py`. | Order-service, reporting, and Odoo messaging tests |
| Idempotent consumers, retry, and DLQ | Inventory worker, reporting consumer, and Odoo consumer. Five delays, then `commerce.dlx`. Manual ack. `requeue=true` is not the failure path. | `services/order-service/tests/unit/test_reliability.py`, `services/reporting-service/projections/tests/test_apply.py`, `services/odoo/tests/` |
| Transactional outbox | The order row and the outbox row share one `order_db` session in `services/order-service/src/order_service/infrastructure/database/unit_of_work.py`. A separate publisher claims rows with `SELECT … FOR UPDATE SKIP LOCKED` in `services/order-service/src/order_service/infrastructure/messaging/outbox_publisher.py`. Odoo writes `InventoryUpdated` to `commerce_event_outbox` in `odoo_db` (`services/odoo/addons/commerce_connector/models/inventory.py`, publisher in `services/odoo/src/commerce_erp/publisher.py`). | `services/order-service/tests/unit/test_outbox.py`, `services/odoo/tests/test_publisher.py` |
| Django projections | `services/reporting-service`, database `reporting_db`. Models in `services/reporting-service/projections/models.py`. | `services/reporting-service/projections/tests/test_apply.py` |
| Odoo sales order from `OrderConfirmed`, and `InventoryUpdated` | `services/odoo`. The consumer accepts only `OrderConfirmed` (`services/odoo/src/commerce_erp/consuming.py`). Stock changes leave as `InventoryUpdated` on `erp.events`. | `services/odoo/tests/test_confirmed.py`, `services/odoo/tests/test_inventory.py` |
| Redis product cache-aside, rate limits, and the order-create lock | `services/order-service/src/order_service/infrastructure/redis/`. TTL 30 seconds (`product_cache_ttl_seconds` in `services/order-service/src/order_service/infrastructure/settings.py`). Lock TTL 15 seconds. Hit, miss, error, and duration series are described in [caching-strategy.md](caching-strategy.md). | `services/order-service/tests/unit/test_redis_cache.py`, `services/order-service/tests/unit/test_cache_behavior.py`, `services/order-service/tests/api/test_redis_limits.py` |
| Traefik gateway | `deploy/gateway`. Public rules omit `/api/v1/internal`. | `deploy/gateway/tests/test_public_routes.py`, `deploy/gateway/tests/test_jwt_check.py` |
| Compose | `deploy/compose/docker-compose.yml`. One container per service. | `deploy/compose/test_stack.py` reads the file. It does not start the stack. |
| Prometheus, Grafana, Alertmanager, OpenTelemetry | `deploy/observability/`. Dashboards are JSON under `deploy/observability/grafana/dashboards/`. Alertmanager posts to the log webhook in `deploy/observability/alertmanager/alertmanager.yml`. Traces go to Tempo through `deploy/observability/otel/collector.yaml`. | `services/order-service/tests/unit/test_observability.py`, `services/reporting-service/projections/tests/test_observability.py` |
| kind deployments, probes, and one HPA | `deploy/kind/`. `order-service` has 2 replicas, readiness `GET /health/ready`, `terminationGracePeriodSeconds: 20`, and an HPA from 2 to 4 on CPU (`deploy/kind/order.yaml`). The HTTP path is [load-balancing.md](load-balancing.md). | `deploy/kind/test_manifests.py` reads YAML. It does not create a cluster. |
| Retention CronJob | `deploy/kind/retention.yaml`. This is README Phase 15. | `services/order-service/tests/unit/test_retention.py` and the manifest check above |
| CI | `.github/workflows/distributed-commerce-ci.yml` in the parent of this directory. It lints, runs the suites that skip when Postgres, RabbitMQ, or Redis is down, and scans dependencies and, in CI, the order-service image. It does not start Compose, kind, Locust, the failure lab, or a backup. | The workflow file itself |
| Locust scenario definitions | `deploy/load/locustfile.py` and `deploy/load/scenario.py`. | `deploy/load/test_scenario.py` reads the files. `deploy/load/RESULTS.md` says no load run happened. |
| Failure-lab and backup scripts | `deploy/failure-lab/` (`rabbitmq.sh`, `redis.sh`, `reporting-consumer.sh`, `inventory-consumer.sh`) and `deploy/backup/` (`dump.sh`, `restore.sh`). | `deploy/failure-lab/test_lab.py` and `deploy/backup/test_backup.py` read the scripts. They do not stop a service or restore a database. |

The Phase 18 checklist sentence names PostgreSQL, Django, Odoo, and FastAPI as things the lab breaks. The scripts that exist stop RabbitMQ, Redis, the reporting consumer, and the inventory consumer. There is no stop script for Postgres, the Odoo HTTP process, or the order-service API.

Details of the broker, the outbox, Kubernetes, observability, the test layout, and JWT stay in the existing pages. This audit does not copy them:

- [docs/rabbitmq.md](rabbitmq.md)
- [docs/outbox.md](outbox.md)
- [docs/kubernetes.md](kubernetes.md)
- [docs/observability.md](observability.md)
- [docs/testing.md](testing.md)
- [docs/security.md](security.md)

A picture of the running pieces is [docs/current-architecture.md](current-architecture.md).

## Product cache

**Product cache-aside.** Extension Phase 5 documented this path in [caching-strategy.md](caching-strategy.md) and left it cache-aside. Get and list read Redis first and fall through to Postgres on a miss or a Redis error. Create and update delete the product key and the list prefix after `commit` (`services/order-service/src/order_service/application/use_cases/catalog.py`). Redis and Postgres are not one atomic update. Redis is shared by the API replicas. `product_cache_hits_total`, `product_cache_misses_total`, `product_cache_errors_total`, and `product_cache_duration_seconds` are on the Dependencies and Platform overview dashboards. The Dependencies board still has the exporter keyspace ratio (`redis_keyspace_hits_total` in `deploy/observability/grafana/dashboards/dependencies.json`). There is no single-flight lock. There is no RabbitMQ invalidation consumer: the writer and the cache client are the same service, and Redis is shared. Stale data, Redis down, concurrent misses, and invalidation are covered by `services/order-service/tests/unit/test_cache_behavior.py`.

## Implemented, and still wrong for the extension

**Saga.** Extension Phase 1 persists the extension state list on `saga_instances` and mirrors it on `orders.saga_status`. Confirm returns `STARTED`. `COMPLETED` means reserve, simulated payment, and ERP create finished. See [saga-pattern.md](saga-pattern.md).

**Odoo creates the sales order from `CreateErpOrder`.** `services/odoo/src/commerce_erp/confirmed.py` records `OrderConfirmed` and does not insert a `sale.order`. Reporting still consumes `OrderConfirmed`.

**`Idempotency-Key` in the API document.** [docs/api.md](api.md) says `POST /api/v1/orders`, confirm, and cancel require `Idempotency-Key`. The service does not read or store that header. `http_idempotency_keys` is named in [docs/database.md](database.md) and in the comment at the top of `services/order-service/src/order_service/infrastructure/redis/order_lock.py`. It is not a table. The only duplicate suppressor on create is the 15-second Redis lock.

**Startup.** Each phase still has a "How to run" section in [README.md](../README.md). The runbook for local dependencies, full Compose, and kind is [run-the-project.md](run-the-project.md). The directory listing is [project-structure.md](project-structure.md).

Two smaller mismatches, so later edits follow the code:

- [docs/rabbitmq.md](rabbitmq.md) says `commerce.retry` is published by broker dead-lettering, not by application code. The workers publish to that exchange themselves, then ack (`services/order-service/src/order_service/infrastructure/messaging/retry.py` and the reporting and Odoo delivery paths).
- [docs/database.md](database.md) still says a laptop may host all three databases in one PostgreSQL container. Compose runs three servers: `postgres` (`order_db`), `reporting-postgres` (`reporting_db`), and `odoo-db` (`odoo_db`) in `deploy/compose/docker-compose.yml`.

## Missing

Items below were absent at Phase 0. A bullet that names a later phase is what that phase added. Paths that are still absent are the ones later phases will add.

- A Flask notification service was absent at Phase 0. Extension Phase 3 added `services/notification-service`, `notification_db`, device tokens, and mock email and push. See [flask-notification-service.md](flask-notification-service.md).
- A React Native app was absent at Phase 0. Extension Phase 6 added `mobile/react-native-app`. The commands from this machine are in that directory's README. FCM credentials are still absent. The app was not launched on a device or emulator.
- `docs/system-architecture.html` was absent at Phase 0. Extension Phase 8 added that file. It is self-contained and linked from the README. Extension Phase 7 added [project-structure.md](project-structure.md) and [run-the-project.md](run-the-project.md). `docs/flask-notification-service.md` was added in Extension Phase 3. `docs/load-balancing.md` was added in Extension Phase 4. `docs/caching-strategy.md` was added in Extension Phase 5.

Also absent, and called out so a reader does not go looking for them: FCM credentials and a payment provider. The React Native dependency is in `mobile/react-native-app`. The Flask process and `notification_db` arrived in Extension Phase 3. `payment_circuit_state` defaults to closed (`0`) until the saga worker copies the simulated breaker (`services/order-service/src/order_service/observability/metrics.py`). `PaymentConfirmed` and `PaymentFailed` are in `ROUTING_KEYS` and are emitted by the saga.

## Decisions later phases will follow

These choices are closed. A later phase implements them. It does not open a second design.

**The saga stays inside the order service.** [docs/architecture.md](architecture.md) already refuses a separate saga service. State is rows in `order_db`, committed with the order and the outbox in the same transaction the unit of work already uses. Process memory is not the record.

**Two state machines.** The order status machine stays as coded: `PENDING` → `CONFIRMED` → `PROCESSING` → `SHIPPED` → `DELIVERED`, and cancel only from `PENDING`. The extension’s saga states are persisted on the saga row, and `orders.saga_status` mirrors that row:

`STARTED`, `INVENTORY_RESERVED`, `PAYMENT_CONFIRMED`, `ODOO_ORDER_CREATED`, `COMPLETED`, `COMPENSATING`, `COMPENSATED`, `FAILED`, `MANUAL_INTERVENTION_REQUIRED`.

Saga `COMPLETED` means reserve, simulated payment, and ERP create finished. It does not mean the parcel was delivered. [docs/architecture.md](architecture.md) uses the same meaning. The order status machine is still what says the parcel was delivered.

**Odoo remains the stock authority.** `inventory_snapshots` stays a projection of `InventoryUpdated`. Reservation is the documented `ReserveInventory` and `ReleaseInventory` commands, made idempotent in Odoo. A timeout is an unknown outcome: look up the reservation before retrying.

**Simulated payment is an adapter in the order service.** It is not a new service and not a real provider. Refund is a simulated compensation and is documented as not guaranteed.

**ERP creation moves to the command.** Once the saga owns ERP creation, the Odoo consumer stops creating a sales order from `OrderConfirmed` and creates it from `CreateErpOrder`. Reporting still consumes `OrderConfirmed`. Existing Odoo tests are updated to that contract.

**Failed compensation is not success.** If compensation fails, the saga becomes `MANUAL_INTERVENTION_REQUIRED`. It is not marked `COMPENSATED`.

**Notifications are a new service.** Flask lives at `services/notification-service` with its own Postgres database. It consumes notification events from RabbitMQ and does not open `order_db`. Email and push start as mock adapters. FCM credentials stay on the backend.

**No second stack.** Do not add another gateway or another monitoring stack. kind already runs two Traefik processes: the Ingress controller and the commerce gateway (`deploy/kind/gateway.yaml`). Cache metrics go on the existing Prometheus and Grafana assets under `deploy/observability/`. The load-balancing page describes the current path: Ingress → commerce gateway (Traefik) → Kubernetes Service `order-service` → order pods. See [load-balancing.md](load-balancing.md).

**The storefront stays where it is.** React Native Community CLI and TypeScript go in `mobile/react-native-app`. Do not move `services/frontend`. Versions and commands come from the installed toolchain when that phase starts, not from guessed package numbers.

**New docs link.** Done in Extension Phase 10. The extension pages link to [docs/rabbitmq.md](rabbitmq.md), [docs/outbox.md](outbox.md), [docs/kubernetes.md](kubernetes.md), [docs/observability.md](observability.md), [docs/testing.md](testing.md), and [docs/security.md](security.md) instead of copying them.

## Sequence after Phase 0

Extension Phase 0 is this page and [docs/current-architecture.md](current-architecture.md). The README Extension plan lists the same order.

1. **Saga.** Done in Extension Phase 1. Tables and legal transitions in the order service; an orchestrator process; simulated payment; Odoo command consumers; an outbox for saga events; the eight scenarios; [docs/saga-pattern.md](saga-pattern.md).
2. **Consistency.** Done in Extension Phase 2. [docs/consistency-models.md](consistency-models.md), the matrix, idempotent reservation against Odoo, and a read of the order row and the Django projection before and after `OrderConfirmed`.
3. **Flask notifications.** `services/notification-service`, `notification_db`, a RabbitMQ consumer, idempotency, retry, DLQ, health, metrics, mock email and push, a device-token API, a service README, and `docs/flask-notification-service.md`.
4. **Load balancing.** Done in Extension Phase 4. [docs/load-balancing.md](load-balancing.md) for the current gateway and kind Service. The manifests already show replicas, readiness, and the HPA, so that page adds no traffic observation and records no equal request counts.
5. **Caching.** Done in Extension Phase 5. [docs/caching-strategy.md](caching-strategy.md). The existing cache-aside path stays. Hit, miss, error, and duration metrics are on the current Grafana dashboards. The page documents the TTL fallback. Tests cover stale data, Redis down, concurrent misses, and invalidation. Redis and Postgres are not one atomic update.
6. **React Native.** Done in Extension Phase 6. `mobile/react-native-app` with auth, catalog, cart, checkout, orders, and in-app notifications. FCM was not added: the app was not launched on a device or emulator. The README records this machine’s Node, Java, and Android SDK commands.
7. **Structure and startup.** Done in Extension Phase 7. [project-structure.md](project-structure.md) is the tree walked on 9 October 2026. That walk marked `docs/system-architecture.html` planned. Extension Phase 8 added the file, so the planned table is empty. [run-the-project.md](run-the-project.md) is the runbook for local dependencies, `deploy/compose/docker-compose.yml`, and `deploy/kind/apply.sh`. No new script was added. `apply.sh` already runs the kind sequence and exits non-zero when Docker, kind, or kubectl is missing. The Compose start is one command.
8. **HTML explorer.** Done in Extension Phase 8. [system-architecture.html](system-architecture.html) is self-contained, uses relative links, and describes the components and workflows in the tree. It was not produced by starting Compose or kind.
9. **Operational tests.** Done in Extension Phase 9. The current suites cover saga, consistency, reservations, notifications, cache, and Redis failure. The commands and the pass counts from this machine are [testing.md](testing.md). No load number was written. `docker info` failed because `unix:///home/asm/.docker/desktop/docker.sock` was missing. `kind` is not installed. `locust` is not installed. Nothing was listening on `127.0.0.1:5672` or `127.0.0.1:6379`.
10. **Final review.** Done in Extension Phase 10. Cross-links only. The extension pages link to [rabbitmq.md](rabbitmq.md), [outbox.md](outbox.md), [kubernetes.md](kubernetes.md), [observability.md](observability.md), [testing.md](testing.md), and [security.md](security.md). No second copy of those pages.
