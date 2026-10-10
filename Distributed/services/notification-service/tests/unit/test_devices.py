"""Device tokens belong to the access-token subject."""

from __future__ import annotations

import uuid

from tests.conftest import OTHER_PRIVATE_KEY, PUBLIC_KEY, access_token

from notification_service.factory import create_app
from notification_service.persistence.store import MemoryStore


def _client(store: MemoryStore):
    app = create_app(store=store, public_key=PUBLIC_KEY)
    app.config["TESTING"] = True
    return app.test_client()


def test_caller_can_store_list_and_remove_a_device_token() -> None:
    store = MemoryStore()
    client = _client(store)
    owner = uuid.uuid4()
    other = uuid.uuid4()
    created = client.post(
        "/api/v1/device-tokens",
        json={"token": "owner-token", "platform": "android"},
        headers={"Authorization": f"Bearer {access_token(owner)}"},
    )
    assert created.status_code == 201
    token_id = created.get_json()["id"]
    client.post(
        "/api/v1/device-tokens",
        json={"token": "other-token", "platform": "ios"},
        headers={"Authorization": f"Bearer {access_token(other)}"},
    )
    listed = client.get(
        "/api/v1/device-tokens",
        headers={"Authorization": f"Bearer {access_token(owner)}"},
    )
    assert listed.status_code == 200
    body = listed.get_json()["device_tokens"]
    assert [row["token"] for row in body] == ["owner-token"]
    assert body[0]["platform"] == "android"
    stolen = client.delete(
        f"/api/v1/device-tokens/{token_id}",
        headers={"Authorization": f"Bearer {access_token(other)}"},
    )
    assert stolen.status_code == 404
    removed = client.delete(
        f"/api/v1/device-tokens/{token_id}",
        headers={"Authorization": f"Bearer {access_token(owner)}"},
    )
    assert removed.status_code == 204
    after = client.get(
        "/api/v1/device-tokens",
        headers={"Authorization": f"Bearer {access_token(owner)}"},
    )
    assert after.get_json()["device_tokens"] == []
    still_there = client.get(
        "/api/v1/device-tokens",
        headers={"Authorization": f"Bearer {access_token(other)}"},
    )
    assert [row["token"] for row in still_there.get_json()["device_tokens"]] == ["other-token"]


def test_missing_and_foreign_tokens_are_rejected() -> None:
    client = _client(MemoryStore())
    missing = client.get("/api/v1/device-tokens")
    assert missing.status_code == 401
    assert missing.get_json()["error"]["code"] == "UNAUTHENTICATED"
    foreign = client.get(
        "/api/v1/device-tokens",
        headers={"Authorization": f"Bearer {access_token(uuid.uuid4(), private=OTHER_PRIVATE_KEY)}"},
    )
    assert foreign.status_code == 401


def test_health_live_does_not_need_a_database() -> None:
    store = MemoryStore()
    store.reachable = False
    client = _client(store)
    live = client.get("/health/live")
    assert live.status_code == 200
    assert live.get_json()["status"] == "live"
    ready = client.get("/health/ready")
    assert ready.status_code == 503
    assert ready.get_json()["error"]["code"] == "DEPENDENCY_UNAVAILABLE"
    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert b"http_requests_total" in metrics.data
