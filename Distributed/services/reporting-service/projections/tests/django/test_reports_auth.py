"""Report routes accept admin and manager tokens and reject everyone else."""

from __future__ import annotations

import time
import uuid

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.test import Client, TestCase, override_settings

_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_PRIVATE = _KEY.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)
_PUBLIC = (
    _KEY.public_key()
    .public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    .decode("ascii")
)
_OTHER = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_OTHER_PRIVATE = _OTHER.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)


def _token(private: bytes, role: str, *, expired: bool = False) -> str:
    now = int(time.time())
    payload = {
        "sub": str(uuid.uuid4()),
        "role": role,
        "iat": now - 10,
        "exp": now - 5 if expired else now + 900,
        "token_type": "access",
    }
    encoded = jwt.encode(payload, private, algorithm="RS256")
    return encoded if isinstance(encoded, str) else encoded.decode("ascii")


@override_settings(JWT_PUBLIC_KEY=_PUBLIC)
class ReportAuthTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_customer_token_is_forbidden(self) -> None:
        response = self.client.get(
            "/api/v1/reports/orders/summary",
            HTTP_AUTHORIZATION=f"Bearer {_token(_PRIVATE, 'customer')}",
        )
        self.assertEqual(response.status_code, 403)
        body = response.json()
        self.assertEqual(body["error"]["code"], "FORBIDDEN")
        self.assertIn("correlation_id", body["error"])
        self.assertEqual(body["error"]["details"], [])

    def test_missing_token_is_unauthenticated(self) -> None:
        response = self.client.get("/api/v1/reports/revenue")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "UNAUTHENTICATED")

    def test_invalid_signature_is_unauthenticated_even_if_the_role_says_admin(self) -> None:
        response = self.client.get(
            "/api/v1/reports/orders",
            HTTP_AUTHORIZATION=f"Bearer {_token(_OTHER_PRIVATE, 'admin')}",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "UNAUTHENTICATED")

    def test_admin_and_manager_can_read_an_empty_report(self) -> None:
        for role in ("admin", "manager"):
            response = self.client.get(
                "/api/v1/reports/orders/summary",
                HTTP_AUTHORIZATION=f"Bearer {_token(_PRIVATE, role)}",
                HTTP_X_CORRELATION_ID="018f1c2a-3333-7c11-8a22-444444444444",
            )
            self.assertEqual(response.status_code, 200, role)
            self.assertEqual(response.json(), {"as_of": None, "by_status": []})
            self.assertEqual(response.headers["X-Correlation-Id"], "018f1c2a-3333-7c11-8a22-444444444444")
