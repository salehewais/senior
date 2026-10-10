"""Device-token routes. The caller is the access-token subject."""

from __future__ import annotations

import uuid
from datetime import datetime

from flask import Blueprint, Response, current_app, jsonify, request

from notification_service.api.errors import error_response
from notification_service.domain.protocols import Store
from notification_service.domain.records import DeviceToken
from notification_service.security.auth import Unauthenticated, VerifierNotConfigured, authenticate
from notification_service.services import device_tokens as token_service

bp = Blueprint("device_tokens", __name__)


@bp.post("/api/v1/device-tokens")
def register_token():
    actor, error = _actor()
    if error is not None:
        return error
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return error_response(400, "INVALID_BODY", "A JSON object with token and platform is required.")
    try:
        row, created = token_service.register_token(
            _store(),
            actor.account_id,
            body.get("token"),
            body.get("platform"),
        )
    except ValueError:
        return error_response(400, "INVALID_BODY", "token and platform are not acceptable.")
    status = 201 if created else 200
    return jsonify(_token_json(row)), status


@bp.get("/api/v1/device-tokens")
def list_tokens():
    actor, error = _actor()
    if error is not None:
        return error
    rows = token_service.list_tokens(_store(), actor.account_id)
    return jsonify({"device_tokens": [_token_json(row) for row in rows]})


@bp.delete("/api/v1/device-tokens/<uuid:token_id>")
def delete_token(token_id: uuid.UUID):
    actor, error = _actor()
    if error is not None:
        return error
    removed = token_service.delete_token(_store(), actor.account_id, token_id)
    if not removed:
        return error_response(404, "NOT_FOUND", "That device token is not registered for this account.")
    return Response(status=204)


def _store() -> Store:
    return current_app.config["STORE"]


def _actor():
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
    return actor, None


def _token_json(row: DeviceToken) -> dict[str, str]:
    return {
        "id": str(row.id),
        "token": row.token,
        "platform": row.platform,
        "created_at": _iso(row.created_at),
    }


def _iso(value: datetime) -> str:
    text = value.isoformat()
    if text.endswith("+00:00"):
        return text[:-6] + "Z"
    return text
