"""Phase M: execution_jobs table + plan-step execution status

Revision ID: f8a9b0c1d2e3
Revises: e7f8a9b0c1d2
Create Date: 2026-07-17 06:10:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f8a9b0c1d2e3"
down_revision: Union[str, None] = "e7f8a9b0c1d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "execution_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("idempotency_key", sa.String(length=128), nullable=False),
        sa.Column("mission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mission_plan_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("mission_plan_step_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("provider_id", sa.String(length=64), nullable=False),
        sa.Column("task_type", sa.String(length=64), nullable=False),
        sa.Column("input_ref", sa.Text(), nullable=False),
        sa.Column(
            "params",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("output_key", sa.String(length=512), nullable=True),
        sa.Column(
            "observed_metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["mission_id"], ["missions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["mission_plan_id"], ["mission_plans.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["mission_plan_step_id"], ["mission_plan_steps.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "idempotency_key", name="uq_execution_jobs_idempotency_key"
        ),
    )
    op.create_index("ix_execution_jobs_mission_id", "execution_jobs", ["mission_id"])
    op.create_index(
        "ix_execution_jobs_mission_plan_step_id",
        "execution_jobs",
        ["mission_plan_step_id"],
    )
    op.create_index("ix_execution_jobs_created_at", "execution_jobs", ["created_at"])

    op.add_column(
        "mission_plan_steps",
        sa.Column(
            "execution_status",
            sa.String(length=32),
            server_default=sa.text("'planned'"),
            nullable=False,
        ),
    )
    op.add_column(
        "mission_plan_steps",
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("mission_plan_steps", "executed_at")
    op.drop_column("mission_plan_steps", "execution_status")
    op.drop_index("ix_execution_jobs_created_at", table_name="execution_jobs")
    op.drop_index(
        "ix_execution_jobs_mission_plan_step_id", table_name="execution_jobs"
    )
    op.drop_index("ix_execution_jobs_mission_id", table_name="execution_jobs")
    op.drop_table("execution_jobs")
