"""Commands the cache and the limiters share. Callers choose fail-open or fail-closed."""

from __future__ import annotations

from typing import Protocol


class RedisUnavailable(Exception):
    """The cache process did not answer before the socket timeout."""


class RedisCommands(Protocol):
    def get(self, key: str) -> str | None: ...

    def set(self, key: str, value: str, *, ttl_seconds: int) -> None: ...

    def set_if_absent(self, key: str, value: str, *, ttl_seconds: int) -> bool: ...

    def delete(self, *keys: str) -> None: ...

    def delete_prefix(self, prefix: str) -> None: ...

    def compare_delete(self, key: str, value: str) -> None: ...

    def incr_window(self, key: str, *, window_seconds: int) -> int: ...

    def ping(self) -> None: ...
