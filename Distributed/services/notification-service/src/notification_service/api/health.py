"""Liveness and readiness."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify

from notification_service.api.errors import error_response
from notification_service.domain.protocols import Store

bp = Blueprint("health", __name__)


@bp.get("/health/live")
def live():
    return jsonify({"status": "live"})


@bp.get("/health/ready")
def ready():
    if not _store().ping():
        return error_response(503, "DEPENDENCY_UNAVAILABLE", "notification_db is unavailable.")
    return jsonify({"status": "ready"})


def _store() -> Store:
    return current_app.config["STORE"]
