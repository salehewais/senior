"""One publish and one consume. Skipped when reporting Postgres or RabbitMQ is down."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.integration


def test_published_order_is_projected() -> None:
    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = "reporting.settings"
    env["REPORTING_DATABASE_URL"] = "postgresql://reporting_service:reporting_service@127.0.0.1:5433/reporting_db"
    env.pop("PYTEST_CURRENT_TEST", None)
    migrated = subprocess.run(
        [sys.executable, "manage.py", "migrate", "--noinput"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    if migrated.returncode != 0:
        pytest.fail(migrated.stderr or migrated.stdout)
    order_id = uuid.uuid4()
    event_id = uuid.uuid4()
    body = {
        "event_id": str(event_id),
        "event_type": "OrderCreated",
        "occurred_at": "2026-10-08T15:00:00Z",
        "producer": "order-service",
        "aggregate_id": str(order_id),
        "correlation_id": str(uuid.uuid4()),
        "causation_id": str(uuid.uuid4()),
        "version": 1,
        "payload": {
            "order_id": str(order_id),
            "customer_id": str(uuid.uuid4()),
            "status": "PENDING",
            "items": [
                {
                    "product_id": str(uuid.uuid4()),
                    "sku": "MUG-01",
                    "quantity": 1,
                    "unit_price": {"amount_minor": 1500, "currency": "USD"},
                }
            ],
            "total": {"amount_minor": 1500, "currency": "USD"},
            "aggregate_version": 1,
        },
    }
    from projections.messaging.broker import close_connection, open_connection
    from projections.messaging.topology import EXCHANGE_COMMERCE_EVENTS, declare_reporting_topology

    broker_url = env.get("RABBITMQ_URL", "amqp://order_service:order_service@127.0.0.1:5672/%2F")
    connection = open_connection(broker_url, 2)
    try:
        channel = connection.channel()
        declare_reporting_topology(channel)
        channel.basic_publish(
            exchange=EXCHANGE_COMMERCE_EVENTS,
            routing_key="order.created",
            body=json.dumps(body).encode(),
        )
    finally:
        close_connection(connection, timeout_seconds=2)
    consumer = subprocess.Popen(
        [sys.executable, "manage.py", "consume_events"],
        cwd=ROOT,
        env=env,
    )
    try:
        import psycopg

        deadline = time.time() + 20
        status = None
        while time.time() < deadline:
            with psycopg.connect(
                env["REPORTING_DATABASE_URL"],
                connect_timeout=2,
            ) as db:
                row = db.execute(
                    "SELECT status FROM order_projections WHERE order_id = %s",
                    (order_id,),
                ).fetchone()
            if row is not None:
                status = row[0]
                break
            if consumer.poll() is not None:
                pytest.fail(f"consumer exited early with code {consumer.returncode}")
            time.sleep(0.25)
        assert status == "PENDING"
    finally:
        consumer.send_signal(signal.SIGTERM)
        try:
            consumer.wait(timeout=10)
        except subprocess.TimeoutExpired:
            consumer.kill()
            consumer.wait(timeout=5)
