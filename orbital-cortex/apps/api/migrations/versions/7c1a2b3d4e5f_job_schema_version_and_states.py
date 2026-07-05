"""job schema_version + new lifecycle state names

Revision ID: 7c1a2b3d4e5f
Revises: 49565e994140
Create Date: 2026-07-05 01:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '7c1a2b3d4e5f'
down_revision: Union[str, None] = '49565e994140'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Old MVP vocabulary -> A4 state machine vocabulary.
STATUS_REMAP = [
    ("scheduled", "routing"),
    ("running", "executing"),
    ("completed", "complete"),
]


def upgrade() -> None:
    op.add_column(
        "jobs",
        sa.Column("schema_version", sa.Integer(), nullable=False, server_default="1"),
    )
    for old, new in STATUS_REMAP:
        op.execute(f"UPDATE jobs SET status = '{new}' WHERE status = '{old}'")


def downgrade() -> None:
    for old, new in STATUS_REMAP:
        op.execute(f"UPDATE jobs SET status = '{old}' WHERE status = '{new}'")
    op.drop_column("jobs", "schema_version")
