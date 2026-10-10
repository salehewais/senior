# Project architecture

This note is the maintainable companion to `STRUCTURE.html`. The HTML page is the primary reading surface. Claims below were checked against the files named here.

## Boundaries

- The order service is the only writer of orders, in `order_db`.
- Reporting, notifications, and Odoo each have their own Postgres database.
- The browser and the React Native client talk to Traefik. They do not open Postgres, RabbitMQ, Redis, or Odoo.
- Odoo fulfillment calls `http://order-service:8000` on the private network. `/api/v1/internal` is not a public Traefik route.
- Redis is cache and shared rate limits. Compose starts it with persistence disabled.
- The saga worker (`python -m order_service.infrastructure.saga.worker`) is not a Compose service and is not in the kind kustomization.

## Packaging

- Local full stack: `deploy/compose/docker-compose.yml`, started by `deploy/compose/up.sh`.
- Kind: `deploy/kind/apply.sh` then `kubectl apply -k deploy/kind`. `kustomization.yaml` is the apply list. `secrets.example.yaml` is not in that list.
- Host exposure on kind is `127.0.0.1:8080` only (`deploy/kind/kind-config.yaml`).

## Messaging

Declared in `services/order-service/src/order_service/infrastructure/messaging/topology.py` plus `services/notification-service/src/notification_service/topology.py` for `q.notification.delivery`.

Durable topic exchanges: `commerce.events`, `erp.events`, `commerce.retry`, `commerce.dlx`. Direct exchange: `commerce.commands`. Retry delays: 5s, 30s, 2min, 10min, 30min, then the DLQ. Consumers prefetch 10 and ack after publishing the retry. Primary queues do not set `x-dead-letter-exchange`.

The outbox publisher confirms to the broker. That is not a distributed transaction with reporting or Odoo.

## Gateway

`jwt_check.py` accepts RS256 access tokens with `exp`, `iat`, `sub`, and `token_type=access`. It does not authorize roles. The Go plugin strips client identity headers. Public auth posts are register, login, refresh, and logout.

## Observability

Prometheus scrapes `/metrics` directly. The collector pipeline is traces only (`deploy/observability/otel/collector.yaml`). Grafana file-provisions six dashboards. Alertmanager posts to `webhook/hook.py`, which logs JSON and does not send mail.

## What this note does not claim

No live cluster, restore, or load test was executed for this write-up. `deploy/load/RESULTS.md` says the load test did not run.
