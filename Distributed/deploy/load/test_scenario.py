"""Static checks for the load scenario. They do not start Locust or call an API."""

from __future__ import annotations

import ast
import os
import py_compile
import unittest
from pathlib import Path

import scenario

ROOT = Path(__file__).resolve().parent
SOURCES = (ROOT / "scenario.py", ROOT / "locustfile.py")


def _source_text() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in SOURCES)


class ScenarioHelperTests(unittest.TestCase):
    def setUp(self) -> None:
        self._saved = {
            key: os.environ.get(key)
            for key in ("LOAD_BASE_URL", "LOAD_MODE", "LOAD_EMAIL", "LOAD_PASSWORD", "LOAD_PRODUCT_ID")
        }
        for key in self._saved:
            os.environ.pop(key, None)

    def tearDown(self) -> None:
        for key, value in self._saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_files_compile(self) -> None:
        for path in SOURCES:
            py_compile.compile(str(path), doraise=True)

    def test_sources_stay_on_the_customer_path(self) -> None:
        text = _source_text()
        self.assertNotIn("/api/v1/internal", text)
        self.assertNotIn("/api/v1/reports", text)
        self.assertNotIn("X-Internal-Token", text)
        self.assertNotIn("unit_price", text)
        self.assertNotIn("amount_minor", text)
        self.assertNotIn('"price"', text)
        self.assertNotIn("'price'", text)
        for marker in (
            "BEGIN PRIVATE KEY",
            "BEGIN RSA PRIVATE KEY",
            "BEGIN OPENSSH PRIVATE KEY",
            "PRIVATE KEY",
        ):
            self.assertNotIn(marker, text)

    def test_order_body_has_product_id_and_quantity_only(self) -> None:
        body = scenario.order_create_body("product-1")
        self.assertEqual(set(body), {"items"})
        line = body["items"][0]
        self.assertEqual(set(line), {"product_id", "quantity"})
        self.assertEqual(line["product_id"], "product-1")
        self.assertEqual(line["quantity"], 1)

    def test_register_body_does_not_send_a_role(self) -> None:
        body = scenario.register_body("load@example.com", "not-stored-in-the-file")
        self.assertEqual(set(body), {"email", "display_name", "password"})

    def test_password_and_email_defaults_are_empty(self) -> None:
        self.assertIsNone(scenario.existing_account())
        self.assertEqual(scenario.product_id_override(), "")
        self.assertEqual(scenario.base_url(), scenario.GATEWAY_BASE_URL)
        os.environ["LOAD_BASE_URL"] = "http://127.0.0.1:8000"
        self.assertEqual(scenario.base_url(), "http://127.0.0.1:8000")

    def test_no_password_literal_in_the_scenario(self) -> None:
        for path in SOURCES:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and "password" in target.id.lower():
                            self.assertNotIsInstance(node.value, ast.Constant)

    def test_new_account_is_not_a_fixed_secret(self) -> None:
        first_email, first_password = scenario.new_account()
        second_email, second_password = scenario.new_account()
        self.assertNotEqual(first_email, second_email)
        self.assertNotEqual(first_password, second_password)
        self.assertGreaterEqual(len(first_password), 8)
        self.assertTrue(first_email.endswith("@example.com"))
        self.assertNotIn(first_password, _source_text())

    def test_gentle_pace_stays_under_the_order_limit(self) -> None:
        rate = scenario.gentle_orders_per_minute(scenario.GENTLE_USERS, scenario.GENTLE_WAIT_SECONDS)
        self.assertLess(rate, scenario.ORDER_CREATE_PER_MINUTE)
        self.assertLessEqual(scenario.GENTLE_USERS, scenario.LOGIN_PER_MINUTE)
        self.assertLessEqual(scenario.GENTLE_USERS, scenario.REGISTER_PER_MINUTE)

    def test_flood_crosses_the_order_limit_and_stays_under_traefik(self) -> None:
        self.assertGreater(scenario.FLOOD_ORDER_ATTEMPTS, scenario.ORDER_CREATE_PER_MINUTE)
        self.assertLess(scenario.flood_request_rate_if_instant(), scenario.TRAEFIK_PER_SECOND)

    def test_shape_rejects_a_crowd_from_one_ip(self) -> None:
        self.assertIsNone(scenario.shape_problem(scenario.GENTLE, 2))
        self.assertIsNone(scenario.shape_problem(scenario.GENTLE, 1))
        self.assertIsNotNone(scenario.shape_problem(scenario.GENTLE, 3))
        self.assertIsNone(scenario.shape_problem(scenario.FLOOD, 1))
        self.assertIsNotNone(scenario.shape_problem(scenario.FLOOD, 2))

    def test_catalog_id_comes_from_the_list_or_the_environment(self) -> None:
        listed = scenario.product_id_from_catalog({"items": [{"id": "from-list"}]}, "")
        self.assertEqual(listed, "from-list")
        chosen = scenario.product_id_from_catalog({"items": []}, "from-env")
        self.assertEqual(chosen, "from-env")
        with self.assertRaises(scenario.ScenarioStop):
            scenario.product_id_from_catalog({"items": []}, "")

    def test_rate_limited_matches_the_error_envelope(self) -> None:
        body = {"error": {"code": "RATE_LIMITED", "message": "slow down", "details": []}}
        self.assertTrue(scenario.is_rate_limited(429, body))
        self.assertFalse(scenario.is_rate_limited(429, {"error": {"code": "OTHER"}}))
        self.assertFalse(scenario.is_rate_limited(503, body))

    def test_pass_bar_is_honest(self) -> None:
        gentle_ok = scenario.RunSummary(scenario.GENTLE, 4, 0, 4, 0, 100.0)
        ok, _message = scenario.evaluate(gentle_ok)
        self.assertTrue(ok)
        gentle_slow = scenario.RunSummary(scenario.GENTLE, 4, 0, 4, 0, 5000.0)
        ok, message = scenario.evaluate(gentle_slow)
        self.assertFalse(ok)
        self.assertIn("starting point", message)
        gentle_limited = scenario.RunSummary(scenario.GENTLE, 4, 0, 2, 2, 100.0)
        ok, _message = scenario.evaluate(gentle_limited)
        self.assertFalse(ok)
        flood_ok = scenario.RunSummary(scenario.FLOOD, 15, 0, 10, 5, None)
        ok, message = scenario.evaluate(flood_ok)
        self.assertTrue(ok)
        self.assertIn("429", message)
        flood_miss = scenario.RunSummary(scenario.FLOOD, 15, 0, 15, 0, None)
        ok, _message = scenario.evaluate(flood_miss)
        self.assertFalse(ok)
        note = scenario.results_note(flood_ok, True, message)
        self.assertIn("not measured", note)
        self.assertIn("429 RATE_LIMITED: 5", note)
        self.assertNotIn("did not run", note)

    def test_checked_in_note_says_the_run_did_not_happen(self) -> None:
        note = (ROOT / "RESULTS.md").read_text(encoding="utf-8")
        self.assertIn("did not run", note)
        self.assertIn("No latency was measured", note)
        self.assertNotIn("Pass bar: met", note)


if __name__ == "__main__":
    unittest.main()
