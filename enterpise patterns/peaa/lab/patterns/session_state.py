"""Session state patterns. فين نحتفظ بحالة المحادثة."""

from __future__ import annotations

import json

from peaa.lab.lease_app.db import fresh
from peaa.lab.registry import register


@register("client_session_state")
def demo_client_session() -> None:
    """The client sends the wizard state back each time. الحالة ترجع مع الطلب."""
    hidden = {"step": "confirm", "lease_id": 1, "asset_id": 2}
    posted = dict(hidden)
    posted["step"] = "done"
    print("client_session_state", posted)


_SERVER: dict[str, dict] = {}


@register("server_session_state")
def demo_server_session() -> None:
    _SERVER.clear()
    _SERVER["sess-7"] = {"lease_id": 1, "step": "choose_asset"}
    _SERVER["sess-7"]["step"] = "confirm"
    print("server_session_state", _SERVER["sess-7"])


@register("database_session_state")
def demo_database_session() -> None:
    conn = fresh()
    payload = {"lease_id": 1, "step": "confirm"}
    conn.execute(
        "INSERT INTO sessions (id, payload) VALUES (?, ?)",
        ("sess-7", json.dumps(payload)),
    )
    conn.commit()
    raw = conn.execute("SELECT payload FROM sessions WHERE id = 'sess-7'").fetchone()["payload"]
    print("database_session_state", json.loads(raw))
