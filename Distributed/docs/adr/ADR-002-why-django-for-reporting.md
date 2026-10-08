# ADR-002: Why Django for reporting

**Status: Phase 0 design; not implemented.** Accepted for this learning project.

## Context

Managers need lists and totals that must not run inside the order transaction and must not join Odoo tables. The read side is a CQRS projection: it consumes events and serves queries from `reporting_db`.

The read side has different pressure from the write side. It is mostly CRUD over projections, migrations, and an admin-shaped UI later. It does not own the order state machine.

## Decision

Build the reporting service in Django, with its own database and Django migrations. HTTP views (or a small DRF surface if a phase chooses it) serve `/api/v1/reports`. A management command or worker consumes RabbitMQ and writes projections. The processed-event insert and the projection write share one database transaction.

Django is not used as a second writer of orders.

## Alternatives

| Alternative | Why it lost |
| --- | --- |
| More FastAPI for reports | One language style, and then two services that look the same. Learners start importing the order repositories into the report process. Django's migration tool and ORM also fit a projection database that is allowed to be boring. |
| SQL views on `order_db` | Strongly consistent reports, and a long query sits on the same database as checkout. That is the failure mode database-per-service exists to avoid. |
| A warehouse such as ClickHouse | The right tool when event volume outgrows Postgres. It is another operational product. This project's volume is "a classroom." Postgres is enough, and the lesson is the projection, not the column store. |
| Metabase or a GUI directly on `order_db` | Useful in companies that already separated a replica. Pointed at the writer database, it teaches the wrong dependency. A later phase may put a GUI on `reporting_db`. It may not put one on `order_db`. |

## Consequences

- Reports are eventually consistent. Every report payload should show `as_of` so staleness is visible. Anyone who needs the order they just confirmed reads the order service, not Django.
- Two migration tools exist (Alembic and Django). They must never be pointed at the same database.
- Django's ORM will happily open a second database if someone adds a `DATABASES` entry. Code review and the database grants have to say no. The framework will not.
- The reporting service does not publish domain events. A wrong total is a projection bug, repaired by replay, not by emitting `OrderCorrected` from Django.
- We accept a heavier process (Django) for a read API. That cost is real on a laptop and is still smaller than a shared-schema incident.

## What happens without this decision

Reporting queries land on `order_db`, indexes are negotiated between checkout and dashboards, and the first schema change needs both teams in the room. The event catalog becomes optional decoration.
