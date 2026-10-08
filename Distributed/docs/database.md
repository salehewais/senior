# Database ownership

**Status: Phase 0 design; not implemented.**

Three databases, three owners, three migration tools. A transaction never opens more than one of them.

## Names

| Database | Owner service | Login role the service uses | Migration tool |
| --- | --- | --- | --- |
| `order_db` | `order-service` | `order_service` | Alembic |
| `reporting_db` | `reporting-service` | `reporting_service` | Django migrations |
| `odoo_db` | `odoo` | `odoo` | Odoo module upgrades |

No passwords, connection strings, or secret files belong in this repository. Later phases read them from the environment. The application roles are not superusers. They do not get `GRANT` on another service's database.

> **Learning simplification.** Phase 1 may run all three databases in one PostgreSQL container so a laptop stays small.
> **Production would require.** Separate servers or separate managed instances, plus network policy so the order service cannot open a socket to `reporting_db` or `odoo_db` even if a bug tries.

The shared container is an infrastructure shortcut. It is not permission to share tables. If the only Postgres process stops, all three databases stop together, and the failure-isolation story is weaker than the design. Say that out loud when you demo it.

## The rule

No cross-service table access. That includes:

- SQL from the order service into `reporting_db` or `odoo_db`
- Django models with a second database connection to `order_db`
- Foreign data wrappers, `dblink`, and shared schemas
- A "read-only reporting user" on `order_db`
- Triggers in one database that write to another

What problem this solves: each service can change its schema on its own release train. A long report query cannot take a lock that blocks checkout. A bad Odoo module upgrade cannot corrupt `orders`.

What happens without it: the services look separate and fail together. The first urgent bugfix will be a join "just this once," and the join becomes permanent.

What happens when the rule is violated in production: an outage or a migration in one area stalls another. Detection is architectural more than metric: code review, a database user that physically lacks grants, and a test that the order service process has no reporting DSN. Recovery is to delete the cross-connection and rebuild the read side from events.

How it scales: `reporting_db` can get a read replica, extra disk, or a different retention policy without touching checkout storage.

## What is strongly consistent

Strong consistency means a single local commit either made all of these writes visible or none of them.

In `order_db`:

- The order row, its items, and the `OrderCreated` or transition outbox row.
- A catalog or customer change and its outbox row.
- A payment outcome row (or the fields on the saga) and the `PaymentConfirmed` or `PaymentFailed` outbox row.
- An `InventoryUpdated` apply: the snapshot row and the processed-event row.
- An HTTP idempotency record and the order it created.
- A refresh-token hash rotation and the new hash.

In `reporting_db`:

- The projection rows touched by one event and the processed-event row for that `event_id`.

In `odoo_db`:

- The ERP document and the connector row that remembers the commerce `event_id` and `order_id`.

## What is eventually consistent

- Django's tables versus the order that was just confirmed.
- Odoo's sales order versus `OrderConfirmed`.
- `inventory_snapshots` in `order_db` versus Odoo stock.
- Redis keys versus Postgres.
- Saga progress versus the outside world. The saga row is strongly consistent with the order row at each local commit, and eventually consistent with the payment provider and Odoo.

A reader must be able to tolerate "not yet." The HTTP response after confirm is the strong view: it returns the order as stored in `order_db`. Reports and Odoo catch up.

There is no two-phase commit across services. A transaction cannot span services. If you need two of these databases to agree inside one user click, the design is wrong; one of the writes should become an event.

## Logical contents

These are conceptual tables, not a migration. Names can match this list when Alembic and Django migrations appear.

### `order_db`

| Table | Purpose |
| --- | --- |
| `accounts` | Email, password hash, role (`customer`, `admin`, `manager`). Role is server state. |
| `customers` | Profile for accounts that are customers. Same id as the account. |
| `products` | Storefront catalog. Price is `Money` stored as minor units and currency. |
| `orders` | Status, customer id, total, version, saga status once the saga exists. |
| `order_items` | Product id, SKU copy, quantity, unit price copy. |
| `inventory_snapshots` | Last stock snapshot per product. Includes the version from Odoo. |
| `outbox` | See below and [outbox.md](outbox.md). |
| `processed_events` | Events this service has applied. See [idempotency.md](idempotency.md). |
| `http_idempotency_keys` | Client idempotency keys for unsafe HTTP. Durable here, not in Redis. |
| `refresh_tokens` | Hash of the current refresh token, expiry, rotation parent. |
| `saga_instances` | Conceptual, Phase 15. Same database so a step and the order commit together. |

