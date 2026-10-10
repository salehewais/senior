"""Fake Redis. The default run does not open a server."""

from __future__ import annotations

import json
import socket
import threading
import time
import uuid

import pytest
from tests.support.clock import FixedClock
from tests.support.fake_redis import FakeRedis
from tests.support.memory import InMemoryUnitOfWork, MemoryStore

from order_service.application.actor import Actor
from order_service.application.rate_limit import RateLimitPolicy
from order_service.application.use_cases.catalog import CreateProduct, GetProduct, ListProducts, UpdateProduct
from order_service.domain.exceptions import DependencyUnavailableError, IdempotencyInProgressError, RateLimitedError
from order_service.domain.repositories import ProductRepository
from order_service.domain.roles import Role
from order_service.infrastructure.redis.catalog_cache import ProductCatalogCache, list_cache_key, product_cache_key
from order_service.infrastructure.redis.client import RedisClient
from order_service.infrastructure.redis.commands import RedisUnavailable
from order_service.infrastructure.redis.limiter import RedisRateLimiter
from order_service.infrastructure.redis.order_lock import RedisOrderLock


class CountingProducts(ProductRepository):
    def __init__(self, inner: ProductRepository) -> None:
        self._inner = inner
        self.gets = 0
        self.lists = 0

    def get(self, product_id):
        self.gets += 1
        return self._inner.get(product_id)

    def get_by_sku(self, sku: str):
        return self._inner.get_by_sku(sku)

    def add(self, product) -> None:
        self._inner.add(product)

    def list_page(self, *, limit: int, offset: int):
        self.lists += 1
        return self._inner.list_page(limit=limit, offset=offset)


def _admin() -> Actor:
    return Actor(account_id=uuid.uuid4(), role=Role.ADMIN)


def _ids() -> tuple[uuid.UUID, uuid.UUID]:
    return uuid.uuid4(), uuid.uuid4()


def _open(store: MemoryStore, products: CountingProducts) -> InMemoryUnitOfWork:
    uow = InMemoryUnitOfWork(store)
    uow.products = products
    return uow


