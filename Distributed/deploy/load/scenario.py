"""Customer browse and order-create plan for the Phase 17 load test.

This module does not open a socket. The Locust file calls it. Limits below are
the ones the order service and Traefik already enforce. This file does not change them.
"""

from __future__ import annotations

import os
import secrets
import uuid
from dataclasses import dataclass

GENTLE = "gentle"
FLOOD = "flood"

REGISTER_PATH = "/api/v1/auth/register"
LOGIN_PATH = "/api/v1/auth/login"
PRODUCTS_PATH = "/api/v1/products"
ORDERS_PATH = "/api/v1/orders"

# Budgets already implemented. Login and register are 5/min. Order create is 10/min.
# Traefik's in-memory limiter is 30 requests/second per IP per replica.
LOGIN_PER_MINUTE = 5
REGISTER_PER_MINUTE = 5
ORDER_CREATE_PER_MINUTE = 10
TRAEFIK_PER_SECOND = 30

GENTLE_USERS = 2
GENTLE_WAIT_SECONDS = 15.0
FLOOD_USERS = 1
FLOOD_WAIT_SECONDS = 0.2
FLOOD_ORDER_ATTEMPTS = ORDER_CREATE_PER_MINUTE + 5
ORDER_QUANTITY = 1
# A hung laptop should fail the gentle bar. This is not a capacity target.
LATENCY_CEILING_MS = 2000

GATEWAY_BASE_URL = "http://127.0.0.1:8080"

REUSE_ACCOUNT = (
    "Register and login allow 5 requests a minute per IP. "
    "Wait for that window to pass, or set LOAD_EMAIL and LOAD_PASSWORD "
    "to one customer you already registered and run again."
)


class ScenarioStop(Exception):
    """Stop the run. The message is safe to print: no token and no password."""


def base_url() -> str:
    raw = os.environ.get("LOAD_BASE_URL", "").strip()
    if not raw:
        raw = GATEWAY_BASE_URL
    return raw.rstrip("/")


def mode() -> str:
    value = os.environ.get("LOAD_MODE", "").strip() or GENTLE
    if value not in (GENTLE, FLOOD):
        raise ScenarioStop("LOAD_MODE must be gentle or flood.")
    return value


def existing_account() -> tuple[str, str] | None:
    """Return a customer from the environment, or None so the run can register one.

    Both variables default to empty. A password is never stored in this file.
    """
    email = os.environ.get("LOAD_EMAIL", "")
    password = os.environ.get("LOAD_PASSWORD", "")
    if not email and not password:
        return None
    if not email or not password:
        raise ScenarioStop("Set both LOAD_EMAIL and LOAD_PASSWORD, or leave both empty.")
    return email, password


def product_id_override() -> str:
    return os.environ.get("LOAD_PRODUCT_ID", "").strip()


def new_account() -> tuple[str, str]:
    email = f"load-{uuid.uuid4().hex[:12]}@example.com"
    password = secrets.token_urlsafe(18)
    return email, password


def register_body(email: str, password: str) -> dict[str, str]:
    return {"email": email, "display_name": "Load customer", "password": password}


def login_body(email: str, password: str) -> dict[str, str]:
    return {"email": email, "password": password}


def order_create_body(product_id: str) -> dict[str, list[dict[str, object]]]:
    return {"items": [{"product_id": product_id, "quantity": ORDER_QUANTITY}]}


def order_read_path(order_id: str) -> str:
    if not order_id or "/" in order_id or "\\" in order_id:
        raise ScenarioStop("The order id was missing, so the read was skipped.")
    return f"{ORDERS_PATH}/{order_id}"


def wait_seconds() -> float:
    if mode() == FLOOD:
        return FLOOD_WAIT_SECONDS
    return GENTLE_WAIT_SECONDS


def gentle_orders_per_minute(users: int, wait_seconds_between: float) -> float:
    """Orders if each user creates one order, then waits. Request time makes this smaller."""
    if users < 1 or wait_seconds_between <= 0:
        raise ScenarioStop("Gentle pacing needs at least one user and a positive wait.")
    return users * (60.0 / wait_seconds_between)


def flood_request_rate_if_instant() -> float:
    """Requests per second if each call returns immediately.

    Each attempt browses, creates, and (when the create is accepted) reads.
    The wait sits between attempts. Setup login is a handful of extra calls.
    """
    calls_per_attempt = 3
    elapsed = FLOOD_WAIT_SECONDS * (FLOOD_ORDER_ATTEMPTS - 1)
    return (FLOOD_ORDER_ATTEMPTS * calls_per_attempt) / elapsed


