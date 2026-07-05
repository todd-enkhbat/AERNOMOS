"""Group D3: convert JSONB spatial columns to PostGIS geometry

Revision ID: e1f2a3b4c5d6
Revises: d1e2f3a4b5c6
Create Date: 2026-07-05 02:27:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = 'e1f2a3b4c5d6'
down_revision: Union[str, None] = 'd1e2f3a4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE detections
        ALTER COLUMN geom TYPE geometry(Point, 4326)
        USING ST_SetSRID(ST_GeomFromGeoJSON(geom::text), 4326)
        """
    )
    op.execute(
        "CREATE INDEX ix_detections_geom ON detections USING GIST (geom)"
    )
    op.execute(
        """
        ALTER TABLE scenes
        ALTER COLUMN aoi TYPE geometry(Polygon, 4326)
        USING ST_SetSRID(ST_GeomFromGeoJSON(aoi::text), 4326)
        """
    )
    op.execute("CREATE INDEX ix_scenes_aoi ON scenes USING GIST (aoi)")


def downgrade() -> None:
    op.execute("DROP INDEX ix_scenes_aoi")
    op.execute(
        "ALTER TABLE scenes ALTER COLUMN aoi TYPE jsonb USING ST_AsGeoJSON(aoi)::jsonb"
    )
    op.execute("DROP INDEX ix_detections_geom")
    op.execute(
        "ALTER TABLE detections ALTER COLUMN geom TYPE jsonb USING ST_AsGeoJSON(geom)::jsonb"
    )
