# Commerce platform (learning project)

This repository is a learning project for a small commerce platform. It is designed with the same boundaries a production system would need. Phase 0 fixed the vocabulary. Phase 1 is the FastAPI order service in `services/order-service`: the domain, `order_db`, and the HTTP API. Phase 2 adds authentication and authorization on that service. Phase 3 is the React storefront in `services/frontend`. It calls the order service over HTTP. Phase 4 publishes domain events to RabbitMQ. Phase 5 makes the order service's inventory consumer idempotent and routes failed deliveries through retry queues into a dead-letter queue. Phase 6 writes each of those events into an outbox row in the same `order_db` transaction, and a separate publisher process sends pending rows to RabbitMQ. Django, Odoo, the gateway, and Kubernetes are not built yet.

Nothing here is production-ready. The order service can run against local Postgres and RabbitMQ containers. The storefront is a Vite dev server. The rest of the platform does not run.

## Learning goal

Build one system in which a customer can browse products and place an order, while three backends keep separate databases and stay aligned through events:

- The **order service** (FastAPI) is the only writer of order state.
- The **reporting service** (Django) builds read models for analytics.
- **Odoo** handles ERP work (sales, inventory, delivery, invoicing) and only learns about orders after they are confirmed.

You will practice why those boundaries exist, how they fail, and how to notice the failure. Later phases add code. This phase fixes the vocabulary so those phases do not invent a second design.

## Architecture snapshot

```mermaid
flowchart LR
  customer[Customer]
  react[React_SPA]
  gw[Traefik_gateway]
  orders[FastAPI_order_service]
  reports[Django_reporting]
  erp[Odoo_ERP]
  pay[Payment_provider]
  broker[RabbitMQ]
  cache[Redis]

  customer --> react
  react -->|HTTP_only| gw
  gw -->|orders_auth_catalog| orders
  gw -->|reports| reports
  orders -->|SQL_order_db| odb[(order_db)]
  orders -->|outbox_publish| broker
  orders -->|cache_and_limits| cache
  orders -->|circuit_breaker| pay
  reports -->|SQL_reporting_db| rdb[(reporting_db)]
  reports -->|consume| broker
  erp -->|SQL_odoo_db| edb[(odoo_db)]
  erp -->|confirmed_orders_and_inventory| broker
  broker --> orders
```

The browser talks only to HTTP APIs through the gateway. It never opens Postgres, RabbitMQ, Redis, or Odoo. Strong consistency stops at a single service database. Everywhere else, consistency is eventual.

Read the picture in detail in [docs/architecture.md](docs/architecture.md).

## How to read the docs

Read in this order. Later files assume the earlier decisions.

| Order | Document | What you should understand when you finish it |
| --- | --- | --- |
| 1 | [docs/architecture.md](docs/architecture.md) | Context, containers, state machine, communication, failure isolation |
| 2 | [docs/services.md](docs/services.md) | What each component owns, and what it must refuse to do |
| 3 | [docs/database.md](docs/database.md) | Which database is authoritative, and what a transaction may include |
| 4 | [docs/events.md](docs/events.md) | The event envelope and every event in the catalog |
| 5 | [docs/outbox.md](docs/outbox.md) | Why the order row and the message are written together |
| 6 | [docs/rabbitmq.md](docs/rabbitmq.md) | Exchanges, queues, retries, dead letters |
| 7 | [docs/idempotency.md](docs/idempotency.md) | Why consumers and POST endpoints must tolerate duplicates |
| 8 | [docs/api.md](docs/api.md) | The HTTP surface later phases will implement |
| 9 | [docs/security.md](docs/security.md) | JWT, roles, and what the gateway is allowed to trust |
| 10 | [docs/adr/](docs/adr/) | Why this stack was chosen, including the alternatives that lost |

Use the remaining docs when you reach the phase that implements them. They are design stubs: the decision is recorded, the software is not built.

