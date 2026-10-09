# Deployment

**Status: Phase 14.** Compose remains the first runtime. `deploy/kind` is the cluster packaging. The order API Deployment starts at 2 replicas. The outbox publisher stays at 1.

Deployment means moving a known revision onto Compose, and then onto kind, without inventing configuration on the host by hand.

## Order of runtimes

1. Developer machine, Docker Compose, Phase 1 onward.
2. kind, Phase 13, using the images Compose already ran. Manifests are in `deploy/kind`.
3. Nothing beyond that is in scope. No cloud account is assumed.

Skipping to kind copies untested process assumptions into manifests. [kubernetes.md](kubernetes.md) keeps that gate.

## What a later deploy contains

| Piece | Rule |
| --- | --- |
| Application image | Built from a known git revision. Tag is the revision, not `latest`. |
| Schema change | Alembic, Django migrations, or Odoo `-u` for that service only, before or as the new process starts serving. |
| Topology | Applied from the repo before publishers start, whenever queues changed. |
| Config | Environment or ConfigMap. Hostnames are configuration, not constants buried in code that only work under Compose DNS. |
| Secrets | Injected at runtime. Absent from images and git. |
| Gateway | Routes from [api.md](api.md). A new route is a gateway change and a service change, reviewed together. |

## Rolling a service

Stateless API replicas can be replaced one at a time once more than one replica exists. Database migrations must be compatible with the code still running during the rollout (expand, then switch, then contract). A migration that drops a column and a deploy that still reads it will fail in the window where both are alive. That window always exists once you run two replicas or a slow restart.

The outbox publisher stays one replica until the partition scheme in [outbox.md](outbox.md) exists. Phase 14 does not copy the API replica count onto that Deployment. Two publishers would be a bug, not high availability.

Odoo upgrades are the riskiest local step because they mix a module update with `odoo_db`. Take the backup in [disaster-recovery.md](disaster-recovery.md) first, even on a laptop, once you care about the data.

## Checks before calling a deploy good

- Gateway returns a route to the order service and to reporting.
- Readiness is green only when that service's database is reachable.
- A create, a confirm, a projection update, and a rejected illegal cancel all behave as in [api.md](api.md) and [failure-scenarios.md](failure-scenarios.md).
- Outbox oldest age returns to a small number after the journey.
- No new DLQ depth.

## Rollback

Roll back the image when the migration was compatible. When the migration was destructive, roll forward with a fix. Practice saying which case you are in before you start. Kubernetes and Compose will both happily restart last week's image against this week's schema and produce errors that look like application bugs.

Detection of a bad deploy: the checks above, plus the alerts in [alerting.md](alerting.md) once they exist. Recovery: previous image or forward fix, then the same journey test. Do not restore a database backup as a casual rollback; it discards committed orders. Prefer a forward fix unless the new code corrupted data.

## What this project will not automate yet

No GitOps controller, no progressive delivery, no multi-region. Those need a system that already deploys plainly. Adding them in Phase 0 would document tools with nothing to deploy.

> **Learning simplification.** Manual commands, one environment, HTTP, revision tags chosen by the human running the drill.
> **Production would require.** A pipeline, environment separation, TLS, migration locks, and the backup taken automatically before an Odoo upgrade.

## Related documents

- [docker.md](docker.md)
- [kubernetes.md](kubernetes.md)
- [database.md](database.md)
