# Prometheus

**Status: Phase 12.** Prometheus scrapes the Compose network. The UI is `http://127.0.0.1:9090` only.

Prometheus is the metrics database. It scrapes HTTP endpoints on an interval, stores series locally, and evaluates alert rules. It does not draw dashboards and it does not page anyone by itself. Grafana reads it. Alertmanager receives the alerts it raises. See [ADR-009](adr/ADR-009-why-prometheus.md).

## Why this job is separate

Metrics need a pull model with a simple query language so a learner can ask "is outbox age above a minute?" without shipping logs to a vendor first. Prometheus is that tool. Mixing it into the order service ("we will just log timings") fails the moment you need a rate over five minutes across two replicas.

What happens without it: incidents are discovered by a human clicking the UI. Eventual consistency bugs, which look like "the report is a bit behind," stay invisible until a customer complains.

## Scrape plan

Phase 12 scrapes:

| Target | What it adds |
| --- | --- |
| Traefik metrics | Edge rate, errors, latency |
| `order-service` `/metrics` | Use-case counts, outbox gauges, circuit gauge |
| `reporting-service` `/metrics` | Projection apply rate, lag, duplicates |
| RabbitMQ exporter or built-in plugin | Queue depth, consumers, DLQ depth |
| Postgres exporter | Connections, transaction rate. Optional on a laptop, valuable when the database is the bottleneck |
| Prometheus itself | So we can alert that scraping stopped |

Application metrics are exposed by the process directly. The scrape file is `deploy/observability/prometheus/prometheus.yml`. It also scrapes the outbox publisher, the inventory consumer, and the reporting consumer, because those counters do not live in the HTTP process. Traces go to the OpenTelemetry collector. Metrics are not forced through the collector. One less hop means a missing trace pipeline cannot hide a missing error rate.

Prometheus labels stay low-cardinality. A label is part of the series identity, and a value that changes per order, user, or request creates a new series on every checkout. `user_id`, `order_id`, `request_id`, `message_id`, and `email` are never labels.

> **Learning simplification.** One Prometheus process, local disk, retention of a few days, static scrape config or a short file-based discovery list.
> **Production would require.** Capacity planning for cardinality, remote write to long-term storage, and recording rules for expensive dashboards. High-cardinality labels (raw order id, raw email) are forbidden even in learning mode, because one bad label will wreck the local disk too.

## Names that later phases should keep stable

So dashboards and alerts do not churn:

- `http_requests_total` with labels `service`, `route` (templated, not raw ids), `status`
- `http_request_duration_seconds` histogram, same labels
- `outbox_unpublished_count`
- `outbox_oldest_pending_age_seconds`
- `outbox_publish_failures_total`
- `consumer_messages_total` with labels `queue`, `result` (`applied`, `duplicate`, `stale`, `error`)
- `consumer_dlq_messages` gauge or the broker's own queue-depth series for the three DLQs
- `payment_circuit_state` (0 closed, 1 half-open, 2 open)
- `projection_lag_versions` on the reporting service

Route labels use the template (`/api/v1/orders/{id}`), never the UUID. Otherwise every order creates a new time series.

## Failure and recovery

If Prometheus is down, scrapes stop and rules do not run. Checkout is unaffected. Detection: Grafana gap, or a dead-man's-switch from outside. Recovery: start it again. The gap stays empty. Do not block application startup on Prometheus being reachable; a metrics outage must not take checkout with it.

Alert rules live in files reviewed with the code, not only in a UI. The first rules are listed in [alerting.md](alerting.md).

## Related documents

- [observability.md](observability.md)
- [grafana.md](grafana.md)
- [alerting.md](alerting.md)
