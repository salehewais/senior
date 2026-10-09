# ADR-010: Why Grafana

**Status: Phase 0 design; not implemented.** Accepted for this learning project.

## Context

Prometheus is the store and the rule evaluator. Its own UI is enough to run a query and poor as a shared picture of checkout, outbox age, and queue depth during a failure drill. Phase 19 needs everyone to open the same boards.

We also need traces somewhere a human can click. Grafana can show those beside the metrics when a trace source exists.

## Decision

Use Grafana for dashboards and for trace lookup. The boards listed in [../grafana.md](../grafana.md) are the set Phase 12 commits as JSON.

Grafana is not an alerting path. Prometheus rules plus Alertmanager remain the only alerts. Grafana's alerting product is capable and, if turned on beside Alertmanager, gives two places a threshold can hide.

## Alternatives

| Alternative | Why it lost |
| --- | --- |
| Prometheus UI only | Honest and limited. Hard to put gateway latency next to outbox age in a way a drill can follow. |
| Grafana alerts instead of Alertmanager | One less process. It also ties paging to the dashboard server and invites panels that alert from a slightly different query than the rule file. We keep one rule source. |
| A notebook or a spreadsheet | Flexible once, not attached to live scrapes, and not something the gateway exports to. |
| Kibana or a log UI as the primary view | Logs answer a different question. Using them as the only picture pushes the team back toward [ADR-009](ADR-009-why-prometheus.md)'s rejected option. |

## Consequences

- Dashboards drift if they are edited only in the UI. Phase 12 commits the JSON. The names in the doc stay the contract. A Kubernetes board waits for Phase 13.
- Grafana credentials come from the environment, not from this repository.
- A SQL data source pointed at `order_db` is forbidden. It would bypass the reporting service and put a long query on the writer. Boards read Prometheus, and traces, and if needed the reporting HTTP API.
- Grafana down does not stop alerts and does not stop checkout. It stops the shared picture. Drills should say that out loud so nobody "fixes" a Grafana outage by failing the deploy.
- Another process to run. Justified by the drill, not by a desire for a logo on the diagram.

## What happens without this decision

Each person writes a private PromQL history. The failure drill becomes a scavenger hunt, and the outbox lesson does not stick because nobody was looking at the same age panel.
