# Load balancing

**Status: Extension Phase 4.** This page describes the HTTP path already in the kind manifests and in Compose. It does not add a gateway or a monitoring stack. The React Native client at `mobile/react-native-app` uses this same gateway path. It does not add a balancer. Probes, queue depth, metrics, and what the suites cover stay in the pages linked below.

This page was written by reading the files. Docker and kind were not used. No request count per pod was collected. No equal-distribution result was measured.

## Who receives the request

On kind, an order API request follows Ingress → Traefik → Service `order-service` → order pods. Two Traefik processes are already in `deploy/kind/gateway.yaml`, both image `traefik:v3.5.0`. This phase leaves both of them as they are.

| Step | What the file says | Where |
| --- | --- | --- |
| Ingress | Ingress `public`, class `traefik`, path `/` with `pathType: Prefix`, backend Service `gateway` port 80 | `deploy/kind/ingress.yaml` |
| Ingress controller | Deployment `ingress`, `replicas: 1`. Static config `deploy/kind/traefik-ingress.yaml` sets provider `kubernetesIngress` for namespace `commerce` and does not load the route file. Service `ingress` is `NodePort` `30080` | `deploy/kind/gateway.yaml` |
| Commerce gateway | Deployment `gateway`, `replicas: 1`. `deploy/kind/apply.sh` builds ConfigMap `gateway-config` from `deploy/kind/traefik-gateway.yaml` and `deploy/compose/dynamic.yaml`. The static file uses provider `file` at `/etc/traefik/dynamic.yaml` | `deploy/kind/gateway.yaml`, `deploy/kind/apply.sh` |
| Traefik upstream | Service `order` has one `loadBalancer` server, `http://order-service:8000`. Routers `auth-public` and `order-api` both name that service | `deploy/compose/dynamic.yaml` |
| Kubernetes Service | Service `order-service`, `type: ClusterIP`, port 8000, `targetPort: http`, selector `app.kubernetes.io/name: order-service`. The spec has no `sessionAffinity` field. The comment on the Deployment says either replica can serve a request | `deploy/kind/order.yaml` |
| Pods | Pods of Deployment `order-service` whose readiness probe succeeds | `deploy/kind/order.yaml` |

`http://order-service:8000` is one URL. The route file does not list pod addresses. The Service selector is what selects the pods. `deploy/gateway/dynamic.yaml` is the other route file, used when the applications run on the host. Its order URL is `http://host.docker.internal:8000`. `apply.sh` does not mount that file into the kind gateway.

## Replica count, readiness, HPA, grace period

Deployment `order-service` starts at 2 replicas. Readiness is `GET /health/ready`. Probe timings, the HPA, and the other replica counts are [kubernetes.md](kubernetes.md).

`deploy/kind/test_manifests.py` reads these objects. It does not create a cluster. What that style of test is for is [testing.md](testing.md). Queue depth and competing consumers are [rabbitmq.md](rabbitmq.md). Gateway and service metrics are [observability.md](observability.md). The outbox publisher replica is [outbox.md](outbox.md). JWT forward-auth on this path is [security.md](security.md).

## Compose

`deploy/compose/docker-compose.yml` defines one `order-service` service and no replica field. Compose runs one container per service. The same `deploy/compose/dynamic.yaml` then points `http://order-service:8000` at that single container. Compose is a single container and is not the kind Service that selects the order pods.

That Compose service sets `stop_grace_period: 20s` and a healthcheck that opens `http://127.0.0.1:8000/health/ready`. Those lines belong to the one container.

## Traffic

The manifests already show the replica count, the readiness probe, and the HPA. No traffic observation was added. No pod log, access log, or Prometheus query was taken for a per-pod split. No equal-distribution result was measured.

The product cache those replicas share is [caching-strategy.md](caching-strategy.md).
