# Project structure

**Status: Extension Phase 7.** This page is the tree under `Distributed` as walked on 9 October 2026. A path is marked planned only when the Extension plan still names it and the walk did not find it.

The walk listed directories and source files. It left out `node_modules`, virtualenvs, `__pycache__`, `.pytest_cache`, `.ruff_cache`, and `*.egg-info`. Those caches and installs were on disk. `services/frontend/dist` was also on disk; it is a Vite build output. Behavior of the running system is [current-architecture.md](current-architecture.md). How to start it is [run-the-project.md](run-the-project.md).

## Top of the tree

| Path | What the walk found |
| --- | --- |
| `README.md` | Phases 0–20 and Extension Phases 0–10. The phase “How to run” sections stay in this file. |
| `services/` | `order-service`, `reporting-service`, `notification-service`, `odoo`, `frontend` |
| `mobile/react-native-app/` | React Native Community CLI app |
| `deploy/` | `compose`, `gateway`, `kind`, `observability`, `failure-lab`, `backup`, `load` |
| `docs/` | The pages listed below, plus `docs/adr/` |
| `.gitignore` | Ignore rules for this directory |

CI is the parent workflow `.github/workflows/distributed-commerce-ci.yml` (one directory above `Distributed`). There is no `scripts/` directory here.

## Services

### `services/order-service`

FastAPI order service. Own Compose file `compose.yaml` starts Postgres (`order_db` on `127.0.0.1:5432`), RabbitMQ (`127.0.0.1:5672` and management `127.0.0.1:15672`), and Redis (`127.0.0.1:6379`). Also present: `Dockerfile`, `pyproject.toml`, `alembic.ini`, `.env.example`, `.dockerignore`.

| Path | What it is |
| --- | --- |
| `alembic/versions/` | `20261008_0001_initial_order_db.py`, `20261008_0002_accounts_and_refresh_tokens.py`, `20261008_0003_processed_events_and_snapshots.py`, `20261008_0004_outbox.py`, `20261009_0005_saga_instances.py` |
| `src/order_service/domain/` | Entities, events, repositories. Saga types are `domain/entities/saga.py` and `domain/entities/saga_status.py`. |
| `src/order_service/application/use_cases/` | `auth.py`, `catalog.py`, `orders.py` |
| `src/order_service/application/saga/` | `orchestrator.py`, `payment.py`, `ports.py`, `results.py`, `contract.py` |
| `src/order_service/infrastructure/database/` | SQLAlchemy models, unit of work, repositories, `saga_repository.py` |
| `src/order_service/infrastructure/messaging/` | Topology, outbox publisher, inventory consumer, retry |
| `src/order_service/infrastructure/redis/` | Catalog cache, limiter, order-create lock |
| `src/order_service/infrastructure/saga/worker.py` | Process entry `python -m order_service.infrastructure.saga.worker` |
| `src/order_service/infrastructure/security/` | JWT keys, passwords, refresh tokens, internal token |
| `src/order_service/observability/` | JSON logs, metrics, tracing |
| `src/order_service/presentation/` | `app.py` and routes `auth.py`, `customers.py`, `health.py`, `orders.py`, `products.py` |
| `tests/unit/`, `tests/api/`, `tests/integration/`, `tests/support/` | Suites and in-memory fakes, including `tests/unit/test_saga_scenarios.py` |

