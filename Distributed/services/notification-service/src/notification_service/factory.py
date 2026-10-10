"""Application factory. Builds the Flask app without starting the server."""

from __future__ import annotations

from pathlib import Path

from flask import Flask

from notification_service.api import register_blueprints
from notification_service.api.hooks import register_hooks
from notification_service.config import jwt_public_key
from notification_service.domain.protocols import Store
from notification_service.persistence.store import SqlStore

_TEMPLATES = Path(__file__).resolve().parent / "templates"


def create_app(*, store: Store | None = None, public_key: str | None = None) -> Flask:
    app = Flask(__name__, template_folder=str(_TEMPLATES))
    app.config["STORE"] = store if store is not None else SqlStore.from_settings()
    app.config["JWT_PUBLIC_KEY"] = jwt_public_key() if public_key is None else public_key
    register_hooks(app)
    register_blueprints(app)
    return app
