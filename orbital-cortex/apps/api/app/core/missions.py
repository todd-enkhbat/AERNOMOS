"""Mission and share-link persistence helpers."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Sequence

from geoalchemy2.elements import WKTElement
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.tokens import hash_token, mint_token
from app.db.mission_orm import AnonymousSession, Mission, ShareLink

# Stable org UUID for curated public example missions (no org table yet).
EXAMPLES_ORGANIZATION_ID = uuid.UUID("00000000-0000-4000-8000-0000000000e1")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _ring_to_wkt(ring: Sequence[Sequence[float]]) -> str:
    points = [f"{float(lon)} {float(lat)}" for lon, lat in ring]
    if points and points[0] != points[-1]:
        points.append(points[0])
    return "(" + ",".join(points) + ")"


def geojson_to_wkt(area: Dict[str, Any]) -> str:
    """Accept GeoJSON Polygon/MultiPolygon or the demo bbox shape."""
    geom_type = area.get("type")
    if geom_type == "bbox":
        coords = area["coordinates"]
        if len(coords) != 4:
            raise ValueError("bbox coordinates must be [west, south, east, north]")
        west, south, east, north = (float(c) for c in coords)
        return (
            f"POLYGON(({west} {south},{east} {south},"
            f"{east} {north},{west} {north},{west} {south}))"
        )
    if geom_type == "Polygon":
        rings = area.get("coordinates") or []
        if not rings:
            raise ValueError("Polygon coordinates are required")
        return "POLYGON(" + ",".join(_ring_to_wkt(ring) for ring in rings) + ")"
    if geom_type == "MultiPolygon":
        polygons = area.get("coordinates") or []
        if not polygons:
            raise ValueError("MultiPolygon coordinates are required")
        parts = []
        for polygon in polygons:
            parts.append("(" + ",".join(_ring_to_wkt(ring) for ring in polygon) + ")")
        return "MULTIPOLYGON(" + ",".join(parts) + ")"
    raise ValueError(
        "area_of_interest must be GeoJSON Polygon/MultiPolygon or {type:'bbox',...}"
    )


def geometry_to_geojson(session: Session, geom: Any) -> Dict[str, Any]:
    if geom is None:
        return {"type": "Polygon", "coordinates": []}
    raw = session.scalar(select(func.ST_AsGeoJSON(geom)))
    if not raw:
        return {"type": "Polygon", "coordinates": []}
    return json.loads(raw)


def mission_to_dict(session: Session, mission: Mission) -> Dict[str, Any]:
    return {
        "id": str(mission.id),
        "anonymous_session_id": (
            str(mission.anonymous_session_id) if mission.anonymous_session_id else None
        ),
        "organization_id": (
            str(mission.organization_id) if mission.organization_id else None
        ),
        "title": mission.title,
        "objective_type": mission.objective_type,
        "status": mission.status,
        "area_of_interest": geometry_to_geojson(session, mission.area_of_interest),
        "start_time": mission.start_time.isoformat() if mission.start_time else None,
        "end_time": mission.end_time.isoformat() if mission.end_time else None,
        "deadline": mission.deadline.isoformat() if mission.deadline else None,
        "max_cost_usd": mission.max_cost_usd,
        "max_data_volume_mb": mission.max_data_volume_mb,
        "preferred_compute_location": mission.preferred_compute_location,
        "allowed_regions": mission.allowed_regions,
        "data_source_preference": mission.data_source_preference,
        "customer_systems": mission.customer_systems,
        "notes": mission.notes,
        "is_example": bool(getattr(mission, "is_example", False)),
        "created_at": mission.created_at.isoformat(),
        "updated_at": mission.updated_at.isoformat(),
    }


def share_link_to_dict(
    link: ShareLink, *, include_token: Optional[str] = None
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "id": str(link.id),
        "mission_id": str(link.mission_id),
        "created_at": link.created_at.isoformat(),
        "expires_at": link.expires_at.isoformat() if link.expires_at else None,
        "revoked_at": link.revoked_at.isoformat() if link.revoked_at else None,
        "permissions": link.permissions,
    }
    if include_token is not None:
        payload["token"] = include_token
    return payload


def _pack_builder_preferences(payload: Dict[str, Any]) -> List[Any]:
    """Merge guided-builder fields into customer_systems JSON (no extra columns)."""
    systems: List[Any] = list(payload.get("customer_systems") or [])

    def _has_kind(kind: str) -> bool:
        return any(
            isinstance(item, dict) and item.get("kind") == kind for item in systems
        )

    org = payload.get("organization_name")
    if org and not _has_kind("organization"):
        systems.append({"kind": "organization", "name": str(org).strip()})

    use_case = payload.get("use_case")
    if use_case and not _has_kind("use_case"):
        systems.append({"kind": "use_case", "value": str(use_case).strip()})

    max_age = payload.get("max_age_days")
    if max_age is not None and not _has_kind("data_freshness"):
        systems.append({"kind": "data_freshness", "max_age_days": int(max_age)})

    onboard = payload.get("onboard_processing")
    if onboard and not _has_kind("onboard_processing"):
        systems.append({"kind": "onboard_processing", "preference": str(onboard)})

    residency = payload.get("data_residency")
    if residency and not _has_kind("data_residency"):
        systems.append({"kind": "data_residency", "requirement": str(residency).strip()})

    return systems


def create_mission(
    session: Session,
    *,
    owner: AnonymousSession,
    payload: Dict[str, Any],
) -> Mission:
    now = utc_now()
    # Re-validate geo at persistence boundary (Pydantic also validates on the route).
    from app.core.mission_geo import validate_area_of_interest

    area = validate_area_of_interest(payload["area_of_interest"])
    wkt = geojson_to_wkt(area)
    customer_systems = _pack_builder_preferences(payload)
    mission = Mission(
        id=uuid.uuid4(),
        anonymous_session_id=owner.id,
        organization_id=None,
        title=payload["title"],
        objective_type=payload["objective_type"],
        status=payload.get("status") or "draft",
        area_of_interest=WKTElement(wkt, srid=4326),
        start_time=payload.get("start_time"),
        end_time=payload.get("end_time"),
        deadline=payload.get("deadline"),
        max_cost_usd=payload.get("max_cost_usd"),
        max_data_volume_mb=payload.get("max_data_volume_mb"),
        preferred_compute_location=payload.get("preferred_compute_location"),
        allowed_regions=payload.get("allowed_regions") or [],
        data_source_preference=payload.get("data_source_preference") or [],
        customer_systems=customer_systems,
        notes=payload.get("notes"),
        is_example=False,
        created_at=now,
        updated_at=now,
    )
    session.add(mission)
    session.flush()
    return mission


def list_session_missions(session: Session, owner_id: uuid.UUID) -> List[Mission]:
    return list(
        session.scalars(
            select(Mission)
            .where(
                Mission.anonymous_session_id == owner_id,
                Mission.is_example.is_(False),
            )
            .order_by(Mission.created_at.desc())
        ).all()
    )


def list_example_missions(session: Session) -> List[Mission]:
    return list(
        session.scalars(
            select(Mission)
            .where(Mission.is_example.is_(True))
            .order_by(Mission.created_at.desc())
        ).all()
    )


def get_mission(session: Session, mission_id: uuid.UUID) -> Optional[Mission]:
    return session.get(Mission, mission_id)


def session_owns_mission(owner: AnonymousSession, mission: Mission) -> bool:
    return (
        mission.anonymous_session_id is not None
        and mission.anonymous_session_id == owner.id
    )


def get_active_share_link(
    session: Session, raw_token: str, *, now: Optional[datetime] = None
) -> Optional[ShareLink]:
    cutoff = now or utc_now()
    link = session.scalars(
        select(ShareLink).where(ShareLink.token_hash == hash_token(raw_token))
    ).one_or_none()
    if link is None:
        return None
    if link.revoked_at is not None:
        return None
    if link.expires_at is not None and link.expires_at <= cutoff:
        return None
    return link


def create_share_link(
    session: Session,
    mission: Mission,
    *,
    settings: Optional[Settings] = None,
    expires_at: Optional[datetime] = None,
    permissions: Optional[Sequence[str]] = None,
) -> tuple[ShareLink, str]:
    settings = settings or get_settings()
    now = utc_now()
    raw = mint_token()
    if expires_at is None:
        expires_at = now + timedelta(days=settings.share_link_default_ttl_days)
    link = ShareLink(
        id=uuid.uuid4(),
        mission_id=mission.id,
        token_hash=hash_token(raw),
        created_at=now,
        expires_at=expires_at,
        permissions=list(permissions) if permissions is not None else ["read"],
    )
    session.add(link)
    session.flush()
    return link, raw


def revoke_share_link(link: ShareLink, *, now: Optional[datetime] = None) -> None:
    link.revoked_at = now or utc_now()


def ensure_example_mission(session: Session) -> None:
    """Idempotently seed one curated public example mission."""
    existing = session.scalar(
        select(func.count()).select_from(Mission).where(Mission.is_example.is_(True))
    )
    if existing:
        return
    now = utc_now()
    session.add(
        Mission(
            id=uuid.uuid4(),
            anonymous_session_id=None,
            organization_id=EXAMPLES_ORGANIZATION_ID,
            title="Example: NY Harbor maritime awareness",
            objective_type="ship_detection",
            status="example",
            area_of_interest=WKTElement(
                "POLYGON((-74.3 40.3,-73.5 40.3,-73.5 41.0,-74.3 41.0,-74.3 40.3))",
                srid=4326,
            ),
            notes=(
                "Curated public example. Not a private user mission. "
                "Demo environment only."
            ),
            is_example=True,
            created_at=now,
            updated_at=now,
        )
    )


def parse_mission_id(raw: str) -> uuid.UUID:
    try:
        return uuid.UUID(raw)
    except ValueError as exc:
        raise ValueError("mission id must be a UUID") from exc
