"""Phase H: orbital provenance columns + ground-station access metadata

Revision ID: d6e7f8a9b0c1
Revises: c5d6e7f8a9b0
Create Date: 2026-07-16 23:30:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "d6e7f8a9b0c1"
down_revision: Union[str, None] = "c5d6e7f8a9b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "satellites",
        sa.Column("retrieved_at", sa.String(), nullable=True),
    )
    op.add_column(
        "contact_windows",
        sa.Column(
            "tle_snapshot_id",
            sa.String(),
            nullable=False,
            server_default="",
        ),
    )
    op.add_column(
        "ground_stations",
        sa.Column(
            "access_level",
            sa.String(length=64),
            nullable=False,
            server_default="public_information",
        ),
    )
    op.add_column(
        "ground_stations",
        sa.Column(
            "source_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column("ground_stations", "source_metadata")
    op.drop_column("ground_stations", "access_level")
    op.drop_column("contact_windows", "tle_snapshot_id")
    op.drop_column("satellites", "retrieved_at")
