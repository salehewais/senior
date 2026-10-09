"""Fixed-window counters in Redis. A dead Redis fails the limited route closed."""

from __future__ import annotations

import hashlib
import uuid

from order_service.application.rate_limit import RateLimitPolicy
from order_service.domain.exceptions import DependencyUnavailableError, RateLimitedError
from order_service.infrastructure.redis.commands import RedisCommands, RedisUnavailable

_LIMITED = "Too many requests. Try again in a minute."
_UNAVAILABLE = "The rate limit service is unavailable."


def _email_hash(email: str) -> str:
    normalized = email.strip().lower()
    return hashlib.sha256(normalized.encode()).hexdigest()


class RedisRateLimiter:
    def __init__(self, commands: RedisCommands, policy: RateLimitPolicy) -> None:
        self._commands = commands
        self._policy = policy

    def consume_login(self, *, ip: str, email: str) -> None:
        # IP and email hash are separate buckets. The email is not the key and not a metric label.
        limit = self._policy.login_per_minute
        window = self._policy.window_seconds
        ip_count = self._count(f"rl:login:ip:{ip}", window)
        email_count = self._count(f"rl:login:email:{_email_hash(email)}", window)
        if ip_count > limit or email_count > limit:
            raise RateLimitedError(_LIMITED)

    def consume_register(self, *, ip: str) -> None:
        count = self._count(f"rl:register:ip:{ip}", self._policy.window_seconds)
        if count > self._policy.register_per_minute:
            raise RateLimitedError(_LIMITED)

    def consume_order_create(self, *, ip: str, account_id: uuid.UUID) -> None:
        # account_id is a Redis key segment so replicas share one budget.
        # Do not copy it onto a Prometheus label.
        limit = self._policy.order_create_per_minute
        window = self._policy.window_seconds
        ip_count = self._count(f"rl:orders:ip:{ip}", window)
        account_count = self._count(f"rl:orders:account:{account_id}", window)
        if ip_count > limit or account_count > limit:
            raise RateLimitedError(_LIMITED)

    def _count(self, key: str, window_seconds: int) -> int:
        try:
            return self._commands.incr_window(key, window_seconds=window_seconds)
        except RedisUnavailable as exc:
            raise DependencyUnavailableError(_UNAVAILABLE) from exc
