"""Group B: satellites, contact_windows, real ground stations

Revision ID: b1c2d3e4f5a6
Revises: 9d2e4f6a8b0c
Create Date: 2026-07-05 02:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, None] = '9d2e4f6a8b0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # B1: ground-station physical parameters for pass modeling.
    op.add_column(
        "ground_stations",
        sa.Column("altitude_m", sa.Float(), nullable=False, server_default="0"),
    )
    op.add_column(
        "ground_stations",
        sa.Column("min_elevation_deg", sa.Float(), nullable=False, server_default="10.0"),
    )
    op.add_column(
        "ground_stations",
        sa.Column("provider", sa.String(), nullable=False, server_default=""),
    )
    # Old fictional seed stations are replaced by real sites on next boot.
    op.execute("DELETE FROM ground_stations")

    # B2: satellite + TLE registry.
    op.create_table(
        "satellites",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("norad_id", sa.Integer(), nullable=False),
        sa.Column("tle_line1", sa.String(), nullable=False),
        sa.Column("tle_line2", sa.String(), nullable=False),
        sa.Column("tle_epoch", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("snapshot_id", sa.String(), nullable=False),
        sa.Column("downlink_rate_mbps", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("norad_id"),
    )

    # B5/B6: cached SGP4 passes with downlink estimates.
    op.create_table(
        "contact_windows",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("satellite_id", sa.String(), nullable=False),
        sa.Column("ground_station_id", sa.String(), nullable=False),
        sa.Column("date", sa.String(), nullable=False),
        sa.Column("aos_utc", sa.String(), nullable=False),
        sa.Column("culminate_utc", sa.String(), nullable=False),
        sa.Column("los_utc", sa.String(), nullable=False),
        sa.Column("max_elevation_deg", sa.Float(), nullable=False),
        sa.Column("duration_s", sa.Float(), nullable=False),
        sa.Column("est_downlink_mb", sa.Float(), nullable=False),
        sa.Column("created_at", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["satellite_id"], ["satellites.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["ground_station_id"], ["ground_stations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_contact_windows_cache_key",
        "contact_windows",
        ["satellite_id", "ground_station_id", "date"],
    )
    op.create_index("ix_contact_windows_aos", "contact_windows", ["aos_utc"])

    # B7: orbital compute nodes ride real satellites; the fake integer dies.
    op.add_column(
        "compute_nodes",
        sa.Column("satellite_id", sa.String(), nullable=True),
    )
    op.create_foreign_key(
        "fk_compute_nodes_satellite",
        "compute_nodes",
        "satellites",
        ["satellite_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.drop_column("compute_nodes", "next_contact_minutes")


def downgrade() -> None:
    op.add_column(
        "compute_nodes",
        sa.Column("next_contact_minutes", sa.Float(), nullable=False, server_default="0"),
    )
    op.drop_constraint("fk_compute_nodes_satellite", "compute_nodes", type_="foreignkey")
    op.drop_column("compute_nodes", "satellite_id")
    op.drop_index("ix_contact_windows_aos", table_name="contact_windows")
    op.drop_index("ix_contact_windows_cache_key", table_name="contact_windows")
    op.drop_table("contact_windows")
    op.drop_table("satellites")
    op.drop_column("ground_stations", "provider")
    op.drop_column("ground_stations", "min_elevation_deg")
    op.drop_column("ground_stations", "altitude_m")
