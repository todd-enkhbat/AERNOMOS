"""Phase P: mission_feedback + design_partner_requests

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-17 13:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "mission_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id_hash", sa.String(length=64), nullable=True),
        sa.Column("rating", sa.String(length=16), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["mission_id"], ["missions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_mission_feedback_mission_id", "mission_feedback", ["mission_id"]
    )
    op.create_index(
        "ix_mission_feedback_created_at", "mission_feedback", ["created_at"]
    )

    op.create_table(
        "design_partner_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mission_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("work_email", sa.String(length=320), nullable=False),
        sa.Column("organization", sa.String(length=200), nullable=False),
        sa.Column("role", sa.String(length=120), nullable=False),
        sa.Column("mission_type", sa.String(length=120), nullable=False),
        sa.Column("requested_integration", sa.String(length=200), nullable=False),
        sa.Column("permission_to_contact", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["mission_id"], ["missions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_design_partner_requests_mission_id",
        "design_partner_requests",
        ["mission_id"],
    )
    op.create_index(
        "ix_design_partner_requests_created_at",
        "design_partner_requests",
        ["created_at"],
    )
    op.create_index(
        "ix_design_partner_requests_organization",
        "design_partner_requests",
        ["organization"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_design_partner_requests_organization",
        table_name="design_partner_requests",
    )
    op.drop_index(
        "ix_design_partner_requests_created_at",
        table_name="design_partner_requests",
    )
    op.drop_index(
        "ix_design_partner_requests_mission_id",
        table_name="design_partner_requests",
    )
    op.drop_table("design_partner_requests")
    op.drop_index("ix_mission_feedback_created_at", table_name="mission_feedback")
    op.drop_index("ix_mission_feedback_mission_id", table_name="mission_feedback")
    op.drop_table("mission_feedback")
