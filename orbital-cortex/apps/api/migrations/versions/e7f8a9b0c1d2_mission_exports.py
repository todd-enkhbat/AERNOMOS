"""Phase K: mission_exports table for PDF brief artifacts

Revision ID: e7f8a9b0c1d2
Revises: d6e7f8a9b0c1
Create Date: 2026-07-17 00:40:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "e7f8a9b0c1d2"
down_revision: Union[str, None] = "d6e7f8a9b0c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "mission_exports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("export_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("artifact_key", sa.String(length=512), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["mission_id"], ["missions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_mission_exports_mission_id", "mission_exports", ["mission_id"]
    )
    op.create_index(
        "ix_mission_exports_created_at", "mission_exports", ["created_at"]
    )
    op.create_index(
        "ix_mission_exports_mission_type_created",
        "mission_exports",
        ["mission_id", "export_type", "created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_mission_exports_mission_type_created", table_name="mission_exports"
    )
    op.drop_index("ix_mission_exports_created_at", table_name="mission_exports")
    op.drop_index("ix_mission_exports_mission_id", table_name="mission_exports")
    op.drop_table("mission_exports")