This directory has no `README.md`. The host commands are in the README sections [How to run Phase 1](../README.md#how-to-run-phase-1) through Phase 6 and [How to run Phase 9](../README.md#how-to-run-phase-9). The saga worker command is in [saga-pattern.md](saga-pattern.md). `deploy/compose/docker-compose.yml` has no saga-worker service.

### `services/reporting-service`

Django reporting service. `compose.yaml` starts only `reporting_db` on `127.0.0.1:5433`. Also present: `Dockerfile`, `pyproject.toml`, `manage.py`, `.env.example`, `.dockerignore`.

| Path | What it is |
| --- | --- |
| `reporting/` | Django project: `settings.py`, `urls.py`, `wsgi.py`, `asgi.py` |
| `projections/models.py` | Read models |
| `projections/management/commands/consume_events.py` | Consumer command |
| `projections/migrations/0001_initial.py` | Initial migration |
| `projections/tests/` | Apply, boundaries, consistency lag, observability, report auth |
| `tests/integration/test_reporting_pipeline.py` | Integration test |

This directory has no `README.md`. Host commands are in [How to run Phase 7](../README.md#how-to-run-phase-7).

### `services/notification-service`

Flask notification service. `compose.yaml` starts only `notification_db` on `127.0.0.1:5435`. Also present: `Dockerfile`, `pyproject.toml`, `alembic.ini`, `.dockerignore`, and [README.md](../services/notification-service/README.md).

| Path | What it is |
| --- | --- |
| `alembic/versions/20261009_0001_notification_tables.py` | Device tokens and deliveries |
| `src/notification_service/http.py` | HTTP process |
| `src/notification_service/consumer.py` | RabbitMQ consumer |
| `tests/` | Boundaries, delivery, devices, and `tests/integration/test_live.py` |

### `services/odoo`

Odoo 18 Community plus the `commerce_connector` addon and the Python workers. `compose.yaml` starts `odoo_db` on `127.0.0.1:5434` and Odoo on `127.0.0.1:8069`. Also present: `Dockerfile`, `pyproject.toml`, `config/odoo.conf`, `.env.example`, `.dockerignore`.

| Path | What it is |
| --- | --- |
| `addons/commerce_connector/` | `__manifest__.py`, `models/` (including `reservation.py` and `sale_order.py`), `security/ir.model.access.csv`, `views/` |
| `src/commerce_erp/` | `consumer.py`, `publisher.py`, `commands.py`, `confirmed.py`, `topology.py`, fulfillment and inventory modules |
| `tests/` | `test_commands.py`, `test_confirmed.py`, `test_consumer.py`, `test_fulfillment.py`, `test_inventory.py`, `test_publisher.py` |

This directory has no `README.md`. Host commands are in [How to run Phase 8](../README.md#how-to-run-phase-8).

### `services/frontend`

React and Vite storefront. Present: `package.json`, `package-lock.json`, `index.html`, `vite.config.ts`, `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json`, `Dockerfile`, `nginx.conf`, `.env.example`, `.dockerignore`, `.gitignore`.

`src/` holds `App.tsx`, `main.tsx`, `styles.css`, `api/`, `auth/`, `components/Chrome.tsx`, and `pages/` (`AuthPages.tsx`, `CatalogPages.tsx`, `CartPages.tsx`, `OrderPages.tsx`). This directory has no `README.md`. Host commands are in [How to run Phase 3](../README.md#how-to-run-phase-3).

## `mobile/react-native-app`

Community CLI project `CommerceApp`. [README.md](../mobile/react-native-app/README.md) records the commands run on this machine. Present at the app root: `package.json`, `package-lock.json`, `App.tsx`, `index.js`, `app.json`, `babel.config.js`, `metro.config.js`, `jest.config.js`, `tsconfig.json`, `Gemfile`, `.eslintrc.js`, `.prettierrc.js`, `.watchmanconfig`, `.gitignore`, `.bundle/config`.

| Path | What it is |
| --- | --- |
| `src/api/` | HTTP client and resources |
| `src/auth/` | Session and claims |
| `src/screens/` | Auth, catalog, cart, orders, notifications |
| `__tests__/` | `App.test.tsx`, `cart.test.ts`, `claims.test.ts` |
| `android/` | Android project from the CLI init |
| `ios/` | iOS project `CommerceApp` from the CLI init |

## `deploy`

### `deploy/compose`

Full stack file `docker-compose.yml`. Beside it: `up.sh`, `dynamic.yaml`, `.env.example`, `test_stack.py`. `up.sh` creates the JWT files and `.env` when they are missing, then runs Compose, and exits non-zero when Docker is down or Compose fails. The Compose file names four Postgres services (`postgres`, `reporting-postgres`, `notification-postgres`, `odoo-db`), RabbitMQ, Redis, the order, reporting, notification, and Odoo processes and their workers, `frontend`, `jwt-check`, `gateway`, and the observability services (`otel-collector`, `tempo`, `prometheus`, `alert-webhook`, `alertmanager`, `grafana`, and the Postgres and Redis exporters).

### `deploy/gateway`

`compose.yaml`, `compose.check.yaml`, `traefik.yaml`, `dynamic.yaml`, `jwt_check.py`, `live_check.py`, `echo_upstream.py`, `jwt-check/Dockerfile`, `tests/test_public_routes.py`, `tests/test_jwt_check.py`, and the Traefik plugin `plugins-local/src/github.com/commerce/edgeheaders/`.

### `deploy/kind`

`apply.sh`, `create-secrets.sh`, `kind-config.yaml`, `kustomization.yaml`, `test_manifests.py`, `secrets.example.yaml`, and the manifests `namespace.yaml`, `configmap.yaml`, `rbac.yaml`, `storage.yaml`, `postgres.yaml`, `rabbitmq.yaml`, `redis.yaml`, `order.yaml`, `reporting.yaml`, `notification.yaml`, `odoo.yaml`, `frontend.yaml`, `gateway.yaml`, `ingress.yaml`, `observability.yaml`, `metrics-server.yaml`, `retention.yaml`, `traefik-gateway.yaml`, `traefik-ingress.yaml`.

### `deploy/observability`

| Path | What it is |
| --- | --- |
| `prometheus/prometheus.yml`, `prometheus/alerts.yml` | Scrape and alert rules |
| `alertmanager/alertmanager.yml` | Alert routing |
| `grafana/dashboards/` | `dependencies.json`, `order-path.json`, `outbox-and-broker.json`, `payment.json`, `platform-overview.json`, `reporting-lag.json` |
| `grafana/provisioning/` | Datasource and dashboard providers |
| `otel/collector.yaml` | Collector |
| `tempo/tempo.yaml` | Trace store |
| `rabbitmq/enabled_plugins` | Broker plugins file |
| `webhook/hook.py` | Log webhook |

The write-up is [observability.md](observability.md).

### `deploy/failure-lab`

`lib.sh`, `rabbitmq.sh`, `redis.sh`, `reporting-consumer.sh`, `inventory-consumer.sh`, `test_lab.py`.

### `deploy/backup`

`lib.sh`, `dump.sh`, `restore.sh`, `test_backup.py`.

### `deploy/load`

`locustfile.py`, `scenario.py`, `test_scenario.py`, `RESULTS.md`.

## `docs`

Pages present on this walk:

`adr/` (`ADR-001` through `ADR-012`), `alerting.md`, `api.md`, `architecture.md`, `architecture-review.md`, `caching-strategy.md`, `consistency-models.md`, `current-architecture.md`, `database.md`, `deployment.md`, `disaster-recovery.md`, `docker.md`, `events.md`, `extension-gap-analysis.md`, `failure-scenarios.md`, `flask-notification-service.md`, `grafana.md`, `idempotency.md`, `kubernetes.md`, `learning-portal.md`, `load-balancing.md`, `observability.md`, `outbox.md`, `prometheus.md`, `rabbitmq.md`, `saga-pattern.md`, `security.md`, `services.md`, `system-architecture.html`, `testing.md`, `project-structure.md`, `run-the-project.md`.

`docs/system-architecture.html` is the bilingual learning portal. [learning-portal.md](learning-portal.md) explains language, the map, and the workflow tracer. The HTML file was not in the 9 October 2026 walk. It is in this directory now.

## Planned

The planned table is empty.

Extension Phase 9 extended the suites recorded in [testing.md](testing.md). It did not name a new path. Extension Phase 10 is cross-links to [rabbitmq.md](rabbitmq.md), [outbox.md](outbox.md), [kubernetes.md](kubernetes.md), [observability.md](observability.md), [testing.md](testing.md), and [security.md](security.md). It does not name a new path.
