# Services and components

**Status: Phase 0 design; not implemented.**

Each component exists because a responsibility has a clear owner. If a responsibility is missing from this list, do not invent a microservice for it. Put it in the owner below, or stop and write an ADR.

Names are the ones later Compose services and Kubernetes Deployments should use.

## React storefront (`frontend`)

**Why it exists.** Customers and staff need a browser UI to browse products, sign in, place orders, and open reports.

**Responsibilities.**

- Render catalog, cart, checkout, order status, and report screens.
- Call only the gateway over HTTP.
- Send the access token. Refresh it through the auth endpoints when it expires.
- Show both `status` and `saga_status` after confirmation so a compensated order is not presented as a healthy one.

**Must not.**

- Open Postgres, RabbitMQ, Redis, or Odoo.
- Decide that a state transition is legal. The server can reject it.
- Send a role, a price, or an order total and expect the server to believe it.
- Talk to FastAPI or Django by a private address that bypasses the gateway.

**Failure.** If the API is down, the UI shows an error and can retry a safe read. Creating an order uses an idempotency key so a retry does not create two orders. Detection is the browser error plus gateway 5xx metrics. Recovery is a retry against a healthy API, not a local database.

**Scale.** The SPA is static files. Scale the file host, not the number of API rules inside the client.

> **Learning simplification.** The SPA is served from a container behind Traefik on a local origin, over HTTP.
> **Production would require.** A CDN, TLS, and a locked CORS origin list.

## Traefik (`gateway`)

**Why it exists.** One front door for routing, CORS, correlation IDs, coarse rate limits, and JWT checks. Business rules stay behind it.

**Responsibilities.**

- Route `/api/v1/reports` to the reporting service.
- Route other `/api/v1` traffic to the order service.
- Route `/` to the frontend.
- Generate or forward `X-Correlation-Id` (UUID).
- Strip client-supplied identity headers (`X-User-Id`, `X-User-Role`, and anything similar) and set them only from a validated token.
- CORS for the storefront origin.
- A coarse anonymous rate limit per client IP.
- Access logs that include the correlation ID and the upstream status.

**Must not.**

- Contain order, price, stock, or role policy.
- Publish or consume RabbitMQ messages.
- Connect to Postgres.
- Expose internal fulfillment routes, metrics, or database ports.

**Failure.** If Traefik is down, public traffic stops. Data stores are unchanged. Detection: an external probe, or the absence of gateway metrics. Recovery: restart the process. No replay is required.

**Scale.** More replicas scale throughput. The built-in rate limit is per process, so it is a coarse shield, not a global budget. Shared budgets for login and order creation live in the order service with Redis.

See [ADR-012](adr/ADR-012-why-api-gateway.md) and [security.md](security.md).

## Order service (`order-service`)

**Why it exists.** Something must be the single writer for customers, the storefront catalog, and orders. That something is this service. It is a FastAPI application structured as Clean Architecture. MVC exists only in the HTTP adapters: a route function receives a request, calls a use case, and maps the result to a response. The framework model is not the domain model.

**Why FastAPI.** [ADR-001](adr/ADR-001-why-fastapi.md).

**Responsibilities.**

- Accounts and roles: Customer, Admin, Manager. Passwords hashed. JWT access and refresh issued here.
- Customer profiles and the product catalog (SKU, name, price, active flag).
- Orders and order lines. Prices are copied onto the line at creation.
- The order state machine, enforced in the domain.
- `InventorySnapshot`, a projection of Odoo stock, never the warehouse authority.
- The saga row for a confirmed order (Phase 15), in `order_db`.
- The transactional outbox.
- The processed-event store for messages this service consumes (`InventoryUpdated`).
- HTTP idempotency keys for unsafe order endpoints.
- The payment HTTP client and its circuit breaker.
- Publishing domain events after commit.
- Private HTTP commands that apply `PROCESSING`, `SHIPPED`, and `DELIVERED` after the domain agrees.

**Must not.**

- Read or write `reporting_db` or `odoo_db`.
- Let a router implement a transition the domain would refuse.
- Treat Redis as durable storage.
- Call Django to "update the report" inside the order transaction.
- Call Odoo synchronously during create or confirm.
- Expose Odoo models to the browser.

