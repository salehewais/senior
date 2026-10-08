"""Consumer dedup and the local inventory snapshot.

processed_events is how this service remembers an event_id it has already
applied. inventory_snapshots is the order service's copy of InventoryUpdated.
Neither table is the outbox. Publishing still happens after commit.

Revision ID: 0003_processed_events
Revises: 0002_accounts_refresh
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_processed_events"
down_revision: str | None = "0002_accounts_refresh"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "processed_events",
        sa.Column("event_id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("aggregate_id", sa.Uuid(), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumer_name", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_table(
        "inventory_snapshots",
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("quantity_on_hand", sa.Integer(), nullable=False),
        sa.Column("quantity_reserved", sa.Integer(), nullable=False),
        sa.Column("warehouse_code", sa.String(length=64), nullable=False),
        sa.Column("source_version", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("product_id"),
    )


def downgrade() -> None:
    op.drop_table("inventory_snapshots")
    op.drop_table("processed_events")