- [docs/docker.md](docs/docker.md) — Compose first
- [docs/kubernetes.md](docs/kubernetes.md) — kind later
- [docs/observability.md](docs/observability.md), [docs/prometheus.md](docs/prometheus.md), [docs/grafana.md](docs/grafana.md), [docs/alerting.md](docs/alerting.md) — how we see failure
- [docs/testing.md](docs/testing.md) — what is worth testing before the cluster exists
- [docs/failure-scenarios.md](docs/failure-scenarios.md) — expected behavior when a dependency dies
- [docs/disaster-recovery.md](docs/disaster-recovery.md) — what must be restorable
- [docs/deployment.md](docs/deployment.md) — how a later phase should ship this

Most design docs are still marked **Phase 0 design; not implemented**. [docs/security.md](docs/security.md) and [docs/api.md](docs/api.md) note what Phase 2 implemented. [docs/rabbitmq.md](docs/rabbitmq.md) is the topology Phase 4 declares and Phase 5 uses for retries. The transactional outbox in that document is still Phase 6.

## Technology decisions (short)

| Concern | Choice |
| --- | --- |
| Storefront | React + TypeScript |
| Edge | Traefik |
| Orders and catalog writes | FastAPI, Clean Architecture; MVC only in HTTP adapters |
| Reporting | Django, own database, CQRS read model |
| ERP | Odoo, own database |
| Databases | PostgreSQL: `order_db`, `reporting_db`, `odoo_db` |
| Broker | RabbitMQ, topology `commerce-platform-topology` |
| Cache and shared rate limits | Redis, never the source of truth |
| Local runtime | Docker Compose, then kind |
| Metrics / dashboards / alerts / traces | Prometheus, Grafana, Alertmanager, OpenTelemetry |

The full table, including what we refused to add, is in [docs/architecture.md](docs/architecture.md). Trade-offs are in the ADRs.

## Phase plan

Phases 0 through 7 are done. Later phases are not started. This checklist is the authoritative order from the project specification. Some design notes still mention an earlier draft numbering (Compose-only as phase 1, observability as phase 17, kind as phase 18). When a sentence and this list disagree, follow this list. Kubernetes does not start before the system runs under Docker Compose.

