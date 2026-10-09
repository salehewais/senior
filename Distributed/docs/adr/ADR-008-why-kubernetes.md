# ADR-008: Why Kubernetes, and why kind after Compose

**Status: Accepted. Implemented in Phase 13** as `deploy/kind`. Compose remains the first runtime. The kind cluster is not production.

## Context

The learning goal includes running the same system under a local orchestrator: probes, a single ingress, and more than one replica of a stateless process. The goal does not include operating a cloud region.

Docker Compose is enough to prove databases, the broker, and service code. It is a poor teacher of scheduling, rolling replacement, and ingress objects. Kubernetes is the usual vocabulary for those, and it is what the later phase should practice.

Doing Kubernetes first would wrap every application bug in cluster machinery.

## Decision

Use Kubernetes only after Docker Compose runs the business path. The local distribution is **kind**.

kind runs upstream Kubernetes nodes as Docker containers, so the Docker install from the Compose phases is reused. Clusters are disposable. Images can be loaded directly onto nodes before we operate a registry. kind does not preinstall our gateway, so Traefik remains an explicit install.

Compose remains the required first runtime. Phase 13 is the earliest phase that may create a cluster.

## Alternatives

| Alternative | Why it lost |
| --- | --- |
| Compose only, forever | Misses probes, rollouts, and ingress as objects. Acceptable for the early phases, not for the stated end of the project. |
| minikube | A good local Kubernetes. Extra profiles and addons, and often more machinery around the same Docker we already have. |
| k3d | Fast and small. Ships opinions (including a default Traefik on k3s) that would hide [ADR-012](ADR-012-why-api-gateway.md). Slightly different from upstream Kubernetes, which is the documentation we want learners to trust. |
| A managed cloud cluster | Accounts, cost, and credentials before the software works on a laptop. Out of scope. |
| kind before any Compose file | Every misconfigured DSN becomes a scheduling problem. Rejected as a sequence, not as a distribution. |

## Consequences

- Two deployment descriptions will exist (Compose and manifests). They can drift. The image and the environment variable names are the shared contract. [../deployment.md](../deployment.md) says hostnames come from configuration so the code does not bake in Compose DNS.
- kind on a laptop is not high availability. A node container is a single point of failure. Do not describe a green kind cluster as production-ready.
- Persistent data inside kind goes away when the cluster is deleted. Treat that as expected, and take the backups in [../disaster-recovery.md](../disaster-recovery.md) if the data matters.
- We will not add a service mesh to "look like production." The mesh would dominate the operational work of three services.
- Some Kubernetes features (autoscaling, network policy) are easy to add as YAML and easy to misunderstand. They wait until a drill needs them. Network policy is the first one that earns its place, because it enforces database isolation. It still waits until the services exist.

## What happens without this decision

The project either never leaves Compose, and the Kubernetes phase is improvised, or it starts from a random manifest set that does not match the exchanges and databases in these docs. Both outcomes throw away Phase 0.