**Interactions.** SQL to `order_db`. Redis for cache and shared rate limits. AMQP publish to `commerce.events`. AMQP consume of `inventory.updated` from `erp.events`. HTTPS to the payment provider. Private HTTP from the Odoo module for fulfillment milestones.

**Failure.** If this service is down, checkout is down. Reports still answer from `reporting_db`. Confirmed facts already published can still be consumed. Detection: readiness probe (database required; broker required for the publisher process), gateway 502, outbox age if only the publisher is sick. Recovery: restart. Unpublished outbox rows drain. In-flight HTTP calls that the client retries are safe when the idempotency key was stored in the same transaction as the order.

**Scale.** API replicas share `order_db` and Redis. The outbox publisher starts as one process so publish order follows `created_at`. A later scale-out partitions by `aggregate_id` and uses `FOR UPDATE SKIP LOCKED`. See [outbox.md](outbox.md).

### Layers inside the order service

| Layer | Holds | Depends on |
| --- | --- | --- |
| Domain | Entities, value objects, state machine, domain errors | Nothing framework-shaped |
| Application | Use cases, ports (repository, clock, publisher claim, payment port) | Domain |
| Infrastructure | SQLAlchemy (or equivalent) repositories, Alembic, RabbitMQ publisher, Redis, payment adapter | Application ports |
| Presentation | FastAPI routers, request and response models | Application use cases |

Dependency direction is inward. A domain test from Phase 3 must run without a database and without FastAPI.

Value objects:

| Type | Rule |
| --- | --- |
| `Money` | Integer minor units plus an ISO 4217 currency. No binary floats. |
| `Quantity` | Integer. Order lines require a quantity greater than zero. Snapshots may be zero. |
| `OrderId`, `ProductId`, `CustomerId` | UUID wrappers. Callers do not pass raw strings into the domain without parsing. |

Aggregates and entities:

| Type | System of record | Notes |
| --- | --- | --- |
| Customer | This service | Profile fields that are safe to publish. No password in events. |
| Product | This service | Storefront catalog. The price on an order line is a copy. |
| Order | This service | Status follows the state machine only. |
| OrderItem | Part of Order | Not a separate aggregate. No events of its own. |
| InventorySnapshot | Odoo is the authority; this row is a projection | Updated only from `InventoryUpdated`. |

## Reporting service (`reporting-service`)

Phase 7 implements this service: Django, `reporting_db`, the consumer on `q.reporting.projection`, and the report routes. It does not open `order_db`.

**Why it exists.** Operations and managers need totals, lists, and stock pictures that must not run inside the order transaction. Django is the read model. [ADR-002](adr/ADR-002-why-django-for-reporting.md).

**Responsibilities.**

- Consume the event catalog and maintain projections in `reporting_db`.
- Serve `/api/v1/reports/...` over HTTP.
- Store processed event IDs in `reporting_db`, in the same transaction as the projection write.
- Ignore an event whose aggregate version is older than what is already stored when the payload is a snapshot. Defer, by retry, a transition event that skips a version.

**Must not.**

- Create, confirm, or cancel orders.
- Connect to `order_db` or `odoo_db`, including foreign data wrappers and "read-only" users.
- Publish domain events. If a figure is wrong, fix the projection, do not emit a second fact.
- Become the place where the state machine is reimplemented with different edges.

**Failure.** Checkout still works. Dashboards stop moving or return errors. Detection: consumer lag, HTTP errors on report routes, a projection version behind the order service. Recovery: fix the consumer, then drain the queue. If the database is rebuilt empty, replay is only possible for messages still in the broker, so a later phase needs a rebuild path (republish or a snapshot export). Phase 0 records that need; it does not build it.

**Scale.** Competing consumers on `q.reporting.projection` once version checks exist. Report HTTP replicas scale reads. They do not each need a private copy of the queue.

## Odoo (`odoo`)

**Why it exists.** Sales orders, stock, pickings, and invoices already have a transactional home in an ERP. Rebuilding that poorly beside FastAPI would split stock from invoicing.

**Responsibilities.**

