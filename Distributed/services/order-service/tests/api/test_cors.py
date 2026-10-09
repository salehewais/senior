from tests.support.http import make_client


def test_order_service_does_not_emit_browser_cors_headers() -> None:
    """Traefik owns the storefront allow-list.

    A second Access-Control-Allow-Origin on this process would duplicate the
    gateway header. Skipping the gateway (a published port) still requires a
    Bearer token: the origin is not checked here, and it does not grant access.
    """

    client, *_ = make_client()

    live = client.get("/health/live", headers={"Origin": "http://127.0.0.1:5173"})
    assert live.status_code == 200
    assert "access-control-allow-origin" not in live.headers

    foreign = client.get("/health/live", headers={"Origin": "https://evil.example"})
    assert foreign.status_code == 200
    assert "access-control-allow-origin" not in foreign.headers

    products = client.get("/api/v1/products", headers={"Origin": "http://127.0.0.1:5173"})
    assert products.status_code == 401
    assert "access-control-allow-origin" not in products.headers
