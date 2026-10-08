# Docker Compose

**Status: Phase 0 design; not implemented.**

Compose is the first runtime. kind comes only after the same images behave correctly here. [ADR-008](adr/ADR-008-why-kubernetes.md) explains why the order is fixed. There is no Compose file in this phase.

## What Compose is for

It gives every later phase a single command that starts the data plane and, when they exist, the services, on one Docker network. Logs stay on one machine. A bad environment variable is a container that exits with the database error in plain text.

What happens without it: each learner installs Postgres, RabbitMQ, and Redis by hand, versions drift, and "works on my machine" starts before any business logic exists.

## Intended services

| Compose service | Image role | Host port in learning mode |
| --- | --- | --- |
| `postgres` | One server, databases `order_db`, `reporting_db`, `odoo_db`, three roles | Localhost only, for debugging, removed before any shared demo |
| `rabbitmq` | Broker plus management UI | Localhost only |
| `redis` | Cache and rate limits | Not published on the host |
| `order-service` | FastAPI, from Phase 2 | Internal |
| `reporting-service` | Django, from Phase 10 | Internal |
| `odoo` | ERP, from Phase 13 | Internal, plus a private port if the Odoo UI is needed |
| `frontend` | React static files, from Phase 11 | Internal |
| `gateway` | Traefik | HTTP on the host, the only public door |
| `otel-collector`, `prometheus`, `alertmanager`, `grafana` | From Phase 17 | Grafana on localhost |

Business services join this file in Phase 11, after they already run on their own. Phase 1 may start a single PostgreSQL container for `order_db` while the order service is built. It does not wait for the full stack, and it does not create the kind cluster.

## Rules the file must follow when it appears

- One user-defined network, `commerce`. Services find each other by Compose DNS name.
- Healthchecks on Postgres, RabbitMQ, and Redis before application services depend on them. `depends_on` without a healthcheck only waits for process start, which is how apps crash-loop on a database that is still running init scripts.
- Configuration by environment variables. No secrets baked into images. No secret values committed. A `.env.example` may list variable names with empty or dummy placeholders; a real `.env` stays untracked.
- Three database roles created by the Postgres init script. The order service receives only the `order_db` DSN.
- Volumes for Postgres data, RabbitMQ data, and later Odoo filestore. Redis may use a volume and still be treated as disposable.
- Images tagged with a digest or a git revision once we build our own. The tag `latest` is not a release name.

## Failure

If the Docker daemon is down, nothing runs. That is acceptable for local learning and unacceptable as a production design; production hosts are [kubernetes.md](kubernetes.md)'s problem later, and even then this project is not a production claim.

If a healthcheck is missing, application containers start too early. Detection: connection-refused logs. Recovery: add the healthcheck, restart the stack. Data in volumes survives `docker compose restart`. `docker compose down -v` destroys it; that flag is a deliberate wipe, not a restart.

## Scale

Compose on one machine does not prove horizontal scale. It can start two replicas of a stateless service badly (port clashes, in-memory rate limits). Real multi-replica practice waits for kind, after the single-replica path is correct.

> **Learning simplification.** One host, privileged enough to run Docker, HTTP at the gateway, database ports on localhost.
> **Production would require.** No published database ports, TLS at the gateway, resource limits, and a registry. Compose itself is often replaced by the cluster, which is why the images must not depend on Compose DNS names hardcoded in application logic. Use configuration for hostnames.

## Related documents

- [deployment.md](deployment.md)
- [kubernetes.md](kubernetes.md)
- [disaster-recovery.md](disaster-recovery.md)
