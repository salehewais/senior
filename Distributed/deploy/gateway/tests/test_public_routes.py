"""The public Traefik file must not route fulfillment callbacks.

These assertions read the router rules as text. They do not start Docker.
"""

from __future__ import annotations

import unittest
from pathlib import Path

DYNAMIC = Path(__file__).resolve().parents[1] / "dynamic.yaml"
ROOT = DYNAMIC.parent


def _rule_lines(text: str) -> list[str]:
    rules: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("rule:"):
            rules.append(stripped)
    return rules


class PublicRouterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = DYNAMIC.read_text(encoding="utf-8")
        self.rules = "\n".join(_rule_lines(self.text))

    def test_internal_fulfillment_is_not_a_public_route(self) -> None:
        self.assertIn("!PathPrefix(`/api/v1/internal`)", self.rules)
        without_negation = self.rules.replace("!PathPrefix(`/api/v1/internal`)", "")
        self.assertNotIn("internal", without_negation)
        self.assertNotIn("/api/v1/internal", without_negation)

    def test_reports_are_not_forwarded_to_the_order_service(self) -> None:
        self.assertIn("Path(`/api/v1/reports`) || PathPrefix(`/api/v1/reports/`)", self.rules)
        self.assertIn("!Path(`/api/v1/reports`)", self.rules)
        self.assertIn("!PathPrefix(`/api/v1/reports/`)", self.rules)
        self.assertIn("service: reporting", self.text)
        self.assertIn("http://host.docker.internal:8001", self.text)
        self.assertIn("http://host.docker.internal:8000", self.text)
        order_block = self.text.split("services:", 1)[1]
        reporting_url = order_block.split("reporting:", 1)[1].split("frontend:", 1)[0]
        order_url = order_block.split("order:", 1)[1].split("reporting:", 1)[0]
        self.assertIn("8001", reporting_url)
        self.assertNotIn("8001", order_url)
        self.assertIn("8000", order_url)

    def test_public_auth_posts_are_the_only_unauthenticated_api_rules(self) -> None:
        self.assertIn("Path(`/api/v1/auth/register`)", self.rules)
        self.assertIn("Path(`/api/v1/auth/login`)", self.rules)
        self.assertIn("Path(`/api/v1/auth/refresh`)", self.rules)
        self.assertIn("Path(`/api/v1/auth/logout`)", self.rules)
        self.assertIn("Method(`POST`)", self.rules)
        self.assertIn("jwt-access", self.text)
        reports = self.text.split("reports:", 1)[1].split("auth-public:", 1)[0]
        auth = self.text.split("auth-public:", 1)[1].split("order-api:", 1)[0]
        order = self.text.split("order-api:", 1)[1].split("frontend:", 1)[0]
        self.assertIn("jwt-access", reports)
        self.assertNotIn("jwt-access", auth)
        self.assertIn("jwt-access", order)

    def test_cors_allowlist_is_not_a_wildcard_and_identity_headers_are_stripped(self) -> None:
        self.assertNotIn("*", self.text)
        for origin in (
            "http://127.0.0.1:8080",
            "http://localhost:8080",
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ):
            self.assertIn(origin, self.text)
        for header in ("X-User-Id", "X-User-Role", "X-Internal-Token"):
            self.assertIn(f"- {header}", self.text)
        strip = self.text.split("stripHeaders:", 1)[1].split("allowOrigins:", 1)[0]
        self.assertNotIn("Authorization", strip)
        self.assertNotIn("X-Correlation-Id", strip)

    def test_timeouts_are_explicit_and_no_data_ports_are_published_here(self) -> None:
        self.assertIn("dialTimeout: 3s", self.text)
        self.assertIn("responseHeaderTimeout: 30s", self.text)
        self.assertIn("idleConnTimeout: 90s", self.text)
        compose = (ROOT / "compose.yaml").read_text(encoding="utf-8")
        self.assertIn("127.0.0.1:8080:80", compose)
        for forbidden in ("5432", "6379", "5672", "15672"):
            self.assertNotIn(forbidden, compose)

    def test_rate_limit_is_traefik_memory_not_a_redis_reimplementation(self) -> None:
        self.assertIn("rateLimit:", self.text)
        self.assertNotIn("redis", self.text.lower())


if __name__ == "__main__":
    unittest.main()
