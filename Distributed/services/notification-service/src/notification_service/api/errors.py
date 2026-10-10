"""Uniform JSON error body."""

from __future__ import annotations

from flask import g, jsonify


def error_response(status: int, code: str, message: str):
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
