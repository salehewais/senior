"""Config assertions, then a Docker curl check when the daemon is up.

The live half starts echo upstreams. It does not need Postgres, Redis,
RabbitMQ, the order service, or the reporting service. If Docker is down,
that half is skipped and this process still exits 0 after the config tests.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tests"))

import test_jwt_check  # noqa: E402
import test_public_routes  # noqa: E402

GATEWAY = "http://127.0.0.1:8080"


def _docker_ready() -> bool:
    if shutil.which("docker") is None:
        return False
    result = subprocess.run(
        ["docker", "info"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def _run_unit_tests() -> None:
    suite = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    suite.addTests(loader.loadTestsFromModule(test_public_routes))
    suite.addTests(loader.loadTestsFromModule(test_jwt_check))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        raise SystemExit(1)


def _mint_keys(directory: Path) -> tuple[str, str]:
    private = directory / "jwt_private.pem"
    public = directory / "jwt_public.pem"
    subprocess.run(
        ["openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-out", str(private)],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(
        ["openssl", "rsa", "-in", str(private), "-pubout", "-out", str(public)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    public.chmod(0o644)
    return str(private), str(public)


def _access_token(private_path: str, *, role: str = "customer") -> str:
    import jwt

    now = int(time.time())
    token = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "role": role,
            "iat": now - 10,
            "exp": now + 900,
            "token_type": "access",
        },
        Path(private_path).read_text(encoding="utf-8"),
        algorithm="RS256",
    )
    return token if isinstance(token, str) else token.decode("ascii")


def _request(
    path: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
) -> tuple[int, dict[str, str], bytes]:
    request = urllib.request.Request(GATEWAY + path, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, dict(response.headers.items()), response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers.items()), exc.read()


def _header(headers: dict[str, str], name: str) -> str:
    for key, value in headers.items():
        if key.lower() == name.lower():
            return value
    return ""


def _wait_until_ready() -> None:
    deadline = time.time() + 40
    last = ""
    while time.time() < deadline:
        try:
            status, _, body = _request("/ping")
            if status == 200:
                return
            last = f"status {status} body {body[:80]!r}"
        except (urllib.error.URLError, TimeoutError) as exc:
            last = str(exc)
        time.sleep(0.5)
    raise SystemExit(f"gateway did not answer /ping ({last})")


def _live(private_path: str) -> None:
    token = _access_token(private_path)
    other = Path(tempfile.mkdtemp()) / "other.pem"
    subprocess.run(
        ["openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-out", str(other)],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    forged = _access_token(str(other), role="admin")

    status, headers, body = _request("/api/v1/products")
    if status != 401:
        raise SystemExit(f"missing token on /api/v1/products returned {status}, expected 401")
    if _header(headers, "X-Upstream-Name"):
        raise SystemExit("missing token was forwarded to an upstream")
    payload = json.loads(body)
    if payload["error"]["code"] != "UNAUTHENTICATED":
        raise SystemExit(f"unexpected 401 body: {payload}")
    if payload["error"]["message"] != "Missing or invalid access token.":
        raise SystemExit("401 did not come from the gateway verifier")

    status, headers, body = _request(
        "/api/v1/products",
        headers={
            "Authorization": f"Bearer {forged}",
            "X-User-Role": "admin",
        },
    )
    if status != 401:
        raise SystemExit(f"forged signature returned {status}, expected 401 at the gateway")
    if _header(headers, "X-Upstream-Name"):
        raise SystemExit("forged signature was forwarded")

    thread = "018f1c2a-3333-7c11-8a22-444444444444"
    status, headers, body = _request(
        "/api/v1/products",
        headers={
            "Authorization": f"Bearer {token}",
            "X-User-Role": "admin",
            "X-User-Id": "11111111-1111-1111-1111-111111111111",
            "X-Internal-Token": "browser-must-not-set-this",
            "X-Correlation-Id": thread,
        },
    )
    if status != 200:
        raise SystemExit(f"valid token returned {status}: {body[:200]!r}")
    echoed = json.loads(body)
    if echoed["upstream"] != "order":
        raise SystemExit(f"products went to {echoed['upstream']}")
    if echoed["x-user-role"] is not None or echoed["x-user-id"] is not None:
        raise SystemExit(f"identity header was forwarded: {echoed}")
    if echoed["x-internal-token"] is not None:
        raise SystemExit("X-Internal-Token was forwarded through the public gateway")
    if not echoed["authorization_present"]:
        raise SystemExit("Authorization was not forwarded")
    if echoed["x-correlation-id"] != thread or thread not in _header(headers, "X-Correlation-Id"):
        raise SystemExit(f"correlation id was not forwarded: {echoed} {_header(headers, 'X-Correlation-Id')}")

    status, headers, _body = _request("/api/v1/products", headers={"X-Correlation-Id": "not-a-uuid"})
    if status != 401:
        raise SystemExit(f"invalid correlation id changed the auth result: {status}")
    generated = _header(headers, "X-Correlation-Id")
    if generated in ("", "not-a-uuid") or len(generated) != 36:
        raise SystemExit(f"invalid correlation id was not replaced: {generated!r}")

    status, headers, body = _request(
        "/api/v1/reports/orders/summary",
        headers={"Authorization": f"Bearer {token}", "X-User-Role": "admin"},
    )
    if status != 200:
        raise SystemExit(f"reports returned {status}: {body[:200]!r}")
    echoed = json.loads(body)
    if echoed["upstream"] != "reporting":
        raise SystemExit(f"/api/v1/reports was forwarded to {echoed['upstream']}, not reporting")
    if echoed["x-user-role"] is not None:
        raise SystemExit("X-User-Role was forwarded to reporting")

    status, headers, body = _request(
        "/api/v1/internal/orders/018f1c2a-3333-7c11-8a22-444444444444/processing",
        method="POST",
        headers={"X-Internal-Token": "secret", "Content-Type": "application/json"},
        body=b"{}",
    )
    if status != 404:
        raise SystemExit(f"internal fulfillment returned {status}, expected 404 from the gateway")
    if b"upstream" in body or _header(headers, "X-Upstream-Name"):
        raise SystemExit("internal fulfillment was forwarded to an upstream")

    status, headers, body = _request(
        "/api/v1/auth/login",
        method="POST",
        headers={"Content-Type": "application/json", "X-User-Role": "admin"},
        body=b"{}",
    )
    if status != 200:
        raise SystemExit(f"public login returned {status}: {body[:200]!r}")
    echoed = json.loads(body)
    if echoed["upstream"] != "order" or echoed["x-user-role"] is not None:
        raise SystemExit(f"public login routing or header strip failed: {echoed}")

    status, headers, _body = _request(
        "/api/v1/products",
        method="OPTIONS",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization,x-correlation-id",
        },
    )
    if status != 204:
        raise SystemExit(f"preflight returned {status}")
    allow_origin = _header(headers, "Access-Control-Allow-Origin")
    if allow_origin != "http://127.0.0.1:5173":
        raise SystemExit(f"CORS origin is {allow_origin!r}")
    if allow_origin == "*":
        raise SystemExit("CORS allow-origin is a wildcard")
    if _header(headers, "X-Upstream-Name"):
        raise SystemExit("preflight was forwarded")

    status, headers, _body = _request(
        "/api/v1/products",
        headers={"Origin": "https://evil.example", "Authorization": f"Bearer {token}"},
    )
    if _header(headers, "Access-Control-Allow-Origin"):
        raise SystemExit("a foreign origin received Access-Control-Allow-Origin")

    print("live gateway checks passed")


def main() -> None:
    _run_unit_tests()
    if not _docker_ready():
        print("Docker is down or not installed. Skipped the live Traefik curl check.")
        return
    if test_jwt_check.jwt is None:
        print("PyJWT is not installed. Skipped the live Traefik curl check.")
        return
    check_dir = ROOT / ".check"
    check_dir.mkdir(exist_ok=True)
    dynamic = (ROOT / "dynamic.yaml").read_text(encoding="utf-8")
    dynamic = dynamic.replace("http://host.docker.internal:8000", "http://order-echo:8000")
    dynamic = dynamic.replace("http://host.docker.internal:8001", "http://reporting-echo:8000")
    dynamic = dynamic.replace("http://host.docker.internal:5173", "http://frontend-echo:8000")
    dynamic_path = check_dir / "dynamic.yaml"
    dynamic_path.write_text(dynamic, encoding="utf-8")
    with tempfile.TemporaryDirectory() as directory:
        _private, public = _mint_keys(Path(directory))
        env = os.environ.copy()
        env["JWT_PUBLIC_KEY_PATH"] = public
        env["GATEWAY_DYNAMIC_FILE"] = str(dynamic_path)
        compose = [
            "docker",
            "compose",
            "-f",
            "compose.yaml",
            "-f",
            "compose.check.yaml",
            "--project-directory",
            str(ROOT),
        ]
        try:
            up = subprocess.run(
                [*compose, "up", "-d", "--build", "--wait"],
                cwd=ROOT,
                env=env,
                check=False,
            )
            if up.returncode != 0:
                subprocess.run([*compose, "logs"], cwd=ROOT, env=env, check=False)
                raise SystemExit(up.returncode)
            _wait_until_ready()
            _live(_private)
        finally:
            subprocess.run([*compose, "down", "--remove-orphans"], cwd=ROOT, env=env, check=False)


if __name__ == "__main__":
    main()
