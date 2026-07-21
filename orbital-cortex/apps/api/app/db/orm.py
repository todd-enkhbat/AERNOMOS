"""SQLAlchemy 2.x ORM models for the orbital-cortex control plane.

Legacy demo tables (jobs, scenes, detections, routing, …) use string IDs.
Mission-planning tables live in ``mission_orm`` (UUID PKs + PostGIS) and are
imported at the bottom so Alembic sees a single ``Base.metadata``.
"""

from __future__ import annotations

from typing import Any, Optional

from geoalchemy2 import Geometry
from sqlalchemy import (
    BigInteger,
    Boolean,
    Float,
    ForeignKey,
    Identity,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    schema_version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="1"
    )
    job_type: Mapped[str] = mapped_column(String, nullable=False)
    area_of_interest_json: Mapped[Any] = mapped_column(JSONB, nullable=False)
    sensor: Mapped[str] = mapped_column(String, nullable=False)
    priority: Mapped[str] = mapped_column(String, nullable=False)
    compute_preference: Mapped[str] = mapped_column(String, nullable=False)
    max_cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    deadline_minutes: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False)
    updated_at: Mapped[str] = mapped_column(String, nullable=False)
    selected_route_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    # Curated public demo examples only; visitor submissions stay hidden from list APIs.
    is_example: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    # SHA-256 hex of the one-time access token returned on create (private jobs).
    # Example jobs leave this null and remain publicly readable by ID.
    access_token_hash: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True
    )


class ComputeNode(Base):
    __tablename__ = "compute_nodes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    orbit: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    gpu_class: Mapped[str] = mapped_column(String, nullable=False)
    supported_models_json: Mapped[Any] = mapped_column(JSONB, nullable=False)
    storage_gb: Mapped[int] = mapped_column(Integer, nullable=False)
    downlink_mbps: Mapped[int] = mapped_column(Integer, nullable=False)
    power_state: Mapped[str] = mapped_column(String, nullable=False)
    availability: Mapped[float] = mapped_column(Float, nullable=False)
    compliance_tags_json: Mapped[Any] = mapped_column(JSONB, nullable=False)
    base_cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    latency_minutes: Mapped[float] = mapped_column(Float, nullable=False)
    # Real satellite this simulated orbital node rides on (None for cloud).
    satellite_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("satellites.id", ondelete="SET NULL"), nullable=True
    )


class GroundStation(Base):
    __tablename__ = "ground_stations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str] = mapped_column(String, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    altitude_m: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    min_elevation_deg: Mapped[float] = mapped_column(
        Float, nullable=False, server_default="10.0"
    )
    provider: Mapped[str] = mapped_column(String, nullable=False, server_default="")
    latency_minutes: Mapped[float] = mapped_column(Float, nullable=False)
    downlink_mbps: Mapped[int] = mapped_column(Integer, nullable=False)
    availability: Mapped[float] = mapped_column(Float, nullable=False)
    access_level: Mapped[str] = mapped_column(
        String(64), nullable=False, server_default="public_information"
    )
    source_metadata: Mapped[Any] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )


