# Notification service

Extension Phase 3. Flask, `notification_db`, and a RabbitMQ consumer. Email and push are mocks. The design is [docs/flask-notification-service.md](../../docs/flask-notification-service.md).

`config.py` reads the environment and still refuses any database other than `notification_db`. HTTP routes live in `api` and call `services` instead of the store. `persistence` owns the tables. `messaging` owns the queue, settlement, and consumer loop. The process commands stay `python -m notification_service.http` and `python -m notification_service.consumer`.

This machine has Python 3.12.3 at `/usr/bin/python3`. The commands below were run from this directory on 9 October 2026. `python -m pytest` reported 9 passed and 2 skipped. Docker was not running, so the Compose database and the broker were not started. The skipped tests are `test_notification_db_stores_a_device_token` (nothing was listening on `127.0.0.1:5435`) and `test_broker_declares_the_notification_queue` (nothing was listening on `127.0.0.1:5672`).

## Unit tests

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
ruff check src tests
python -m pytest
```

`GET /health/live` does not open a database. The unit tests cover that with Flask's test client.

## Database on the host

When Docker is running, this file starts only `notification_db` on `127.0.0.1:5435`. It does not start `order_db`.

```bash
docker compose up -d
alembic upgrade head
```

`alembic upgrade head` was not run here, because Docker was down and port 5435 was closed.

## Processes

HTTP, after the migration has been applied:

```bash
python -m notification_service.http
```

That listens on `0.0.0.0:8002`. Readiness is `GET /health/ready`, which runs `SELECT 1` on `notification_db`.

Consumer, in another shell with the same virtualenv:

```bash
python -m notification_service.consumer
```

It exits if `notification_db` does not answer. Metrics for that process listen on port 9100. It declares `q.notification.delivery` on the broker from `RABBITMQ_URL` (default `amqp://order_service:order_service@127.0.0.1:5672/%2F`).

The full stack, including this image, is `deploy/compose/docker-compose.yml`. That file does not publish port 8002. The gateway reaches `http://notification-service:8002`.
