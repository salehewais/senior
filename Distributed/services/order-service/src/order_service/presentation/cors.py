"""Temporary browser access for the Phase 3 Vite dev server.

Phase 10 (Traefik) owns CORS. Until that gateway exists, this process allows
only the local storefront origins so the browser can call the order service
directly. That is a shortcut, not a second architecture.

Do not set Access-Control-Allow-Origin to *. A matching Origin does not grant
access: protected routes still require a Bearer token.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Vite's default dev origins. The page is not the same origin as the API on :8000.
LOCAL_FRONTEND_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]


def install_local_frontend_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=LOCAL_FRONTEND_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Correlation-Id"],
    )