- [x] **Phase 0 — Architecture.** Boundaries, events, state machine, communication matrix, ADRs. No application code.
- [x] **Phase 1 — FastAPI foundation.** Clean Architecture, MVC at the HTTP edge, PostgreSQL, SQLAlchemy, Alembic, domain model, order state machine, basic REST APIs, unit tests. See [How to run Phase 1](#how-to-run-phase-1).
- [x] **Phase 2 — Authentication.** Registration, login, JWT access and refresh, roles, authorization. See [How to run Phase 2](#how-to-run-phase-2).
- [x] **Phase 3 — React.** Login, products, cart, checkout, orders, order history. HTTP only. See [How to run Phase 3](#how-to-run-phase-3).
- [x] **Phase 4 — RabbitMQ.** Exchanges, queues, producers, consumers, routing keys, acknowledgements. See [How to run Phase 4](#how-to-run-phase-4).
- [x] **Phase 5 — Reliability.** Idempotency, retry, backoff, dead-letter queue, timeouts. See [How to run Phase 5](#how-to-run-phase-5).
- [x] **Phase 6 — Outbox.** Order and outbox event in one transaction, then the publisher. See [How to run Phase 6](#how-to-run-phase-6).
- [x] **Phase 7 — Django reporting.** Reporting database, consumers, read models, reports. See [How to run Phase 7](#how-to-run-phase-7).
- [ ] **Phase 8 — Odoo.** Confirmed-order integration, customers, products, inventory sync, failures.
- [ ] **Phase 9 — Redis.** Product cache, rate limiting, optional idempotency support.
- [ ] **Phase 10 — API gateway.** Traefik: routing, CORS, request IDs, authentication enforcement, rate limiting.
- [ ] **Phase 11 — Docker Compose.** The full local stack, after the applications already work.
- [ ] **Phase 12 — Observability.** Structured logs, Prometheus, Grafana, Alertmanager, OpenTelemetry.
- [ ] **Phase 13 — Kubernetes.** kind, after Compose. Namespace, deployments, services, ConfigMaps, Secrets, PVCs, Ingress, probes.
- [ ] **Phase 14 — Scaling.** FastAPI replicas, competing consumers, HPA, queue-backlog monitoring.
- [ ] **Phase 15 — CronJobs.** Retention, batched cleanup.
- [ ] **Phase 16 — CI/CD.** Lint, tests, security scans, image build and scan.
- [ ] **Phase 17 — Load testing.** Product browse, order create, order read.
- [ ] **Phase 18 — Failure lab.** Break RabbitMQ, PostgreSQL, Redis, Django, Odoo, and FastAPI pods on purpose.
- [ ] **Phase 19 — Disaster recovery.** Backup, restore, persistent volume recovery. RTO and RPO.
- [ ] **Phase 20 — Architecture review.** What would still have to change for a real production system.

## How to run Phase 1

From `services/order-service`:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
docker compose up -d
alembic upgrade head
uvicorn order_service.presentation.app:app --app-dir src --port 8000
```

Open `http://127.0.0.1:8000/docs` for the generated OpenAPI document. `GET /health/live` answers even when Postgres is down. `GET /health/ready` answers only when `order_db` accepts a query.

```bash
pytest
```

Unit and API tests use an in-memory unit of work. The Postgres tests in `tests/integration` run when the Compose database is up and skip when it is not.

The database password in `compose.yaml` is a local placeholder bound to `127.0.0.1`. It is not a credential for any shared environment.

## How to run Phase 2

Start the service the same way as Phase 1 (`alembic upgrade head` applies the accounts revision). Then create a local RS256 key pair outside git. `*.pem` is gitignored.

```bash
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out jwt_private.pem
openssl rsa -in jwt_private.pem -pubout -out jwt_public.pem
```

Point the process at those files (or paste the PEM text into `JWT_PRIVATE_KEY_PEM` and `JWT_PUBLIC_KEY_PEM`). Names are listed empty in `.env.example`.

```bash
export JWT_PRIVATE_KEY_PATH=jwt_private.pem
export JWT_PUBLIC_KEY_PATH=jwt_public.pem
export INTERNAL_SERVICE_TOKEN=local-dev-only
uvicorn order_service.presentation.app:app --app-dir src --port 8000
```

Register a customer. The server sets the role to `customer`. A `role` field in the body is ignored.

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H 'content-type: application/json' \
  -d '{"email":"ada@example.com","display_name":"Ada","password":"choose-a-password"}'
```

Send the access token on later calls: `Authorization: Bearer <access_token>`. Refresh with `POST /api/v1/auth/refresh` and the refresh token in the JSON body. Logout with `POST /api/v1/auth/logout` revokes that refresh token.

Staff are not created by register. From `services/order-service`, with the database migrated:

```bash
SEED_ADMIN_EMAIL=admin@example.com SEED_ADMIN_PASSWORD='choose-a-password' \
  python -m order_service.infrastructure.seed_staff
```

`SEED_MANAGER_EMAIL` and `SEED_MANAGER_PASSWORD` follow the same rule. If the email already exists, the seed skips it. The password is not printed.

`POST /api/v1/orders` takes the customer from the access token. Internal fulfillment (`/api/v1/internal/orders/...`) needs `X-Internal-Token` equal to `INTERNAL_SERVICE_TOKEN`. If that variable is empty, those routes return 503.

## How to run Phase 3

Two processes. The storefront does not open Postgres, RabbitMQ, Redis, or Odoo. Start the order service the same way as [Phase 2](#how-to-run-phase-2), including the JWT key pair and `alembic upgrade head`. Then, in another terminal, from `services/frontend`:

```bash
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. `VITE_API_BASE_URL` defaults to `http://127.0.0.1:8000` (see `services/frontend/.env.example`). Register a customer in the browser, or sign in with an account you already created.

The browser calls the order service directly. That is a shortcut until Phase 10, when Traefik is the only public front door. It is not a second architecture: the same `/api/v1` routes, the same tokens, and the same rule that the client does not choose prices, totals, `customer_id`, or roles.

Vite (`http://127.0.0.1:5173` and `http://localhost:5173`) is a different origin from the API, so the order service allows those two origins in CORS middleware. That middleware is temporary. Traefik replaces it in Phase 10. The allowlist is not `*`. A matching `Origin` does not skip authentication.

The access token stays in memory. The refresh token is also written to `sessionStorage` so a reload of this tab can call `POST /api/v1/auth/refresh`. Production would use an httpOnly cookie set by the server. `sessionStorage` is readable by any script on the page, which is the same exposure as `localStorage`.

There is no cart API. The cart lives in React state and `sessionStorage`. Checkout sends `POST /api/v1/orders` with product ids and quantities. The server prices the lines and stores the order. The number on the cart page is an estimate.

`POST /api/v1/products` is admin-only. The new-product form is shown only when the access token payload says `admin`. The browser does not verify the signature; the API does. Seed an admin with the Phase 2 command if you want that form. Customers can browse, check out, confirm, cancel a pending order, and read their own history.

```bash
cd services/frontend
npm test
npm run build
```

## How to run Phase 4

RabbitMQ is the second service in `services/order-service/compose.yaml`. This is still not the full platform Compose file. From `services/order-service`, with the virtualenv from Phase 1:

```bash
docker compose up -d
pip install -e ".[dev]"
```

AMQP is published on `127.0.0.1:5672` only. The management UI is [http://127.0.0.1:15672](http://127.0.0.1:15672) (user `order_service`, password `order_service`). Those values are local placeholders, the same kind as the Postgres password in that file. They are not credentials for a shared environment.

Start the API the same way as [Phase 2](#how-to-run-phase-2). The API writes an outbox row in that same commit. The outbox publisher, not the request, sends the stored envelope to the topic exchange `commerce.events`. See [How to run Phase 6](#how-to-run-phase-6). The routing keys in use are:

| Event | Routing key |
| --- | --- |
| `OrderCreated` | `order.created` |
| `OrderConfirmed` | `order.confirmed` |
| `OrderCancelled` | `order.cancelled` |
| `OrderProcessingStarted` | `order.processing-started` |
| `OrderShipped` | `order.shipped` |
| `OrderDelivered` | `order.delivered` |
| `ProductCreated` | `product.created` |
| `ProductUpdated` | `product.updated` |
| `CustomerUpdated` | `customer.updated` |

The producer names the exchange and the routing key. It does not name a queue. Queues belong to consumers. `q.reporting.projection` is bound to `order.*`, `product.*`, `customer.*`, and `payment.*` on `commerce.events` (and to `inventory.updated` on `erp.events`). `q.odoo.order-confirmed` is bound only to `order.confirmed`, so a pending order never lands there. Adding another consumer is a new binding, not a new release of the order service.

A publisher confirm is the broker's ack that it accepted the publish onto the exchange. It is not a consumer ack. The consumer acks only after its handler returns. Until that ack, the broker can redeliver the message. Phase 4 runs one consumer. Prefetch is 10, the starting value in [docs/rabbitmq.md](docs/rabbitmq.md), so that process is not handed an unbounded number of unacked messages.

Create an order through the API or the storefront, with the publisher running. The event is on `q.reporting.projection` until something acks it. An `OrderCreated` message does not appear on `q.odoo.order-confirmed`. Payloads are not logged, because `CustomerUpdated` contains an email.

Phase 4 stopped at a nack with `requeue` false, which dropped the message. Phase 5 does not do that. The checked-in consumer listens on `q.order.inventory`. See [How to run Phase 5](#how-to-run-phase-5). Order events arrive on `q.reporting.projection`. The Phase 7 reporting worker consumes that queue.

Phase 4 published on the request, after the commit, and that confirm was bounded by `RABBITMQ_TIMEOUT_SECONDS` (default 5). That path is gone. The failure it left open, and the outbox that closes it, are in [How to run Phase 6](#how-to-run-phase-6).

```bash
pytest
ruff check
```

The RabbitMQ integration test skips when the broker is not reachable, so `pytest` stays green without Docker.

## How to run Phase 5

Start Postgres and RabbitMQ the same way as [Phase 4](#how-to-run-phase-4), then apply the new revision. From `services/order-service`:

```bash
alembic upgrade head
python -m order_service.infrastructure.messaging.consumer
```

That process is the order-service inventory worker. It consumes `q.order.inventory`, which is bound to `inventory.updated` on `erp.events`. It does not own `q.reporting.projection`. That queue is for the reporting service. One consumer, prefetch 10. Connect, declare, publisher confirms, the consumer's idle wait, and database calls on this path all stop at a timeout (`RABBITMQ_TIMEOUT_SECONDS`, default 5; `DB_CONNECT_TIMEOUT_SECONDS` and `DB_STATEMENT_TIMEOUT_MS` for Postgres). Shutdown stops new deliveries, finishes the one already in the callback, then closes the channel and the connection.

### Main queue, retry, dead letter

A handler failure is not put back on the same queue. `requeue=true` would deliver a poison message again immediately, fill the prefetch window with that message, and burn CPU until someone deletes the queue. The worker also does not `nack` with `requeue=false` on the main queue: those queues have no dead-letter argument, so that nack drops the message, and a nack cannot attach the attempt number.

What happens instead:

1. The worker publishes the same body to the exchange `commerce.retry` with routing key `order.inventory.retry.{attempt}` and header `x-retry-count`, and waits for a broker confirm.
2. It then acks the original delivery.
3. The retry queue holds the message for that attempt's TTL, then dead-letters it to `erp.events`. `q.order.inventory` is bound to those retry keys, so the message comes back to the main queue.
4. After five delayed retries the next failure is published to `commerce.dlx` with routing key `order.inventory`, which lands on `q.order.inventory.dlq`. Nothing consumes a dead-letter queue.

Backoff, from [docs/rabbitmq.md](docs/rabbitmq.md):

| Failure | Where it goes | Delay |
| --- | --- | --- |
| 1 | `q.order.inventory.retry.1` | 5 seconds |
| 2 | `q.order.inventory.retry.2` | 30 seconds |
| 3 | `q.order.inventory.retry.3` | 2 minutes |
| 4 | `q.order.inventory.retry.4` | 10 minutes |
| 5 | `q.order.inventory.retry.5` | 30 minutes |
| 6 | `q.order.inventory.dlq` | no further automatic retry |

The same ladder exists for `q.reporting.projection` and `q.odoo.order-confirmed`. This process only runs the inventory one.

**Transient** failures take that ladder: the handler returns a transient outcome, or it raises (a database timeout, a connection reset). **Permanent** failures go to the dead-letter queue on the first attempt. Retrying them cannot succeed. Those are a body that is not a JSON object, an `event_id` or `aggregate_id` that is not a UUID, a schema `version` other than 1, an event type this consumer does not handle (`InventoryUpdated` only), and an `InventoryUpdated` payload that breaks the schema (missing fields, a non-integer quantity, a non-positive `aggregate_version`). An older snapshot is not a failure. It is acked and ignored.

### Why event_id is stored

Delivery is at least once. The broker can redeliver after the consumer has committed and before it has acked, and a publisher can send the same `event_id` more than once. RabbitMQ does not dedupe. The inventory worker inserts `event_id` into `order_db.processed_events` (`event_id` primary key, `event_type`, `aggregate_id`, `processed_at`, `consumer_name`) in the same transaction as the `inventory_snapshots` write, then acks. A duplicate insert conflicts, the transaction commits nothing else, and the delivery is acked. The snapshot is not applied twice. A crash before commit leaves no row, so the redelivery tries again.

`inventory_snapshots` stores the last snapshot per product. The row changes only when `aggregate_version` is newer than `source_version`. Odoo is still the stock authority. This service does not write `reporting_db` or `odoo_db`.

If the AMQP `message_id` or `type` property disagrees with the JSON body, the body wins.

Consumer retries do not close the hole Phase 4 left on the way out of the service. That hole, and the outbox that closes it, are in [How to run Phase 6](#how-to-run-phase-6). A green HTTP response is still not proof that this inventory worker, reporting, or Odoo has already applied the fact. It is proof the fact is in `order_db`, including the outbox row.

```bash
pytest
ruff check
```

The RabbitMQ retry test skips when the broker or Postgres is down. It waits through the 5-second and 30-second backoff, so a full run with Docker takes about a minute longer. `pytest` stays green without Docker.

## What Phase 1 deliberately leaves out

Phase 1 had no JWT. Phase 2 added it. Phase 3 adds the React storefront. Phase 4 publishes domain events. Phase 5 retries and dedupes consumption. Phase 6 stores those events in the outbox. Still no gateway, no Redis, no Django, no Odoo, and no cluster. `saga_status` stays null.

## What Phase 2 deliberately leaves out

No Redis rate limits and no idempotency keys. The outbox is Phase 6. Access tokens are not denylisted; logout revokes the refresh token only. Refresh-token family revocation after theft, key storage in a KMS, and gateway verification are later work. The internal fulfillment check is a shared header, not mTLS.

## What Phase 3 deliberately leaves out

No gateway, so no Traefik routing, rate limit, or public CORS policy. The temporary allowlist on the order service is only for the Vite dev server. No RabbitMQ, outbox, Redis, Django, Odoo, Compose for the full stack, or Kubernetes. `saga_status` is still null; the order page renders it when the API sends a non-null value. `docs/api.md` lists `Idempotency-Key` on order writes. The service does not enforce that header yet, so the storefront does not send one.

## What Phase 4 deliberately leaves out

Phase 4 had no idempotency store, no retry loop, and no dead-letter path. A handler that raised was nacked without requeue, and the message was dropped. Phase 5 routes that failure through the retry queues. Publish-after-commit could still lose an event; Phase 6 closes that hole with the outbox. No Django projection and no Odoo client. No Redis, Traefik, Kubernetes, or the full platform Compose file. One consumer, prefetch 10. Competing consumers are a later phase. `PaymentConfirmed` and `PaymentFailed` are in the catalog and on the bindings. This service does not emit them. `saga_status` stays null.

## What Phase 5 deliberately leaves out

No Django projection, so `q.reporting.projection` is declared and bound but this process does not apply those events. No Odoo client and no stock authority in this service: `inventory_snapshots` is a copy of `InventoryUpdated`, applied only when the version is newer. No HTTP idempotency keys, no Redis, no gateway, and no Kubernetes. Nothing consumes a dead-letter queue; a person replays or discards those messages later. `saga_status` stays null. The outbox is Phase 6.

## How to run Phase 6

Start Postgres and RabbitMQ the same way as [Phase 4](#how-to-run-phase-4), and apply the new revision. From `services/order-service`:

```bash
alembic upgrade head
```

Run three processes. The API and the inventory consumer are unchanged in how you start them. The new one is the outbox publisher:

```bash
uvicorn order_service.presentation.app:app --app-dir src --port 8000
python -m order_service.infrastructure.messaging.consumer
python -m order_service.infrastructure.messaging.outbox_publisher
```

The API writes the order, product, or customer row and one outbox row per domain event, then commits, then returns the resource. Those two writes are one `order_db` transaction. If the business write rolls back, the outbox row rolls back with it. The handler does not open RabbitMQ. A broker outage does not fail the sale and does not hold the request. Pending rows are the signal that publishing is behind.

### The hole Phase 4 left open

Phase 4 published after `commit`. Two failures lose the fact:

- The process dies after the commit and before the broker confirm.
- RabbitMQ rejects the publish, or it is down for that one attempt.

The HTTP response is still the order that was committed. Confirming again does not emit the event again: the state machine returns 409. The event was not stored anywhere else.

The outbox closes that hole by storing the full envelope in `outbox.payload` before the commit. The publisher sends that stored JSON. It does not read the order again and build a new payload. The outbox `id` is the envelope `event_id`. A crash after the broker accepts the message and before `published_at` is set sends the same `event_id` again. Consumers already dedupe on `event_id`, so that republish is the same fact, not a second one.

This is still one service and one database. Postgres and RabbitMQ do not share a transaction. There is no two-phase commit. Other services see the fact after the publisher's confirm, which can be later than the HTTP response. A green response means the order and the outbox row are committed. It does not mean reporting or Odoo has applied them.

### Publisher

The publisher claims a batch of `pending` rows with `SELECT ... FOR UPDATE SKIP LOCKED`, ordered by `created_at`, then `id`. It publishes each stored envelope to `commerce.events` with the same routing keys as Phase 4, `mandatory`, and publisher confirms. Connect, declare, and the confirm each stop after `RABBITMQ_TIMEOUT_SECONDS` (default 5).

On confirm it sets `status` to `published` and sets `published_at` in that same short transaction. `retry_count` stays as it was. On failure it increments `retry_count` and leaves `status` as `pending`, so the next poll tries again. It does not roll the order back.

`OUTBOX_POLL_INTERVAL_SECONDS` defaults to 1. `OUTBOX_BATCH_SIZE` defaults to 100. `OUTBOX_MAX_ATTEMPTS` defaults to 5, the same count as the consumer retry budget. After that many failed confirms the row becomes `status=failed` and the publisher stops claiming it. Logs include `event_id`, `event_type`, and `correlation_id`. They do not include the payload, because `CustomerUpdated` contains an email.

Shutdown finishes the batch already claimed, does not claim another, and closes the broker connection. One publisher is the learning default. `SKIP LOCKED` is there so a second publisher takes a different batch instead of the same rows. It does not promise a global order across those publishers. Consumers still use `aggregate_version`.

To retry a `failed` row, set `status` back to `pending` and `retry_count` back to 0, and record why. Do not delete the row to silence it.

### Failed outbox row versus a consumer DLQ message

These are different failures.

- **`outbox.status = failed`.** The publisher never got a broker confirm. The message may never have reached a queue. The order in `order_db` is unchanged. A person fixes the broker or the payload and sets the row back to `pending`. This is not `q.order.inventory.dlq`.
- **A dead-letter queue message.** The broker accepted the publish, so the outbox row can already be `published`. A consumer then failed to apply the delivery, or used up the retry ladder. Phase 5 describes that path. Nothing in this phase consumes a DLQ. Republishing from the outbox would send the same `event_id`, which a consumer that already processed it will ack as a duplicate.

```bash
pytest
ruff check
```

The Postgres and RabbitMQ integration test skips when either is down, so `pytest` stays green without Docker. If port 5432 is already taken and this project's `order_db` is not reachable, that test skips rather than failing the suite.

## What Phase 6 deliberately leaves out

No Django projection and no Odoo client. No Redis, Traefik, React changes, Kubernetes, or the full platform Compose file. No distributed transaction: the outbox is a row in `order_db`, and RabbitMQ is a later confirm. No outbox age metrics yet. `saga_status` stays null. `PaymentConfirmed` and `PaymentFailed` are still not emitted. The inventory consumer, its retry ladder, and `processed_events` are unchanged.

## How to run Phase 7

The reporting service is `services/reporting-service`. It is a Django project with its own database, `reporting_db`, on host port **5433**. That port is not 5432, so it does not collide with `order_db`. The Compose file next to the service starts only that Postgres. It does not start RabbitMQ, Redis, Odoo, or Traefik, and it is not the full platform Compose file.

The database user is `reporting_service`. The password in `compose.yaml` and `.env.example` is the local placeholder `reporting_service`. This Postgres server has no `order_db` and no `odoo_db`. Django settings refuse a DSN whose database name is either of those. There is no private key setting. Copy the order service **public** key path into `JWT_PUBLIC_KEY_PATH`.

RabbitMQ is still the broker from `services/order-service/compose.yaml` (`127.0.0.1:5672`, user and password `order_service`).

From `services/reporting-service`:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
docker compose up -d
python manage.py migrate
```

`migrate` applies Django migrations to `reporting_db` only.

Run the consumer and the report HTTP server in two processes:

```bash
python manage.py consume_events
python manage.py runserver 127.0.0.1:8001
```

The consumer listens on `q.reporting.projection` with prefetch 10 and manual ack. It applies `OrderCreated`, `OrderConfirmed`, `OrderCancelled`, `OrderProcessingStarted`, `OrderShipped`, `OrderDelivered`, `ProductCreated`, `ProductUpdated`, `CustomerUpdated`, `InventoryUpdated`, `PaymentConfirmed`, and `PaymentFailed`. Connect, declare, and broker confirms stop after `RABBITMQ_TIMEOUT_SECONDS` (default 5). Database connect and statement timeouts are `DB_CONNECT_TIMEOUT_SECONDS` (default 5) and `DB_STATEMENT_TIMEOUT_MS` (default 10000). Shutdown stops new deliveries, finishes the callback already in hand or leaves that message unacked, then closes the connection. It does not use `requeue=true`.

A version gap on an order stream (the next `aggregate_version` is not the stored version plus one, including a payment fact on that order) is published to `commerce.retry` and then acked. Five delays use the same TTLs as the inventory worker. The sixth failure is published to `commerce.dlx` with routing key `reporting.projection`, which lands on `q.reporting.projection.dlq`. An unknown `event_type` or a schema `version` other than 1 is dead-lettered on the first delivery, after a log line that has ids and not the payload. A duplicate `event_id` is acked and does not change the projection. The `processed_events` insert and the projection write are one transaction. Product, customer, and inventory events are snapshots: a newer `aggregate_version` replaces the row, and an older one is acked and ignored.

Log in as admin or manager on the order service (port 8000) and call the report with that access token. The storefront does not call these routes yet. There is no gateway yet, so this request goes to Django directly:

```bash
curl -H "Authorization: Bearer $ACCESS_TOKEN" http://127.0.0.1:8001/api/v1/reports/orders/summary
```

The other routes are `GET /api/v1/reports/orders`, `GET /api/v1/reports/inventory`, and `GET /api/v1/reports/revenue`. Each JSON body includes `as_of`, the timestamp of the newest event applied for that projection, or null when nothing has been applied. A missing or invalid token is 401. A customer token is 403. The error body is `{"error": {"code", "message", "correlation_id", "details"}}`.

### Eventual consistency

A confirmed order can exist in `order_db` before any report shows it. The order service commits the order and the outbox row, returns HTTP success, and only then does the publisher send the stored envelope to RabbitMQ. Django applies that message in `reporting_db` when the consumer commits. Until that happens, the report still shows the previous projection. `as_of` is how a reader sees that lag.

The report must not query `order_db`. A dashboard query on the order tables would sit on the same database checkout writes, so a slow report or a Django migration could stall a sale. The projection is the copy this service is allowed to read. If a figure is wrong, fix the projection or replay the event. Django does not emit a correcting domain event, and it does not grow a second order state machine.

```bash
pytest
ruff check
```

The integration test skips when reporting Postgres or RabbitMQ is down, so `pytest` stays green without Docker. If port 5432 is taken by something else, that does not matter here: reporting Postgres is on 5433. The order-service suite is unchanged and still skips its own Docker tests when `order_db` or the broker is down.

## What Phase 7 deliberately leaves out

No Odoo client, no Redis, no Traefik, no Kubernetes, and no full platform Compose file. No Grafana dashboards. Django does not publish domain events and does not issue access tokens. One reporting database on the laptop is enough for this phase. Production would put `reporting_db` on a network the order service cannot reach, so a wrong setting still could not open `order_db`. JWT verification here is the service's own check. The gateway will repeat it later. A role claim is ignored when the signature does not verify.