`orders.version` is an integer starting at 1 and incrementing on each accepted order change that emits an order event. Payment facts increment it too when they are recorded against the order, so a single aggregate stream stays ordered. Implementers should not also mutate status inside a payment write unless the state machine allows that transition. Recording `PaymentConfirmed` while status stays `CONFIRMED` is legal if the version still moves.

### `reporting_db`

| Table | Purpose |
| --- | --- |
| `order_projections` and item rows | Read model for lists and totals. |
| `product_projections` | Catalog as last seen. |
| `customer_projections` | Fields needed on reports. No password material, ever. |
| `inventory_projections` | Stock snapshots for operational screens. |
| `payment_projections` | Payment outcomes joined to orders by `order_id`. |
| `processed_events` | Dedup for this consumer. |
| `projection_versions` | Last applied version per aggregate, so older snapshots and skipped transitions are detectable. |

Django may split or name these differently. It may not collapse them back into a live connection to `order_db`.

### `odoo_db`

Odoo owns its internal schema. Phase 0 does not redraw `sale_order` or `stock_quant`. The custom module must be able to store:

- The commerce `order_id` on the ERP sales order it created.
- The `event_id` values it has already applied.
- Enough stock information to emit a full `InventoryUpdated` snapshot (on hand, reserved, SKU, warehouse code, monotonic version).

Do not replicate Odoo's tables into `order_db`.

## Outbox table (conceptual)

Lives only in `order_db`. Reporting and Odoo do not have this table unless they someday publish their own facts through the same pattern. In this design, Odoo publishes `InventoryUpdated` from the module after the stock transaction commits. That publisher has the same inconsistency problem. Phase 14 should use an outbox-shaped table inside `odoo_db` for inventory events rather than "publish inside the stock transaction and hope." The columns match:

| Column | Role |
| --- | --- |
| `id` | UUID, primary key. Also the `event_id` inside the payload envelope. |
| `event_type` | Catalog name, such as `OrderConfirmed`. |
| `aggregate_type` | `order`, `product`, `customer`, or `inventory`. |
| `aggregate_id` | UUID of the aggregate. |
| `payload` | Full event envelope JSON. The publisher sends this body. |
| `created_at` | When the business transaction inserted the row. |
| `published_at` | Null until the broker confirms. |
| `retry_count` | Publisher attempts after failure. |
| `status` | `pending`, `published`, or `failed`. |

`payload` is the full envelope so the publisher does not reassemble events from current table state. Reassembly would publish "whatever the row looks like now," not "what was true at commit," and would drop intermediate transitions.

Index for the publisher: pending rows ordered by `created_at`, then `id`.

Details of the race this solves: [outbox.md](outbox.md).

## Migration strategy

Each service migrates only its database, as a step in its own release, before or as its new code starts.

| Service | Practice |
| --- | --- |
| Order service | Alembic revisions in that service. Linear history. `upgrade` runs against `order_db` only. |
| Reporting | Django migrations against `reporting_db` only. |
| Odoo | A versioned module. Upgrades through Odoo's `-u` path, never through Alembic. |

Rules that keep this survivable:

- Expand, then migrate data, then contract. Do not drop a column in the same release that stops writing it, once real data exists.
- A breaking event schema change is a new event `version` in the envelope. It is not a silent change to a JSON column. Database migrations and event versions are related and not identical. You can need one, the other, or both.
- No migration job receives two DSNs.
- Roll back application code only when the migration was backward compatible. A destructive migration needs a forward fix. Practice that honesty in Phase 20; do not pretend `downgrade` always works.

What happens without per-service migrations: one global script becomes the only person who knows the order of alters, and a failure halfway leaves two services half-upgraded with no owner.

Detection: migration job logs, plus a startup check that the expected revision is present (Alembic current, Django `migrate --check`, Odoo module version). Recovery: restore that database from backup if a migration corrupted it, or apply a forward revision. Do not "fix" `order_db` by editing it from Django.

## Backups

Backup each database on its own schedule. Restoring `reporting_db` must not require restoring `order_db` to the same second, because they are not a single consistent snapshot across services. After an `order_db` restore to an earlier time, republishing or accepting a gap is an operational decision recorded in [disaster-recovery.md](disaster-recovery.md). Redis is not backed up.

## Related documents

- [outbox.md](outbox.md)
- [idempotency.md](idempotency.md)
- [ADR-004](adr/ADR-004-why-database-per-service.md)
- [ADR-005](adr/ADR-005-why-outbox.md)
- [ADR-006](adr/ADR-006-why-eventual-consistency.md)
