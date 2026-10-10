"""Order row committed in the order service, projection missing, then present.

SQLite in this process. The order row comes from the order-service in-memory
unit of work, not from Postgres. No broker and no Docker.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

import pytest
from django.test import TestCase

from projections.domain.apply import apply_envelope
from projections.domain.envelope import ParsedEnvelope, inspect_envelope
from projections.domain.outcomes import REASON_DUPLICATE, Outcome
from projections.httpapi.queries import orders_summary
from projections.models import OrderProjection, PaymentProjection

pytestmark = pytest.mark.cross_service

ORDER_SERVICE = Path(__file__).resolve().parents[4] / "order-service"
ORDER_PYTHON = ORDER_SERVICE / ".venv" / "bin" / "python"


def _apply(body: object):
    assert isinstance(body, dict)
    inspected = inspect_envelope(json.dumps(body).encode("utf-8"))
    assert isinstance(inspected, ParsedEnvelope)
    return apply_envelope(inspected)


def _export_confirmed_order() -> dict[str, object]:
    return _export("export_confirmed_order")


def _order_interpreter() -> str:
    """Prefer the order-service virtualenv. CI installs that package into the job interpreter."""

    if ORDER_PYTHON.is_file():
        return str(ORDER_PYTHON)
    return sys.executable


def _export(function_name: str) -> dict[str, object]:
    env = os.environ.copy()
    env.pop("DJANGO_SETTINGS_MODULE", None)
    env["PYTHONPATH"] = os.pathsep.join([str(ORDER_SERVICE / "src"), str(ORDER_SERVICE)])
    completed = subprocess.run(
        [
            _order_interpreter(),
            "-c",
            "import json; from tests.support.consistency_export import "
            f"{function_name}; print(json.dumps({function_name}()))",
        ],
        cwd=ORDER_SERVICE,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr or completed.stdout)
    loaded = json.loads(completed.stdout)
    if not isinstance(loaded, dict):
        raise AssertionError("export was not an object")
    return loaded


class ProjectionLagTests(TestCase):
    def test_projection_is_missing_then_present_after_order_confirmed(self) -> None:
        exported = _export_confirmed_order()
        order = exported["order"]
        events = exported["events"]
        assert isinstance(order, dict)
        assert isinstance(events, list)
        order_id = uuid.UUID(str(order["order_id"]))

        before = OrderProjection.objects.filter(order_id=order_id).first()
        self.assertIsNone(before)
        self.assertIsNone(orders_summary()["as_of"])
        self.assertEqual(order["status"], "CONFIRMED")
        self.assertEqual(order["version"], 2)

        created = _apply(events[0])
        self.assertEqual(created.outcome, Outcome.SUCCESS)
        stale = OrderProjection.objects.get(order_id=order_id)
        self.assertEqual(stale.status, "PENDING")
        self.assertEqual(stale.aggregate_version, 1)
        self.assertEqual(order["status"], "CONFIRMED")

        confirmed = _apply(events[1])
        self.assertEqual(confirmed.outcome, Outcome.SUCCESS)
        after = OrderProjection.objects.get(order_id=order_id)
        self.assertEqual(after.status, order["status"])
        self.assertEqual(after.aggregate_version, order["version"])
        self.assertEqual(after.total_amount_minor, order["total_amount_minor"])
        self.assertEqual(after.currency, order["currency"])
        self.assertEqual(OrderProjection.objects.filter(order_id=order_id).count(), 1)

        again = _apply(events[1])
        self.assertEqual(again.reason, REASON_DUPLICATE)
        self.assertEqual(OrderProjection.objects.filter(order_id=order_id).count(), 1)
        summary = orders_summary()
        self.assertEqual(summary["by_status"][0]["status"], "CONFIRMED")
        self.assertEqual(summary["by_status"][0]["count"], 1)

    def test_completed_saga_does_not_deliver_the_projection_before_payment_arrives(self) -> None:
        exported = _export("export_completed_saga_order")
        order = exported["order"]
        saga = exported["saga"]
        events = exported["events"]
        assert isinstance(order, dict)
        assert isinstance(saga, dict)
        assert isinstance(events, list)
        order_id = uuid.UUID(str(order["order_id"]))
        payment = events[2]
        assert isinstance(payment, dict)

        self.assertEqual(order["status"], "CONFIRMED")
        self.assertEqual(order["version"], 3)
        self.assertEqual(saga["status"], "COMPLETED")
        self.assertIsNone(OrderProjection.objects.filter(order_id=order_id).first())
        self.assertEqual(PaymentProjection.objects.filter(order_id=order_id).count(), 0)

        self.assertEqual(_apply(events[0]).outcome, Outcome.SUCCESS)
        pending = OrderProjection.objects.get(order_id=order_id)
        self.assertEqual(pending.status, "PENDING")
        self.assertEqual(PaymentProjection.objects.filter(order_id=order_id).count(), 0)

        self.assertEqual(_apply(events[1]).outcome, Outcome.SUCCESS)
        confirmed = OrderProjection.objects.get(order_id=order_id)
        self.assertEqual(confirmed.status, "CONFIRMED")
        self.assertNotEqual(confirmed.status, "DELIVERED")
        self.assertEqual(confirmed.aggregate_version, 2)
        self.assertEqual(PaymentProjection.objects.filter(order_id=order_id).count(), 0)
        self.assertEqual(order["saga_status"], "COMPLETED")

        applied = _apply(payment)
        self.assertEqual(applied.outcome, Outcome.SUCCESS)
        stored = PaymentProjection.objects.get(order_id=order_id)
        payload = payment["payload"]
        assert isinstance(payload, dict)
        amount = payload["amount"]
        assert isinstance(amount, dict)
        self.assertEqual(stored.outcome, "confirmed")
        self.assertEqual(stored.payment_reference, payload["payment_reference"])
        self.assertEqual(stored.amount_minor, amount["amount_minor"])
        self.assertEqual(stored.currency, amount["currency"])
        self.assertEqual(stored.aggregate_version, order["version"])
        after = OrderProjection.objects.get(order_id=order_id)
        self.assertEqual(after.status, "CONFIRMED")
        self.assertNotEqual(after.status, "DELIVERED")
        self.assertEqual(OrderProjection.objects.filter(order_id=order_id).count(), 1)
        self.assertEqual(PaymentProjection.objects.filter(order_id=order_id).count(), 1)
