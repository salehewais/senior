# ADR-011: Why OpenTelemetry

**Status: Accepted. Phase 12 exports OTLP from the order path to a collector.** Odoo and Django ORM auto-instrumentation are not in that wiring.

## Context

A confirm request crosses Traefik, the order service, Postgres, the outbox publisher, RabbitMQ, and a consumer. Metrics say the system is slow. They do not say which hop was slow for the request a customer just retried.

We also already have a correlation id for business events. Traces are a second identifier, the technical one, and they die if we sample them. Events must keep the correlation id even when no span was stored.

The ecosystem of tracers is full of vendor SDKs. This project should not couple the learning code to one vendor's agent.

## Decision

Instrument the order service, the reporting service, and the gateway path with OpenTelemetry. Export OTLP to a collector. Propagate W3C `traceparent` on HTTP and on message headers.

OpenTelemetry does not replace Prometheus. Metrics stay on `/metrics` for the first implementation. Traces are the OTel job. A later export of metrics through OTel is allowed and not required.

The collector is not on the checkout correctness path. If it is down, spans are dropped and orders still commit.

## Alternatives

| Alternative | Why it lost |
| --- | --- |
| A single vendor SDK | Faster setup against that vendor's cloud, and a rewrite if you leave. OTel is the portability layer. |
| Correlation ids only, no traces | Enough to find logs for one request if every log line has the id. Not enough to see that the payment client consumed four seconds. We keep the correlation id and add spans. |
| OpenTelemetry as the only telemetry plane, including metrics storage | Collapses three jobs into one pipeline. A broken collector would then also blind alerts. We refuse that coupling. |
| No collector, SDK exports straight to a SaaS | Fine later. Locally we want a process we can stop as a failure drill. |

## Consequences

- Two ids exist. Document them in logs: `correlation_id` and trace id. Do not overwrite one with the other.
- Instrumentation can become noisy. Start with server spans, client spans for Postgres, Redis, HTTP payment, and consumer spans. Do not manually span every domain method.
- Sampling policy is a later knob. Until it exists, a laptop can keep every span. The design still assumes spans can disappear, so business facts never live only in a span.
- The collector is another moving part. Phase 12 adds it. `X-Correlation-Id` is still propagated, and it is not replaced by the trace id.
- Context must cross the outbox. The publisher creates a span when it publishes and puts trace context on the AMQP headers. If it only logs the correlation id, the consumer trace is disconnected, which is survivable and worse. Do both.

## What happens without this decision

A slow confirm is a debate between "the database" and "Odoo" with no span to point at. Teams then add synchronous calls "so we can see the error," which undoes the outbox. Traces are how we keep the async design debuggable.
