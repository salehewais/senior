# Kubernetes

**Status: Phase 14.** Manifests are in `deploy/kind`, namespace `commerce`. Compose is still the first runtime. This is one kind node on a laptop. Phase 14 adds API replicas, competing consumers, and a CPU HorizontalPodAutoscaler. It is not production.

The cluster is a packaging of the same system. It is not a different architecture. Phase 13 is the first phase allowed to create a cluster. Compose must already run the business path.

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

## Intended shape (Phase 13)

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

Phase 13 proved the port with one replica of each business service. Phase 14 is the replica count. The order API starts at 2, behind the existing Service, with no session affinity. Orders stay in `order_db`. Login and order-create limits stay in Redis, which is why a second API replica does not reset the budget ([ADR-007](adr/ADR-007-why-redis.md)). The outbox publisher stays at 1 replica: the claim uses `FOR UPDATE SKIP LOCKED`, and a second publisher would still break `created_at` order ([outbox.md](outbox.md)).

## Failure

kind failing means the local cluster is gone, not that the architecture changed. Detection: node not ready, pods not scheduled. Recovery: recreate the cluster, reload images, reapply manifests. Persistent volumes go with the cluster unless you designed them not to; treat cluster delete as data loss for local disks and rely on the backup story in [disaster-recovery.md](disaster-recovery.md) if you cared about the data.

Application failure modes do not change: a dead `order_db` still must not block reading `reporting_db`. If both databases share one Postgres pod, that isolation is still the laptop shortcut from [database.md](database.md).

## What we are not adding

No service mesh. Three services behind one gateway do not repay the operational cost of sidecar injection, mTLS automation, and mesh upgrades. Network policy plus the gateway is the isolation tool. A mesh can be an ADR later if the service count grows. It is not a Phase 13 default.

## Scaling (Phase 14)

| Workload | Replicas | What changes the count |
| --- | --- | --- |
| `order-service` | 2 at start | HPA `order-service`, CPU, min 2, max 4, target 70% of the `100m` request |
| `order-inventory-consumer` | 2 | Fixed. Competing consumers on `q.order.inventory` |
| `reporting-consumer` | 2 | Fixed. Competing consumers on `q.reporting.projection` |
| `order-outbox-publisher` | 1 | Fixed, so publish order follows `created_at` |

The API container requests `100m` CPU and `128Mi` memory. The HPA cannot compute a utilization percentage without a request. `deploy/kind/metrics-server.yaml` is metrics-server v0.9.0 with `--kubelet-insecure-tls`, the usual kind workaround. It serves resource metrics. It does not serve queue depth. A Kubernetes Grafana board is still not installed.

CPU on the API is the wrong signal for a consumer that is idle while its queue grows. The metric for that exercise is `rabbitmq_detailed_queue_messages` on the primary queues. It is already graphed (Platform overview, "RabbitMQ primary backlog"; Outbox and broker) and alerted (`RabbitQueueGrowth`). This phase does not install KEDA or a custom metrics adapter. The README section "What you would scale on queue depth" is the exercise.

No CronJob in this phase. Probes are unchanged from Phase 13.

startup means the process has finished booting. readiness means it can take traffic. liveness means it should be restarted.

A pod restart mounts the same PVC. Deleting the cluster deletes the kind node disk, including these hostPath volumes. Redis has no PVC. It is a cache.

> **Learning simplification.** Single-node kind, images loaded locally, HTTP ingress, two API replicas, a CPU HPA, two competing consumers, one publisher, no mesh.
> **Production would require.** Multiple nodes, a registry, TLS, network policies that enforce database-per-service routing, separate data-service operations, and someone on call. This repository will not become that environment by adding manifests.

## Related documents

- [docker.md](docker.md)
- [deployment.md](deployment.md)
- [ADR-008](adr/ADR-008-why-kubernetes.md)
