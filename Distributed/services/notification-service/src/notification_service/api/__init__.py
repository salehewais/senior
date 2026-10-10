"""Register HTTP blueprints."""

from __future__ import annotations

from flask import Flask

from notification_service.api.device_tokens import bp as device_tokens_bp
from notification_service.api.health import bp as health_bp
from notification_service.api.metrics import bp as metrics_bp
from notification_service.api.notifications import bp as notifications_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(health_bp)
    app.register_blueprint(metrics_bp)
    app.register_blueprint(device_tokens_bp)
    app.register_blueprint(notifications_bp)
