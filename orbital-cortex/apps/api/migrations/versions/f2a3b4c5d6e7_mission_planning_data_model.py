"""Phase B: private mission planning data model

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6
Create Date: 2026-07-16 20:00:00.000000

Additive only — does not alter jobs, scenes, detections, or other demo tables.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

revision: str = "f2a3b4c5d6e7"
down_revision: Union[str, None] = "e1f2a3b4c5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TRUTH_STATUS = sa.Enum(
    "OBSERVED",
    "CALCULATED",
    "PROVIDER_REPORTED",
    "ESTIMATED",
    "SIMULATED",
    "STALE",
    "UNAVAILABLE",
    name="truth_status",
    native_enum=False,
    length=32,
)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "anonymous_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_token_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("converted_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_token_hash"),
    )
    op.create_index(
        "ix_anonymous_sessions_expires_at", "anonymous_sessions", ["expires_at"]
    )

    op.create_table(
        "infrastructure_resources",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider_name", sa.String(length=128), nullable=False),
        sa.Column("resource_type", sa.String(length=64), nullable=False),
        sa.Column("external_resource_id", sa.String(length=256), nullable=True),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column(
            "location",
            Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=False),
            nullable=True,
        ),
        sa.Column(
            "capabilities",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "constraints",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("pricing", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("access_level", sa.String(length=64), nullable=False),
        sa.Column(
            "source_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("truth_status", TRUTH_STATUS, nullable=False),
        sa.Column("data_freshness_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_infrastructure_resources_provider_type",
        "infrastructure_resources",
        ["provider_name", "resource_type"],
    )
    op.create_index(
        "ix_infrastructure_resources_external_id",
        "infrastructure_resources",
        ["provider_name", "external_resource_id"],
    )
    op.create_index(
        "ix_infrastructure_resources_location",
        "infrastructure_resources",
        ["location"],
        postgresql_using="gist",
    )

    op.create_table(
        "missions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("anonymous_session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("objective_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column(
            "area_of_interest",
            Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=False),
            nullable=False,
        ),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("max_cost_usd", sa.Float(), nullable=True),
        sa.Column("max_data_volume_mb", sa.Float(), nullable=True),
        sa.Column("preferred_compute_location", sa.String(length=64), nullable=True),
        sa.Column(
            "allowed_regions",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "data_source_preference",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "customer_systems",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "(anonymous_session_id IS NOT NULL) OR (organization_id IS NOT NULL)",
            name="ck_missions_has_owner",
        ),
        sa.ForeignKeyConstraint(
            ["anonymous_session_id"],
            ["anonymous_sessions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_missions_anonymous_session_id", "missions", ["anonymous_session_id"]
    )
    op.create_index("ix_missions_organization_id", "missions", ["organization_id"])
    op.create_index("ix_missions_created_at", "missions", ["created_at"])
    op.create_index(
        "ix_missions_area_of_interest",
        "missions",
        ["area_of_interest"],
        postgresql_using="gist",
    )

    op.create_table(
        "mission_data_candidates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_provider", sa.String(length=64), nullable=False),
        sa.Column("collection", sa.String(length=128), nullable=False),
        sa.Column("external_item_id", sa.String(length=256), nullable=False),
        sa.Column("acquisition_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "footprint",
            Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=False),
            nullable=False,
        ),
        sa.Column(
            "asset_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("estimated_size_bytes", sa.Integer(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("source_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("truth_status", TRUTH_STATUS, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["mission_id"], ["missions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_mission_data_candidates_mission_id",
        "mission_data_candidates",
        ["mission_id"],
    )
    op.create_index(
        "ix_mission_data_candidates_catalog",
        "mission_data_candidates",
        ["source_provider", "collection", "external_item_id"],
    )
    op.create_index(
        "ix_mission_data_candidates_footprint",
        "mission_data_candidates",
        ["footprint"],
        postgresql_using="gist",
    )

    op.create_table(
        "mission_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "recommended",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("estimated_total_time_seconds", sa.Float(), nullable=True),
        sa.Column("estimated_total_cost_usd", sa.Float(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column(
            "assumptions",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["mission_id"], ["missions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "mission_id", "version", name="uq_mission_plans_mission_version"
        ),
    )
    op.create_index("ix_mission_plans_mission_id", "mission_plans", ["mission_id"])
    op.create_index("ix_mission_plans_created_at", "mission_plans", ["created_at"])

    op.create_table(
        "share_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "permissions",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[\"read\"]'::jsonb"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "revoked_at IS NULL OR revoked_at >= created_at",
            name="ck_share_links_revoked_after_created",
        ),
        sa.CheckConstraint(
            "expires_at IS NULL OR expires_at >= created_at",
            name="ck_share_links_expires_after_created",
        ),
        sa.ForeignKeyConstraint(
            ["mission_id"], ["missions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_share_links_mission_id", "share_links", ["mission_id"])
    op.create_index("ix_share_links_expires_at", "share_links", ["expires_at"])

    op.create_table(
        "mission_plan_steps",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mission_plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("step_type", sa.String(length=64), nullable=False),
        sa.Column("provider_name", sa.String(length=128), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("estimated_cost_usd", sa.Float(), nullable=True),
        sa.Column("input_artifact", sa.String(length=256), nullable=True),
        sa.Column("output_artifact", sa.String(length=256), nullable=True),
        sa.Column("truth_status", TRUTH_STATUS, nullable=False),
        sa.Column(
            "source_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("feasibility_status", sa.String(length=32), nullable=False),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["mission_plan_id"], ["mission_plans.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["resource_id"],
            ["infrastructure_resources.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "mission_plan_id",
            "sequence",
            name="uq_mission_plan_steps_plan_sequence",
        ),
    )
    op.create_index(
        "ix_mission_plan_steps_mission_plan_id",
        "mission_plan_steps",
        ["mission_plan_id"],
    )
    op.create_index(
        "ix_mission_plan_steps_resource_id", "mission_plan_steps", ["resource_id"]
    )

    op.create_table(
        "source_evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("mission_plan_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "mission_plan_step_id", postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.Column("source_name", sa.String(length=256), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("effective_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "raw_value",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "transformed_value",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("transformation_method", sa.String(length=128), nullable=True),
        sa.Column("truth_status", TRUTH_STATUS, nullable=False),
        sa.ForeignKeyConstraint(
            ["mission_id"], ["missions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["mission_plan_id"], ["mission_plans.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["mission_plan_step_id"],
            ["mission_plan_steps.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_source_evidence_mission_id", "source_evidence", ["mission_id"]
    )
    op.create_index(
        "ix_source_evidence_mission_plan_id", "source_evidence", ["mission_plan_id"]
    )
    op.create_index(
        "ix_source_evidence_mission_plan_step_id",
        "source_evidence",
        ["mission_plan_step_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_source_evidence_mission_plan_step_id", table_name="source_evidence"
    )
    op.drop_index("ix_source_evidence_mission_plan_id", table_name="source_evidence")
    op.drop_index("ix_source_evidence_mission_id", table_name="source_evidence")
    op.drop_table("source_evidence")

    op.drop_index(
        "ix_mission_plan_steps_resource_id", table_name="mission_plan_steps"
    )
    op.drop_index(
        "ix_mission_plan_steps_mission_plan_id", table_name="mission_plan_steps"
    )
    op.drop_table("mission_plan_steps")

    op.drop_index("ix_share_links_expires_at", table_name="share_links")
    op.drop_index("ix_share_links_mission_id", table_name="share_links")
    op.drop_table("share_links")

    op.drop_index("ix_mission_plans_created_at", table_name="mission_plans")
    op.drop_index("ix_mission_plans_mission_id", table_name="mission_plans")
    op.drop_table("mission_plans")

    op.drop_index(
        "ix_mission_data_candidates_footprint",
        table_name="mission_data_candidates",
        postgresql_using="gist",
    )
    op.drop_index(
        "ix_mission_data_candidates_catalog", table_name="mission_data_candidates"
    )
    op.drop_index(
        "ix_mission_data_candidates_mission_id",
        table_name="mission_data_candidates",
    )
    op.drop_table("mission_data_candidates")

    op.drop_index(
        "ix_missions_area_of_interest",
        table_name="missions",
        postgresql_using="gist",
    )
    op.drop_index("ix_missions_created_at", table_name="missions")
    op.drop_index("ix_missions_organization_id", table_name="missions")
    op.drop_index("ix_missions_anonymous_session_id", table_name="missions")
    op.drop_table("missions")

    op.drop_index(
        "ix_infrastructure_resources_location",
        table_name="infrastructure_resources",
        postgresql_using="gist",
    )
    op.drop_index(
        "ix_infrastructure_resources_external_id",
        table_name="infrastructure_resources",
    )
    op.drop_index(
        "ix_infrastructure_resources_provider_type",
        table_name="infrastructure_resources",
    )
    op.drop_table("infrastructure_resources")

    op.drop_index(
        "ix_anonymous_sessions_expires_at", table_name="anonymous_sessions"
    )
    op.drop_table("anonymous_sessions")
