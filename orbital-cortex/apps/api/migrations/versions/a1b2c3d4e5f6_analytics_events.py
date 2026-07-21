"""Phase O: privacy-safe analytics_events table

Revision ID: a1b2c3d4e5f6
Revises: f8a9b0c1d2e3
Create Date: 2026-07-17 12:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "f8a9b0c1d2e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "analytics_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_name", sa.String(length=64), nullable=False),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_analytics_events_event_name", "analytics_events", ["event_name"]
    )
    op.create_index(
        "ix_analytics_events_created_at", "analytics_events", ["created_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_analytics_events_created_at", table_name="analytics_events")
    op.drop_index("ix_analytics_events_event_name", table_name="analytics_events")
    op.drop_table("analytics_events")
