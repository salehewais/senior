# Architecture review

This system is a learning platform on one laptop. It is not production-ready.

Phase 20 does not add a service, a workflow, or a cluster. It reads the system that Phases 0–19 left in the repository and names what is consistent, what was checked, and what still keeps this off a production path. No latency, queue depth, restore time, or scan count is invented here. Where a live run did not happen, the review says so.

## What the system is

A customer uses a React storefront. On its own, Phase 3 runs that UI as a Vite dev server. The full Compose stack and the kind manifests serve the production build with nginx. The browser talks HTTP to Traefik. Traefik is the only public door. It forwards storefront pages, order and catalog calls, and report calls. It does not route `/api/v1/internal`.

The order service is FastAPI, arranged as Clean Architecture: the state machine lives in the domain, use cases commit one database transaction, and HTTP is an adapter. Django owns reporting. Odoo Community 18 owns ERP work: a confirmed order becomes one sales order, and a stock change comes back as `InventoryUpdated`. Each of those three has its own Postgres database: `order_db`, `reporting_db`, and `odoo_db`. They are three servers in Compose, not one server with three databases.

RabbitMQ carries domain events. Redis holds the product cache, the login, register, and order-create counters, and a short lock around an in-flight order create. Orders, the outbox, refresh-token hashes, and processed events stay in Postgres.

There is no payment provider. The architecture diagram still draws one. The order service exposes `payment_circuit_state` and leaves it at 0, with a comment that no provider is wired.

## What is consistent

Strong consistency stops at one database transaction. The order row and its outbox row are added on the same session and commit together (`SqlUnitOfWork` in `services/order-service/src/order_service/infrastructure/database/unit_of_work.py`). If that commit fails, the event is not stored. RabbitMQ is a later confirm. A green HTTP response means the fact is in `order_db`. It does not mean reporting or Odoo has applied it.

Across services, consistency is eventual and delivery is at least once. The publisher can send the same `event_id` again if it crashes after the broker accepts the message and before `published_at` is set. Consumers insert `event_id` as the primary key of `processed_events` in the same transaction as the business write (`ProcessedEventRow` in `services/order-service/src/order_service/infrastructure/database/models.py`, and the same key on `reporting_db.processed_events`). A duplicate conflicts and is acked. It is not applied twice.

The publisher claims pending rows with `SELECT ... FOR UPDATE SKIP LOCKED`, ordered by `created_at`, then `id` (`SqlOutboxLease` in `services/order-service/src/order_service/infrastructure/messaging/outbox_publisher.py`). The kind Deployment `order-outbox-publisher` is one replica (`deploy/kind/order.yaml`). One process is what keeps publish order equal to `created_at`. `SKIP LOCKED` only stops two processes from locking the same row.

Money is an integer number of minor units (`Money.amount_minor` in `services/order-service/src/order_service/domain/value_objects.py`). Prices are not binary floats.

Access tokens are RS256. Login and refresh copy `role` from the account row into the token (`RefreshSession` and the login path in `services/order-service/src/order_service/application/use_cases/auth.py`). The gateway and reporting verify with the public key. They do not hold the private key.

The order state machine allows cancel only from `PENDING`. `CONFIRMED` goes to `PROCESSING`, then `SHIPPED`, then `DELIVERED`. There is no edge from `CONFIRMED` to `CANCELLED` (`ALLOWED_TRANSITIONS` in `services/order-service/src/order_service/domain/entities/order_status.py`).

Reporting refuses a DSN whose database name is `order_db` or `odoo_db` (`services/reporting-service/reporting/config.py`). The Odoo inventory publisher refuses `order_db` and `reporting_db` (`services/odoo/src/commerce_erp/settings.py`). Compose and the kind order Deployment pass the order service only the `order_db` URL. The order-service engine opens `DATABASE_URL` as given and does not itself reject another database name (`services/order-service/src/order_service/infrastructure/database/engine.py`).

The public Traefik rule for the order service is `/api/v1` except `/api/v1/internal` and the report paths (`deploy/compose/dynamic.yaml` and `deploy/gateway/dynamic.yaml`). Fulfillment stays on the order service's own address with `X-Internal-Token`.

Redis is not where orders live. A cache miss reads Postgres. Login, register, and order create fail closed when Redis is down. The in-flight create lock expires; it is not an idempotency table.

Retention deletes only old `DELIVERED` and `CANCELLED` orders, in batches, and only from `order_db` (`TERMINAL_ORDER_STATUSES` in `services/order-service/src/order_service/application/retention.py`). `PENDING`, `CONFIRMED`, `PROCESSING`, and `SHIPPED` stay. Pending and failed outbox rows stay.

The HorizontalPodAutoscaler named `order-service` watches CPU only (`deploy/kind/order.yaml`). It does not watch queue depth.

The GitHub Actions workflow lints, runs the suites that skip when Postgres, RabbitMQ, or Redis is down, and scans dependencies and, in CI, the order-service image. It does not deploy, and it does not start Compose, kind, Locust, the failure lab, or a backup (`.github/workflows/distributed-commerce-ci.yml` in the parent of this directory).

## What was checked, and what was not run

This review read the code, the manifests, the tests, and the phase notes. It did not execute the test suite, and it did not start Docker or a cluster.

These properties are asserted by tests or by static file checks that are already in the tree:

