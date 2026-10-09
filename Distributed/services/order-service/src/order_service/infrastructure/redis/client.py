"""redis-py adapter. Connect and command timeouts are required so a hung server cannot stall a request."""

from __future__ import annotations

import redis
from redis.backoff import NoBackoff
from redis.retry import Retry

from order_service.infrastructure.redis.commands import RedisUnavailable

# Fixed window. If INCR lands and the process dies before EXPIRE, the next call repairs a missing TTL.
_INCR_WINDOW = """
local current = redis.call('INCR', KEYS[1])
if redis.call('TTL', KEYS[1]) < 0 then
  redis.call('EXPIRE', KEYS[1], tonumber(ARGV[1]))
end
return current
"""

# Release only the lock this request holds. A late release must not delete a newer holder's key.
_COMPARE_DELETE = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
  return redis.call('DEL', KEYS[1])
end
return 0
"""


class RedisClient:
    def __init__(self, url: str, *, connect_timeout: float, socket_timeout: float) -> None:
        if connect_timeout <= 0 or socket_timeout <= 0:
            raise ValueError("Redis timeouts must be positive so a hung server cannot stall a request.")
        self.connect_timeout = connect_timeout
        self.socket_timeout = socket_timeout
        # retry attempts is 0: one try, then RedisUnavailable. retry_on_timeout would multiply the wait.
        self._client = redis.Redis.from_url(
            url,
            decode_responses=True,
            socket_connect_timeout=connect_timeout,
            socket_timeout=socket_timeout,
            retry_on_timeout=False,
            retry=Retry(NoBackoff(), 0),
            health_check_interval=0,
        )

    def close(self) -> None:
        self._client.close()

    def get(self, key: str) -> str | None:
        value = self._run(lambda: self._client.get(key))
        if value is None:
            return None
        return str(value)

    def set(self, key: str, value: str, *, ttl_seconds: int) -> None:
        self._run(lambda: self._client.set(key, value, ex=ttl_seconds))

    def set_if_absent(self, key: str, value: str, *, ttl_seconds: int) -> bool:
        stored = self._run(lambda: self._client.set(key, value, nx=True, ex=ttl_seconds))
        return bool(stored)

    def delete(self, *keys: str) -> None:
        if not keys:
            return
        self._run(lambda: self._client.delete(*keys))

    def delete_prefix(self, prefix: str) -> None:
        pattern = f"{prefix}*"

        def run() -> None:
            cursor = 0
            while True:
                cursor, keys = self._client.scan(cursor=cursor, match=pattern, count=100)
                if keys:
                    self._client.delete(*keys)
                if cursor == 0 or cursor == "0":
                    break

        self._run(run)

    def compare_delete(self, key: str, value: str) -> None:
        self._run(lambda: self._client.eval(_COMPARE_DELETE, 1, key, value))

    def incr_window(self, key: str, *, window_seconds: int) -> int:
        count = self._run(lambda: self._client.eval(_INCR_WINDOW, 1, key, str(window_seconds)))
        return int(count)

    def ping(self) -> None:
        self._run(lambda: self._client.ping())

    def _run(self, fn):
        try:
            return fn()
        except (redis.RedisError, OSError, TimeoutError) as exc:
            raise RedisUnavailable("Redis did not answer in time.") from exc
