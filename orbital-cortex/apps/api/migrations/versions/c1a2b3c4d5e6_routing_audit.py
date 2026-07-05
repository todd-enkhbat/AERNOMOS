"""Group C: routing audit columns + routing_candidates + job deadline

Revision ID: c1a2b3c4d5e6
Revises: b1c2d3e4f5a6
Create Date: 2026-07-05 02:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'c1a2b3c4d5e6'
down_revision: Union[str, None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("deadline_minutes", sa.Float(), nullable=True))

    for name, column in [
        ("config_version", sa.Column("config_version", sa.String(), nullable=False, server_default="")),
        ("input_hash", sa.Column("input_hash", sa.String(), nullable=False, server_default="")),
        ("decision_hash", sa.Column("decision_hash", sa.String(), nullable=False, server_default="")),
        ("tle_snapshot_id", sa.Column("tle_snapshot_id", sa.String(), nullable=False, server_default="")),
        ("seed", sa.Column("seed", sa.Integer(), nullable=False, server_default="0")),
        ("inputs_json", sa.Column("inputs_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}")),
    ]:
        op.add_column("routing_decisions", column)

    op.create_table(
        "routing_candidates",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("routing_decision_id", sa.String(), nullable=False),
        sa.Column("node_id", sa.String(), nullable=False),
        sa.Column("eligible", sa.Boolean(), nullable=False),
        sa.Column("hard_constraint_failures", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("soft_scores", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("weights", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("final_score", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["routing_decision_id"], ["routing_decisions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_routing_candidates_decision",
        "routing_candidates",
        ["routing_decision_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_routing_candidates_decision", table_name="routing_candidates")
    op.drop_table("routing_candidates")
    for name in [
        "inputs_json", "seed", "tle_snapshot_id",
        "decision_hash", "input_hash", "config_version",
    ]:
        op.drop_column("routing_decisions", name)
    op.drop_column("jobs", "deadline_minutes")
