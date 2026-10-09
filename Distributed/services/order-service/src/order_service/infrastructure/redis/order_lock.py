"""In-flight duplicate suppressor for order create. Not an exactly-once record.

The key expires. The request releases it when it finishes. A crash before release
holds the key only until the TTL. After that, the same create inserts another order
in Postgres. The durable HTTP idempotency row is http_idempotency_keys, and this
phase does not add that table. This lock is not that row.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass

from order_service.domain.exceptions import DependencyUnavailableError, IdempotencyInProgressError
from order_service.infrastructure.redis.commands import RedisCommands, RedisUnavailable

logger = logging.getLogger("order_service")

_IN_PROGRESS = "An identical order create is already running."
_UNAVAILABLE = "The rate limit service is unavailable."


def order_lock_key(account_id: uuid.UUID, lines: list[tuple[uuid.UUID, int]]) -> str:
    ordered = sorted((str(product_id), quantity) for product_id, quantity in lines)
    body = ",".join(f"{product_id}:{quantity}" for product_id, quantity in ordered)
    digest = hashlib.sha256(f"{account_id}|{body}".encode()).hexdigest()
    return f"lock:order-create:{digest}"


@dataclass(frozen=True, slots=True)
class HeldOrderLock:
    key: str
    token: str


class RedisOrderLock:
    def __init__(self, commands: RedisCommands, *, ttl_seconds: int) -> None:
        if ttl_seconds <= 0:
            raise ValueError("The order-create lock must expire so a crash cannot hold it forever.")
        self._commands = commands
        self._ttl_seconds = ttl_seconds

    def acquire(self, *, account_id: uuid.UUID, lines: list[tuple[uuid.UUID, int]]) -> HeldOrderLock:
        key = order_lock_key(account_id, lines)
        token = uuid.uuid4().hex
        try:
            stored = self._commands.set_if_absent(key, token, ttl_seconds=self._ttl_seconds)
        except RedisUnavailable as exc:
            raise DependencyUnavailableError(_UNAVAILABLE) from exc
        if not stored:
            raise IdempotencyInProgressError(_IN_PROGRESS)
        return HeldOrderLock(key=key, token=token)

    def release(self, held: HeldOrderLock) -> None:
        try:
            self._commands.compare_delete(held.key, held.token)
        except RedisUnavailable:
            # The order, if it committed, is already in Postgres. The TTL drops the marker.
            logger.warning("order create lock release failed; the ttl will expire the key")
