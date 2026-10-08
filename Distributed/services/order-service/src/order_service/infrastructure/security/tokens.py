"""RS256 access tokens. The private key issues them. Verifiers only need the public key.

Expiry is checked against the injected clock. Library checks against the wall clock
are turned off so a test clock and a running process can disagree.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import jwt

from order_service.application.actor import Actor
from order_service.application.auth_policy import ACCESS_TOKEN_TTL
from order_service.application.ports import InvalidAccessToken
from order_service.domain.roles import Role

_ALGORITHM = "RS256"


class RsaAccessTokenIssuer:
    def __init__(self, private_pem: str, public_pem: str, *, ttl: timedelta = ACCESS_TOKEN_TTL) -> None:
        self._private = private_pem
        self._public = public_pem
        self._ttl = ttl

    def issue(self, *, account_id: uuid.UUID, role: str, now: datetime) -> str:
        payload = {
            "sub": str(account_id),
            "role": role,
            "iat": int(now.timestamp()),
            "exp": int((now + self._ttl).timestamp()),
            "token_type": "access",
        }
        encoded = jwt.encode(payload, self._private, algorithm=_ALGORITHM)
        return encoded if isinstance(encoded, str) else encoded.decode("ascii")

    def parse(self, token: str, *, now: datetime) -> Actor:
        try:
            payload = jwt.decode(
                token,
                self._public,
                algorithms=[_ALGORITHM],
                options={
                    "verify_exp": False,
                    "verify_iat": False,
                    "require": ["exp", "iat", "sub"],
                },
            )
        except jwt.PyJWTError as exc:
            raise InvalidAccessToken("invalid access token") from exc
        if payload.get("token_type") != "access":
            raise InvalidAccessToken("invalid access token")
        try:
            if int(now.timestamp()) >= int(payload["exp"]):
                raise InvalidAccessToken("invalid access token")
            role = Role(str(payload.get("role")))
            account_id = uuid.UUID(str(payload["sub"]))
        except (ValueError, TypeError) as exc:
            raise InvalidAccessToken("invalid access token") from exc
        return Actor(account_id=account_id, role=role)