- Own warehouse quantities in `odoo_db`.
- Consume `OrderConfirmed` only, and create the ERP sales order from that payload.
- Publish `InventoryUpdated` as a full snapshot when stock changes.
- Call the order service's private fulfillment routes when processing starts, when the goods ship, and when they are delivered.
- Consume saga commands (`reserve`, `release`, `create sales order`, `cancel sales order`) when Phase 15 adds them.
- Keep a processed-event table, in `odoo_db`, for message IDs it has applied.

**Must not.**

- Receive `OrderCreated` or otherwise learn about `PENDING` orders. Those are not ERP documents.
- Write `order_db` or `reporting_db`.
- Publish `OrderShipped` or any other order-status event. It asks the order service to apply the transition. The order service publishes the fact after the domain accepts it.
- Depend on Django.

**Failure.** Confirm still succeeds. `q.odoo.order-confirmed` grows. Inventory snapshots go stale, so the catalog guard becomes less accurate, and the saga's reserve step waits or retries. Detection: queue depth, snapshot age, Odoo logs. Recovery: restore Odoo, let consumers drain, retry commands. Messages are idempotent on `event_id` and on the commerce order id stored on the Odoo sales order.

**Scale.** Use Odoo's workers. The connector is an Odoo module deployed with Odoo, not a new microservice. A separate connector would need its own database or would cheat and share `odoo_db`.

> **Learning simplification.** One Odoo database named `odoo_db`, one custom module, Community edition, version pinned only when the image is introduced.
> **Production would require.** A pinned Odoo version, a tested module upgrade path, filestore backups beside `odoo_db`, and a private network path for the fulfillment callback.

## PostgreSQL (`postgres` locally)

**Why it exists.** Each service needs a transactional store. Postgres is the store for all three. Ownership rules are in [database.md](database.md).

**Must not.** Host a shared `public` schema that all services migrate. The local server is one process only as a laptop shortcut.

## RabbitMQ (`rabbitmq`)

**Why it exists.** Confirmed orders, catalog facts, payment facts, and stock snapshots must reach other processes after the writer's transaction commits, and must survive a consumer being down. [ADR-003](adr/ADR-003-why-rabbitmq.md). Topology: [rabbitmq.md](rabbitmq.md).

**Must not.** Be the source of truth for an order. The database is. The broker can lose a node in this learning setup; the outbox is how we publish again.

## Redis (`redis`)

**Why it exists.** Product reads are frequent and rebuildable. Login and order-create limits must be shared across API replicas. [ADR-007](adr/ADR-007-why-redis.md).

**Responsibilities.** Cache product documents with a TTL. Store rate-limit counters for login and order creation.

**Must not.** Store orders, outbox rows, refresh tokens, idempotency keys, or processed event IDs. Those are durable and belong in Postgres. If Redis disappears, the next read uses `order_db`, and auth limits fail closed until Redis returns (the endpoint answers 503 rather than becoming unlimited).

## Payment provider (external)

**Why it is on the diagram.** The saga has a payment step. We do not operate a payment service.

**Interaction.** The order service calls it synchronously through the circuit breaker. Outcomes are recorded as `PaymentConfirmed` or `PaymentFailed` in `order_db` and then published by the outbox. The provider never writes our broker or our tables.

## Observability components

| Name | Why it exists | Must not |
| --- | --- | --- |
| `otel-collector` | Receive traces and forward them | Become a business database |
| `prometheus` | Scrape and store metrics | Page a human by itself |
| `alertmanager` | Route alerts from Prometheus rules | Decide business transitions |
| `grafana` | Dashboards and trace lookup for humans | Be a second Alertmanager |

They are not on the request path for checkout. If Grafana is down, orders still flow. If Prometheus is down, we fly blind until it returns; the business data is unchanged. See [observability.md](observability.md).

## Responsibility matrix

| Capability | Owner | Everyone else |
| --- | --- | --- |
| Order status | Order service domain | May request a legal transition; may not write the row |
| Catalog price | Order service | Order lines store a copy; reports copy the event |
| Warehouse stock | Odoo | Others store snapshots from events |
| Report queries | Reporting service | Do not scan `order_db` to answer them |
| JWT issuance | Order service | Gateway and reporting verify; they do not issue |
| Correlation ID at the edge | Traefik | Services propagate |
| Payment charge | Payment provider, called by the order service | No other caller |

## Related documents

- [architecture.md](architecture.md)
- [database.md](database.md)
- [api.md](api.md)
- [security.md](security.md)
