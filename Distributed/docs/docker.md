# Docker Compose

**Status: Phase 11 ships the platform file at `deploy/compose/docker-compose.yml`.** Phase 10's gateway-only file remains at `deploy/gateway/compose.yaml` for apps already running on the host. The per-service files under `services/` remain for the same reason. Kubernetes is Phase 13 and is not started here.

Compose is the first runtime. kind comes only after the same images behave correctly here. [ADR-008](adr/ADR-008-why-kubernetes.md) explains why the order is fixed.

## What Compose is for

It gives every later phase a single command that starts the data plane and, when they exist, the services, on one Docker network. Logs stay on one machine. A bad environment variable is a container that exits with the database error in plain text.

What happens without it: each learner installs Postgres, RabbitMQ, and Redis by hand, versions drift, and "works on my machine" starts before any business logic exists.

## Intended services

| Compose service | Image role | Host port in the Phase 11 file |
| --- | --- | --- |
| `postgres` | `order_db` only, role `order_service` | Not published |
| `reporting-postgres` | `reporting_db` only, role `reporting_service` | Not published |
| `odoo-db` | `odoo_db` only, role `odoo` | Not published |
| `rabbitmq` | Broker plus management UI | Management UI on `127.0.0.1:15672` only. AMQP is not published |
| `redis` | Cache and rate limits | Not published |
| `order-service` | FastAPI, plus migrate, outbox publisher, and inventory consumer | Internal |
| `reporting-service` | Django, plus migrate and `consume_events` | Internal |
| `odoo` | Odoo 18, plus the OrderConfirmed consumer and the inventory publisher | UI on `127.0.0.1:8069` |
| `frontend` | React production build behind nginx | Internal |
| `gateway` | Traefik, with `jwt-check` | `127.0.0.1:8080`, the only public door |
| `otel-collector`, `tempo`, `prometheus`, `alertmanager`, `grafana`, exporters | Phase 12. Grafana `127.0.0.1:3000`, Prometheus `127.0.0.1:9090`, Alertmanager `127.0.0.1:9093`. Exporters are not published | Learning only. Not a production deploy |

The early design sketched one Postgres server with three databases and three roles. That shared server is a fate-sharing shortcut: one process dying takes orders, reports, and Odoo together, and host port 5432 is often already taken. Phase 11 uses three Postgres services instead. Each has one role and one database, and no host port. The order service still receives only the `order_db` URL.

Phase 1 may still start a single PostgreSQL container for `order_db` from `services/order-service/compose.yaml` while that service is developed on the host. That file is not the full stack, and it does not create the kind cluster.

## Rules the file follows

- One user-defined network, `commerce`. Services find each other by Compose DNS name.
- Healthchecks on Postgres, RabbitMQ, and Redis before application services depend on them. `depends_on` without a healthcheck only waits for process start, which is how apps crash-loop on a database that is still running init scripts.
- Configuration by environment variables. No secrets baked into images. No secret values committed. A `.env.example` may list variable names with empty or dummy placeholders; a real `.env` stays untracked.
- Three database roles, one per Postgres service (`order_service`, `reporting_service`, `odoo`). The order service receives only the `order_db` DSN. A single server with three databases would be the shortcut above, and this file does not use it.
- Volumes for Postgres data, RabbitMQ data, and the Odoo filestore. Redis has no volume: persistence is off, and Redis is not a system of record.
- Built images are tagged `0.1.0` (Odoo `18.0.1`), not `latest`.

## Failure

If the Docker daemon is down, nothing runs. That is acceptable for local learning and unacceptable as a production design; production hosts are [kubernetes.md](kubernetes.md)'s problem later, and even then this project is not a production claim.

If a healthcheck is missing, application containers start too early. Detection: connection-refused logs. Recovery: add the healthcheck, restart the stack. Data in volumes survives `docker compose restart`. `docker compose down -v` destroys it; that flag is a deliberate wipe, not a restart.

## Scale

Compose on one machine does not prove horizontal scale. It can start two replicas of a stateless service badly (port clashes, in-memory rate limits). Real multi-replica practice waits for kind, after the single-replica path is correct.

> **Learning simplification.** One host, privileged enough to run Docker, HTTP at the gateway. The full stack does not publish database ports. The per-service files still bind them to localhost for debugging.
> **Production would require.** No published database ports, TLS at the gateway, resource limits, and a registry. Compose itself is often replaced by the cluster, which is why the images must not depend on Compose DNS names hardcoded in application logic. Use configuration for hostnames.

## Related documents

- [deployment.md](deployment.md)
- [kubernetes.md](kubernetes.md)
- [disaster-recovery.md](disaster-recovery.md)
