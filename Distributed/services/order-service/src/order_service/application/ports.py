"""Ports the auth use cases depend on. Infrastructure implements them. Tests can fake them."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Protocol

from order_service.application.actor import Actor


class InvalidAccessToken(Exception):
    """The bearer token is missing a required claim, expired, or not signed by us."""


class PasswordHasher(Protocol):
    def hash_password(self, password: str) -> str: ...

    def verify_password(self, password: str, password_hash: str) -> bool: ...

    def verify_dummy(self, password: str) -> None:
        """Spend the same kind of work as a real verify when the account does not exist."""


class AccessTokenIssuer(Protocol):
    def issue(self, *, account_id: uuid.UUID, role: str, now: datetime) -> str: ...

    def parse(self, token: str, *, now: datetime) -> Actor: ...


class RefreshTokenCodec(Protocol):
    def new_secret(self) -> str: ...

    def hash_secret(self, raw: str) -> str: ...
