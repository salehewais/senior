"""JSON cache of the public product view. A miss, or a dead Redis, reads order_db.

A request can read Postgres before a product update commits, then write this cache
after that update has deleted the key. The cached price is then the old one.
The TTL is the backstop. Deleting the key after commit is not a lock around the fill.
"""

from __future__ import annotations

import json
import logging
import time
import uuid

from order_service.application.dto import MoneyView, ProductView
from order_service.infrastructure.redis.commands import RedisCommands, RedisUnavailable
from order_service.observability.metrics import record_product_cache

logger = logging.getLogger("order_service")

PRODUCT_PREFIX = "catalog:product:"
LIST_PREFIX = "catalog:list:"

def product_cache_key(product_id: uuid.UUID) -> str:
    return f"{PRODUCT_PREFIX}{product_id}"


def list_cache_key(*, limit: int, offset: int) -> str:
    return f"{LIST_PREFIX}{limit}:{offset}"


def _dump_product(view: ProductView) -> str:
    payload = {
        "id": str(view.id),
        "sku": view.sku,
        "name": view.name,
        "unit_price": {
            "amount_minor": view.unit_price.amount_minor,
            "currency": view.unit_price.currency,
        },
        "active": view.active,
        "version": view.version,
    }
    return json.dumps(payload, separators=(",", ":"), sort_keys=True)


def _load_product(data: object) -> ProductView:
    if not isinstance(data, dict):
        raise TypeError("product cache entry is not an object")
    price = data["unit_price"]
    if not isinstance(price, dict):
        raise TypeError("product cache price is not an object")
    active = data["active"]
    if not isinstance(active, bool):
        raise TypeError("product cache active flag is not a boolean")
    return ProductView(
        id=uuid.UUID(str(data["id"])),
        sku=str(data["sku"]),
        name=str(data["name"]),
        unit_price=MoneyView(int(price["amount_minor"]), str(price["currency"])),
        active=active,
        version=int(data["version"]),
    )


def _load_product_json(raw: str) -> ProductView:
    return _load_product(json.loads(raw))


class ProductCatalogCache:
    def __init__(self, commands: RedisCommands, *, ttl_seconds: int) -> None:
        if ttl_seconds <= 0:
            raise ValueError("The product cache TTL is the backstop for a stale fill. It must be positive.")
        self._commands = commands
        self._ttl_seconds = ttl_seconds

    def get_product(self, product_id: uuid.UUID) -> ProductView | None:
        raw, elapsed = self._read(product_cache_key(product_id), operation="get")
        if raw is None:
            return None
        try:
            view = _load_product_json(raw)
        except (TypeError, ValueError, KeyError, json.JSONDecodeError):
            record_product_cache(operation="get", result="miss", seconds=elapsed)
            return None
        record_product_cache(operation="get", result="hit", seconds=elapsed)
        return view

    def put_product(self, view: ProductView) -> None:
        self._write(product_cache_key(view.id), _dump_product(view))

    def get_list(self, *, limit: int, offset: int) -> list[ProductView] | None:
        raw, elapsed = self._read(list_cache_key(limit=limit, offset=offset), operation="list")
        if raw is None:
            return None
        try:
            data = json.loads(raw)
            if not isinstance(data, list):
                raise TypeError("product list cache entry is not a list")
            views = [_load_product(item) for item in data]
        except (TypeError, ValueError, KeyError, json.JSONDecodeError):
            record_product_cache(operation="list", result="miss", seconds=elapsed)
            return None
        record_product_cache(operation="list", result="hit", seconds=elapsed)
        return views

    def put_list(self, views: list[ProductView], *, limit: int, offset: int) -> None:
        body = "[" + ",".join(_dump_product(view) for view in views) + "]"
        self._write(list_cache_key(limit=limit, offset=offset), body)

    def invalidate(self, product_id: uuid.UUID) -> None:
        """Drop this product and every cached list page. Call this after the database commit.

        A reader that already loaded the old row can put it back after this delete.
        That stale value lives until the TTL. This method does not prevent that race.
        """

        try:
            self._commands.delete(product_cache_key(product_id))
            self._commands.delete_prefix(LIST_PREFIX)
        except RedisUnavailable:
            logger.warning("product cache invalidation failed; the ttl is the backstop")

    def _read(self, key: str, *, operation: str) -> tuple[str | None, float]:
        """Return the stored JSON and the read time, or `(None, seconds)` to stop.

        A missing key is a miss. `RedisUnavailable` is an error. Both return None
        so the caller reads `order_db`. A present payload is not a hit until the
        caller parses it; a payload that does not parse is a miss. There is no
        single-flight lock around this read.
        """

        started = time.perf_counter()
        try:
            raw = self._commands.get(key)
        except RedisUnavailable:
            elapsed = time.perf_counter() - started
            record_product_cache(operation=operation, result="error", seconds=elapsed)
            logger.debug("product cache read skipped; using the database")
            return None, elapsed
        elapsed = time.perf_counter() - started
        if raw is None:
            record_product_cache(operation=operation, result="miss", seconds=elapsed)
            return None, elapsed
        return raw, elapsed

    def _write(self, key: str, value: str) -> None:
        try:
            self._commands.set(key, value, ttl_seconds=self._ttl_seconds)
        except RedisUnavailable:
            logger.debug("product cache fill skipped")
