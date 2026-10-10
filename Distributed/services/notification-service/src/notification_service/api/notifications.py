"""Staff list of mock deliveries, and the public HTML page that reads it."""

from __future__ import annotations

from datetime import UTC, datetime

from flask import Blueprint, current_app, jsonify, render_template, request

from notification_service.api.errors import error_response
from notification_service.domain.protocols import Store
from notification_service.domain.records import ListedDelivery
from notification_service.security.auth import Unauthenticated, VerifierNotConfigured, authenticate
from notification_service.services.notifications import list_deliveries

bp = Blueprint("notifications", __name__)

_STAFF = frozenset({"admin", "manager"})


@bp.get("/api/v1/notifications")
def list_notifications():
    actor, error = _staff()
    if error is not None:
        return error
    del actor
    rows = list_deliveries(_store())
    return jsonify({"notifications": [_delivery_json(row) for row in rows]})


@bp.get("/notifications/")
@bp.get("/notifications")
def notifications_page():
    return render_template("notifications.html")


def _store() -> Store:
    return current_app.config["STORE"]


def _staff():
    try:
        actor = authenticate(request.headers.get("Authorization"), current_app.config["JWT_PUBLIC_KEY"])
    except VerifierNotConfigured:
        return None, error_response(
            503,
            "DEPENDENCY_UNAVAILABLE",
            "The notification service cannot verify access tokens.",
        )
    except Unauthenticated:
        return None, error_response(401, "UNAUTHENTICATED", "Missing or invalid access token.")
    if actor.role not in _STAFF:
        return None, error_response(403, "FORBIDDEN", "Notifications are available to admin and manager.")
    return actor, None


def _delivery_json(row: ListedDelivery) -> dict[str, str]:
    return {
        "channel": row.channel,
        "summary": row.summary,
        "account_id": str(row.account_id),
        "destination": row.destination,
        "created_at": _iso(row.created_at),
    }


def _iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    text = value.astimezone(UTC).isoformat()
    if text.endswith("+00:00"):
        return text[:-6] + "Z"
    return text
