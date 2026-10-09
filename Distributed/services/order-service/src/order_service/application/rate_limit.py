"""Shared request budgets. The key is a coarse value in Redis, not a metric label."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class RateLimitPolicy:
    """Laptop-demo budgets. One fixed window for every limited route."""

    login_per_minute: int = 5
    register_per_minute: int = 5
    order_create_per_minute: int = 10
    window_seconds: int = 60


class RateLimiter(Protocol):
    def consume_login(self, *, ip: str, email: str) -> None: ...

    def consume_register(self, *, ip: str) -> None: ...

    def consume_order_create(self, *, ip: str, account_id: uuid.UUID) -> None: ...
