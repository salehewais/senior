# HTTP API

**Status: Phase 2 authenticates the order-service routes below. Phase 7 serves the report routes from the reporting service. Phase 9 rate-limits login, register, and order create in Redis. Phase 10 publishes `/api/v1` through Traefik and does not route `/api/v1/internal`.** Durable idempotency keys are still design-only. Order create holds a short Redis lock for an in-flight duplicate and does not require `Idempotency-Key`. A retry after that lock expires can create a second order. `customer_id` on an order comes from the access token. A client field with that name is ignored.

There is no OpenAPI file in Phase 0. This page is the contract sketch later phases implement. Routes are stable once a phase ships them; until then they exist only on paper.

All JSON uses UTF-8. All authenticated routes go through the gateway. The browser never calls a pod address.

## Versioning

Public routes are prefixed with `/api/v1`.

A future `/api/v2` may exist on the same gateway at the same time. v1 stays mounted until a documented sunset. Clients opt in by path, not by a hidden header, so access logs show the version.

Within v1:

- Adding a JSON field is compatible. Clients ignore what they do not know.
- Removing a field, renaming it, or changing a type is a v2 change.
- Event schema versions ([events.md](events.md)) are independent. An API version bump does not imply an event version bump.

The gateway routes both prefixes when v2 exists. It does not rewrite v1 bodies into v2.

## Error envelope

Errors are one shape. Success responses are the resource, not wrapped.

```json
{
  "error": {
    "code": "INVALID_STATE_TRANSITION",
    "message": "An order in CONFIRMED cannot be cancelled.",
    "correlation_id": "018f1c2a-3333-7c11-8a22-444444444444",
    "details": []
  }
}
```

`message` is safe to show a user. `details` may carry field errors (`{"field": "quantity", "issue": "must be at least 1"}`). Do not put stack traces, SQL, or token contents in the body.

| HTTP | `code` | When |
| --- | --- | --- |
| 400 | `VALIDATION_ERROR` | Body or query fails shape checks |
| 401 | `UNAUTHENTICATED` | Missing or invalid token |
| 403 | `FORBIDDEN` | Token is valid and the role or owner check failed |
| 404 | `NOT_FOUND` | No such resource, or a resource the caller must not know exists |
| 409 | `INVALID_STATE_TRANSITION` | Domain rejected the edge |
| 409 | `IDEMPOTENCY_IN_PROGRESS` | Same key is still running |
| 409 | `IDEMPOTENCY_KEY_REUSE` | Same key, different body |
| 429 | `RATE_LIMITED` | Gateway coarse limit or Redis-backed limit |
| 500 | `INTERNAL` | Unexpected |
| 503 | `DEPENDENCY_UNAVAILABLE` | Circuit open, or Redis fail-closed on login, register, or order create |

Controllers map domain errors to this table. They do not invent a parallel set of transition rules.

## Pagination

Two styles exist because they fail differently.

| Style | Use here | Failure mode |
| --- | --- | --- |
| Cursor | Orders, reports, any list that grows while you read it | Harder to jump to "page 50." Stable under inserts. |
| Offset | Product catalog only, while it is small | Rows shift or repeat when someone inserts above the offset. Fine for a short admin catalog. |

Cursor request: `GET /api/v1/orders?limit=20&cursor=<opaque>`. Response includes `items` and `next_cursor` (null at the end). The cursor is opaque. Clients do not decode it. Limit default 20, maximum 100.

Offset request, products only: `GET /api/v1/products?limit=20&offset=0`. Maximum limit 100. If the catalog later needs stable scans, move products to cursors in v2 or as an additive query mode; do not break existing offset clients inside v1 without a version bump.

## Auth overview

Details and threat assumptions are in [security.md](security.md). The API shape is:

| Method and path | Who | Effect |
| --- | --- | --- |
| `POST /api/v1/auth/register` | Public | Creates a customer account. Role is `customer` because the server says so. |
| `POST /api/v1/auth/login` | Public | Returns access and refresh tokens. Roles copied from `accounts`, never from the body. |
| `POST /api/v1/auth/refresh` | Refresh token | Rotates the refresh token and returns a new pair. |
| `POST /api/v1/auth/logout` | Refresh token | Revokes the refresh token server-side. |

Access tokens are short-lived (design value: 15 minutes). Refresh tokens last longer (design value: 7 days) and are stored only as a hash in `order_db`. Signing is RS256 so the gateway and Django can verify with a public key.

A body field named `role` on register or login is ignored. Staff accounts are not created through public register. Seed them with `python -m order_service.infrastructure.seed_staff` when `SEED_ADMIN_EMAIL` and `SEED_ADMIN_PASSWORD` are set (the manager pair is optional). The client cannot choose Admin.

## Orders

Owner: order service.

| Method and path | Who | Effect |
| --- | --- | --- |
| `POST /api/v1/orders` | Customer | Create `PENDING`. Requires `Idempotency-Key`. |
| `GET /api/v1/orders/{id}` | Owner, Admin, Manager | Fetch one order. |
| `GET /api/v1/orders` | Customer sees own; Admin and Manager see all | Cursor list. |
| `POST /api/v1/orders/{id}/confirm` | Owner, Admin, Manager | `PENDING` to `CONFIRMED`, or 409. Requires `Idempotency-Key`. |
| `POST /api/v1/orders/{id}/cancel` | Owner, Admin, Manager | `PENDING` to `CANCELLED`, or 409. Requires `Idempotency-Key`. Body: `{"reason": "customer_request"}` or `staff_request`. |