def test_second_product_read_is_a_hit_and_update_deletes_the_key() -> None:
    store = MemoryStore()
    clock = FixedClock()
    fake = FakeRedis()
    cache = ProductCatalogCache(fake, ttl_seconds=30)
    created = CreateProduct(clock, cache).execute(
        InMemoryUnitOfWork(store),
        sku="MUG-01",
        name="Mug",
        amount_minor=1500,
        currency="USD",
        actor=_admin(),
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    products = CountingProducts(InMemoryUnitOfWork(store).products)
    actor = _admin()
    first = GetProduct(cache).execute(_open(store, products), actor=actor, product_id=created.id)
    assert first.unit_price.amount_minor == 1500
    assert products.gets == 1
    cached = json.loads(fake.values[product_cache_key(created.id)])
    assert set(cached) == {"active", "id", "name", "sku", "unit_price", "version"}
    assert "email" not in fake.values[product_cache_key(created.id)]
    assert "password" not in fake.values[product_cache_key(created.id)]
    assert fake.ttls[product_cache_key(created.id)] == 30

    second = GetProduct(cache).execute(_open(store, products), actor=actor, product_id=created.id)
    assert second == first
    assert products.gets == 1

    listed = ListProducts(cache).execute(_open(store, products), actor=actor, limit=20, offset=0)
    assert [item.id for item in listed] == [created.id]
    assert products.lists == 1
    again = ListProducts(cache).execute(_open(store, products), actor=actor, limit=20, offset=0)
    assert again == listed
    assert products.lists == 1
    assert list_cache_key(limit=20, offset=0) in fake.values

    correlation_id, causation_id = _ids()
    updated = UpdateProduct(clock, cache).execute(
        _open(store, products),
        product_id=created.id,
        name=None,
        amount_minor=2500,
        currency=None,
        active=None,
        actor=actor,
        correlation_id=correlation_id,
        causation_id=causation_id,
    )
    assert updated.unit_price.amount_minor == 2500
    assert product_cache_key(created.id) not in fake.values
    assert list_cache_key(limit=20, offset=0) not in fake.values

    refreshed = GetProduct(cache).execute(_open(store, products), actor=actor, product_id=created.id)
    assert refreshed.unit_price.amount_minor == 2500
    assert products.gets == 3


def test_late_cache_fill_can_restore_a_price_deleted_by_an_update() -> None:
    """A read that started before the commit can put the old price back. The TTL is the backstop."""

    fake = FakeRedis()
    cache = ProductCatalogCache(fake, ttl_seconds=30)
    store = MemoryStore()
    clock = FixedClock()
    created = CreateProduct(clock).execute(
        InMemoryUnitOfWork(store),
        sku="MUG-01",
        name="Mug",
        amount_minor=1500,
        currency="USD",
        actor=_admin(),
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    stale = GetProduct().execute(InMemoryUnitOfWork(store), actor=_admin(), product_id=created.id)
    cache.invalidate(created.id)
    cache.put_product(stale)
    restored = cache.get_product(created.id)
    assert restored is not None
    assert restored.unit_price.amount_minor == 1500
    assert fake.ttls[product_cache_key(created.id)] == 30


def test_redis_errors_on_get_product_still_return_the_postgres_row() -> None:
    store = MemoryStore()
    clock = FixedClock()
    created = CreateProduct(clock).execute(
        InMemoryUnitOfWork(store),
        sku="MUG-01",
        name="Mug",
        amount_minor=1500,
        currency="USD",
        actor=_admin(),
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    fake = FakeRedis()
    fake.fail = True
    products = CountingProducts(InMemoryUnitOfWork(store).products)
    view = GetProduct(ProductCatalogCache(fake, ttl_seconds=30)).execute(
        _open(store, products),
        actor=_admin(),
        product_id=created.id,
    )
    assert view.name == "Mug"
    assert view.unit_price.amount_minor == 1500
    assert products.gets == 1


def test_login_buckets_are_ip_and_email_hash() -> None:
    fake = FakeRedis()
    limiter = RedisRateLimiter(fake, RateLimitPolicy(login_per_minute=1))
    limiter.consume_login(ip="10.0.0.1", email="Ada@Example.com")
    assert all("ada@example.com" not in key and "Ada@" not in key for key in fake.values)
    assert any(key.startswith("rl:login:email:") for key in fake.values)
    with pytest.raises(RateLimitedError) as same_email:
        limiter.consume_login(ip="10.0.0.2", email="ada@example.com")
    assert same_email.value.code == "RATE_LIMITED"
    other = RedisRateLimiter(FakeRedis(), RateLimitPolicy(login_per_minute=1))
    other.consume_login(ip="10.0.0.9", email="a@example.com")
    with pytest.raises(RateLimitedError):
        other.consume_login(ip="10.0.0.9", email="b@example.com")


def test_limiter_redis_errors_fail_closed() -> None:
    fake = FakeRedis()
    fake.fail = True
    limiter = RedisRateLimiter(fake, RateLimitPolicy())
    with pytest.raises(DependencyUnavailableError):
        limiter.consume_login(ip="127.0.0.1", email="ada@example.com")
    with pytest.raises(DependencyUnavailableError):
        limiter.consume_register(ip="127.0.0.1")
    with pytest.raises(DependencyUnavailableError):
        limiter.consume_order_create(ip="127.0.0.1", account_id=uuid.uuid4())


def test_order_lock_blocks_only_while_it_is_held() -> None:
    fake = FakeRedis()
    lock = RedisOrderLock(fake, ttl_seconds=15)
    account_id = uuid.uuid4()
    lines = [(uuid.uuid4(), 1)]
    held = lock.acquire(account_id=account_id, lines=lines)
    with pytest.raises(IdempotencyInProgressError):
        lock.acquire(account_id=account_id, lines=lines)
    lock.release(held)
    again = lock.acquire(account_id=account_id, lines=lines)
    lock.release(again)
    fake.fail = True
    with pytest.raises(DependencyUnavailableError):
        lock.acquire(account_id=account_id, lines=lines)


def test_hung_redis_raises_instead_of_waiting_forever() -> None:
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    port = listener.getsockname()[1]
    stop = threading.Event()

    def accept_and_hold() -> None:
        listener.settimeout(2)
        try:
            conn, _ = listener.accept()
        except OSError:
            return
        try:
            stop.wait(3)
        finally:
            conn.close()

    thread = threading.Thread(target=accept_and_hold, daemon=True)
    thread.start()
    client = RedisClient(f"redis://127.0.0.1:{port}/0", connect_timeout=0.2, socket_timeout=0.2)
    started = time.monotonic()
    try:
        with pytest.raises(RedisUnavailable):
            client.ping()
        assert time.monotonic() - started < 2
    finally:
        stop.set()
        client.close()
        listener.close()
        thread.join(timeout=2)
