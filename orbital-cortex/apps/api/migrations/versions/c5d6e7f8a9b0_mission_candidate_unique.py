"""Phase F: unique dedupe for mission catalog candidates + BigInteger sizes

Revision ID: c5d6e7f8a9b0
Revises: b4c5d6e7f8a9
Create Date: 2026-07-16 22:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c5d6e7f8a9b0"
down_revision: Union[str, None] = "b4c5d6e7f8a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Dedupe any accidental duplicates before adding the unique constraint.
    op.execute(
        """
        DELETE FROM mission_data_candidates a
        USING mission_data_candidates b
        WHERE a.ctid < b.ctid
          AND a.mission_id = b.mission_id
          AND a.source_provider = b.source_provider
          AND a.external_item_id = b.external_item_id
        """
    )
    op.create_unique_constraint(
        "uq_mission_data_candidates_mission_provider_item",
        "mission_data_candidates",
        ["mission_id", "source_provider", "external_item_id"],
    )
    # Sentinel scene sizes often exceed 32-bit INTEGER range.
    op.alter_column(
        "mission_data_candidates",
        "estimated_size_bytes",
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=True,
    )


def downgrade() -> None:
    # Values may exceed INTEGER after Phase F discovers multi-GB Sentinel scenes.
    op.execute(
        """
        UPDATE mission_data_candidates
        SET estimated_size_bytes = NULL
        WHERE estimated_size_bytes IS NOT NULL
          AND (
            estimated_size_bytes > 2147483647
            OR estimated_size_bytes < -2147483648
          )
        """
    )
    op.alter_column(
        "mission_data_candidates",
        "estimated_size_bytes",
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=True,
    )
    op.drop_constraint(
        "uq_mission_data_candidates_mission_provider_item",
        "mission_data_candidates",
        type_="unique",
    )
