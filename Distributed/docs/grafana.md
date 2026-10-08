# Grafana

**Status: Phase 0 design; not implemented.**

Grafana is how a person looks at Prometheus metrics and, later, traces. It is not the alerting path. Alertmanager owns pages. If both Grafana and Alertmanager raise the same condition, people learn to ignore one of them. See [ADR-010](adr/ADR-010-why-grafana.md).

## Dashboards to build in Phase 17

Names stay stable so lessons and screenshots match.

| Dashboard | Question it answers |
| --- | --- |
| Platform overview | Is the gateway healthy, and are the three services up? |
| Order path | Create and confirm rate, 409 transitions, 5xx, latency |
| Outbox and broker | Unpublished age, queue depth, DLQ depth, publish failures |
| Reporting lag | How far projections sit behind the latest aggregate version |
| Payment | Circuit state, payment success and failure counts |
| Dependencies | Postgres connections, Redis errors, broker up |

Each panel needs a unit and a time range that fits the signal. Outbox age in seconds. Request rate per second. A single "stat" panel with no unit is how a dashboard teaches the wrong lesson.

What happens without shared dashboards: every learner builds a private view, and a failure drill in Phase 19 cannot say "open Outbox and broker." The drill becomes a treasure hunt.

## Access

On a laptop, Grafana is bound to localhost. There is no shared password in git. The default admin password is set from the environment when the container is created, and the documentation never contains the value.

> **Learning simplification.** One Grafana, Prometheus as the only required data source, traces added when the collector is up, no SSO.
> **Production would require.** SSO, locked-down data sources, and dashboard JSON in version control. Editing only through the UI means the next machine does not have the boards.

Dashboard JSON should be committed once it exists, so the picture is reproducible. Phase 0 commits the list above, not fake JSON for boards that have never been opened.

## Failure

Grafana down means humans lose the picture. Alerts still fire if Prometheus and Alertmanager are up. Detection: the UI does not load. Recovery: restart the container. Dashboards are configuration; they should reload from files. Business data is untouched.

Do not query `order_db` from Grafana with a SQL plugin to "see the truth." That shortcut teaches people to bypass the reporting service and, worse, puts a dashboard password on the transactional database. If a board needs business totals, it reads metrics or the reporting API.

## Related documents

- [prometheus.md](prometheus.md)
- [alerting.md](alerting.md)
- [observability.md](observability.md)
