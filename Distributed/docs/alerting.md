# Alerting

**Status: Phase 0 design; not implemented.**

Alertmanager receives alerts from Prometheus and groups them. Grafana is for looking. A second alert system inside Grafana would page twice or, worse, page differently, and nobody would know which rule is the real one.

Phase 0 defines the first rules. Phase 17 implements them. Phase 19 is allowed to fire them on purpose.

## What a good alert is

It asks a human to do something that the software could not finish. "CPU above 50%" on a laptop is not that. "Facts have been sitting in the outbox for five minutes" is that, because consumers will not heal it by themselves if the publisher is dead.

Each rule below should carry a short annotation: what is wrong, which document to open, and the first recovery step. An alert without a next step becomes a notification people mute.

## First rules

| Alert | Condition (starting point) | Likely meaning | First response |
| --- | --- | --- | --- |
| `OutboxStale` | Oldest pending age over 60 seconds for 5 minutes | Publisher stopped or broker is refusing | Check publisher logs and RabbitMQ, then let it drain |
| `OutboxFailed` | Any row counted in failed status | A message will not publish without a human | Read `event_id`, fix the cause, mark pending again deliberately |
| `DeadLetterBacklog` | Any primary DLQ depth greater than 0 for 5 minutes | Consumer gave up after 5 retries | Read the payload and the last error, fix, replay |
| `OrderServiceDown` | Ready probe failing or scrape down for 2 minutes | Checkout is dead or metrics are dead | If probes fail, restore `order_db` or the process. If only the scrape fails, say so. |
| `Gateway5xx` | 5xx ratio above a small threshold for 5 minutes | Users are hitting failures | Split gateway-versus-upstream using Traefik's upstream status |
| `PaymentCircuitOpen` | Circuit state open for 2 minutes | Provider is being failed fast | Confirm compensation is running. Do not close the circuit by hand as the first move. |
| `ReportingLagHigh` | Version lag above a threshold for 10 minutes | Dashboards are stale | Look at consumer errors and `q.reporting.projection` depth |
| `RabbitDown` | Broker scrape missing | Integration is paused; checkout may still commit | Restore the broker, watch outbox age fall |

Thresholds are starting points for a quiet laptop. They will be wrong under a load test. Tuning them is part of Phase 19, not a reason to skip them.

What happens without the DLQ alert: poison messages sit until a report is visibly wrong. What happens without the outbox alert: confirmations look successful and Odoo stays empty.

## Routing

Learning setup: one receiver, the Alertmanager UI, no email and no chat webhook required. Group by alert name so a down service does not create fifty pages.

> **Learning simplification.** UI only, no on-call rotation, no inhibit rules beyond a simple group.
> **Production would require.** A paging provider, a severity that matches customer impact, inhibit rules so "broker down" suppresses the flood of "queue not scraping," and a runbook link that is kept current.

Severity sketch when those labels appear:

- **page** — checkout cannot commit, or outbox/DLQ conditions that mean lost integration
- **ticket** — report lag while checkout is healthy

Do not page on a single 409 `INVALID_STATE_TRANSITION`. That is the domain doing its job.

## Failure of alerting

If Alertmanager is down, Prometheus still stores metrics and can still show pending alerts in its own UI, but nothing groups them. Detection: Alertmanager scrape fails. Recovery: restart it. This is also why a dead-man's-switch must be thought about: a completely dead Prometheus sends nothing, and silence looks like health. A learning-phase substitute is a panel that goes red when samples stop. A production substitute is an external heartbeat. Record that honestly; do not fake an external heartbeat in Compose and call it done.

## Related documents

- [prometheus.md](prometheus.md)
- [failure-scenarios.md](failure-scenarios.md)
- [outbox.md](outbox.md)
