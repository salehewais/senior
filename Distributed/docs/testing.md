# Testing

**Status: Extension Phase 9 ran the operational unit suites listed below on 9 October 2026. Live Compose, kind, Locust, the failure lab, and a timed restore were not run. `docker info` could not reach the daemon, `kind` is not installed, and `locust` is not installed.**

Tests show up with the phase that introduces the behavior. Phase 0 had nothing to execute. Later phases added the tests this page describes, so a state machine is not discovered only through the UI.

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

## Extension Phase 9

This phase extends the suites that already exist. It does not add a second runner. The commands below are the ones run on this machine on 9 October 2026. None of them skipped.

```bash
cd services/order-service && .venv/bin/python -m pytest tests/unit/test_saga_scenarios.py tests/unit/test_consistency_export.py tests/unit/test_cache_behavior.py
cd services/reporting-service && .venv/bin/python -m pytest projections/tests/test_consistency_lag.py
cd services/odoo && .venv/bin/python -m pytest tests/test_commands.py
cd services/notification-service && .venv/bin/python -m pytest tests/test_delivery.py tests/test_boundaries.py
```

Results from that run:

| Command | Result |
| --- | --- |
| order-service pytest above | 19 passed in 0.19s |
| reporting-service pytest above | 2 passed in 0.20s |
| odoo pytest above | 5 passed in 0.01s |
| notification-service pytest above | 7 passed in 0.20s |

No requests per second, latency, or per-replica count was written. `docker info` exited 1: `failed to connect to the docker API at unix:///home/asm/.docker/desktop/docker.sock` (`connect: no such file or directory`). The `kind` command is not installed. The `locust` command is not installed. Nothing accepted a connection on `127.0.0.1:5672` (RabbitMQ) or `127.0.0.1:6379` (Redis); both refused the connection. A load run was not started.

### Already covered

These tests were already in the tree. Phase 9 did not rewrite them.

| Behavior | Test |
| --- | --- |
| Eight saga scenarios, including a crash halfway through, a restart that looks up a timed-out reserve, and compensation that ends in `MANUAL_INTERVENTION_REQUIRED` | `services/order-service/tests/unit/test_saga_scenarios.py`: `test_every_step_succeeds`, `test_inventory_reservation_fails`, `test_payment_fails_after_inventory_reservation`, `test_odoo_is_unavailable`, `test_an_event_arrives_twice`, `test_process_crashes_halfway_through_the_saga`, `test_compensation_fails`, `test_workflow_resumes_after_restart`. `test_refund_failure_is_manual_intervention_and_not_a_guaranteed_refund` is the same manual-intervention rule after a failed refund. |
| Order row versus the Django projection before and after `OrderConfirmed` | `services/order-service/tests/unit/test_consistency_export.py` `test_confirmed_order_row_and_outbox_share_one_snapshot` and `services/reporting-service/projections/tests/test_consistency_lag.py` `test_projection_is_missing_then_present_after_order_confirmed` |
| A second `ReserveInventory` does not reserve twice, and an unknown timeout looks the reservation up before another reserve | `services/odoo/tests/test_commands.py` `test_an_event_arrives_twice` and `test_unknown_timeout_looks_up_before_a_second_reserve` |
| A failing mock adapter retries, then dead-letters | `services/notification-service/tests/test_delivery.py` `test_failing_mock_adapter_retries_then_dead_letters` |
| The notification service does not open `order_db` | `services/notification-service/tests/test_boundaries.py` `test_order_reporting_and_odoo_databases_are_refused_before_an_engine_exists` and `test_service_files_do_not_embed_another_database_url` |
| Stale cache key, Redis down falls through to the product row, concurrent misses, invalidation after commit | `services/order-service/tests/unit/test_cache_behavior.py` `test_stale_product_is_served_when_the_delete_has_not_happened`, `test_redis_down_falls_through_to_postgres`, `test_concurrent_misses_both_fill_and_the_last_write_wins`, `test_successful_catalog_change_deletes_the_product_key` |

`test_duplicate_event_is_not_delivered_twice` already asserts that a second `apply_notification` does not call the adapters again. It does not settle the broker delivery.

### Added in this phase

| Behavior | Test |
| --- | --- |
| Compensation resumes after a crash when the release reply was lost. The restarted process looks the hold up, does not release a second time, and ends `COMPENSATED`. The order stays `CONFIRMED`. | `services/order-service/tests/unit/test_saga_scenarios.py` `test_compensation_resumes_after_a_crash_without_a_second_release` |
| A saga at `COMPLETED` leaves the order `CONFIRMED` at version 3, with `PaymentConfirmed` in the outbox and no `OrderDelivered` | `services/order-service/tests/unit/test_consistency_export.py` `test_completed_saga_stays_confirmed_and_records_payment_before_any_projection` |
| That same order row is ahead of Django: the projection is missing, then `PENDING`, then `CONFIRMED` while `payment_projections` is still empty. After `PaymentConfirmed` is applied, the payment row matches and the order projection stays `CONFIRMED`. | `services/reporting-service/projections/tests/test_consistency_lag.py` `test_completed_saga_does_not_deliver_the_projection_before_payment_arrives` |
| A duplicate notification delivery is acked once, is not retried, and is not dead-lettered | `services/notification-service/tests/test_delivery.py` `test_duplicate_delivery_is_acked_once` |

## Related documents

- [architecture.md](architecture.md)
- [failure-scenarios.md](failure-scenarios.md)
