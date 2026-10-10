"""XML-RPC client for the Odoo module. This process does not open odoo_db.

Each call stops at odoo_timeout_seconds. A refused connection, a timeout, or
an XML-RPC fault is OdooCallError. The consumer treats that as transient:
it publishes to commerce.retry and acks. It does not wait forever, and it
does not call requeue=true.
"""

from __future__ import annotations

import xmlrpc.client
from xmlrpc.client import SafeTransport, Transport

from commerce_erp.settings import Settings


class OdooCallError(Exception):
    """Odoo did not return an apply result inside the timeout."""


class _TimeoutTransport(Transport):
    def __init__(self, timeout: float) -> None:
        super().__init__()
        self._timeout = timeout

    def make_connection(self, host):
        connection = super().make_connection(host)
        connection.timeout = self._timeout
        return connection


class _TimeoutSafeTransport(SafeTransport):
    def __init__(self, timeout: float) -> None:
        super().__init__()
        self._timeout = timeout

    def make_connection(self, host):
        connection = super().make_connection(host)
        connection.timeout = self._timeout
        return connection


class OdooClient:
    def __init__(self, settings: Settings) -> None:
        if settings.odoo_timeout_seconds <= 0:
            raise ValueError("Odoo timeout must be greater than zero.")
        self._settings = settings
        self._uid: int | None = None

    def apply_order_confirmed(self, envelope: dict[str, object]) -> dict[str, object]:
        try:
            uid = self._uid or self._authenticate()
            self._uid = uid
            result = self._models().execute_kw(
                self._settings.odoo_db,
                uid,
                self._settings.odoo_password,
                "commerce.connector",
                "apply_order_confirmed",
                [envelope],
            )
        except OdooCallError:
            self._uid = None
            raise
        except Exception as exc:
            self._uid = None
            raise OdooCallError(type(exc).__name__) from exc
        if not isinstance(result, dict) or not isinstance(result.get("outcome"), str):
            raise OdooCallError("unexpected-result")
        return result

    def apply_command(self, envelope: dict[str, object]) -> dict[str, object]:
        try:
            uid = self._uid or self._authenticate()
            self._uid = uid
            result = self._models().execute_kw(
                self._settings.odoo_db,
                uid,
                self._settings.odoo_password,
                "commerce.connector",
                "apply_command",
                [envelope],
            )
        except OdooCallError:
            self._uid = None
            raise
        except Exception as exc:
            self._uid = None
            raise OdooCallError(type(exc).__name__) from exc
        if not isinstance(result, dict) or not isinstance(result.get("outcome"), str):
            raise OdooCallError("unexpected-result")
        return result

    def _authenticate(self) -> int:
        try:
            uid = self._common().authenticate(
                self._settings.odoo_db,
                self._settings.odoo_user,
                self._settings.odoo_password,
                {},
            )
        except Exception as exc:
            raise OdooCallError(type(exc).__name__) from exc
        if not isinstance(uid, int) or isinstance(uid, bool) or uid < 1:
            raise OdooCallError("authenticate-failed")
        return uid

    def _common(self) -> xmlrpc.client.ServerProxy:
        return self._proxy("/xmlrpc/2/common")

    def _models(self) -> xmlrpc.client.ServerProxy:
        return self._proxy("/xmlrpc/2/object")

    def _proxy(self, path: str) -> xmlrpc.client.ServerProxy:
        base = self._settings.odoo_url.rstrip("/")
        transport: Transport
        if base.startswith("https://"):
            transport = _TimeoutSafeTransport(self._settings.odoo_timeout_seconds)
        else:
            transport = _TimeoutTransport(self._settings.odoo_timeout_seconds)
        return xmlrpc.client.ServerProxy(f"{base}{path}", transport=transport, allow_none=True)
