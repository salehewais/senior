"""Product cache-aside behavior. Fake Redis only. A live server is not required."""

from __future__ import annotations

import json
import threading
import uuid
from pathlib import Path

import pytest
from prometheus_client import REGISTRY
from tests.support.clock import FixedClock
from tests.support.fake_redis import FakeRedis
from tests.support.memory import InMemoryUnitOfWork, MemoryStore
from tests.unit.test_redis_cache import CountingProducts, _admin, _ids

from order_service.application.dto import product_view
from order_service.application.use_cases.catalog import GetProduct, ListProducts, UpdateProduct
from order_service.domain.entities.catalog import Product
from order_service.domain.ids import ProductId
from order_service.domain.repositories import ProductRepository
from order_service.infrastructure.redis.catalog_cache import ProductCatalogCache, list_cache_key, product_cache_key
from order_service.observability.metrics import (
    product_cache_duration_seconds,
    product_cache_errors_total,
    product_cache_hits_total,
    product_cache_misses_total,
    record_product_cache,
)

_DASHBOARDS = Path(__file__).resolve().parents[4] / "deploy" / "observability" / "grafana" / "dashboards"
_SERIES = (
    "product_cache_hits_total",
    "product_cache_misses_total",
    "product_cache_errors_total",
    "product_cache_duration_seconds",
)


def _counter(name: str, operation: str) -> float:
    found = 0.0
    for family in REGISTRY.collect():
        for sample in family.samples:
            if sample.name == name and sample.labels.get("operation") == operation:
                found += sample.value
    return found


def _duration_count(operation: str, result: str) -> float:
    for family in REGISTRY.collect():
        for sample in family.samples:
            if (
                sample.name == "product_cache_duration_seconds_count"
                and sample.labels.get("operation") == operation
                and sample.labels.get("result") == result
            ):
                return sample.value
    return 0.0


