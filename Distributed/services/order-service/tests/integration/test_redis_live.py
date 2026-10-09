"""Live Redis. Skipped when the Phase 9 server is not reachable."""

from __future__ import annotations

import uuid

import pytest

from order_service.infrastructure.redis.client import RedisClient
from order_service.infrastructure.redis.commands import RedisUnavailable
from order_service.infrastructure.settings import Settings


def test_redis_round_trip_when_the_server_is_up() -> None:
    settings = Settings()
    client = RedisClient(
        settings.redis_url,
        connect_timeout=settings.redis_socket_connect_timeout_seconds,
        socket_timeout=settings.redis_socket_timeout_seconds,
    )
    try:
        client.ping()
    except RedisUnavailable:
        client.close()
        pytest.skip("Redis is not running. From services/order-service: docker compose up -d redis")
    key = f"catalog:product:probe-{uuid.uuid4()}"
    window = f"rl:probe:{uuid.uuid4()}"
    try:
        client.set(key, '{"active":true}', ttl_seconds=10)
        assert client.get(key) == '{"active":true}'
        assert client.incr_window(window, window_seconds=10) == 1
        client.delete(key)
        assert client.get(key) is None
    finally:
        client.delete(key, window)
        client.close()
