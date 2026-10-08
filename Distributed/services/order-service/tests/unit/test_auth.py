import uuid

import pytest
from tests.support.clock import FixedClock
from tests.support.memory import InMemoryUnitOfWork, MemoryStore

from order_service.application.actor import Actor
from order_service.application.ports import InvalidAccessToken
from order_service.application.use_cases.auth import (
    CreateStaffAccount,
    LoginAccount,
    RefreshSession,
    RegisterAccount,
)
from order_service.application.use_cases.catalog import CreateProduct
from order_service.application.use_cases.orders import CancelOrder, CreateOrder
from order_service.domain.exceptions import ForbiddenError, UnauthenticatedError
from order_service.domain.roles import Role
from order_service.infrastructure.security.refresh_tokens import Sha256RefreshTokens


class FakePasswords:
    def __init__(self) -> None:
        self.dummy_calls = 0

    def hash_password(self, password: str) -> str:
        return "hashed:" + password

    def verify_password(self, password: str, password_hash: str) -> bool:
        return password_hash == "hashed:" + password

    def verify_dummy(self, password: str) -> None:
        self.dummy_calls += 1


class FakeTokens:
    def __init__(self) -> None:
        self.issued: list[tuple[uuid.UUID, str]] = []

    def issue(self, *, account_id: uuid.UUID, role: str, now) -> str:
        self.issued.append((account_id, role))
        return f"access-{len(self.issued)}"

    def parse(self, token: str, *, now):
        raise InvalidAccessToken("unused")


def _register(store: MemoryStore, clock: FixedClock, passwords: FakePasswords, tokens: FakeTokens):
    uow = InMemoryUnitOfWork(store)
    pair = RegisterAccount(clock, passwords, tokens, Sha256RefreshTokens()).execute(
        uow,
        email="ada@example.com",
        display_name="Ada",
        password="password-1",
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    uow.close()
    return pair


def test_register_stores_a_hash_and_the_customer_role() -> None:
    store = MemoryStore()
    passwords = FakePasswords()
    tokens = FakeTokens()
    pair = _register(store, FixedClock(), passwords, tokens)
    account = store.accounts[pair.account_id]
    assert account.password_hash == "hashed:password-1"
    assert account.password_hash != "password-1"
    assert account.role == Role.CUSTOMER
    assert tokens.issued == [(pair.account_id, "customer")]
    assert store.customers[pair.account_id].id.value == pair.account_id
    raw = pair.refresh_token
    assert all(token.token_hash != raw for token in store.refresh_tokens.values())


def test_unknown_email_and_wrong_password_raise_the_same_error() -> None:
    store = MemoryStore()
    clock = FixedClock()
    passwords = FakePasswords()
    tokens = FakeTokens()
    _register(store, clock, passwords, tokens)
    uow = InMemoryUnitOfWork(store)
    login = LoginAccount(clock, passwords, tokens, Sha256RefreshTokens())
    with pytest.raises(UnauthenticatedError) as wrong:
        login.execute(uow, email="ada@example.com", password="nope-nope")
    uow.close()
    before = passwords.dummy_calls
    uow = InMemoryUnitOfWork(store)
    with pytest.raises(UnauthenticatedError) as missing:
        login.execute(uow, email="missing@example.com", password="nope-nope")
    uow.close()
    assert str(wrong.value) == str(missing.value)
    assert passwords.dummy_calls == before + 1


def test_refresh_reuse_does_not_issue_another_token() -> None:
    store = MemoryStore()
    clock = FixedClock()
    passwords = FakePasswords()
    tokens = FakeTokens()
    codec = Sha256RefreshTokens()
    pair = _register(store, clock, passwords, tokens)
    uow = InMemoryUnitOfWork(store)
    rotated = RefreshSession(clock, tokens, codec).execute(uow, refresh_token=pair.refresh_token)
    uow.close()
    assert rotated.refresh_token != pair.refresh_token
    uow = InMemoryUnitOfWork(store)
    with pytest.raises(UnauthenticatedError):
        RefreshSession(clock, tokens, codec).execute(uow, refresh_token=pair.refresh_token)
    uow.close()
    active = [token for token in store.refresh_tokens.values() if token.revoked_at is None]
    assert len(active) == 1
    assert len(store.refresh_tokens) == 2


def test_staff_account_is_not_a_customer_profile() -> None:
    store = MemoryStore()
    uow = InMemoryUnitOfWork(store)
    CreateStaffAccount(FixedClock(), FakePasswords()).execute(
        uow,
        email="admin@example.com",
        password="password-1",
        role=Role.ADMIN,
    )
    uow.close()
    account = next(iter(store.accounts.values()))
    assert account.role == Role.ADMIN
    assert store.customers == {}


def test_customer_cannot_create_a_product_and_cannot_cancel_with_staff_reason() -> None:
    store = MemoryStore()
    clock = FixedClock()
    passwords = FakePasswords()
    tokens = FakeTokens()
    pair = _register(store, clock, passwords, tokens)
    customer = Actor(account_id=pair.account_id, role=Role.CUSTOMER)
    uow = InMemoryUnitOfWork(store)
    with pytest.raises(ForbiddenError):
        CreateProduct(clock).execute(
            uow,
            sku="MUG-01",
            name="Mug",
            amount_minor=100,
            currency="USD",
            actor=customer,
            correlation_id=uuid.uuid4(),
            causation_id=uuid.uuid4(),
        )
    uow.close()
    assert store.products == {}

    admin = Actor(account_id=uuid.uuid4(), role=Role.ADMIN)
    uow = InMemoryUnitOfWork(store)
    product = CreateProduct(clock).execute(
        uow,
        sku="MUG-01",
        name="Mug",
        amount_minor=100,
        currency="USD",
        actor=admin,
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    order = CreateOrder(clock).execute(
        uow,
        actor=customer,
        lines=[(product.id, 1)],
        correlation_id=uuid.uuid4(),
        causation_id=uuid.uuid4(),
    )
    uow.close()
    uow = InMemoryUnitOfWork(store)
    with pytest.raises(ForbiddenError):
        CancelOrder(clock).execute(
            uow,
            actor=customer,
            order_id=order.id,
            reason="staff_request",
            correlation_id=uuid.uuid4(),
            causation_id=uuid.uuid4(),
        )
    uow.close()
    assert store.orders[order.id].status.value == "PENDING"