class Satellite(Base):
    __tablename__ = "satellites"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    norad_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    tle_line1: Mapped[str] = mapped_column(String, nullable=False)
    tle_line2: Mapped[str] = mapped_column(String, nullable=False)
    tle_epoch: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    snapshot_id: Mapped[str] = mapped_column(String, nullable=False)
    downlink_rate_mbps: Mapped[float] = mapped_column(Float, nullable=False)
    retrieved_at: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class ContactWindow(Base):
    __tablename__ = "contact_windows"
    __table_args__ = (
        # One row per physical pass; (sat, station, date) is the cache key.
        {"comment": "SGP4-propagated passes; cache key (satellite_id, ground_station_id, date)"},
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    satellite_id: Mapped[str] = mapped_column(
        String, ForeignKey("satellites.id", ondelete="CASCADE"), nullable=False
    )
    ground_station_id: Mapped[str] = mapped_column(
        String, ForeignKey("ground_stations.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[str] = mapped_column(String, nullable=False)  # AOS date, YYYY-MM-DD UTC
    aos_utc: Mapped[str] = mapped_column(String, nullable=False)
    culminate_utc: Mapped[str] = mapped_column(String, nullable=False)
    los_utc: Mapped[str] = mapped_column(String, nullable=False)
    max_elevation_deg: Mapped[float] = mapped_column(Float, nullable=False)
    duration_s: Mapped[float] = mapped_column(Float, nullable=False)
    est_downlink_mb: Mapped[float] = mapped_column(Float, nullable=False)
    tle_snapshot_id: Mapped[str] = mapped_column(
        String, nullable=False, server_default=""
    )
    created_at: Mapped[str] = mapped_column(String, nullable=False)


class RoutingDecision(Base):
    __tablename__ = "routing_decisions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    job_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    selected_node_id: Mapped[str] = mapped_column(String, nullable=False)
    selected_ground_station_id: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )
    fallback_node_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    estimated_latency_minutes: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    reasons_json: Mapped[Any] = mapped_column(JSONB, nullable=False)
    candidate_scores_json: Mapped[Any] = mapped_column(JSONB, nullable=False)
    # C3/C4 audit trail: everything needed to reproduce this decision.
    config_version: Mapped[str] = mapped_column(String, nullable=False, server_default="")
    input_hash: Mapped[str] = mapped_column(String, nullable=False, server_default="")
    decision_hash: Mapped[str] = mapped_column(String, nullable=False, server_default="")
    tle_snapshot_id: Mapped[str] = mapped_column(String, nullable=False, server_default="")
    seed: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    inputs_json: Mapped[Any] = mapped_column(JSONB, nullable=False, server_default="{}")
    created_at: Mapped[str] = mapped_column(String, nullable=False)


class RoutingCandidate(Base):
    __tablename__ = "routing_candidates"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    routing_decision_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("routing_decisions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    node_id: Mapped[str] = mapped_column(String, nullable=False)
    eligible: Mapped[bool] = mapped_column(Boolean, nullable=False)
    hard_constraint_failures: Mapped[Any] = mapped_column(JSONB, nullable=False)
    soft_scores: Mapped[Any] = mapped_column(JSONB, nullable=False)
    weights: Mapped[Any] = mapped_column(JSONB, nullable=False)
    final_score: Mapped[float] = mapped_column(Float, nullable=False)


class Scene(Base):
    __tablename__ = "scenes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    job_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    # JSONB at creation (D2); converted to geometry(Polygon,4326) in D3.
    aoi: Mapped[Any] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326), nullable=False
    )
    captured_utc: Mapped[str] = mapped_column(String, nullable=False)
    sensor: Mapped[str] = mapped_column(String, nullable=False)
    mode: Mapped[str] = mapped_column(String, nullable=False)
    resolution_m: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    provenance: Mapped[str] = mapped_column(String, nullable=False)
    stac_item_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cog_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[str] = mapped_column(String, nullable=False)


class Detection(Base):
    __tablename__ = "detections"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    scene_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("scenes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # JSONB at creation (D2); converted to geometry(Point,4326) in D3.
    geom: Mapped[Any] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=False
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    bbox: Mapped[Any] = mapped_column(JSONB, nullable=False)
    ais_correlated: Mapped[bool] = mapped_column(Boolean, nullable=False)
    vessel_hint: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    properties: Mapped[Any] = mapped_column(JSONB, nullable=False, server_default="{}")
    detected_utc: Mapped[str] = mapped_column(String, nullable=False)


class JobEvent(Base):
    __tablename__ = "job_events"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    # Monotonic insert order; replaces SQLite's implicit rowid for event ordering.
    seq: Mapped[int] = mapped_column(
        BigInteger, Identity(always=False), nullable=False, unique=True
    )
    job_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[Any] = mapped_column(
        JSONB, nullable=False, server_default="{}"
    )
    ts_utc: Mapped[str] = mapped_column(String, nullable=False)


class Result(Base):
    __tablename__ = "results"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    job_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    geojson_json: Mapped[Any] = mapped_column(JSONB, nullable=False)
    output_files_json: Mapped[Any] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False)


# Register mission-planning models on Base.metadata (Phase B).
from app.db import mission_orm as _mission_orm  # noqa: E402,F401
