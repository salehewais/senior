# Run the project

**Status: Extension Phase 7.** One path for local dependencies, the full Compose stack, and kind. The README sections [How to run Phase 1](../README.md#how-to-run-phase-1) through [How to run on kind](../README.md#how-to-run-on-kind) stay where they are. This page points at them.

Checked on this machine on 9 October 2026:

- The `docker` client is `/usr/local/bin/docker` (Docker Engine client 29.8.0, Compose plugin v5.5.1). `docker info` failed. The client could not open `unix:///home/asm/.docker/desktop/docker.sock` (`connect: no such file or directory`). The daemon was not running.
- `kind` is not on `PATH`.
- `kubectl` is not on `PATH`.

The Compose stack and the kind cluster were not started. Nothing below is a record of a successful start.

The directory layout is [project-structure.md](project-structure.md). Cluster shape is [kubernetes.md](kubernetes.md). What the suites cover, and the limit that live Compose and kind were not run on this machine, is [testing.md](testing.md). Dashboards, metrics, and traces are [observability.md](observability.md). Compose as the first runtime is [docker.md](docker.md). Exchanges and retries are [rabbitmq.md](rabbitmq.md). The outbox publisher is [outbox.md](outbox.md). JWT rules are [security.md](security.md).

## Local dependencies

Use this path when a process runs on the host and only its database (and, for the order service, the broker and Redis) runs in Docker. Each service Compose file is smaller than `deploy/compose/docker-compose.yml`. The README section [How to run the full stack](../README.md#how-to-run-the-full-stack) says to stop these projects first when they hold `127.0.0.1:8080`, `127.0.0.1:15672`, or `127.0.0.1:8069`.

On this machine the daemon was down, so these `docker compose` commands were not run.

### Order service

Needs `order_db`, RabbitMQ, and Redis from `services/order-service/compose.yaml` (host ports 5432, 5672, 15672, and 6379). Auth also needs the JWT PEM files from [How to run Phase 2](../README.md#how-to-run-phase-2). This directory has no service README. From `services/order-service`, the commands in [How to run Phase 1](../README.md#how-to-run-phase-1) are:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
docker compose up -d
alembic upgrade head
uvicorn order_service.presentation.app:app --app-dir src --port 8000
```

The saga worker is a second process, documented in [saga-pattern.md](saga-pattern.md):

```bash
python -m order_service.infrastructure.saga.worker
```

`deploy/compose/docker-compose.yml` does not define a saga-worker service. Outbox publish and the inventory consumer are the processes in [How to run Phase 6](../README.md#how-to-run-phase-6) and [How to run Phase 5](../README.md#how-to-run-phase-5).

### Reporting service

Needs `reporting_db` from `services/reporting-service/compose.yaml` (host port 5433) and the RabbitMQ from the order-service Compose file. Copy the order-service public key into `JWT_PUBLIC_KEY_PATH`. This directory has no service README. From `services/reporting-service`, the commands in [How to run Phase 7](../README.md#how-to-run-phase-7) are:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
docker compose up -d
python manage.py migrate
python manage.py consume_events
python manage.py runserver 127.0.0.1:8001
```

`consume_events` and `runserver` are two processes.

### Notification service

Needs `notification_db` from `services/notification-service/compose.yaml` (host port 5435) and RabbitMQ. The commands, including the unit-test run recorded when Docker was down, are in [services/notification-service/README.md](../services/notification-service/README.md). From that directory:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
docker compose up -d
alembic upgrade head
python -m notification_service.http
python -m notification_service.consumer
```

HTTP and the consumer are two processes. The service README is the place for ports, health, and the pytest result from that machine.

### Odoo

Needs `odoo_db` and the Odoo container from `services/odoo/compose.yaml` (host ports 5434 and 8069) and the RabbitMQ from the order-service Compose file. This directory has no service README. From `services/odoo`, the commands in [How to run Phase 8](../README.md#how-to-run-phase-8) are:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
docker compose up -d
python -m commerce_erp.consumer
python -m commerce_erp.publisher
```

The consumer and the publisher are two processes. Set `INTERNAL_SERVICE_TOKEN` to the same value the order service uses. The README section has the sign-in URL and the timeout names.

### Storefront

Needs Node, and an order service or the gateway to call. This directory has no service README. From `services/frontend`, the commands in [How to run Phase 3](../README.md#how-to-run-phase-3) are:

```bash
npm install
npm run dev
```

The dev server is `http://127.0.0.1:5173`. `VITE_API_BASE_URL` defaults to `http://127.0.0.1:8000`. The same section says to set `VITE_API_BASE_URL=http://127.0.0.1:8080` when the gateway is the public path.

The gateway alone, with upstreams still on the host, is [How to run Phase 10](../README.md#how-to-run-phase-10):

```bash
export JWT_PUBLIC_KEY_PATH=$PWD/services/order-service/jwt_public.pem
chmod a+r "$JWT_PUBLIC_KEY_PATH"
docker compose -f deploy/gateway/compose.yaml up -d --build
```

Run that from the `Distributed` root. The published port is `127.0.0.1:8080`.

### React Native

Needs the toolchain recorded in [mobile/react-native-app/README.md](../mobile/react-native-app/README.md). That README has the init, typecheck, Jest, and ESLint commands that were run, and the `npx react-native doctor` result. `npx react-native run-android` was not run. The app was not installed on a device or emulator. The base URL in `src/config.ts` is `http://127.0.0.1:8080`.

## Full Compose

The file is `deploy/compose/docker-compose.yml`. From the `Distributed` root, after the key and env steps in [How to run the full stack](../README.md#how-to-run-the-full-stack):

```bash
mkdir -p deploy/compose/secrets
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out deploy/compose/secrets/jwt_private.pem
openssl rsa -in deploy/compose/secrets/jwt_private.pem -pubout -out deploy/compose/secrets/jwt_public.pem
chmod a+r deploy/compose/secrets/jwt_private.pem deploy/compose/secrets/jwt_public.pem
cp deploy/compose/.env.example deploy/compose/.env
```

Set `INTERNAL_SERVICE_TOKEN` in `deploy/compose/.env`. Then the start command from that same README section:

```bash
docker compose -f deploy/compose/docker-compose.yml up -d --build
```

That command was not run. The daemon socket was missing. The process table, the private ports, and `docker compose -f deploy/compose/docker-compose.yml down` are in [How to run the full stack](../README.md#how-to-run-the-full-stack). Grafana, Prometheus, and Alertmanager URLs are in [How to look at observability](../README.md#how-to-look-at-observability) and [observability.md](observability.md).

## kind

The script is `deploy/kind/apply.sh`. From the `Distributed` root, after the JWT files and `INTERNAL_SERVICE_TOKEN` from the Compose section above:

```bash
bash deploy/kind/apply.sh
```

The script uses `set -euo pipefail`. It exits 1 when `docker info` fails, and it exits 1 when `kind` or `kubectl` is missing. It does not delete a cluster. The longer sequence it replaces is written out in [How to run on kind](../README.md#how-to-run-on-kind). The script also builds `commerce/notification-service:0.1.0`, which that README code block does not list. Follow the script. Manifest checks that do not need a cluster are `python3 deploy/kind/test_manifests.py`. What the manifests mean is [kubernetes.md](kubernetes.md).

`bash deploy/kind/apply.sh` was not run. `kind` and `kubectl` are not on `PATH`, and the Docker daemon was not running.

## Scripts

No new script was added. `deploy/kind/apply.sh` already replaces the repeated kind build, load, and apply sequence, and it exits non-zero when Docker, kind, or kubectl is missing. The full Compose start is the single `docker compose -f deploy/compose/docker-compose.yml up -d --build` command above. A wrapper around that one command was not added. Failure-lab and backup scripts that already exist are `deploy/failure-lab/` and `deploy/backup/`; their README sections are [Failure lab (Phase 18)](../README.md#failure-lab-phase-18) and [Backup and restore (Phase 19)](../README.md#backup-and-restore-phase-19).
