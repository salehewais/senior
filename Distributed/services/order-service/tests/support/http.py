"""API test app. The RSA key exists only in memory. Passwords use a cheap argon2id."""

from __future__ import annotations

from functools import lru_cache

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from tests.support.clock import FixedClock
from tests.support.memory import InMemoryUnitOfWork, MemoryStore

from order_service.application.use_cases.auth import CreateStaffAccount
from order_service.domain.roles import Role
from order_service.infrastructure.security.passwords import Argon2PasswordHasher
from order_service.infrastructure.security.tokens import RsaAccessTokenIssuer
from order_service.presentation.app import create_app

INTERNAL_TOKEN = "internal-test-token"
PASSWORD = "password-1"


@lru_cache(maxsize=1)
def ephemeral_keypair() -> tuple[str, str]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("ascii")
    public = (
        key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("ascii")
    )
    return private, public


def fast_hasher() -> Argon2PasswordHasher:
    return Argon2PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)


def make_client(
    *,
    internal_service_token: str | None = INTERNAL_TOKEN,
    clock: FixedClock | None = None,
) -> tuple[TestClient, MemoryStore, FixedClock, str]:
    store = MemoryStore()
    clock = clock or FixedClock()
    private_pem, public_pem = ephemeral_keypair()
    app = create_app(
        uow_factory=lambda: InMemoryUnitOfWork(store),
        clock=clock,
        engine=None,
        password_hasher=fast_hasher(),
        token_issuer=RsaAccessTokenIssuer(private_pem, public_pem),
        internal_service_token=internal_service_token,
    )
    return TestClient(app), store, clock, public_pem


def bearer(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def register(
    client: TestClient,
    *,
    email: str = "ada@example.com",
    display_name: str = "Ada",
    password: str = PASSWORD,
    extra: dict | None = None,
):
    body: dict = {"email": email, "display_name": display_name, "password": password}
    if extra:
        body.update(extra)
    return client.post("/api/v1/auth/register", json=body)


def login(client: TestClient, email: str, password: str = PASSWORD) -> tuple[str, str]:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    payload = response.json()
    return payload["access_token"], payload["refresh_token"]


def add_staff(store: MemoryStore, clock: FixedClock, *, email: str, role: Role, password: str = PASSWORD) -> None:
    uow = InMemoryUnitOfWork(store)
    CreateStaffAccount(clock, fast_hasher()).execute(uow, email=email, password=password, role=role)
    uow.close()
