"""Transactional outbox in order_db.

The business row and this row commit together. A separate publisher process
sends pending payloads. This revision does not publish anything.

Revision ID: 0004_outbox
Revises: 0003_processed_events
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_outbox"
down_revision: str | None = "0003_processed_events"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "outbox",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("aggregate_type", sa.String(length=32), nullable=False),
        sa.Column("aggregate_id", sa.Uuid(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.CheckConstraint(
            "status IN ('pending', 'published', 'failed')",
            name="ck_outbox_status",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # The publisher claims pending rows in this order. Published and failed rows stay out of the index.
    op.create_index(
        "ix_outbox_pending_created_at_id",
        "outbox",
        ["created_at", "id"],
        unique=False,
        postgresql_where=sa.text("status = 'pending'"),
    )


def downgrade() -> None:
    op.drop_index("ix_outbox_pending_created_at_id", table_name="outbox")
    op.drop_table("outbox")
