# Operations and recovery

These commands change running data or containers. They were not executed while writing this note. Read the script before you run it.

## Local stack

```bash
bash deploy/compose/up.sh
docker compose -f deploy/compose/docker-compose.yml down
```

`down` without `-v` keeps named volumes. `up.sh` does not delete volumes. It does not start the saga worker.

## Kind

Requires Docker, kind, and kubectl. If cluster `commerce` exists, `deploy/kind/apply.sh` does not delete it.

```bash
bash deploy/kind/apply.sh
python -m unittest deploy/kind/test_manifests.py
```

Public HTTP is `http://127.0.0.1:8080`. Databases are not published on the host.

## Failure lab

One service at a time. Recovery is the matching `start`.

```bash
bash deploy/failure-lab/rabbitmq.sh stop
bash deploy/failure-lab/rabbitmq.sh start
bash deploy/failure-lab/redis.sh stop
bash deploy/failure-lab/redis.sh start
bash deploy/failure-lab/inventory-consumer.sh stop
bash deploy/failure-lab/inventory-consumer.sh start
bash deploy/failure-lab/reporting-consumer.sh stop
bash deploy/failure-lab/reporting-consumer.sh start
python -m unittest deploy/failure-lab/test_lab.py
```

`test_lab.py` does not stop containers. There is no script here for Postgres, the order API, Odoo, or Django HTTP.

## Backup

Dumps one of `order_db`, `reporting_db`, or `odoo_db`. Does not include `notification_db`, Redis, RabbitMQ, config, or keys. Tests do not perform a live dump or restore.

```bash
bash deploy/backup/dump.sh order_db
bash deploy/backup/restore.sh order_db deploy/backup/dumps/<file>.dump --yes
python -m unittest deploy/backup/test_backup.py
```

Restore is destructive for objects in the named database. `--yes` is required. The archive header must name that database.

## Load

Do not point Locust at a shared system. `deploy/load/RESULTS.md` says no run was measured.

## Secrets

Generate JWT PEMs on the host. `deploy/kind/create-secrets.sh` reads them and does not commit them. `deploy/kind/secrets.example.yaml` is not applied.