def shape_problem(run_mode: str, users: int) -> str | None:
    if run_mode == GENTLE and users not in (1, GENTLE_USERS):
        return (
            "Gentle mode uses 1 or 2 virtual users so one IP stays under the Redis "
            f"login limit ({LOGIN_PER_MINUTE}/min) and the order-create limit "
            f"({ORDER_CREATE_PER_MINUTE}/min). The documented command uses {GENTLE_USERS}."
        )
    if run_mode == FLOOD and users != FLOOD_USERS:
        return (
            "Flood mode uses 1 virtual user. "
            f"{FLOOD_ORDER_ATTEMPTS} order creates then exceed the "
            f"{ORDER_CREATE_PER_MINUTE}/min account and IP limits."
        )
    return None


def error_code(body: object) -> str | None:
    if not isinstance(body, dict):
        return None
    error = body.get("error")
    if not isinstance(error, dict):
        return None
    code = error.get("code")
    if not isinstance(code, str):
        return None
    return code


def is_rate_limited(status_code: int, body: object) -> bool:
    return status_code == 429 and error_code(body) == "RATE_LIMITED"


def product_id_from_catalog(body: object, override: str) -> str:
    chosen = override.strip()
    if chosen:
        return chosen
    if not isinstance(body, dict):
        raise ScenarioStop("GET /api/v1/products did not return a JSON object.")
    items = body.get("items")
    if not isinstance(items, list) or not items:
        raise ScenarioStop(
            "GET /api/v1/products returned no items. Create a product as an admin, "
            "or set LOAD_PRODUCT_ID. This scenario does not create products."
        )
    first = items[0]
    if not isinstance(first, dict):
        raise ScenarioStop("GET /api/v1/products returned an item that was not an object.")
    product_id = first.get("id")
    if not isinstance(product_id, str) or not product_id:
        raise ScenarioStop("GET /api/v1/products returned an item without an id.")
    return product_id


def order_id_from_create(body: object) -> str:
    if not isinstance(body, dict):
        raise ScenarioStop("Order create did not return a JSON object.")
    order_id = body.get("id")
    if not isinstance(order_id, str) or not order_id:
        raise ScenarioStop("Order create did not return an id.")
    return order_id


def access_token(body: object) -> str:
    if not isinstance(body, dict):
        raise ScenarioStop("Login did not return a JSON object.")
    token = body.get("access_token")
    if not isinstance(token, str) or not token:
        raise ScenarioStop("Login did not return an access token.")
    return token


@dataclass(frozen=True)
class RunSummary:
    mode: str
    requests: int
    failures: int
    order_created: int
    order_rate_limited: int
    p95_ms: float | None


def evaluate(summary: RunSummary) -> tuple[bool, str]:
    if summary.requests == 0:
        return False, "No requests were recorded, so there is no result to compare."
    if summary.mode == GENTLE:
        if summary.order_rate_limited:
            return False, (
                "The gentle run saw 429 RATE_LIMITED. Wait a minute for the Redis window, "
                "or keep the documented 2 users and 15 second wait."
            )
        if summary.failures:
            return False, "The gentle run had failed requests."
        if summary.p95_ms is None:
            return False, "The gentle run recorded requests but no p95, so latency was not measured."
        if summary.p95_ms > LATENCY_CEILING_MS:
            return False, (
                f"p95 was {summary.p95_ms:.0f} ms, above the {LATENCY_CEILING_MS} ms "
                "laptop starting point."
            )
        return True, "Gentle pass bar met: no failures, no 429, p95 within the starting point."
    if summary.mode == FLOOD:
        if summary.failures:
            return False, "The flood run had a failure other than 429 RATE_LIMITED."
        if summary.order_rate_limited < 1:
            return False, (
                "The flood run did not see 429 RATE_LIMITED on order create. "
                "The Redis window may already have slid, or the creates were too slow."
            )
        return True, "Flood pass bar met: order create returned 429 RATE_LIMITED."
    return False, "LOAD_MODE must be gentle or flood."


def results_note(summary: RunSummary, ok: bool, message: str) -> str:
    if summary.p95_ms is None:
        latency = "p95: not measured."
    else:
        latency = (
            f"p95: {summary.p95_ms:.0f} ms. The gentle ceiling is {LATENCY_CEILING_MS} ms. "
            "That ceiling is a laptop starting point, not a capacity number."
        )
    lines = [
        "# Load test results",
        "",
        f"Mode: {summary.mode}",
        f"Requests recorded: {summary.requests}",
        f"Failed requests: {summary.failures}",
        f"Order create 201: {summary.order_created}",
        f"Order create 429 RATE_LIMITED: {summary.order_rate_limited}",
        latency,
        f"Pass bar: {'met' if ok else 'not met'}. {message}",
        "",
        "These numbers are from this process. They are not a capacity test.",
        "",
    ]
    return "\n".join(lines)
