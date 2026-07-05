"""job_events: add payload jsonb, rename timestamp -> ts_utc

Revision ID: 9d2e4f6a8b0c
Revises: 7c1a2b3d4e5f
Create Date: 2026-07-05 01:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '9d2e4f6a8b0c'
down_revision: Union[str, None] = '7c1a2b3d4e5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "job_events",
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
    )
    op.alter_column("job_events", "timestamp", new_column_name="ts_utc")


def downgrade() -> None:
    op.alter_column("job_events", "ts_utc", new_column_name="timestamp")
    op.drop_column("job_events", "payload")
