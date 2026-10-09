"""HTTP limits and the catalog cache. Redis is the in-memory fake."""

from __future__ import annotations

import uuid

from tests.support.fake_redis import FakeRedis
from tests.support.http import add_staff, bearer, fast_hasher, login, make_client, register

from order_service.application.rate_limit import RateLimitPolicy
from order_service.domain.roles import Role
from order_service.infrastructure.redis.catalog_cache import product_cache_key
from order_service.infrastructure.redis.order_lock import order_lock_key


class CountingHasher:
    def __init__(self) -> None:
        self._inner = fast_hasher()
        self.verifies = 0
        self.hashes = 0

    def hash_password(self, password: str) -> str:
        self.hashes += 1
        return self._inner.hash_password(password)

    def verify_password(self, password: str, password_hash: str) -> bool:
        self.verifies += 1
        return self._inner.verify_password(password, password_hash)

    def verify_dummy(self, password: str) -> None:
        self.verifies += 1
        self._inner.verify_dummy(password)


def _login(client, email: str = "ada@example.com", password: str = "not-the-password"):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


def test_login_over_the_limit_returns_429() -> None:
    hasher = CountingHasher()
    client, _store, _clock, _public = make_client(
        password_hasher=hasher,
        rate_limit_policy=RateLimitPolicy(login_per_minute=2),
    )
    assert _login(client).status_code == 401
    assert _login(client).status_code == 401
    blocked = _login(client)
    assert hasher.verifies == 2
    assert blocked.status_code == 429
    error = blocked.json()["error"]
    assert error["code"] == "RATE_LIMITED"
    assert error["details"] == []
    assert error["correlation_id"]
    assert set(error) == {"code", "message", "correlation_id", "details"}


def test_register_over_the_limit_returns_429() -> None:
    client, _store, _clock, _public = make_client(rate_limit_policy=RateLimitPolicy(register_per_minute=2))
    assert register(client, email="a@example.com").status_code == 201
    assert register(client, email="b@example.com").status_code == 201
    blocked = register(client, email="c@example.com")
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "RATE_LIMITED"


def test_redis_errors_on_login_do_not_call_the_password_checker() -> None:
    fake = FakeRedis()
    fake.fail = True
    hasher = CountingHasher()
    client, store, _clock, _public = make_client(redis_commands=fake, password_hasher=hasher)
    for _ in range(20):
        response = _login(client)
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "DEPENDENCY_UNAVAILABLE"
    assert hasher.verifies == 0
    assert hasher.hashes == 0
    assert store.accounts == {}
    blocked = register(client, email="ada@example.com")
    assert blocked.status_code == 503
    assert hasher.hashes == 0
    assert store.accounts == {}


def test_redis_errors_on_get_product_still_return_200() -> None:
    fake = FakeRedis()
    client, store, clock, _public = make_client(redis_commands=fake)
    add_staff(store, clock, email="admin@example.com", role=Role.ADMIN)
    admin, _refresh = login(client, "admin@example.com")
    created = client.post(
        "/api/v1/products",
        headers=bearer(admin),
        json={"sku": "MUG-01", "name": "Mug", "unit_price": {"amount_minor": 1500, "currency": "USD"}},
    )
    assert created.status_code == 201
    product_id = created.json()["id"]
    fake.fail = True
    listed = client.get("/api/v1/products", headers=bearer(admin))
    one = client.get(f"/api/v1/products/{product_id}", headers=bearer(admin))
    assert listed.status_code == 200
    assert listed.json()["items"][0]["name"] == "Mug"
    assert one.status_code == 200
    assert one.json()["unit_price"] == {"amount_minor": 1500, "currency": "USD"}


