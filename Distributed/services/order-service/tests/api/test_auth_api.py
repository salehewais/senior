import hashlib
import uuid
from datetime import timedelta

import jwt
from tests.support.http import INTERNAL_TOKEN, PASSWORD, add_staff, bearer, login, make_client, register

from order_service.domain.roles import Role


def test_register_ignores_role_and_does_not_return_the_password() -> None:
    client, store, _clock, public_pem = make_client()
    response = register(
        client,
        email="Ada@Example.com",
        extra={"role": "admin"},
    )
    assert response.status_code == 201
    body = response.json()
    assert PASSWORD not in response.text
    assert "password_hash" not in response.text
    assert body["token_type"] == "Bearer"
    assert body["expires_in"] == 900
    claims = jwt.decode(
        body["access_token"],
        public_pem,
        algorithms=["RS256"],
        options={"verify_exp": False, "verify_iat": False},
    )
    assert claims["role"] == "customer"
    assert claims["token_type"] == "access"
    assert claims["sub"]
    account = next(iter(store.accounts.values()))
    assert account.role == Role.CUSTOMER
    assert account.email == "ada@example.com"
    assert account.password_hash.startswith("$argon2id$")
    assert account.password_hash != PASSWORD
    assert account.id.value == uuid.UUID(claims["sub"])
    assert store.customers[account.id.value].email == account.email
    raw_refresh = body["refresh_token"]
    stored = next(iter(store.refresh_tokens.values()))
    assert stored.token_hash != raw_refresh
    assert stored.token_hash == hashlib.sha256(raw_refresh.encode()).hexdigest()
    for customer in store.customers.values():
        for event in customer.pending_events():
            assert not hasattr(event, "password")
            assert not hasattr(event, "password_hash")


def test_login_hides_whether_the_email_exists_and_ignores_role() -> None:
    client, _store, _clock, public_pem = make_client()
    assert register(client, email="ada@example.com").status_code == 201
    wrong = client.post(
        "/api/v1/auth/login",
        json={"email": "ada@example.com", "password": "not-the-password", "role": "admin"},
    )
    missing = client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "not-the-password"},
    )
    assert wrong.status_code == missing.status_code == 401
    assert wrong.json()["error"]["code"] == "UNAUTHENTICATED"
    assert wrong.json()["error"]["message"] == missing.json()["error"]["message"]
    assert "ada@" not in wrong.json()["error"]["message"]

    logged_in = client.post(
        "/api/v1/auth/login",
        json={"email": "ADA@example.com", "password": PASSWORD, "role": "admin"},
    )
    assert logged_in.status_code == 200
    claims = jwt.decode(
        logged_in.json()["access_token"],
        public_pem,
        algorithms=["RS256"],
        options={"verify_exp": False, "verify_iat": False},
    )
    assert claims["role"] == "customer"


def test_refresh_rotates_and_reuse_of_the_old_token_is_rejected() -> None:
    client, store, _clock, _public = make_client()
    first = register(client).json()
    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": first["refresh_token"]})
    assert refreshed.status_code == 200
    second = refreshed.json()
    assert second["refresh_token"] != first["refresh_token"]
    assert second["access_token"] != first["access_token"]
    reused = client.post("/api/v1/auth/refresh", json={"refresh_token": first["refresh_token"]})
    assert reused.status_code == 401
    assert reused.json()["error"]["code"] == "UNAUTHENTICATED"
    active = [token for token in store.refresh_tokens.values() if token.revoked_at is None]
    assert len(active) == 1
    assert active[0].parent_id is not None
    still_good = client.post("/api/v1/auth/refresh", json={"refresh_token": second["refresh_token"]})
    assert still_good.status_code == 200


def test_logout_revokes_refresh_and_leaves_the_access_token_until_it_expires() -> None:
    client, _store, _clock, _public = make_client()
    tokens = register(client).json()
    logged_out = client.post("/api/v1/auth/logout", json={"refresh_token": tokens["refresh_token"]})
    assert logged_out.status_code == 204
    assert logged_out.content == b""
    again = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert again.status_code == 401
    listed = client.get("/api/v1/products", headers=bearer(tokens["access_token"]))
    assert listed.status_code == 200


