"""Shared fixtures for the notification service tests."""

from __future__ import annotations

import json
import time
import uuid

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
PRIVATE_KEY = _KEY.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)
PUBLIC_KEY = (
    _KEY.public_key()
    .public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    .decode("ascii")
)
_OTHER = rsa.generate_private_key(public_exponent=65537, key_size=2048)
OTHER_PRIVATE_KEY = _OTHER.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)


def access_token(account_id: uuid.UUID, *, private: bytes = PRIVATE_KEY, role: str = "customer") -> str:
    now = int(time.time())
    payload = {
        "sub": str(account_id),
        "role": role,
        "iat": now - 10,
        "exp": now + 900,
        "token_type": "access",
    }
    encoded = jwt.encode(payload, private, algorithm="RS256")
    return encoded if isinstance(encoded, str) else encoded.decode("ascii")


def envelope(
    event_type: str,
    order_id: uuid.UUID,
    payload: dict[str, object],
    *,
    event_id: uuid.UUID | None = None,
) -> dict:
    return {
        "event_id": str(event_id or uuid.uuid4()),
        "event_type": event_type,
        "occurred_at": "2026-10-09T12:00:00Z",
        "producer": "order-service",
        "aggregate_id": str(order_id),
        "correlation_id": str(uuid.uuid4()),
        "causation_id": str(uuid.uuid4()),
        "version": 1,
        "payload": payload,
    }


def confirmed_body(order_id: uuid.UUID, account_id: uuid.UUID, *, event_id: uuid.UUID | None = None) -> bytes:
    body = envelope(
        "OrderConfirmed",
        order_id,
        {
            "order_id": str(order_id),
            "customer_id": str(account_id),
            "status": "CONFIRMED",
            "items": [],
            "total": {"amount_minor": 3000, "currency": "USD"},
            "aggregate_version": 2,
        },
        event_id=event_id,
    )
    return json.dumps(body).encode("utf-8")