def _seed_product(store: MemoryStore) -> uuid.UUID:
    from order_service.application.use_cases.catalog import CreateProduct

    created = CreateProduct(FixedClock()).execute(
        InMemoryUnitOfWork(store),
        sku="MUG-01",
        name="Mug",
        amount_minor=1500,
        currency="USD",
        actor=_admin(),
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    return created.id


def _update(store: MemoryStore, product_id: uuid.UUID, cache: ProductCatalogCache | None, amount_minor: int) -> None:
    correlation_id, causation_id = _ids()
    UpdateProduct(FixedClock(), cache).execute(
        InMemoryUnitOfWork(store),
        product_id=product_id,
        name=None,
        amount_minor=amount_minor,
        currency=None,
        active=None,
        actor=_admin(),
        correlation_id=correlation_id,
        causation_id=causation_id,
    )


class _AfterCommit:
    """Delegates to the real cache and records that invalidate ran after commit."""

    def __init__(self, inner: ProductCatalogCache) -> None:
        self._inner = inner
        self.invalidations = 0
        self.saw_committed = False
        self._uow: InMemoryUnitOfWork | None = None

    def bind(self, uow: InMemoryUnitOfWork) -> None:
        self._uow = uow

    def get_product(self, product_id: uuid.UUID):
        return self._inner.get_product(product_id)

    def put_product(self, view) -> None:
        self._inner.put_product(view)

    def get_list(self, *, limit: int, offset: int):
        return self._inner.get_list(limit=limit, offset=offset)

    def put_list(self, views, *, limit: int, offset: int) -> None:
        self._inner.put_list(views, limit=limit, offset=offset)

    def invalidate(self, product_id: uuid.UUID) -> None:
        assert self._uow is not None
        assert self._uow._committed
        self.saw_committed = True
        self.invalidations += 1
        self._inner.invalidate(product_id)


class _RefusingCommit(InMemoryUnitOfWork):
    def commit(self) -> None:
        raise RuntimeError("commit refused")


class _LockedRedis(FakeRedis):
    def __init__(self) -> None:
        super().__init__()
        self._lock = threading.Lock()
        self.sets: list[tuple[str, str]] = []
        self.absent_sets = 0

    def get(self, key: str) -> str | None:
        with self._lock:
            return super().get(key)

    def set(self, key: str, value: str, *, ttl_seconds: int) -> None:
        with self._lock:
            self.sets.append((key, value))
            super().set(key, value, ttl_seconds=ttl_seconds)

    def set_if_absent(self, key: str, value: str, *, ttl_seconds: int) -> bool:
        with self._lock:
            self.absent_sets += 1
            return super().set_if_absent(key, value, ttl_seconds=ttl_seconds)


class _RacingProducts(ProductRepository):
    """Both callers enter get before either returns, so both observe a miss."""

    def __init__(self, inner: ProductRepository, snapshots: list[Product]) -> None:
        self._inner = inner
        self._snapshots = snapshots
        self.gets = 0
        self._lock = threading.Lock()
        self.barrier = threading.Barrier(2)

    def get(self, product_id: ProductId) -> Product | None:
        with self._lock:
            index = self.gets
            self.gets += 1
        self.barrier.wait(timeout=2)
        return self._snapshots[index]

    def get_by_sku(self, sku: str) -> Product | None:
        return self._inner.get_by_sku(sku)

    def add(self, product: Product) -> None:
        self._inner.add(product)

    def list_page(self, *, limit: int, offset: int) -> list[Product]:
        return self._inner.list_page(limit=limit, offset=offset)


def test_stale_product_is_served_when_the_delete_has_not_happened() -> None:
    store = MemoryStore()
    product_id = _seed_product(store)
    fake = FakeRedis()
    cache = ProductCatalogCache(fake, ttl_seconds=30)
    products = CountingProducts(InMemoryUnitOfWork(store).products)
    actor = _admin()
    filled = GetProduct(cache).execute(_open(store, products), actor=actor, product_id=product_id)
    assert filled.unit_price.amount_minor == 1500
    assert products.gets == 1

    _update(store, product_id, None, 2500)
    assert product_cache_key(product_id) in fake.values
    assert fake.ttls[product_cache_key(product_id)] == 30

    stale = GetProduct(cache).execute(_open(store, products), actor=actor, product_id=product_id)
    assert stale.unit_price.amount_minor == 1500
    assert products.gets == 1

    current = GetProduct().execute(InMemoryUnitOfWork(store), actor=actor, product_id=product_id)
    assert current.unit_price.amount_minor == 2500


def test_redis_down_falls_through_to_postgres() -> None:
    store = MemoryStore()
    product_id = _seed_product(store)
    fake = FakeRedis()
    fake.fail = True
    cache = ProductCatalogCache(fake, ttl_seconds=30)
    products = CountingProducts(InMemoryUnitOfWork(store).products)
    actor = _admin()
    errors_before = _counter("product_cache_errors_total", "get")
    misses_before = _counter("product_cache_misses_total", "get")
    error_duration_before = _duration_count("get", "error")

    view = GetProduct(cache).execute(_open(store, products), actor=actor, product_id=product_id)
    assert view.name == "Mug"
    assert view.unit_price.amount_minor == 1500
    assert products.gets == 1
    assert _counter("product_cache_errors_total", "get") == errors_before + 1
    assert _counter("product_cache_misses_total", "get") == misses_before
    assert _duration_count("get", "error") == error_duration_before + 1

    list_errors_before = _counter("product_cache_errors_total", "list")
    listed = ListProducts(cache).execute(_open(store, products), actor=actor, limit=20, offset=0)
    assert [item.id for item in listed] == [product_id]
    assert products.lists == 1
    assert _counter("product_cache_errors_total", "list") == list_errors_before + 1
    assert list_cache_key(limit=20, offset=0) not in fake.values


def test_concurrent_misses_both_fill_and_the_last_write_wins() -> None:
    store = MemoryStore()
    product_id = _seed_product(store)
    old = InMemoryUnitOfWork(store).products.get(ProductId(product_id))
    assert old is not None
    _update(store, product_id, None, 2500)
    new = InMemoryUnitOfWork(store).products.get(ProductId(product_id))
    assert new is not None
    assert old.unit_price.amount_minor == 1500
    assert new.unit_price.amount_minor == 2500
    assert product_view(old).version != product_view(new).version

    fake = _LockedRedis()
    cache = ProductCatalogCache(fake, ttl_seconds=30)
    racing = _RacingProducts(InMemoryUnitOfWork(store).products, [old, new])
    left = _open(store, racing)
    right = _open(store, racing)
    actor = _admin()
    misses_before = _counter("product_cache_misses_total", "get")
    hits_before = _counter("product_cache_hits_total", "get")
    results: list[object] = []
    errors: list[BaseException] = []

    def read(uow: InMemoryUnitOfWork) -> None:
        try:
            results.append(GetProduct(cache).execute(uow, actor=actor, product_id=product_id))
        except BaseException as exc:
            errors.append(exc)

    first = threading.Thread(target=read, args=(left,))
    second = threading.Thread(target=read, args=(right,))
    first.start()
    second.start()
    first.join(timeout=3)
    second.join(timeout=3)

    assert errors == []
    assert not first.is_alive()
    assert not second.is_alive()
    assert racing.gets == 2
    assert fake.absent_sets == 0
    assert len(fake.sets) == 2
    assert fake.sets[0][1] != fake.sets[1][1]
    stored = fake.values[product_cache_key(product_id)]
    assert stored in {payload for _key, payload in fake.sets}
    body = json.loads(stored)
    if body["unit_price"]["amount_minor"] == 1500:
        assert body["version"] == product_view(old).version
    else:
        assert body["unit_price"]["amount_minor"] == 2500
        assert body["version"] == product_view(new).version
    assert _counter("product_cache_misses_total", "get") == misses_before + 2
    assert _counter("product_cache_hits_total", "get") == hits_before
    assert len(results) == 2


def test_successful_catalog_change_deletes_the_product_key() -> None:
    store = MemoryStore()
    product_id = _seed_product(store)
    fake = FakeRedis()
    inner = ProductCatalogCache(fake, ttl_seconds=30)
    products = CountingProducts(InMemoryUnitOfWork(store).products)
    actor = _admin()
    GetProduct(inner).execute(_open(store, products), actor=actor, product_id=product_id)
    ListProducts(inner).execute(_open(store, products), actor=actor, limit=20, offset=0)
    assert product_cache_key(product_id) in fake.values
    assert list_cache_key(limit=20, offset=0) in fake.values

    guard = _AfterCommit(inner)
    uow = InMemoryUnitOfWork(store)
    guard.bind(uow)
    correlation_id, causation_id = _ids()
    updated = UpdateProduct(FixedClock(), guard).execute(
        uow,
        product_id=product_id,
        name=None,
        amount_minor=2500,
        currency=None,
        active=None,
        actor=actor,
        correlation_id=correlation_id,
        causation_id=causation_id,
    )
    assert updated.unit_price.amount_minor == 2500
    assert guard.invalidations == 1
    assert guard.saw_committed
    assert product_cache_key(product_id) not in fake.values
    assert list_cache_key(limit=20, offset=0) not in fake.values

    refusing_guard = _AfterCommit(inner)
    refusing = _RefusingCommit(store)
    refusing_guard.bind(refusing)
    GetProduct(inner).execute(_open(store, products), actor=actor, product_id=product_id)
    assert product_cache_key(product_id) in fake.values
    with pytest.raises(RuntimeError, match="commit refused"):
        UpdateProduct(FixedClock(), refusing_guard).execute(
            refusing,
            product_id=product_id,
            name=None,
            amount_minor=2600,
            currency=None,
            active=None,
            actor=actor,
            correlation_id=uuid.uuid4(),
            causation_id=uuid.uuid4(),
        )
    assert refusing_guard.invalidations == 0
    assert product_cache_key(product_id) in fake.values
    cached = json.loads(fake.values[product_cache_key(product_id)])
    assert cached["unit_price"]["amount_minor"] == 2500


def test_product_get_and_list_record_hit_miss_error_and_duration() -> None:
    assert product_cache_hits_total._labelnames == ("operation",)
    assert product_cache_misses_total._labelnames == ("operation",)
    assert product_cache_errors_total._labelnames == ("operation",)
    assert product_cache_duration_seconds._labelnames == ("operation", "result")
    for metric in (
        product_cache_hits_total,
        product_cache_misses_total,
        product_cache_errors_total,
        product_cache_duration_seconds,
    ):
        assert "product_id" not in metric._labelnames
        assert "account_id" not in metric._labelnames
        assert "token" not in metric._labelnames
    with pytest.raises(ValueError, match="get or list"):
        record_product_cache(operation=str(uuid.uuid4()), result="hit", seconds=0.0)

    store = MemoryStore()
    product_id = _seed_product(store)
    fake = FakeRedis()
    cache = ProductCatalogCache(fake, ttl_seconds=30)
    products = CountingProducts(InMemoryUnitOfWork(store).products)
    actor = _admin()
    get_misses = _counter("product_cache_misses_total", "get")
    get_hits = _counter("product_cache_hits_total", "get")
    list_misses = _counter("product_cache_misses_total", "list")
    list_hits = _counter("product_cache_hits_total", "list")
    get_miss_duration = _duration_count("get", "miss")
    get_hit_duration = _duration_count("get", "hit")
    list_miss_duration = _duration_count("list", "miss")
    list_hit_duration = _duration_count("list", "hit")

    GetProduct(cache).execute(_open(store, products), actor=actor, product_id=product_id)
    GetProduct(cache).execute(_open(store, products), actor=actor, product_id=product_id)
    ListProducts(cache).execute(_open(store, products), actor=actor, limit=20, offset=0)
    ListProducts(cache).execute(_open(store, products), actor=actor, limit=20, offset=0)

    assert _counter("product_cache_misses_total", "get") == get_misses + 1
    assert _counter("product_cache_hits_total", "get") == get_hits + 1
    assert _counter("product_cache_misses_total", "list") == list_misses + 1
    assert _counter("product_cache_hits_total", "list") == list_hits + 1
    assert _duration_count("get", "miss") == get_miss_duration + 1
    assert _duration_count("get", "hit") == get_hit_duration + 1
    assert _duration_count("list", "miss") == list_miss_duration + 1
    assert _duration_count("list", "hit") == list_hit_duration + 1
    assert products.gets == 1
    assert products.lists == 1

    for family in REGISTRY.collect():
        if not family.name.startswith("product_cache"):
            continue
        for sample in family.samples:
            assert "product_id" not in sample.labels
            assert "account_id" not in sample.labels
            assert "token" not in sample.labels
            assert str(product_id) not in sample.labels.values()


def test_grafana_dashboards_include_the_product_cache_series() -> None:
    assert _DASHBOARDS.is_dir()
    texts = []
    for name in ("dependencies.json", "platform-overview.json"):
        document = json.loads((_DASHBOARDS / name).read_text(encoding="utf-8"))
        exprs = [target["expr"] for panel in document["panels"] for target in panel["targets"]]
        blob = "\n".join(exprs)
        for series in _SERIES:
            assert series in blob
        texts.append(blob)
    assert "redis_keyspace_hits_total" in texts[0]
    for blob in texts:
        for series_line in blob.splitlines():
            if "product_cache_" not in series_line:
                continue
            assert "product_id" not in series_line
            assert "account_id" not in series_line
            assert "token" not in series_line


def _open(store: MemoryStore, products: ProductRepository) -> InMemoryUnitOfWork:
    uow = InMemoryUnitOfWork(store)
    uow.products = products
    return uow
