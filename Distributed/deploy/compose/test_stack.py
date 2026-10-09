"""Text checks for the Phase 11 stack. They do not start Docker."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMPOSE = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
DYNAMIC = (ROOT / "dynamic.yaml").read_text(encoding="utf-8")


class StackContractTests(unittest.TestCase):
    def test_full_stack_does_not_use_the_host_gateway_name(self) -> None:
        self.assertNotIn("host.docker.internal", COMPOSE)
        self.assertNotIn("host.docker.internal", DYNAMIC)

    def test_published_ports_are_localhost_only(self) -> None:
        self.assertIn("127.0.0.1:8080:80", COMPOSE)
        self.assertIn("127.0.0.1:15672:15672", COMPOSE)
        self.assertIn("127.0.0.1:8069:8069", COMPOSE)
        self.assertNotIn("0.0.0.0:", COMPOSE)
        for published in ("5432:5432", "5433:5432", "5434:5432", "6379:6379", "5672:5672"):
            self.assertNotIn(published, COMPOSE)

    def test_internal_fulfillment_is_not_a_public_route(self) -> None:
        self.assertIn("!PathPrefix(`/api/v1/internal`)", DYNAMIC)
        rules = "\n".join(line.strip() for line in DYNAMIC.splitlines() if line.strip().startswith("rule:"))
        without_negation = rules.replace("!PathPrefix(`/api/v1/internal`)", "")
        self.assertNotIn("/api/v1/internal", without_negation)
        self.assertIn("http://order-service:8000", DYNAMIC)
        self.assertIn("http://reporting-service:8001", DYNAMIC)
        self.assertIn("http://notification-service:8002", DYNAMIC)
        self.assertIn("!PathPrefix(`/api/v1/device-tokens/`)", DYNAMIC)
        self.assertIn("http://frontend:8080", DYNAMIC)

    def test_workers_are_separate_services_and_the_token_is_not_on_the_frontend(self) -> None:
        for name in (
            "order-outbox-publisher:",
            "order-inventory-consumer:",
            "reporting-consumer:",
            "notification-migrate:",
            "notification-consumer:",
            "odoo-consumer:",
            "odoo-publisher:",
            "order-migrate:",
            "reporting-migrate:",
        ):
            self.assertIn(name, COMPOSE)
        frontend = COMPOSE.split("\n  frontend:\n", 1)[1].split("\n  jwt-check:\n", 1)[0]
        self.assertNotIn("INTERNAL_SERVICE_TOKEN", frontend)
        self.assertNotIn("DATABASE_URL", frontend)
        self.assertNotIn("RABBITMQ_URL", frontend)
        self.assertIn("alembic", COMPOSE)
        self.assertIn("upgrade", COMPOSE)
        self.assertIn("manage.py", COMPOSE)
        self.assertIn("consume_events", COMPOSE)

    def test_built_images_are_not_tagged_latest(self) -> None:
        self.assertNotIn(":latest", COMPOSE)
        self.assertIn("commerce/order-service:0.1.0", COMPOSE)
        self.assertIn("commerce/reporting-service:0.1.0", COMPOSE)
        self.assertIn("commerce/notification-service:0.1.0", COMPOSE)
        self.assertIn("commerce/frontend:0.1.0", COMPOSE)
        self.assertIn("commerce/odoo:18.0.1", COMPOSE)
        self.assertIn("commerce/jwt-check:0.1.0", COMPOSE)


if __name__ == "__main__":
    unittest.main()
