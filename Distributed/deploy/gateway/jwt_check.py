"""RS256 check used by Traefik ForwardAuth.

The process has the order-service public key only. It does not issue tokens.
It does not read a role, a price, a stock figure, or an order. A request that
passes here is still verified again by the order service or the reporting service.
"""

from __future__ import annotations

import json
import os
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import jwt

_ALGORITHM = "RS256"
_MESSAGE = "Missing or invalid access token."


class TokenRejected(Exception):
    """The Authorization header is missing or the access token does not verify."""


def verify_authorization(header: str | None, public_key_pem: str) -> None:
    """Raise TokenRejected unless header is a Bearer access token signed with public_key_pem.

    Role is not inspected. Authorization policy stays in the services.
    """

    if not public_key_pem.strip():
        raise TokenRejected(_MESSAGE)
    if header is None:
        raise TokenRejected(_MESSAGE)
    scheme, separator, token = header.partition(" ")
    if separator != " " or scheme.lower() != "bearer" or not token.strip():
        raise TokenRejected(_MESSAGE)
    try:
        payload = jwt.decode(
            token.strip(),
            public_key_pem,
            algorithms=[_ALGORITHM],
            leeway=5,
            options={"require": ["exp", "iat", "sub"]},
        )
    except jwt.PyJWTError as exc:
        raise TokenRejected(_MESSAGE) from exc
    if payload.get("token_type") != "access":
        raise TokenRejected(_MESSAGE)


def correlation_id(raw: str | None) -> str:
    if raw:
        try:
            return str(uuid.UUID(raw))
        except (ValueError, TypeError, AttributeError):
            pass
    return str(uuid.uuid4())


def error_document(correlation: str) -> bytes:
    body = {
        "error": {
            "code": "UNAUTHENTICATED",
            "message": _MESSAGE,
            "correlation_id": correlation,
            "details": [],
        }
    }
    return json.dumps(body).encode("utf-8")


def load_public_key(path: str) -> str:
    with open(path, encoding="utf-8") as handle:
        pem = handle.read()
    if "BEGIN PUBLIC KEY" not in pem and "BEGIN RSA PUBLIC KEY" not in pem:
        raise SystemExit(f"public key at {path} is not a PEM public key")
    return pem


class Checker:
    def __init__(self, public_key_pem: str) -> None:
        self.public_key_pem = public_key_pem

    def handler(self) -> type[BaseHTTPRequestHandler]:
        checker = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def do_GET(self) -> None:  # noqa: N802 - stdlib name
                path = self.path.split("?", 1)[0].rstrip("/") or "/"
                if path == "/ready":
                    self._empty(200)
                    return
                if path != "/verify":
                    self._empty(404)
                    return
                thread = correlation_id(self.headers.get("X-Correlation-Id"))
                try:
                    verify_authorization(self.headers.get("Authorization"), checker.public_key_pem)
                except TokenRejected:
                    body = error_document(thread)
                    self.send_response(401)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("X-Correlation-Id", thread)
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
                self.send_response(204)
                self.send_header("X-Correlation-Id", thread)
                self.send_header("Content-Length", "0")
                self.end_headers()

            def _empty(self, status: int) -> None:
                self.send_response(status)
                self.send_header("Content-Length", "0")
                self.end_headers()

            def log_message(self, fmt: str, *args: object) -> None:
                # Request line only. Never the Authorization header.
                super().log_message("%s", args[0] if args else fmt)

        return Handler


def serve(public_key_pem: str, host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), Checker(public_key_pem).handler())
    print(f"jwt-check listening on {host}:{port}", flush=True)
    server.serve_forever()


def main() -> None:
    path = os.environ.get("JWT_PUBLIC_KEY_PATH", "/keys/jwt_public.pem")
    host = os.environ.get("JWT_CHECK_HOST", "0.0.0.0")
    port = int(os.environ.get("JWT_CHECK_PORT", "8081"))
    serve(load_public_key(path), host, port)


if __name__ == "__main__":
    main()
