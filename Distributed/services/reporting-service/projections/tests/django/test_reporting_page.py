"""The reporting HTML page is public. The JSON routes stay staff-only."""

from __future__ import annotations

from django.test import Client, TestCase


class ReportingPageTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_page_loads_without_a_token(self) -> None:
        for path in ("/reporting/", "/reporting"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertIn("text/html", response["Content-Type"])
            body = response.content.decode("utf-8")
            self.assertIn("admin@admin.com", body)
            self.assertIn("/api/v1/auth/login", body)
            self.assertIn("sessionStorage", body)
            self.assertIn("/api/v1/reports/orders/summary", body)
            self.assertIn("/api/v1/reports/orders", body)
            self.assertIn("/api/v1/reports/revenue", body)
            self.assertIn("/api/v1/reports/inventory", body)
            self.assertNotIn("/api/v1/orders", body)
