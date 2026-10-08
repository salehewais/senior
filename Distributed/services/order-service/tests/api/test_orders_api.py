import uuid

from tests.support.http import INTERNAL_TOKEN, add_staff, bearer, login, make_client, register

from order_service.domain.roles import Role


def test_order_flow_and_error_envelope() -> None:
    client, store, clock, _public = make_client()
    add_staff(store, clock, email="admin@example.com", role=Role.ADMIN)
    admin_token, _admin_refresh = login(client, "admin@example.com")
    product = client.post(
        "/api/v1/products",
        headers=bearer(admin_token),
        json={"sku": "MUG-01", "name": "Mug", "unit_price": {"amount_minor": 1500, "currency": "USD"}},
    )
    assert product.status_code == 201
    product_id = product.json()["id"]

    registered = register(client, email="ada@example.com", display_name="Ada")
    assert registered.status_code == 201
    access = registered.json()["access_token"]
    customer_id = client.get("/api/v1/customers/me", headers=bearer(access)).json()["id"]

    created = client.post(
        "/api/v1/orders",
        headers={**bearer(access), "X-Correlation-Id": "018f1c2a-3333-7c11-8a22-444444444444"},
        json={
            "customer_id": str(uuid.uuid4()),
            "items": [{"product_id": product_id, "quantity": 2}],
            "unit_price": {"amount_minor": 1, "currency": "USD"},
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["customer_id"] == customer_id
    assert body["status"] == "PENDING"
    assert body["total"] == {"amount_minor": 3000, "currency": "USD"}
    assert body["saga_status"] is None
    assert created.headers["X-Correlation-Id"] == "018f1c2a-3333-7c11-8a22-444444444444"
    assert created.headers["X-Request-Id"]
    order_id = body["id"]
    created_outbox = [
        row
        for row in store.outbox.values()
        if row.event_type == "OrderCreated" and row.payload["aggregate_id"] == order_id
    ]
    assert len(created_outbox) == 1
    assert created_outbox[0].status == "pending"
    assert created_outbox[0].published_at is None
    assert created_outbox[0].payload["event_id"] == str(created_outbox[0].id)
    assert created_outbox[0].payload["correlation_id"] == "018f1c2a-3333-7c11-8a22-444444444444"

    confirmed = client.post(f"/api/v1/orders/{order_id}/confirm", headers=bearer(access))
    assert confirmed.status_code == 200
    assert confirmed.json()["status"] == "CONFIRMED"
    assert confirmed.json()["version"] == 2
    confirmed_outbox = [row for row in store.outbox.values() if row.event_type == "OrderConfirmed"]
    assert len(confirmed_outbox) == 1
    assert confirmed_outbox[0].status == "pending"
    assert confirmed_outbox[0].aggregate_id == uuid.UUID(order_id)

    cancelled = client.post(
        f"/api/v1/orders/{order_id}/cancel",
        headers=bearer(access),
        json={"reason": "customer_request"},
    )
    assert cancelled.status_code == 409
    error = cancelled.json()["error"]
    assert error["code"] == "INVALID_STATE_TRANSITION"
    assert "CONFIRMED" in error["message"]
    assert "Traceback" not in error["message"]
    assert error["correlation_id"]
    assert not any(row.event_type == "OrderCancelled" for row in store.outbox.values())

    internal = {"X-Internal-Token": INTERNAL_TOKEN}
    processing = client.post(f"/api/v1/internal/orders/{order_id}/processing", headers=internal)
    assert processing.status_code == 200
    shipped = client.post(
        f"/api/v1/internal/orders/{order_id}/shipped",
        headers=internal,
        json={"tracking_reference": "TRK-100"},
    )
    assert shipped.json()["status"] == "SHIPPED"
    assert shipped.json()["tracking_reference"] == "TRK-100"
    delivered = client.post(f"/api/v1/internal/orders/{order_id}/delivered", headers=internal)
    assert delivered.json()["status"] == "DELIVERED"

    listed = client.get("/api/v1/orders?limit=10", headers=bearer(access))
    assert listed.status_code == 200
    assert listed.json()["items"][0]["id"] == order_id
    assert listed.json()["next_cursor"] is None

    # A customer bearer token is not permission for fulfillment, even on a later call.
    rejected = client.post(
        f"/api/v1/internal/orders/{order_id}/processing",
        headers=bearer(access),
    )
    assert rejected.status_code == 401
    assert rejected.json()["error"]["code"] == "UNAUTHENTICATED"


def test_validation_error_uses_the_error_envelope() -> None:
    client, _store, _clock, _public = make_client()
    registered = register(client)
    assert registered.status_code == 201
    response = client.post(
        "/api/v1/orders",
        headers=bearer(registered.json()["access_token"]),
        json={"items": []},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert response.json()["error"]["details"]


def test_unknown_order_is_404() -> None:
    client, _store, _clock, _public = make_client()
    registered = register(client)
    response = client.get(
        f"/api/v1/orders/{uuid.uuid4()}",
        headers=bearer(registered.json()["access_token"]),
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_live_does_not_require_a_database_and_ready_does() -> None:
    client, _store, _clock, _public = make_client()
    assert client.get("/health/live").json() == {"status": "live"}
    ready = client.get("/health/ready")
    assert ready.status_code == 503
    assert ready.json()["error"]["code"] == "DEPENDENCY_UNAVAILABLE"


def test_offset_pagination_on_products() -> None:
    client, store, clock, _public = make_client()
    add_staff(store, clock, email="admin@example.com", role=Role.ADMIN)
    token, _refresh = login(client, "admin@example.com")
    for sku in ("A", "B", "C"):
        created = client.post(
            "/api/v1/products",
            headers=bearer(token),
            json={"sku": sku, "name": sku, "unit_price": {"amount_minor": 100, "currency": "USD"}},
        )
        assert created.status_code == 201
    page = client.get("/api/v1/products?limit=2&offset=0", headers=bearer(token))
    assert page.status_code == 200
    assert len(page.json()["items"]) == 2
    assert page.json()["offset"] == 0
