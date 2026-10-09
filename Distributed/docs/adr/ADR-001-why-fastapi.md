# ADR-001: Why FastAPI for the order service

**Status: Accepted. Implemented in Phase 1** as `services/order-service`. This is a learning project.

## Context

The order service is the only writer of order state. It must expose an HTTP API, run domain rules that reject illegal transitions, commit those rules in one Postgres transaction with an outbox row, and stay understandable to someone who will implement it in phases.

The presentation layer needs to be thin. The domain must be testable without a web framework. The team has already chosen Python for the custom services (Django is the reporting stack), so the order service should stay in Python and avoid a second language before the domain is even written.

## Decision

Use FastAPI for the HTTP adapters. Structure the service as Clean Architecture:

- Domain: aggregates, value objects, state machine. No FastAPI imports.
- Application: use cases and ports.
- Infrastructure: Postgres, outbox publisher, Redis, payment client.
- Presentation: routers that map HTTP to use cases. This is the only MVC-style layer. The controller does not own business rules.

Pydantic models at the edge validate JSON. They are not the domain model.

## Alternatives

| Alternative | Why it lost |
| --- | --- |
| Django for orders and reports | One framework would hide the boundary. It would be easy to query the order tables from a report view "just this once." A second codebase makes the illegal join obvious. Django's admin is also a temptation to edit order rows and skip the state machine. |
| Flask or Starlette alone | Fine frameworks. FastAPI adds typed request models and OpenAPI generation later without a pile of extensions. We still do not commit an OpenAPI file in Phase 0. |
| A second JVM or Go service | A better fit for some production shops. Here it would slow a learner who also has Django and Odoo to understand. The architecture lessons are the transactions and the events, not the HTTP library. |
| Put the domain in routers | Faster for a demo. The first illegal transition will be reimplemented slightly differently in a second route, and unit tests will boot the app. |

## Consequences

- Two Python web stacks exist in the project (FastAPI and Django). Shared code is limited to event envelope conventions, not a shared database layer. That is extra dependency surface and a conscious wall.
- Async FastAPI does not make the database transaction async-safe by magic. The implementer must not hold a session across unrelated awaits in a way that breaks the unit of work. If that becomes a trap, a sync SQLAlchemy session in a threadpool is an acceptable implementation detail. The ADR does not mandate async database drivers.
- OpenAPI can be generated later from the routers. The contract that matters first is [../api.md](../api.md), so generated docs do not drift ahead of the decisions.
- Staff who expected Django admin for orders will not get it. Order changes go through use cases.

## What happens without this decision

Either the order rules live in Django beside the read models, and the CQRS split collapses, or they live in ad-hoc scripts, and the state machine has no home. Both fail the "single writer" rule in [../architecture.md](../architecture.md).
