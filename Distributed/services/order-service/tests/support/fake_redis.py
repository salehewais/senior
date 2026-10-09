"""In-memory Redis stand-in. The default test run does not need a server."""

from __future__ import annotations

from order_service.infrastructure.redis.commands import RedisUnavailable


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.ttls: dict[str, int] = {}
        self.fail = False

    def get(self, key: str) -> str | None:
        self._check()
        return self.values.get(key)

    def set(self, key: str, value: str, *, ttl_seconds: int) -> None:
        self._check()
        self.values[key] = value
        self.ttls[key] = ttl_seconds

    def set_if_absent(self, key: str, value: str, *, ttl_seconds: int) -> bool:
        self._check()
        if key in self.values:
            return False
        self.values[key] = value
        self.ttls[key] = ttl_seconds
        return True

    def delete(self, *keys: str) -> None:
        self._check()
        for key in keys:
            self.values.pop(key, None)
            self.ttls.pop(key, None)

    def delete_prefix(self, prefix: str) -> None:
        self._check()
        for key in list(self.values):
            if key.startswith(prefix):
                self.values.pop(key, None)
                self.ttls.pop(key, None)

    def compare_delete(self, key: str, value: str) -> None:
        self._check()
        if self.values.get(key) == value:
            self.values.pop(key, None)
            self.ttls.pop(key, None)

    def incr_window(self, key: str, *, window_seconds: int) -> int:
        self._check()
        current = int(self.values.get(key, "0")) + 1
        self.values[key] = str(current)
        self.ttls[key] = window_seconds
        return current

    def ping(self) -> None:
        self._check()

    def _check(self) -> None:
        if self.fail:
            raise RedisUnavailable("redis down")
