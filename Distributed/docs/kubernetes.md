# Kubernetes

**Status: Phase 0 design; not implemented.**

The cluster is a later packaging of the same system. It is not a different architecture. Phase 18 is the first phase allowed to create a cluster. Compose must already run the business path.

## Choice: kind

**kind** (Kubernetes in Docker) is the local distribution.

Why kind:

- The project already requires Docker for Compose. kind runs cluster nodes as containers. There is no second hypervisor to feed.
- The control plane is upstream Kubernetes. Objects you write (Deployment, Service, Ingress, probes) match upstream documentation.
- Clusters are disposable. Deleting one does not uninstall Docker or the images you already built.
- `kind load docker-image` puts a locally built image onto nodes without a registry. That is the right first step. A registry can come once the manifests work.
- kind does not install an ingress controller for you. We install Traefik on purpose, which matches [ADR-012](adr/ADR-012-why-api-gateway.md). The gateway stays a decision instead of a distro default.

Alternatives, and why they wait:

| Option | Why not first |
| --- | --- |
| minikube | A solid local cluster, with an extra profile and addon layer. Often heavier. We would be learning minikube and the platform at once. |
| k3d / k3s | Fast, and Traefik is bundled. Bundled Traefik hides the gateway install. k3s also replaces some upstream components, so a manifest that works there can still surprise you on a stock cluster. |
| A hosted cluster | Cost and credentials before the Compose path is proven. Out of scope for this learning project. |

## Why Compose comes first

1. You learn what the process actually needs: environment, ports, health, volumes, and startup order.
2. A failed database migration is one container log, not a Job object plus a CrashLoopBackOff plus an ingress timeout.
3. The event path (commit, outbox, broker, consumer) can be watched with ordinary tools.
4. Kubernetes then adds scheduling, probes, rolling updates, resource limits, and ingress on top of images you trust.

Starting in YAML before any of that works teaches the control plane and hides the bug.

## Intended shape (Phase 18)

| Kubernetes idea | What it maps from |
| --- | --- |
| Namespace `commerce` | The Compose network boundary |
| Deployment per stateless service | `order-service`, `reporting-service`, `frontend`, `gateway` |
| Stateful handling for Postgres, RabbitMQ, Odoo | Volumes. A laptop may still run them as single replicas. |
| Service | Stable DNS inside the namespace |
| Ingress via Traefik | The only public HTTP entry, with host port mapping on the kind node |
| Probes | Live versus ready. Ready fails when that process's database is unreachable. |
| Resource requests | Small, explicit, so a local cluster does not overcommit silently |
| ConfigMap and Secret | Non-secret config versus credentials. Secrets are still not committed. |

One replica of each business service is enough to prove the port. A second order-service replica is the optional stretch, to show that rate limits and outbox publishing need the designs in [outbox.md](outbox.md) and [ADR-007](adr/ADR-007-why-redis.md).

## Failure

kind failing means the local cluster is gone, not that the architecture changed. Detection: node not ready, pods not scheduled. Recovery: recreate the cluster, reload images, reapply manifests. Persistent volumes go with the cluster unless you designed them not to; treat cluster delete as data loss for local disks and rely on the backup story in [disaster-recovery.md](disaster-recovery.md) if you cared about the data.

Application failure modes do not change: a dead `order_db` still must not block reading `reporting_db`. If both databases share one Postgres pod, that isolation is still the laptop shortcut from [database.md](database.md).

## What we are not adding

No service mesh. Three services behind one gateway do not repay the operational cost of sidecar injection, mTLS automation, and mesh upgrades. Network policy plus the gateway is the isolation tool. A mesh can be an ADR later if the service count grows. It is not a Phase 18 default.

No horizontal pod autoscaler until something has been measured. Autoscaling an empty metric is theater.

> **Learning simplification.** Single-node kind, images loaded locally, HTTP ingress, one replica, no mesh.
> **Production would require.** Multiple nodes, a registry, TLS, network policies that enforce database-per-service routing, separate data-service operations, and someone on call. This repository will not become that environment by adding manifests.

## Related documents

- [docker.md](docker.md)
- [deployment.md](deployment.md)
- [ADR-008](adr/ADR-008-why-kubernetes.md)
