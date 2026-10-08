# ADR-004: Why a database per service

**Status: Phase 0 design; not implemented.** Accepted for this learning project.

## Context

Three backends have different jobs and different release rhythms: order transactions, report projections, and Odoo. Odoo already assumes it owns its database and will create a large schema of its own. Reporting wants indexes that would be hostile on a hot order table. The order service wants a small transactional schema it can migrate with Alembic.

## Decision

Three PostgreSQL databases: `order_db`, `reporting_db`, and `odoo_db`. Three login roles. No cross-grants. Each service migrates only its database, with its own tool (Alembic, Django migrations, Odoo module upgrades).

Local learning may host all three databases on one PostgreSQL server. That is an infrastructure shortcut documented in [../database.md](../database.md). Application code still uses three DSNs and three roles.

## Alternatives

| Alternative | Why it lost |
| --- | --- |
| One database, schema per service | Better than shared tables, and still one disk, one superuser temptation, and one backup that pretends the services are a single snapshot. Odoo is also painful to confine to a schema beside hand-written tables. |
| One shared schema | Fastest demo and the end of independent deploys. A report migration can lock an order table. |
| Separate engines (Postgres for orders, something else for reports) | Extra operations for no lesson. The boundary is ownership, not engine brand. Odoo wants PostgreSQL anyway. |

## Consequences

- You cannot join an order to live stock in SQL. You copy facts through events and accept lag.
- You cannot use a foreign key to Odoo. The commerce `order_id` stored on an Odoo sales order is a plain identifier, checked by the application.
- Three backup streams, three restore decisions. [../disaster-recovery.md](../disaster-recovery.md) exists because of this.
- A bug that opens the wrong DSN is still possible. Grants make it fail closed. Reviews have to catch a superuser DSN in the order service environment.
- Transactions stay simple because they are local. The complexity moves to the outbox, the consumers, and the saga. That is a transfer, not a free lunch.
- The single local Postgres server means a container crash takes all three databases down. Failure drills on a laptop will understate isolation until the processes are actually separate. Say so when you demo.

## What happens without this decision

The system looks like microservices and behaves like a modular monolith with network overhead. The worst of both: deploys are coupled, and calls are remote.
