"""Verify an order-service access token with the public key only.

This service does not issue tokens and does not read a private key.
The caller is the token subject. A role claim is not a second identity.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

import jwt

_ALGORITHM = "RS256"


class Unauthenticated(Exception):
    def __init__(self, message: str = "Missing or invalid access token.") -> None:
        super().__init__(message)
        self.message = message


class VerifierNotConfigured(Exception):
    def __init__(self) -> None:
        super().__init__("JWT public key is not configured.")
        self.message = "The notification service cannot verify access tokens."


@dataclass(frozen=True, slots=True)
class Actor:
    account_id: uuid.UUID
    role: str


def authenticate(header: str | None, public_key: str, *, now: datetime | None = None) -> Actor:
    if not public_key:
        raise VerifierNotConfigured()
    if not header or not header.startswith("Bearer ") or not header.removeprefix("Bearer ").strip():
        raise Unauthenticated()
    token = header.removeprefix("Bearer ").strip()
    return _parse(token, public_key, now or datetime.now(UTC))


def _parse(token: str, public_key: str, now: datetime) -> Actor:
    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=[_ALGORITHM],
            options={
                "verify_exp": False,
                "verify_iat": False,
                "require": ["exp", "iat", "sub"],
            },
        )
    except jwt.PyJWTError as exc:
        raise Unauthenticated() from exc
    if payload.get("token_type") != "access":
        raise Unauthenticated()
    try:
        if int(now.timestamp()) >= int(payload["exp"]):
            raise Unauthenticated()
        role = str(payload.get("role"))
        if role not in {"customer", "admin", "manager"}:
            raise Unauthenticated()
        account_id = uuid.UUID(str(payload["sub"]))
    except Unauthenticated:
        raise
    except (ValueError, TypeError) as exc:
        raise Unauthenticated() from exc
    return Actor(account_id=account_id, role=role)
