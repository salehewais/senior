"""Saga rows in order_db.

A step, the order mirror, and the outbox row commit together. This revision
does not start the orchestrator.

Revision ID: 0005_saga_instances
Revises: 0004_outbox
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_saga_instances"
down_revision: str | None = "0004_outbox"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_STATUSES = (
    "STARTED",
    "INVENTORY_RESERVED",
    "PAYMENT_CONFIRMED",
    "ODOO_ORDER_CREATED",
    "COMPLETED",
    "COMPENSATING",
    "COMPENSATED",
    "FAILED",
    "MANUAL_INTERVENTION_REQUIRED",
)


def upgrade() -> None:
    op.create_table(
        "saga_instances",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("correlation_id", sa.Uuid(), nullable=False),
        sa.Column("causation_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("completed_steps", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("reservation_id", sa.String(length=80), nullable=True),
        sa.Column("payment_reference", sa.String(length=128), nullable=True),
        sa.Column("failure_reason", sa.String(length=64), nullable=True),
        sa.Column("pending_step", sa.String(length=32), nullable=True),
        sa.Column("pending_outcome", sa.String(length=16), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN (" + ", ".join(f"'{status}'" for status in _STATUSES) + ")",
            name="ck_saga_instances_status",
        ),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_id"),
    )
    op.create_index(
        "ix_saga_instances_status_updated_at",
        "saga_instances",
        ["status", "updated_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_saga_instances_status_updated_at", table_name="saga_instances")
    op.drop_table("saga_instances")
