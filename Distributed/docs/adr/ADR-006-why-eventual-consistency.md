# ADR-006: Why eventual consistency between services

**Status: Accepted. Implemented** as one transaction inside a service database and events after that. This is a learning project.

## Context

We want checkout to commit even when reporting or Odoo is down. [ADR-004](ADR-004-why-database-per-service.md) removed shared transactions. [ADR-005](ADR-005-why-outbox.md) removed a shared commit with the broker. Something has to give: either availability across services, or the illusion that all databases match on the same millisecond.

The business can tolerate a dashboard that is a few seconds behind and an ERP order that appears shortly after confirm. It cannot tolerate a confirmed sale that exists only on the screen and not in `order_db`. So the strong guarantee stays inside one database transaction, and nowhere wider.

## Decision

Strong consistency only inside a single service database transaction. Between services, consumers apply events and catch up. The user-visible contract:

- After a successful confirm, `GET` on the order service returns `CONFIRMED`.
- Reports may lag, and they expose `as_of`.
- Odoo may lag, and the saga status shows how far integration has gone.
- Stock on the product page is a snapshot. Reservation in Odoo is the authority. Oversell races are handled by saga compensation, not by a distributed lock.

There is no two-phase commit and no "read your writes" guarantee across services.

## Alternatives

| Alternative | Why it lost |
| --- | --- |
| Synchronous calls to Django and Odoo inside confirm | Consistency feels immediate until one of them is slow. Checkout latency and failure rate become the worst participant. |
| Sagas that pretend to be ACID | A saga is a sequence of local commits plus compensation. Calling it a distributed transaction leads people to expect rollback of Odoo from a Postgres `ROLLBACK`. |
| Block the HTTP response until consumers ack | That is synchronous with extra steps. A stuck consumer becomes a stuck checkout. |
| Strong consistency for inventory only | Tempting, and it pulls Odoo back onto the confirm path. We refuse it. The snapshot guard is allowed as a user-experience check and is documented as racy. |

## Consequences

- The UI must show `status` and `saga_status`. `CONFIRMED` does not mean paid, shipped, or present in Odoo.
- Compensation cannot use `CANCELLED` after confirm, because that transition is illegal. Operators and the UI live with `CONFIRMED` plus `COMPENSATED`. That is awkward and honest. Adding a new order status would be a catalog and state-machine change, not a quiet patch.
- Tests that sleep "for a bit" will flake. Tests should poll for the projection with a timeout.
- Some user questions ("why does the report disagree?") are support load. `as_of` is how we answer them without a war room.
- Developers will be tempted to "just query the other database this once" when a lag bug is hard. That shortcut deletes the decision. The grants should make it fail.

## What happens without this decision

Either we adopt distributed transactions and inherit their outages, or we keep separate databases and still tell users the data is always aligned. The second option is how trust in the system dies: the screen is confidently wrong.
