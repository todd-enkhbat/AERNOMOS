"""Mission-planning ORM models (Phase B).

Additive tables for private mission plans. Legacy Job / Scene / Detection
tables are unchanged. Primary keys are UUIDs so missions are not sequential
or publicly enumerable.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from geoalchemy2 import Geometry
from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.orm import Base
from app.db.truth import TruthStatus

_TRUTH_STATUS_ENUM = Enum(
    TruthStatus,
    name="truth_status",
    native_enum=False,
    length=32,
    values_callable=lambda enum_cls: [member.value for member in enum_cls],
)


class AnonymousSession(Base):
    __tablename__ = "anonymous_sessions"
    __table_args__ = (
        Index("ix_anonymous_sessions_expires_at", "expires_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_token_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    # Future auth linkage; no users table yet (Phase C+).
    converted_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )


class Mission(Base):
    __tablename__ = "missions"
    __table_args__ = (
        CheckConstraint(
            "(anonymous_session_id IS NOT NULL) OR (organization_id IS NOT NULL)",
            name="ck_missions_has_owner",
        ),
        Index("ix_missions_anonymous_session_id", "anonymous_session_id"),
        Index("ix_missions_organization_id", "organization_id"),
        Index("ix_missions_created_at", "created_at"),
        Index("ix_missions_is_example", "is_example"),
        Index(
            "ix_missions_area_of_interest",
            "area_of_interest",
            postgresql_using="gist",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    anonymous_session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("anonymous_sessions.id", ondelete="CASCADE"),
        nullable=True,
    )
    # Reserved for future org tenancy; no organizations table yet.
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    objective_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    area_of_interest: Mapped[Any] = mapped_column(
        Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=False),
        nullable=False,
    )
    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    max_cost_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_data_volume_mb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    preferred_compute_location: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )
    allowed_regions: Mapped[Any] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    data_source_preference: Mapped[Any] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    customer_systems: Mapped[Any] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_example: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class MissionDataCandidate(Base):
    __tablename__ = "mission_data_candidates"
    __table_args__ = (
        UniqueConstraint(
            "mission_id",
            "source_provider",
            "external_item_id",
            name="uq_mission_data_candidates_mission_provider_item",
        ),
        Index("ix_mission_data_candidates_mission_id", "mission_id"),
        Index(
            "ix_mission_data_candidates_catalog",
            "source_provider",
            "collection",
            "external_item_id",
        ),
        Index(
            "ix_mission_data_candidates_footprint",
            "footprint",
            postgresql_using="gist",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("missions.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_provider: Mapped[str] = mapped_column(String(64), nullable=False)
    collection: Mapped[str] = mapped_column(String(128), nullable=False)
    external_item_id: Mapped[str] = mapped_column(String(256), nullable=False)
    acquisition_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    footprint: Mapped[Any] = mapped_column(
        Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=False),
        nullable=False,
    )
    asset_metadata: Mapped[Any] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    estimated_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    truth_status: Mapped[TruthStatus] = mapped_column(
        _TRUTH_STATUS_ENUM, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class InfrastructureResource(Base):
    __tablename__ = "infrastructure_resources"
    __table_args__ = (
        Index(
            "ix_infrastructure_resources_provider_type",
            "provider_name",
            "resource_type",
        ),
        Index(
            "ix_infrastructure_resources_external_id",
            "provider_name",
            "external_resource_id",
        ),
        Index(
            "ix_infrastructure_resources_location",
            "location",
            postgresql_using="gist",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    provider_name: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    external_resource_id: Mapped[Optional[str]] = mapped_column(
        String(256), nullable=True
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    location: Mapped[Optional[Any]] = mapped_column(
        Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=False),
        nullable=True,
    )
    capabilities: Mapped[Any] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    constraints: Mapped[Any] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    pricing: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    access_level: Mapped[str] = mapped_column(String(64), nullable=False)
    source_metadata: Mapped[Any] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    truth_status: Mapped[TruthStatus] = mapped_column(
        _TRUTH_STATUS_ENUM, nullable=False
    )
    data_freshness_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )


class MissionPlan(Base):
    __tablename__ = "mission_plans"
    __table_args__ = (
        UniqueConstraint("mission_id", "version", name="uq_mission_plans_mission_version"),
        Index("ix_mission_plans_mission_id", "mission_id"),
        Index("ix_mission_plans_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("missions.id", ondelete="CASCADE"),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    recommended: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_total_time_seconds: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    estimated_total_cost_usd: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    assumptions: Mapped[Any] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class MissionPlanStep(Base):
    __tablename__ = "mission_plan_steps"
    __table_args__ = (
        UniqueConstraint(
            "mission_plan_id", "sequence", name="uq_mission_plan_steps_plan_sequence"
        ),
        Index("ix_mission_plan_steps_mission_plan_id", "mission_plan_id"),
        Index("ix_mission_plan_steps_resource_id", "resource_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mission_plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mission_plans.id", ondelete="CASCADE"),
        nullable=False,
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    step_type: Mapped[str] = mapped_column(String(64), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("infrastructure_resources.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    estimated_cost_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    input_artifact: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    output_artifact: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    truth_status: Mapped[TruthStatus] = mapped_column(
        _TRUTH_STATUS_ENUM, nullable=False
    )
    source_metadata: Mapped[Any] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    feasibility_status: Mapped[str] = mapped_column(String(32), nullable=False)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class SourceEvidence(Base):
    __tablename__ = "source_evidence"
    __table_args__ = (
        Index("ix_source_evidence_mission_id", "mission_id"),
        Index("ix_source_evidence_mission_plan_id", "mission_plan_id"),
        Index("ix_source_evidence_mission_plan_step_id", "mission_plan_step_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("missions.id", ondelete="CASCADE"),
        nullable=False,
    )
    mission_plan_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mission_plans.id", ondelete="CASCADE"),
        nullable=True,
    )
    mission_plan_step_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mission_plan_steps.id", ondelete="CASCADE"),
        nullable=True,
    )
    source_name: Mapped[str] = mapped_column(String(256), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    effective_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    raw_value: Mapped[Any] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    transformed_value: Mapped[Any] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    transformation_method: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True
    )
    truth_status: Mapped[TruthStatus] = mapped_column(
        _TRUTH_STATUS_ENUM, nullable=False
    )


class ShareLink(Base):
    __tablename__ = "share_links"
    __table_args__ = (
        Index("ix_share_links_mission_id", "mission_id"),
        Index("ix_share_links_expires_at", "expires_at"),
        CheckConstraint(
            "revoked_at IS NULL OR revoked_at >= created_at",
            name="ck_share_links_revoked_after_created",
        ),
        CheckConstraint(
            "expires_at IS NULL OR expires_at >= created_at",
            name="ck_share_links_expires_after_created",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("missions.id", ondelete="CASCADE"),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    permissions: Mapped[Any] = mapped_column(
        JSONB, nullable=False, server_default=text("'[\"read\"]'::jsonb")
    )


class MissionExport(Base):
    """PDF (and future) mission brief export artifacts (Phase K)."""

    __tablename__ = "mission_exports"
    __table_args__ = (
        Index("ix_mission_exports_mission_id", "mission_id"),
        Index("ix_mission_exports_created_at", "created_at"),
        Index(
            "ix_mission_exports_mission_type_created",
            "mission_id",
            "export_type",
            "created_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("missions.id", ondelete="CASCADE"),
        nullable=False,
    )
    export_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    artifact_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
