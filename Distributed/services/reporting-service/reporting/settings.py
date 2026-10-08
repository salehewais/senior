"""Django settings. One database: reporting_db. No private key. No order_db."""

from __future__ import annotations

import os
from pathlib import Path

from reporting.config import (
    db_connect_timeout_seconds,
    db_statement_timeout_ms,
    django_database,
    rabbitmq_timeout_seconds,
    rabbitmq_url,
)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "local-reporting-dev-only")
DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]
APPEND_SLASH = False

INSTALLED_APPS = [
    "projections",
]

MIDDLEWARE = [
    "projections.middleware.CorrelationIdMiddleware",
    "projections.middleware.ApiErrorMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "reporting.urls"
WSGI_APPLICATION = "reporting.wsgi.application"
ASGI_APPLICATION = "reporting.asgi.application"

DATABASES = {"default": django_database()}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = False
USE_TZ = True

# RS256 verification only. The order service holds the private key and issues tokens.
JWT_PUBLIC_KEY = os.environ.get("JWT_PUBLIC_KEY_PEM", "").strip()
_jwt_public_key_path = os.environ.get("JWT_PUBLIC_KEY_PATH", "").strip()
if not JWT_PUBLIC_KEY and _jwt_public_key_path:
    JWT_PUBLIC_KEY = Path(_jwt_public_key_path).read_text(encoding="utf-8")

RABBITMQ_URL = rabbitmq_url()
RABBITMQ_TIMEOUT_SECONDS = rabbitmq_timeout_seconds()
DB_CONNECT_TIMEOUT_SECONDS = db_connect_timeout_seconds()
DB_STATEMENT_TIMEOUT_MS = db_statement_timeout_ms()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain": {"format": "%(levelname)s %(name)s %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "plain"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
}
