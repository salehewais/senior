"""Read models in reporting_db.

Names follow docs/database.md. Customer rows store the public profile only.
There is no password column and no connection to order_db.
"""

from __future__ import annotations

import uuid

from django.db import models


class OrderProjection(models.Model):
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    customer_id = models.UUIDField(null=True)
    status = models.CharField(max_length=32)
    total_amount_minor = models.BigIntegerField(default=0)
    currency = models.CharField(max_length=3, default="")
    cancel_reason = models.CharField(max_length=64, blank=True, default="")
    tracking_reference = models.CharField(max_length=128, null=True, blank=True)
    aggregate_version = models.PositiveIntegerField()
    occurred_at = models.DateTimeField()

    class Meta:
        db_table = "order_projections"
        indexes = [
            models.Index(fields=["occurred_at", "order_id"], name="ix_order_proj_cursor"),
            models.Index(fields=["status"], name="ix_order_proj_status"),
        ]


class OrderItemProjection(models.Model):
    order = models.ForeignKey(OrderProjection, related_name="items", on_delete=models.CASCADE)
    position = models.PositiveIntegerField()
    product_id = models.UUIDField()
    sku = models.CharField(max_length=64)
    quantity = models.PositiveIntegerField()
    unit_price_amount_minor = models.BigIntegerField()
    currency = models.CharField(max_length=3)

    class Meta:
        db_table = "order_item_projections"
        constraints = [
            models.UniqueConstraint(fields=["order", "position"], name="uq_order_item_position"),
        ]


class ProductProjection(models.Model):
    product_id = models.UUIDField(primary_key=True)
    sku = models.CharField(max_length=64)
    name = models.CharField(max_length=200)
    unit_price_amount_minor = models.BigIntegerField()
    currency = models.CharField(max_length=3)
    active = models.BooleanField()
    aggregate_version = models.PositiveIntegerField()
    occurred_at = models.DateTimeField()

    class Meta:
        db_table = "product_projections"
        indexes = [
            models.Index(fields=["occurred_at", "product_id"], name="ix_product_proj_cursor"),
        ]


class CustomerProjection(models.Model):
    """Public profile copied from CustomerUpdated. Never a password or token."""

    customer_id = models.UUIDField(primary_key=True)
    email = models.CharField(max_length=254)
    display_name = models.CharField(max_length=200)
    aggregate_version = models.PositiveIntegerField()
    occurred_at = models.DateTimeField()

    class Meta:
        db_table = "customer_projections"


class InventoryProjection(models.Model):
    product_id = models.UUIDField(primary_key=True)
    sku = models.CharField(max_length=64)
    quantity_on_hand = models.IntegerField()
    quantity_reserved = models.IntegerField()
    warehouse_code = models.CharField(max_length=64)
    aggregate_version = models.PositiveIntegerField()
    occurred_at = models.DateTimeField()

    class Meta:
        db_table = "inventory_projections"
        indexes = [
            models.Index(fields=["occurred_at", "product_id"], name="ix_inventory_proj_cursor"),
        ]


class PaymentProjection(models.Model):
    """Payment outcome for an order. Ready for PaymentConfirmed and PaymentFailed."""

    order_id = models.UUIDField(primary_key=True)
    outcome = models.CharField(max_length=16)
    payment_reference = models.CharField(max_length=128, blank=True, default="")
    amount_minor = models.BigIntegerField(null=True)
    currency = models.CharField(max_length=3, blank=True, default="")
    reason_code = models.CharField(max_length=32, blank=True, default="")
    aggregate_version = models.PositiveIntegerField()
    occurred_at = models.DateTimeField()

    class Meta:
        db_table = "payment_projections"


class ProcessedEvent(models.Model):
    """Dedup key. Inserted in the same transaction as the projection write."""

    event_id = models.UUIDField(primary_key=True)
    event_type = models.CharField(max_length=64)
    aggregate_id = models.UUIDField()
    processed_at = models.DateTimeField()

    class Meta:
        db_table = "processed_events"


class ProjectionVersion(models.Model):
    """Last applied aggregate_version for one stream."""

    aggregate_type = models.CharField(max_length=32)
    aggregate_id = models.UUIDField()
    aggregate_version = models.PositiveIntegerField()

    class Meta:
        db_table = "projection_versions"
        constraints = [
            models.UniqueConstraint(
                fields=["aggregate_type", "aggregate_id"],
                name="uq_projection_version",
            ),
        ]
