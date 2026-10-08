"""Opaque refresh secrets. The database stores sha256(secret), never the secret."""

import hashlib
import secrets


class Sha256RefreshTokens:
    def new_secret(self) -> str:
        return secrets.token_urlsafe(32)

    def hash_secret(self, raw: str) -> str:
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
