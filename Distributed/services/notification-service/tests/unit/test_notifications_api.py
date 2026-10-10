"""Staff can list deliveries. Customers cannot. The HTML page is public."""

from __future__ import annotations

import uuid

from tests.conftest import OTHER_PRIVATE_KEY, PUBLIC_KEY, access_token

from notification_service.domain.records import DeliveryRecord
from notification_service.factory import create_app
from notification_service.persistence.store import MemoryStore


def _client(store: MemoryStore):
    app = create_app(store=store, public_key=PUBLIC_KEY)
    app.config["TESTING"] = True
    return app.test_client()


def test_page_loads_without_a_token() -> None:
    client = _client(MemoryStore())
    for path in ("/notifications/", "/notifications"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.content_type.startswith("text/html")
        body = response.get_data(as_text=True)
        assert "admin@admin.com" in body
        assert "/api/v1/auth/login" in body
        assert "sessionStorage" in body
        assert "/api/v1/notifications" in body
        assert "/api/v1/orders" not in body


def test_staff_can_list_deliveries_and_customers_cannot() -> None:
    store = MemoryStore()
    account_id = uuid.uuid4()
    store.add_delivery(
        DeliveryRecord(
            event_id=uuid.uuid4(),
            channel="email",
            account_id=account_id,
            destination=f"account:{account_id}",
            summary="OrderConfirmed",
        )
    )
    client = _client(store)
    missing = client.get("/api/v1/notifications")
    assert missing.status_code == 401
    assert missing.get_json()["error"]["code"] == "UNAUTHENTICATED"
    customer = client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {access_token(uuid.uuid4(), role='customer')}"},
    )
    assert customer.status_code == 403
    assert customer.get_json()["error"]["code"] == "FORBIDDEN"
    foreign = client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {access_token(uuid.uuid4(), private=OTHER_PRIVATE_KEY, role='admin')}"},
    )
    assert foreign.status_code == 401
    for role in ("admin", "manager"):
        listed = client.get(
            "/api/v1/notifications",
            headers={"Authorization": f"Bearer {access_token(uuid.uuid4(), role=role)}"},
        )
        assert listed.status_code == 200, role
        row = listed.get_json()["notifications"][0]
        assert row["channel"] == "email"
        assert row["summary"] == "OrderConfirmed"
        assert row["account_id"] == str(account_id)
        assert row["destination"] == f"account:{account_id}"
        assert row["created_at"].endswith("Z")
