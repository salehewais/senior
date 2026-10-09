"""Flask HTTP: health, metrics, and the device-token API."""

from __future__ import annotations

import time
import uuid
from datetime import datetime

from flask import Flask, Response, g, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from notification_service.auth import Unauthenticated, VerifierNotConfigured, authenticate
from notification_service.metrics import record_http
from notification_service.settings import http_port, jwt_public_key
from notification_service.store import DeviceToken, MemoryStore, SqlStore

Store = MemoryStore | SqlStore


def create_app(*, store: Store | None = None, public_key: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config["STORE"] = store if store is not None else SqlStore.from_settings()
    app.config["JWT_PUBLIC_KEY"] = jwt_public_key() if public_key is None else public_key

    @app.before_request
    def _begin() -> None:
        g.started = time.perf_counter()
        incoming = request.headers.get("X-Correlation-Id", "")
        g.correlation_id = incoming if _safe_correlation(incoming) else str(uuid.uuid4())

    @app.after_request
    def _finish(response: Response) -> Response:
        response.headers["X-Correlation-Id"] = g.correlation_id
        if request.path != "/metrics":
            rule = request.url_rule.rule if request.url_rule is not None else "unmatched"
            record_http(rule, response.status_code, time.perf_counter() - g.started)
        return response

    @app.get("/health/live")
    def live():
        return jsonify({"status": "live"})

    @app.get("/health/ready")
    def ready():
        if not _store().ping():
            return _error(503, "DEPENDENCY_UNAVAILABLE", "notification_db is unavailable.")
        return jsonify({"status": "ready"})

    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    @app.post("/api/v1/device-tokens")
    def register_token():
        actor, error = _actor()
        if error is not None:
            return error
        body = request.get_json(silent=True)
        if not isinstance(body, dict):
            return _error(400, "INVALID_BODY", "A JSON object with token and platform is required.")
        try:
            with _store().transaction():
                row, created = _store().register_token(actor.account_id, body.get("token"), body.get("platform"))
        except ValueError:
            return _error(400, "INVALID_BODY", "token and platform are not acceptable.")
        status = 201 if created else 200
        return jsonify(_token_json(row)), status

    @app.get("/api/v1/device-tokens")
    def list_tokens():
        actor, error = _actor()
        if error is not None:
            return error
        with _store().transaction():
            rows = _store().list_tokens(actor.account_id)
        return jsonify({"device_tokens": [_token_json(row) for row in rows]})

    @app.delete("/api/v1/device-tokens/<uuid:token_id>")
    def delete_token(token_id: uuid.UUID):
        actor, error = _actor()
        if error is not None:
            return error
        with _store().transaction():
            removed = _store().delete_token(actor.account_id, token_id)
        if not removed:
            return _error(404, "NOT_FOUND", "That device token is not registered for this account.")
        return Response(status=204)

    return app


def _store() -> Store:
    from flask import current_app

    return current_app.config["STORE"]


def _actor():
    from flask import current_app

    try:
        actor = authenticate(request.headers.get("Authorization"), current_app.config["JWT_PUBLIC_KEY"])
    except VerifierNotConfigured:
        return None, _error(503, "DEPENDENCY_UNAVAILABLE", "The notification service cannot verify access tokens.")
    except Unauthenticated:
        return None, _error(401, "UNAUTHENTICATED", "Missing or invalid access token.")
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


def _error(status: int, code: str, message: str):
    correlation_id = getattr(g, "correlation_id", "")
    return jsonify(
        {
            "error": {
                "code": code,
                "message": message,
                "correlation_id": correlation_id,
                "details": [],
            }
        }
    ), status


def _safe_correlation(value: str) -> bool:
    if not value or len(value) > 200:
        return False
    return all(char.isalnum() or char in "-_" for char in value)


def main() -> None:
    app = create_app()
    app.run(host="0.0.0.0", port=http_port(), threaded=True)


if __name__ == "__main__":
    main()
