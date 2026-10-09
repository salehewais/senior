"""Static checks for the Phase 18 failure lab. They do not start Docker or stop a service."""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMPOSE = (ROOT.parent / "compose" / "docker-compose.yml").read_text(encoding="utf-8")
LIB = (ROOT / "lib.sh").read_text(encoding="utf-8")

EXPERIMENTS = {
    "reporting-consumer.sh": "reporting-consumer",
    "rabbitmq.sh": "rabbitmq",
    "redis.sh": "redis",
    "inventory-consumer.sh": "order-inventory-consumer",
}

OBSERVATIONS = {
    "reporting-consumer.sh": (
        "q.reporting.projection",
        "http://127.0.0.1:8080/api/v1/orders/{order_id}/confirm",
        "processed_events",
        "reason=duplicate",
        "requeue=true",
    ),
    "rabbitmq.sh": (
        "outbox",
        "pending",
        "order-outbox-publisher",
        "outbox publish failed; row stays pending",
        "retry_count",
        "Do not delete the outbox row.",
    ),
    "redis.sh": (
        "http://127.0.0.1:8080/api/v1/products",
        "http://127.0.0.1:8080/api/v1/auth/login",
        "http://127.0.0.1:8080/api/v1/orders",
        "DEPENDENCY_UNAVAILABLE",
        "order_db",
    ),
    "inventory-consumer.sh": (
        "q.order.inventory",
        "http://127.0.0.1:8080/api/v1/orders/{order_id}/confirm",
        "processed_events",
        "duplicate delivery acked without a second effect",
        "requeue=true",
        "order-inventory",
    ),
}

FORBIDDEN = (
    re.compile(r"docker\s+compose\s+[^\n]*\bdown\b"),
    re.compile(r"\bcompose\s+down\b"),
    re.compile(r"\bdown\s+-v\b"),
    re.compile(r"\bdown\s+--volumes\b"),
    re.compile(r"\bvolume\s+rm\b"),
    re.compile(r"\bvolume\s+prune\b"),
    re.compile(r"\bdocker\s+volume\b"),
    re.compile(r"\bDROP\s+DATABASE\b", re.IGNORECASE),
    re.compile(r"\bDROP\s+TABLE\b", re.IGNORECASE),
    re.compile(r"\bdropdb\b", re.IGNORECASE),
    re.compile(r"\bTRUNCATE\b", re.IGNORECASE),
    re.compile(r"\bDELETE\s+FROM\b", re.IGNORECASE),
    re.compile(r"/api/v1/internal"),
    re.compile(r"BEGIN (?:RSA |OPENSSH )?PRIVATE KEY"),
    re.compile(r"PRIVATE KEY"),
    re.compile(r"jwt_private"),
)


def _script(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


class FailureLabTests(unittest.TestCase):
    def test_scripts_parse_and_fail_closed_on_options(self) -> None:
        for name in ("lib.sh", *EXPERIMENTS):
            subprocess.run(["bash", "-n", str(ROOT / name)], check=True)
        for name in EXPERIMENTS:
            text = _script(name)
            self.assertIn("set -euo pipefail", text)
            self.assertIn('source "${LAB_DIR}/lib.sh"', text)
            self.assertLess(text.index("require_docker"), text.index("compose stop"))
            self.assertLess(text.index("require_docker"), text.index("compose start"))

    def test_each_script_names_one_compose_service(self) -> None:
        self.assertEqual(set(EXPERIMENTS), {path.name for path in ROOT.glob("*.sh")} - {"lib.sh"})
        for name, service in EXPERIMENTS.items():
            text = _script(name)
            self.assertIn(f"SERVICE={service}\n", text)
            self.assertIn(f"  {service}:\n", COMPOSE)
            self.assertEqual(text.count('compose stop "${SERVICE}"'), 1)
            self.assertEqual(text.count('compose start "${SERVICE}"'), 1)
            self.assertNotRegex(text, r"compose\s+(stop|start)\s+\"(?!\$\{SERVICE\}\")")

    def test_lib_checks_docker_info_before_compose_and_limits_the_subcommand(self) -> None:
        self.assertLess(LIB.index("docker info"), LIB.index("docker compose"))
        self.assertIn("Nothing was stopped or started.", LIB)
        self.assertIn('cd "${COMPOSE_DIR}"', LIB)
        self.assertIn("docker compose -f docker-compose.yml", LIB)
        self.assertIn('COMPOSE_DIR="$(cd "${LAB_DIR}/../compose" && pwd)"', LIB)
        self.assertIn("stop|start)", LIB)
        self.assertIn('"$2" != "${SERVICE}"', LIB)
        self.assertNotIn("docker-compose.yml down", LIB)

    def test_scripts_say_what_to_look_at(self) -> None:
        for name, markers in OBSERVATIONS.items():
            text = _script(name)
            for marker in markers:
                self.assertIn(marker, text)

    def test_scripts_do_not_wipe_or_call_internal_routes(self) -> None:
        blob = LIB + "\n" + "\n".join(_script(name) for name in EXPERIMENTS)
        for pattern in FORBIDDEN:
            self.assertIsNone(pattern.search(blob), pattern.pattern)
        self.assertNotIn("toxiproxy", blob.lower())
        self.assertNotIn("chaos mesh", blob.lower())
        self.assertNotIn("kind create", blob.lower())


if __name__ == "__main__":
    unittest.main()