def test_product_update_deletes_the_cached_price() -> None:
    fake = FakeRedis()
    client, store, clock, _public = make_client(redis_commands=fake)
    add_staff(store, clock, email="admin@example.com", role=Role.ADMIN)
    admin, _refresh = login(client, "admin@example.com")
    created = client.post(
        "/api/v1/products",
        headers=bearer(admin),
        json={"sku": "MUG-01", "name": "Mug", "unit_price": {"amount_minor": 1500, "currency": "USD"}},
    )
    product_id = uuid.UUID(created.json()["id"])
    assert client.get(f"/api/v1/products/{product_id}", headers=bearer(admin)).status_code == 200
    key = product_cache_key(product_id)
    assert "1500" in fake.values[key]
    patched = client.patch(
        f"/api/v1/products/{product_id}",
        headers=bearer(admin),
        json={"unit_price": {"amount_minor": 2500, "currency": "USD"}},
    )
    assert patched.status_code == 200
    assert key not in fake.values
    refreshed = client.get(f"/api/v1/products/{product_id}", headers=bearer(admin))
    assert refreshed.json()["unit_price"]["amount_minor"] == 2500
    assert "2500" in fake.values[key]


def test_order_create_fails_closed_before_a_row_is_written() -> None:
    fake = FakeRedis()
    client, store, _clock, _public = make_client(redis_commands=fake)
    registered = register(client, email="ada@example.com")
    assert registered.status_code == 201
    access = registered.json()["access_token"]
    fake.fail = True
    created = client.post(
        "/api/v1/orders",
        headers=bearer(access),
        json={"items": [{"product_id": str(uuid.uuid4()), "quantity": 1}]},
    )
    assert created.status_code == 503
    assert created.json()["error"]["code"] == "DEPENDENCY_UNAVAILABLE"
    assert store.orders == {}


def test_order_create_over_the_limit_returns_429_and_a_second_sequential_create_is_allowed() -> None:
    fake = FakeRedis()
    client, store, clock, _public = make_client(
        redis_commands=fake,
        rate_limit_policy=RateLimitPolicy(order_create_per_minute=2),
    )
    add_staff(store, clock, email="admin@example.com", role=Role.ADMIN)
    admin, _refresh = login(client, "admin@example.com")
    product = client.post(
        "/api/v1/products",
        headers=bearer(admin),
        json={"sku": "MUG-01", "name": "Mug", "unit_price": {"amount_minor": 1500, "currency": "USD"}},
    )
    product_id = product.json()["id"]
    access = register(client, email="ada@example.com").json()["access_token"]
    body = {"items": [{"product_id": product_id, "quantity": 1}]}
    first = client.post("/api/v1/orders", headers=bearer(access), json=body)
    second = client.post("/api/v1/orders", headers=bearer(access), json=body)
    assert first.status_code == second.status_code == 201
    assert first.json()["id"] != second.json()["id"]
    blocked = client.post("/api/v1/orders", headers=bearer(access), json=body)
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "RATE_LIMITED"
    assert len(store.orders) == 2


def test_in_flight_order_lock_returns_409_and_writes_nothing() -> None:
    fake = FakeRedis()
    client, store, clock, _public = make_client(redis_commands=fake)
    add_staff(store, clock, email="admin@example.com", role=Role.ADMIN)
    admin, _refresh = login(client, "admin@example.com")
    product = client.post(
        "/api/v1/products",
        headers=bearer(admin),
        json={"sku": "MUG-01", "name": "Mug", "unit_price": {"amount_minor": 1500, "currency": "USD"}},
    )
    product_id = product.json()["id"]
    access = register(client, email="ada@example.com").json()["access_token"]
    account_id = uuid.UUID(client.get("/api/v1/customers/me", headers=bearer(access)).json()["id"])
    fake.set(order_lock_key(account_id, [(uuid.UUID(product_id), 1)]), "held", ttl_seconds=15)
    created = client.post(
        "/api/v1/orders",
        headers=bearer(access),
        json={"items": [{"product_id": product_id, "quantity": 1}]},
    )
    assert created.status_code == 409
    assert created.json()["error"]["code"] == "IDEMPOTENCY_IN_PROGRESS"
    assert store.orders == {}
