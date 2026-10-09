# Testing

**Status: Phase 0 design; not implemented.**

Tests show up with the phase that introduces the behavior. Phase 0 has nothing to execute. This page fixes what is worth testing so later phases do not discover the state machine only through the UI.

## Layers

| Layer | What it proves | When it starts | What it must not need |
| --- | --- | --- | --- |
| Domain unit tests | Legal and illegal order transitions, money math, quantity rules | Phase 3 | Database, HTTP, broker |
| Application tests | A use case writes the outbox with the order, authorization, idempotency key reuse | Phase 5–7 | Real RabbitMQ. A fake repository is enough for pure rules; one integration test should use a real database. |
| Contract tests | Envelope required fields, routing keys, error envelope shape | Phase 7–8 | A full browser |
| Consumer tests | Duplicate `event_id` does not double-apply; older inventory snapshot is ignored; skipped order version is retried | Phase 9–10 | The whole platform. A database and a fixture envelope are enough. |
| API tests | Status codes in [api.md](api.md), especially 409 on illegal transitions | Phase 5 | Odoo and Django |
| Compose journey | Create, confirm, see the message, see the projection | After Phase 10, extended as services appear | kind |
| Failure drills | [failure-scenarios.md](failure-scenarios.md) | Phase 19 | New features mid-drill |

The domain test for transitions is the cheapest safety net in the project. If it needs FastAPI imported, the layering is already wrong.

Suggested transition cases, all in the domain:

- `PENDING` to `CONFIRMED` and to `CANCELLED`
- `CONFIRMED` to `PROCESSING` to `SHIPPED` to `DELIVERED`
- `CONFIRMED` to `CANCELLED` rejected
- `DELIVERED` to anything rejected
- `SHIPPED` to `PROCESSING` rejected
- Cancel with an empty order rejected at creation time (no items, or quantity below 1)

## What "done" means for an integration test

An order test that mocks the database and the outbox does not prove the transaction. At least one test per critical write should run against Postgres and assert that a rolled-back order leaves no outbox row, and a committed order leaves one.

An idempotency test should apply the same envelope twice inside one database and assert a single projection row.

A test that sleeps for "eventual consistency" without a bound is a flake. Prefer polling a condition with a timeout and a failure message that says which consumer did not move.

## What we do not pretend to test in early phases

- Multi-node RabbitMQ partitions
- A real card network
- Kubernetes scheduling drills. Phase 13 checks the manifests. It does not break pods on purpose.
- Load that would size production hardware

A single happy-path click in the browser is not a substitute for the transition table. It is still useful once the UI exists, as one journey test, not as the only test.

## Failure

A test suite that needs every container is slow, so people stop running it. Keep domain tests instant. If the suite is skipped, detection is a red CI job once CI exists. Until then, detection is discipline. Recovery is to delete the shared fixture that forced every test to boot Odoo.

> **Learning simplification.** Tests run on the developer's machine. No CI definition in Phase 0.
> **Production would require.** CI that runs domain tests on every change and integration tests against ephemeral Postgres and RabbitMQ, plus the failure drills on a schedule rather than once for a demo.

## Related documents

- [architecture.md](architecture.md)
- [failure-scenarios.md](failure-scenarios.md)
