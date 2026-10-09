"""Signature checks for the gateway verifier. No Docker and no role policy."""

from __future__ import annotations

import importlib.util
import time
import unittest
import uuid
from pathlib import Path

try:
    import jwt
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
except ImportError:  # pragma: no cover - host without the order-service deps
    jwt = None


def _load():
    path = Path(__file__).resolve().parents[1] / "jwt_check.py"
    spec = importlib.util.spec_from_file_location("jwt_check", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("jwt_check.py is missing")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(jwt is not None, "PyJWT is not installed")
class JwtCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.jwt_check = _load()
        cls.private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.public_pem = (
            cls.private.public_key()
            .public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode("ascii")
        )
        other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cls.other_private = other

    def _token(self, private, **overrides: object) -> str:
        now = int(time.time())
        payload = {
            "sub": str(uuid.uuid4()),
            "role": "customer",
            "iat": now - 10,
            "exp": now + 900,
            "token_type": "access",
        }
        payload.update(overrides)
        encoded = jwt.encode(payload, private, algorithm="RS256")
        return encoded if isinstance(encoded, str) else encoded.decode("ascii")

    def test_missing_and_bad_signature_are_rejected(self) -> None:
        verify = self.jwt_check.verify_authorization
        with self.assertRaises(self.jwt_check.TokenRejected):
            verify(None, self.public_pem)
        with self.assertRaises(self.jwt_check.TokenRejected):
            verify("Bearer", self.public_pem)
        forged = self._token(self.other_private, role="admin")
        with self.assertRaises(self.jwt_check.TokenRejected):
            verify(f"Bearer {forged}", self.public_pem)

    def test_role_claim_is_not_a_gateway_decision(self) -> None:
        verify = self.jwt_check.verify_authorization
        for role in ("customer", "admin", "manager", "not-a-role"):
            token = self._token(self.private, role=role)
            verify(f"Bearer {token}", self.public_pem)

    def test_expired_and_non_access_tokens_are_rejected(self) -> None:
        verify = self.jwt_check.verify_authorization
        expired = self._token(self.private, exp=int(time.time()) - 60)
        with self.assertRaises(self.jwt_check.TokenRejected):
            verify(f"Bearer {expired}", self.public_pem)
        refresh_shaped = self._token(self.private, token_type="refresh")
        with self.assertRaises(self.jwt_check.TokenRejected):
            verify(f"Bearer {refresh_shaped}", self.public_pem)

    def test_error_document_uses_the_api_envelope(self) -> None:
        thread = "018f1c2a-3333-7c11-8a22-444444444444"
        body = self.jwt_check.error_document(thread).decode("utf-8")
        self.assertIn('"code": "UNAUTHENTICATED"', body)
        self.assertIn(thread, body)
        self.assertNotIn("admin", body)


if __name__ == "__main__":
    unittest.main()