- The legal order edges, including the refusal of `CONFIRMED` to `CANCELLED`, in `services/order-service/tests/unit/test_order_state.py`.
- Outbox rows staged in the business unit of work, in `services/order-service/tests/unit/test_outbox.py`.
- Duplicate `event_id` handling for inventory and for reporting, in `services/order-service/tests/unit/test_reliability.py` and `services/reporting-service/projections/tests/test_apply.py`.
- Gateway rules that omit `/api/v1/internal`, in `deploy/gateway/tests/test_public_routes.py`.
- Kind replica counts, the CPU HPA, and the retention CronJob, in `deploy/kind/test_manifests.py`. Those checks read YAML. They do not create a cluster.
- Compose, the Locust scenario, the failure-lab scripts, and the backup scripts, in `deploy/compose/test_stack.py`, `deploy/load/test_scenario.py`, `deploy/failure-lab/test_lab.py`, and `deploy/backup/test_backup.py`. Those checks read files. They do not talk to a daemon.

These were not run live. No number from them is recorded, because none was measured:

- The full Compose stack was not started for this review. Phases 17, 18, and 19 already say Docker was down on this machine (the engine socket was missing), so Locust was not pointed at the API, the failure-lab stop/start scripts were not run, and `pg_dump` / `pg_restore` was not timed. `deploy/load/RESULTS.md` says the load run did not happen.
- A kind cluster was not created. `deploy/kind/kind-config.yaml` describes one node. That file was not applied here.
- Trivy did not scan an image on this machine. The workflow contains an image-scan job. Phase 16 records that Docker was down, so the order-service image was not built here and was not scanned here.

## Learning simplifications

The README already states these. They are choices for a laptop, not unfinished accidents hiding in the code.

- Database, RabbitMQ, and Odoo passwords in the Compose file and the kind Deployments are local placeholders (`order_service`, `reporting_service`, `odoo`, `admin`).
- Traefik's coarse limit is in memory: 30 requests per second, burst 60, on one gateway replica (`rateLimit` in `deploy/compose/dynamic.yaml`). It is not a budget shared across gateway replicas.
- metrics-server is started with `--kubelet-insecure-tls` (`deploy/kind/metrics-server.yaml`).
- One outbox publisher. A second publisher with `SKIP LOCKED` can still publish a later row first. Partitioning by `aggregate_id` is not implemented.
- The HPA scales the order API on CPU. A consumer can sit idle on CPU while a queue grows. No Prometheus adapter and no KEDA are installed.
- Backups are hand scripts. Nothing schedules them. The Odoo filestore is not in the dump. Redis and RabbitMQ are not dumped.
- No payment provider. `PaymentConfirmed` and `PaymentFailed` are in the catalog. This service does not emit them.
- `saga_status` stays null. The column exists. The order API returns null (`services/order-service/tests/api/test_orders_api.py`).
- The public listener is HTTP. There is no TLS certificate on Traefik. The trace exporter sets `tls.insecure: true` toward Tempo (`deploy/observability/otel/collector.yaml`).
- There is no NetworkPolicy in `deploy/kind`.

## Production gaps

A reviewer can check each line against the file named beside it.

- No off-site backup and no point-in-time recovery. `deploy/backup/dump.sh` writes a custom-format dump under `deploy/backup/dumps/` on this machine. `docs/disaster-recovery.md` says point-in-time recovery for `order_db` is not built.
- No tested RTO. The exercise target in `docs/disaster-recovery.md` is 8 hours. Phase 19 records that no restore was timed. `deploy/backup/dumps/last-restore.txt` is written only when a restore actually runs. It was not produced here.
- No queue-based autoscaler. The only HorizontalPodAutoscaler is CPU on the order API (`deploy/kind/order.yaml`). Consumer Deployments have fixed replica counts.
- No second publisher and no aggregate partitioning. `order-outbox-publisher` is `replicas: 1`, and the comment in that file says partitioning by `aggregate_id` is not implemented.
- Refresh-token reuse does not revoke the family. `RefreshSession` revokes the token just presented and stores a new row with `parent_id` set to that token. A token that is already revoked is rejected and nothing else is revoked (`services/order-service/src/order_service/application/use_cases/auth.py`). `docs/security.md` still says family revocation is not implemented.
- No HTTP idempotency-key table. `docs/api.md` lists `Idempotency-Key` on order writes. The service does not store that key. Order create uses an expiring Redis lock (`services/order-service/src/order_service/infrastructure/redis/order_lock.py`). After the lock expires, the same body can insert another order.
- No payment. Checkout confirms an order without charging anyone. `payment_circuit_state` is a constant 0 in `services/order-service/src/order_service/observability/metrics.py`.
- The order-service container image was not scanned on this machine. The CI job is defined. It did not run here.
- The frontend lockfile still records critical advisories in transitive `tinypool` (GHSA-5gmw-xhrv-c9v3 and GHSA-85c8-ppgw-ccpr), pulled in by the devDependency `vitest`. Phase 16 left that recorded and did not bump vitest. The production-dependency audit is a separate bar. This review does not claim the advisory was fixed.
- The kind cluster is one node (`deploy/kind/kind-config.yaml` has a single `control-plane`). Deleting the cluster deletes the hostPath volumes.
- Secrets are files on the laptop. `deploy/kind/create-secrets.sh` reads PEM files from `deploy/compose/secrets/` and `INTERNAL_SERVICE_TOKEN` from the environment or `deploy/compose/.env`. Database passwords are written in the Deployment manifests. There is no KMS.

## Verdict

This system is a learning platform on one laptop. It is not production-ready.

The boundaries a production commerce system needs are visible: one writer of order state, a database per service, an outbox, idempotent consumers, and a gateway that does not own the domain. The gaps above are what still separate that shape from a system you would run for real customers.
