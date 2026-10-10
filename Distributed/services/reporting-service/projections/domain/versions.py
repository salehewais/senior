"""Read-model facts the metrics registry samples without importing Prometheus."""

from __future__ import annotations

from django.db.models import Max

from projections.models import OrderProjection


def order_projection_max_version() -> float:
    value = OrderProjection.objects.aggregate(max_version=Max("aggregate_version"))["max_version"]
    return float(value or 0)