def test_missing_or_invalid_access_token_is_401_and_expired_token_is_401() -> None:
    client, _store, clock, _public = make_client()
    missing = client.get("/api/v1/products")
    assert missing.status_code == 401
    assert missing.json()["error"]["code"] == "UNAUTHENTICATED"
    garbage = client.get("/api/v1/products", headers={"Authorization": "Bearer not-a-jwt"})
    assert garbage.status_code == 401
    assert garbage.json()["error"]["message"] == missing.json()["error"]["message"]

    tokens = register(client).json()
    clock.jump(timedelta(minutes=16))
    expired = client.get("/api/v1/products", headers=bearer(tokens["access_token"]))
    assert expired.status_code == 401
    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refreshed.status_code == 200
    recovered = client.get("/api/v1/products", headers=bearer(refreshed.json()["access_token"]))
    assert recovered.status_code == 200


def test_customer_cannot_see_another_customers_order_or_use_a_staff_cancel_reason() -> None:
    client, store, clock, _public = make_client()
    add_staff(store, clock, email="admin@example.com", role=Role.ADMIN)
    add_staff(store, clock, email="manager@example.com", role=Role.MANAGER)
    admin, _refresh = login(client, "admin@example.com")
    manager, _refresh = login(client, "manager@example.com")
    product = client.post(
        "/api/v1/products",
        headers=bearer(admin),
        json={"sku": "MUG-01", "name": "Mug", "unit_price": {"amount_minor": 500, "currency": "USD"}},
    )
    assert product.status_code == 201
    ada = register(client, email="ada@example.com", display_name="Ada").json()["access_token"]
    grace = register(client, email="grace@example.com", display_name="Grace").json()["access_token"]
    created = client.post(
        "/api/v1/orders",
        headers=bearer(ada),
        json={"items": [{"product_id": product.json()["id"], "quantity": 1}]},
    )
    assert created.status_code == 201
    order_id = created.json()["id"]

    hidden = client.get(f"/api/v1/orders/{order_id}", headers=bearer(grace))
    missing = client.get(f"/api/v1/orders/{uuid.uuid4()}", headers=bearer(grace))
    assert hidden.status_code == missing.status_code == 404
    assert hidden.json()["error"]["message"] == missing.json()["error"]["message"]

    own_list = client.get("/api/v1/orders", headers=bearer(grace))
    ada_list = client.get("/api/v1/orders", headers=bearer(ada))
    admin_list = client.get("/api/v1/orders", headers=bearer(admin))
    assert own_list.json()["items"] == []
    assert [item["id"] for item in ada_list.json()["items"]] == [order_id]
    assert [item["id"] for item in admin_list.json()["items"]] == [order_id]

    staff_reason = client.post(
        f"/api/v1/orders/{order_id}/cancel",
        headers=bearer(ada),
        json={"reason": "staff_request"},
    )
    assert staff_reason.status_code == 403
    assert staff_reason.json()["error"]["code"] == "FORBIDDEN"
    assert client.get(f"/api/v1/orders/{order_id}", headers=bearer(ada)).json()["status"] == "PENDING"

    other_cancel = client.post(
        f"/api/v1/orders/{order_id}/cancel",
        headers=bearer(grace),
        json={"reason": "customer_request"},
    )
    assert other_cancel.status_code == 404

    cancelled = client.post(
        f"/api/v1/orders/{order_id}/cancel",
        headers=bearer(manager),
        json={"reason": "staff_request"},
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["cancel_reason"] == "staff_request"


def test_admin_cannot_skip_the_state_machine() -> None:
    client, store, clock, _public = make_client()
    add_staff(store, clock, email="admin@example.com", role=Role.ADMIN)
    admin, _refresh = login(client, "admin@example.com")
    product = client.post(
        "/api/v1/products",
        headers=bearer(admin),
        json={"sku": "MUG-02", "name": "Mug", "unit_price": {"amount_minor": 500, "currency": "USD"}},
    )
    ada = register(client, email="ada@example.com").json()["access_token"]
    created = client.post(
        "/api/v1/orders",
        headers=bearer(ada),
        json={"items": [{"product_id": product.json()["id"], "quantity": 1}]},
    )
    order_id = created.json()["id"]
    assert client.post(f"/api/v1/orders/{order_id}/confirm", headers=bearer(admin)).status_code == 200
    illegal = client.post(
        f"/api/v1/orders/{order_id}/cancel",
        headers=bearer(admin),
        json={"reason": "staff_request"},
    )
    assert illegal.status_code == 409
    assert illegal.json()["error"]["code"] == "INVALID_STATE_TRANSITION"


def test_catalog_and_customer_authorization() -> None:
    client, store, clock, _public = make_client()
    add_staff(store, clock, email="admin@example.com", role=Role.ADMIN)
    add_staff(store, clock, email="manager@example.com", role=Role.MANAGER)
    admin, _refresh = login(client, "admin@example.com")
    manager, _refresh = login(client, "manager@example.com")
    ada_body = register(client, email="ada@example.com", display_name="Ada").json()
    ada = ada_body["access_token"]
    grace = register(client, email="grace@example.com", display_name="Grace").json()["access_token"]

    assert client.post(
        "/api/v1/products",
        headers=bearer(ada),
        json={"sku": "NOPE", "name": "Nope", "unit_price": {"amount_minor": 100, "currency": "USD"}},
    ).status_code == 403
    assert client.post(
        "/api/v1/products",
        headers=bearer(manager),
        json={"sku": "NOPE", "name": "Nope", "unit_price": {"amount_minor": 100, "currency": "USD"}},
    ).status_code == 403
    created = client.post(
        "/api/v1/products",
        headers=bearer(admin),
        json={"sku": "MUG-03", "name": "Mug", "unit_price": {"amount_minor": 100, "currency": "USD"}},
    )
    assert created.status_code == 201
    product_id = created.json()["id"]
    assert client.get(f"/api/v1/products/{product_id}", headers=bearer(ada)).status_code == 200
    patched = client.patch(
        f"/api/v1/products/{product_id}",
        headers=bearer(manager),
        json={"name": "Large mug"},
    )
    assert patched.status_code == 200
    assert patched.json()["name"] == "Large mug"
    assert client.patch(
        f"/api/v1/products/{product_id}",
        headers=bearer(ada),
        json={"name": "Stolen"},
    ).status_code == 403

    assert client.get("/api/v1/customers", headers=bearer(ada)).status_code == 403
    assert client.get("/api/v1/customers", headers=bearer(manager)).status_code == 200
    ada_id = client.get("/api/v1/customers/me", headers=bearer(ada)).json()["id"]
    grace_id = client.get("/api/v1/customers/me", headers=bearer(grace)).json()["id"]
    assert client.get(f"/api/v1/customers/{ada_id}", headers=bearer(ada)).status_code == 200
    hidden = client.get(f"/api/v1/customers/{grace_id}", headers=bearer(ada))
    assert hidden.status_code == 404
    assert hidden.json()["error"]["code"] == "NOT_FOUND"
    assert client.get(f"/api/v1/customers/{grace_id}", headers=bearer(admin)).status_code == 200

    renamed = client.patch(
        "/api/v1/customers/me",
        headers=bearer(ada),
        json={"display_name": "Augusta", "email": "x@y.z"},
    )
    assert renamed.status_code == 200
    assert renamed.json()["display_name"] == "Augusta"
    assert renamed.json()["email"] == "ada@example.com"
    assert client.get("/api/v1/customers/me", headers=bearer(admin)).status_code == 403
    assert client.post(
        "/api/v1/orders",
        headers=bearer(admin),
        json={"items": [{"product_id": product_id, "quantity": 1}]},
    ).status_code == 403

    open_create = client.post(
        "/api/v1/customers",
        json={"email": "new@example.com", "display_name": "New", "password": PASSWORD},
    )
    assert open_create.status_code != 201
    assert "new@example.com" not in {account.email for account in store.accounts.values()}


def test_internal_token_fails_closed_and_rejects_a_customer_jwt() -> None:
    client, store, clock, _public = make_client()
    add_staff(store, clock, email="admin@example.com", role=Role.ADMIN)
    admin, _refresh = login(client, "admin@example.com")
    product = client.post(
        "/api/v1/products",
        headers=bearer(admin),
        json={"sku": "MUG-04", "name": "Mug", "unit_price": {"amount_minor": 100, "currency": "USD"}},
    )
    ada = register(client, email="ada@example.com").json()["access_token"]
    order_id = client.post(
        "/api/v1/orders",
        headers=bearer(ada),
        json={"items": [{"product_id": product.json()["id"], "quantity": 1}]},
    ).json()["id"]
    assert client.post(f"/api/v1/orders/{order_id}/confirm", headers=bearer(ada)).status_code == 200

    blocked = client.post(
        f"/api/v1/internal/orders/{order_id}/processing",
        headers={**bearer(ada), "X-Internal-Token": "nope"},
    )
    assert blocked.status_code == 401

    closed, _store, _clock, _public = make_client(internal_service_token=None)
    unconfigured = closed.post(
        f"/api/v1/internal/orders/{order_id}/processing",
        headers={"X-Internal-Token": INTERNAL_TOKEN},
    )
    assert unconfigured.status_code == 503
    assert unconfigured.json()["error"]["code"] == "DEPENDENCY_UNAVAILABLE"
    assert "internal-test-token" not in unconfigured.text