Create body:

```json
{
  "items": [
    {"product_id": "uuid", "quantity": 2}
  ]
}
```

The server loads prices. A client `unit_price` is ignored if sent. The server computes `total`. Phase 2 sets `customer_id` from the access token subject. A client field named `customer_id` is ignored.

Order response:

```json
{
  "id": "uuid",
  "customer_id": "uuid",
  "status": "CONFIRMED",
  "saga_status": "INVENTORY_RESERVING",
  "items": [
    {
      "product_id": "uuid",
      "sku": "MUG-01",
      "quantity": 2,
      "unit_price": {"amount_minor": 1500, "currency": "USD"}
    }
  ],
  "total": {"amount_minor": 3000, "currency": "USD"},
  "version": 2
}
```

`saga_status` is null while the order is `PENDING` or `CANCELLED`. After confirm it is one of the saga states in [architecture.md](architecture.md). `version` is `aggregate_version`.

### Internal fulfillment routes

Not routed by the public gateway. Called by the Odoo module on the cluster network, authenticated with a service credential the browser does not have. Phase 2 checks the header `X-Internal-Token` against `INTERNAL_SERVICE_TOKEN` with a constant-time compare. A customer access token is not accepted. If the variable is unset, the routes return 503 `DEPENDENCY_UNAVAILABLE` rather than failing open. This is a learning stand-in for the Odoo credential in Phase 8. Production would use a private network plus a rotated credential or mTLS, not a long-lived shared header.

| Method and path | Effect |
| --- | --- |
| `POST /api/v1/internal/orders/{id}/processing` | `CONFIRMED` to `PROCESSING`, or 409 |
| `POST /api/v1/internal/orders/{id}/shipped` | `PROCESSING` to `SHIPPED`, or 409. Optional `tracking_reference`. |
| `POST /api/v1/internal/orders/{id}/delivered` | `SHIPPED` to `DELIVERED`, or 409 |

These still pass through the domain. The internal caller does not get a back door around the state machine. A 409 means "retry later if the previous milestone has not been applied yet."

## Products

Owner: order service. Prices and names are written here. Stock numbers on the read response come from `InventorySnapshot` and can be stale.

| Method and path | Who | Effect |
| --- | --- | --- |
| `GET /api/v1/products` | Any authenticated role; public read is a later choice, default is authenticated | Offset list. |
| `GET /api/v1/products/{id}` | Same | One product plus snapshot quantities if present. |
| `POST /api/v1/products` | Admin | Create. Emits `ProductCreated`. |
| `PATCH /api/v1/products/{id}` | Admin, Manager | Update name, price, or active flag. Emits `ProductUpdated`. |

Product writes do not change historical order lines.

## Customers

Owner: order service.

| Method and path | Who | Effect |
| --- | --- | --- |
| `GET /api/v1/customers/me` | Customer | Own profile. |
| `PATCH /api/v1/customers/me` | Customer | Update display name. Emits `CustomerUpdated`. |
| `GET /api/v1/customers` | Admin, Manager | Cursor list. |
| `GET /api/v1/customers/{id}` | Admin, Manager, or the customer themselves | One profile. |

Email change, if added, is a versioned decision later because it is an identifier. Phase 0 allows display name updates only.

## Reports

Owner: reporting service. Gateway prefix `/api/v1/reports`.

| Method and path | Who | Effect |
| --- | --- | --- |
| `GET /api/v1/reports/orders/summary` | Admin, Manager | Counts and totals by status. Eventually consistent. |
| `GET /api/v1/reports/orders` | Admin, Manager | Cursor list of projected orders. |
| `GET /api/v1/reports/inventory` | Admin, Manager | Projected stock snapshots. |
| `GET /api/v1/reports/revenue` | Admin, Manager | Sums from payment projections, not from a live join to `order_db`. |

Every report response includes `as_of`, the timestamp of the newest event applied for that query's projection, so a reader can see staleness instead of trusting a total that is ten minutes behind.

Customers do not get these routes. A customer reads their orders from the order service, which is the strong read of their own aggregate.

## Correlation and request headers

| Header | Rule |
| --- | --- |
| `Authorization` | `Bearer` access token on protected routes. |
| `Idempotency-Key` | Required on the unsafe order routes above. |
| `X-Correlation-Id` | Optional UUID from the client. The gateway creates one if it is missing or not a UUID. Echoed on the response. |
| `traceparent` | W3C trace context, propagated by OpenTelemetry. Do not replace the correlation id with it. |

## What this API will not grow

- A route that runs arbitrary SQL.
- A route that proxies RabbitMQ.
- A public route that sets order status to an arbitrary string.
- A report route implemented by the order service "for now."

## Related documents

- [security.md](security.md)
- [services.md](services.md)
- [idempotency.md](idempotency.md)
