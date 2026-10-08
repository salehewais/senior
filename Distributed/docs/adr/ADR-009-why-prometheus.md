# ADR-009: Why Prometheus

**Status: Phase 0 design; not implemented.** Accepted for this learning project.

## Context

Eventual consistency fails quietly. An empty report can mean "no sales" or "the consumer is dead." Logs of a single request do not show that outbox age has been climbing for ten minutes. We need a time-series store and a query language that a small set of alert rules can sit on.

The order service, reporting service, gateway, and broker will all expose numbers. One database should scrape them.

## Decision

Use Prometheus as the only metrics store. Applications expose `/metrics`. Prometheus scrapes them. Alert rules live in files Prometheus evaluates. Alertmanager sends them on. Grafana reads Prometheus for pictures.

Metrics do not have to pass through the OpenTelemetry collector to be alertable. Traces can be broken while error rate is still visible.

## Alternatives

| Alternative | Why it lost |
| --- | --- |
| Logs only | You can grep a crash. You cannot cheaply graph "age of oldest unpublished event" or alert on it without building a worse Prometheus. |
| A vendor APM as the only store | Fine in a company that already pays for one. This project would then teach the vendor's agent instead of a scrape target you can read with curl. |
| StatsD to Graphite | Historical, and an extra hop. Prometheus's pull model makes a dead process look like a missed scrape, which is itself a signal. |
| OpenTelemetry metrics as a replacement for Prometheus | OTel can export metrics. Something still stores and evaluates them. Using OTel to *replace* the store confuses the pipeline with the database. [ADR-011](ADR-011-why-opentelemetry.md) keeps OTel on traces first. |

## Consequences

- Cardinality is a design constraint. Labels are `service`, `route` template, `status`, `queue`, `result`. They are not order ids or emails. One careless label will fill the disk on a laptop, which is a useful lesson and still something we forbid in the metric list in [../prometheus.md](../prometheus.md).
- Pull scrape means Prometheus must be able to reach the pod network. That is natural in Compose and kind and is a network path to protect (do not publish `/metrics` on the public gateway).
- Local disk retention will be short. A gap after Prometheus is down is not backfilled. Business correctness must not depend on a metric existing.
- Alert rules need owners. A rule that pages and has no response in [../alerting.md](../alerting.md) will be muted. We start with a small set.
- We operate another stateful process. Its outage is a blindness outage, not a checkout outage. Application startup must not wait for Prometheus.

## What happens without this decision

Failure detection stays manual. The outbox pattern in particular looks successful from the user's side when it is stuck. Without a metric, that failure waits for a human comparing screens.
