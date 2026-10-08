from tests.support.http import make_client


def test_cors_allowlist_is_only_the_local_frontend_and_does_not_skip_auth() -> None:
    client, *_ = make_client()

    allowed = client.get("/health/live", headers={"Origin": "http://127.0.0.1:5173"})
    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
    assert allowed.headers["access-control-allow-origin"] != "*"

    preflight = client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,x-correlation-id",
        },
    )
    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "*" not in preflight.headers["access-control-allow-origin"]

    foreign = client.get("/health/live", headers={"Origin": "https://evil.example"})
    assert foreign.status_code == 200
    assert "access-control-allow-origin" not in foreign.headers

    products = client.get("/api/v1/products", headers={"Origin": "http://127.0.0.1:5173"})
    assert products.status_code == 401
    assert products.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
