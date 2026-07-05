"""Group D2: scenes + detections tables (spatial columns start as JSONB)

Revision ID: d1e2f3a4b5c6
Revises: c1a2b3c4d5e6
Create Date: 2026-07-05 02:26:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'd1e2f3a4b5c6'
down_revision: Union[str, None] = 'c1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scenes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("job_id", sa.String(), nullable=False),
        # Staged spatial schema: JSONB now, geometry(Polygon,4326) in D3.
        sa.Column("aoi", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("captured_utc", sa.String(), nullable=False),
        sa.Column("sensor", sa.String(), nullable=False),
        sa.Column("mode", sa.String(), nullable=False),
        sa.Column("resolution_m", sa.Float(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("provenance", sa.String(), nullable=False),
        sa.Column("stac_item_id", sa.String(), nullable=True),
        sa.Column("cog_url", sa.String(), nullable=True),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id"),
    )
    op.create_table(
        "detections",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("scene_id", sa.String(), nullable=False),
        # Staged spatial schema: JSONB now, geometry(Point,4326) in D3.
        sa.Column("geom", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("bbox", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("ais_correlated", sa.Boolean(), nullable=False),
        sa.Column("vessel_hint", sa.String(), nullable=True),
        sa.Column("properties", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("detected_utc", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["scene_id"], ["scenes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_detections_scene_id", "detections", ["scene_id"])


def downgrade() -> None:
    op.drop_index("ix_detections_scene_id", table_name="detections")
    op.drop_table("detections")
    op.drop_table("scenes")
