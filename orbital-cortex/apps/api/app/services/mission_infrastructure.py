"""Mission-specific orbital / ground infrastructure selection (Phase H).

Does not dump the full tracked catalog — only the small Nomos fleet entries
relevant to a mission's catalog candidates and data-source preferences.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set

from geoalchemy2.elements import WKTElement
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.mission_orm import InfrastructureResource, Mission, MissionDataCandidate, SourceEvidence
from app.db.orm import GroundStation, Satellite
from app.db.truth import AccessLevel, InfrastructureResourceType, TruthStatus
from app.models.provenance import (
    EXPLANATION_SIMULATED,
    freshness_for,
    provenanced,
)
from app.services import contact_windows as cw_service
from app.services import tle_cache

# Catalog collection / preference tokens → fleet satellite ids.
_COLLECTION_SATELLITES: Dict[str, List[str]] = {
    "sentinel-1-grd": ["sat_sentinel_1a", "sat_sentinel_1c"],
    "sentinel-1": ["sat_sentinel_1a", "sat_sentinel_1c"],
    "sentinel1": ["sat_sentinel_1a", "sat_sentinel_1c"],
    "s1": ["sat_sentinel_1a", "sat_sentinel_1c"],
    "capella": ["sat_capella_14", "sat_capella_15"],
    "iceye": ["sat_iceye_x2"],
}

_SAT_NAME_HINTS: Dict[str, List[str]] = {
    "sentinel-1a": ["sat_sentinel_1a"],
    "sentinel-1c": ["sat_sentinel_1c"],
    "sentinel1a": ["sat_sentinel_1a"],
    "sentinel1c": ["sat_sentinel_1c"],
    "capella-14": ["sat_capella_14"],
    "capella-15": ["sat_capella_15"],
    "iceye-x2": ["sat_iceye_x2"],
}

GS_COORDINATE_METADATA = {
    "coordinate_truth_status": TruthStatus.PROVIDER_REPORTED.value,
    "coordinate_note": (
        "Latitude/longitude from public ground-station registries / provider docs."
    ),
    "ops_params_truth_status": TruthStatus.SIMULATED.value,
    "ops_params_note": (
        "latency_minutes, downlink_mbps, and availability are authored planning "
        "estimates for the demo fleet — not live provider capacity."
    ),
}


def _normalize_token(value: str) -> str:
    return value.strip().lower().replace("_", "-").replace(" ", "")


def _tokens_from_preference(item: Any) -> List[str]:
    if isinstance(item, str):
        return [_normalize_token(item)]
    if isinstance(item, dict):
        tokens: List[str] = []
        for key in ("collection", "provider", "sensor", "name", "id", "source"):
            raw = item.get(key)
            if isinstance(raw, str) and raw.strip():
                tokens.append(_normalize_token(raw))
        return tokens
    return []


def satellite_ids_for_collections(
    collections: Iterable[str],
    preferences: Optional[Sequence[Any]] = None,
) -> Set[str]:
    """Map STAC collections / mission preferences to fleet satellite ids."""
    selected: Set[str] = set()
    tokens: List[str] = [_normalize_token(c) for c in collections if c]
    if preferences:
        for pref in preferences:
            tokens.extend(_tokens_from_preference(pref))

    for token in tokens:
        if token in _COLLECTION_SATELLITES:
            selected.update(_COLLECTION_SATELLITES[token])
        if token in _SAT_NAME_HINTS:
            selected.update(_SAT_NAME_HINTS[token])
        for prefix, sat_ids in _COLLECTION_SATELLITES.items():
            if token.startswith(prefix) or prefix in token:
                selected.update(sat_ids)
        for hint, sat_ids in _SAT_NAME_HINTS.items():
            if hint in token:
                selected.update(sat_ids)
    return selected


def select_satellites_for_mission(
    session: Session,
    mission: Mission,
    candidates: Optional[Sequence[MissionDataCandidate]] = None,
) -> List[Satellite]:
    """Return only fleet satellites relevant to the mission — never the full catalog."""
    if candidates is None:
        candidates = session.scalars(
            select(MissionDataCandidate).where(MissionDataCandidate.mission_id == mission.id)
        ).all()
    collections = [row.collection for row in candidates]
    prefs = mission.data_source_preference or []
    wanted = satellite_ids_for_collections(collections, prefs)
    if not wanted:
        return []
    rows = session.scalars(
        select(Satellite).where(Satellite.id.in_(sorted(wanted))).order_by(Satellite.id.asc())
    ).all()
    return list(rows)


def record_orbital_snapshot_evidence(
    session: Session,
    *,
    mission_id: uuid.UUID,
    snapshot_meta: Dict[str, Any],
    mission_plan_id: Optional[uuid.UUID] = None,
    mission_plan_step_id: Optional[uuid.UUID] = None,
) -> SourceEvidence:
    """Persist SourceEvidence for a TLE / orbital snapshot used in mission context."""
    retrieved_raw = snapshot_meta.get("retrieved_at")
    if isinstance(retrieved_raw, datetime):
        retrieved_at = retrieved_raw
    elif isinstance(retrieved_raw, str) and retrieved_raw:
        retrieved_at = tle_cache.parse_iso_utc(retrieved_raw)
    else:
        retrieved_at = datetime.now(timezone.utc)

    epochs = snapshot_meta.get("epochs") or []
    effective_at = None
    if epochs:
        try:
            effective_at = min(tle_cache.parse_iso_utc(str(e)) for e in epochs)
        except (TypeError, ValueError):
            effective_at = None

    truth_raw = snapshot_meta.get("truth_status") or TruthStatus.STALE.value
    truth = TruthStatus(truth_raw) if not isinstance(truth_raw, TruthStatus) else truth_raw

    evidence = SourceEvidence(
        id=uuid.uuid4(),
        mission_id=mission_id,
        mission_plan_id=mission_plan_id,
        mission_plan_step_id=mission_plan_step_id,
        source_name=f"orbital-tle:{snapshot_meta.get('snapshot_id', '')}",
        source_type="orbital_tle_snapshot",
        source_url=snapshot_meta.get("source_url"),
        retrieved_at=retrieved_at,
        effective_at=effective_at,
        raw_value={
            "snapshot_id": snapshot_meta.get("snapshot_id"),
            "source": snapshot_meta.get("source"),
            "epochs": epochs,
            "used_pinned_fallback": snapshot_meta.get("used_pinned_fallback"),
        },
        transformed_value={
            "stale_epoch_days": snapshot_meta.get(
                "stale_epoch_days", tle_cache.STALE_EPOCH_DAYS
            ),
        },
        transformation_method="tle_cache.resolve_orbital_snapshot",
        truth_status=truth,
    )
    session.add(evidence)
    session.flush()
    return evidence


def record_contact_window_evidence(
    session: Session,
    *,
    mission_id: uuid.UUID,
    window: Dict[str, Any],
    mission_plan_id: Optional[uuid.UUID] = None,
    mission_plan_step_id: Optional[uuid.UUID] = None,
) -> SourceEvidence:
    """Persist SourceEvidence for a calculated contact window."""
    evidence = SourceEvidence(
        id=uuid.uuid4(),
        mission_id=mission_id,
        mission_plan_id=mission_plan_id,
        mission_plan_step_id=mission_plan_step_id,
        source_name="contact-window:sgp4",
        source_type="contact_window",
        source_url=None,
        retrieved_at=datetime.now(timezone.utc),
        effective_at=tle_cache.parse_iso_utc(window["aos_utc"])
        if window.get("aos_utc")
        else None,
        raw_value=dict(window),
        transformed_value={
            "tle_snapshot_id": window.get("tle_snapshot_id"),
            "calculation_method": window.get(
                "calculation_method", cw_service.CONTACT_WINDOW_METHOD
            ),
        },
        transformation_method=cw_service.CONTACT_WINDOW_METHOD,
        truth_status=TruthStatus.CALCULATED,
    )
    session.add(evidence)
    session.flush()
    return evidence


def _orbital_snapshot_out(snapshot_meta: Dict[str, Any]) -> Dict[str, Any]:
    truth_raw = snapshot_meta.get("truth_status") or TruthStatus.STALE.value
    truth = TruthStatus(truth_raw) if not isinstance(truth_raw, TruthStatus) else truth_raw
    retrieved_at = snapshot_meta.get("retrieved_at")
    stale_days = int(snapshot_meta.get("stale_epoch_days") or tle_cache.STALE_EPOCH_DAYS)
    return {
        **snapshot_meta,
        "freshness": freshness_for(
            truth,
            retrieved_at=str(retrieved_at) if retrieved_at else None,
            stale_epoch_days=stale_days,
        ),
    }


def _satellite_resource_dict(sat: Satellite, snapshot_meta: Dict[str, Any]) -> Dict[str, Any]:
    truth_raw = snapshot_meta.get("truth_status") or TruthStatus.STALE.value
    truth = TruthStatus(truth_raw) if not isinstance(truth_raw, TruthStatus) else truth_raw
    retrieved_at = snapshot_meta.get("retrieved_at")
    snap_id = snapshot_meta.get("snapshot_id") or sat.snapshot_id
    source = f"CelesTrak TLE snapshot {snap_id}"
    return {
        "id": sat.id,
        "name": sat.name,
        "norad_id": int(sat.norad_id),
        "tle_epoch": provenanced(
            sat.tle_epoch,
            truth,
            source=source,
            retrieved_at=retrieved_at,
            effective_at=sat.tle_epoch,
            method="TLE epoch parse",
        ),
        "snapshot_id": sat.snapshot_id,
        "source": sat.source,
        "retrieved_at": sat.retrieved_at,
        "downlink_rate_mbps": provenanced(
            float(sat.downlink_rate_mbps),
            TruthStatus.PROVIDER_REPORTED,
            source="Public X-band specifications",
            explanation="Published downlink rate for fleet planning.",
        ),
        "resource_type": InfrastructureResourceType.SATELLITE.value,
        "access_level": AccessLevel.PUBLIC_INFORMATION.value,
        "truth_status": truth.value,
    }


def _ground_station_dict(station: GroundStation) -> Dict[str, Any]:
    meta = station.source_metadata or {}
    coord_status = TruthStatus(
        meta.get("coordinate_truth_status", TruthStatus.PROVIDER_REPORTED.value)
    )
    ops_status = TruthStatus(
        meta.get("ops_params_truth_status", TruthStatus.SIMULATED.value)
    )
    coord_source = meta.get("coordinate_note") or "Public ground-station registries"
    ops_source = meta.get("ops_params_note") or GS_COORDINATE_METADATA["ops_params_note"]
    return {
        "id": station.id,
        "name": station.name,
        "location": station.location,
        "provider": station.provider,
        "latitude": provenanced(
            float(station.latitude),
            coord_status,
            source=coord_source,
        ),
        "longitude": provenanced(
            float(station.longitude),
            coord_status,
            source=coord_source,
        ),
        "altitude_m": provenanced(
            float(station.altitude_m),
            coord_status,
            source=coord_source,
        ),
        "min_elevation_deg": provenanced(
            float(station.min_elevation_deg),
            coord_status,
            source=coord_source,
        ),
        "latency_minutes": provenanced(
            float(station.latency_minutes),
            ops_status,
            source=ops_source,
            explanation=EXPLANATION_SIMULATED,
        ),
        "downlink_mbps": provenanced(
            int(station.downlink_mbps),
            ops_status,
            source=ops_source,
            explanation=EXPLANATION_SIMULATED,
        ),
        "availability": provenanced(
            float(station.availability),
            ops_status,
            source=ops_source,
            explanation=EXPLANATION_SIMULATED,
        ),
        "resource_type": InfrastructureResourceType.GROUND_STATION.value,
        "access_level": station.access_level or AccessLevel.PUBLIC_INFORMATION.value,
        "source_metadata": meta,
        "coordinate_truth_status": coord_status.value,
        "ops_params_truth_status": ops_status.value,
        "truth_status": coord_status.value,
    }


def get_mission_infrastructure(
    session: Session,
    mission: Mission,
    *,
    record_evidence: bool = False,
) -> Dict[str, Any]:
    """Mission-scoped sats + public GS + orbital snapshot provenance."""
    satellites = select_satellites_for_mission(session, mission)
    snapshot_meta = tle_cache.metadata_from_db_satellites(
        list(session.scalars(select(Satellite)).all())
    )
    stations = session.scalars(select(GroundStation).order_by(GroundStation.id.asc())).all()

    if record_evidence:
        record_orbital_snapshot_evidence(
            session,
            mission_id=mission.id,
            snapshot_meta=snapshot_meta,
        )

    return {
        "mission_id": str(mission.id),
        "orbital_snapshot": _orbital_snapshot_out(snapshot_meta),
        "satellites": [_satellite_resource_dict(s, snapshot_meta) for s in satellites],
        "ground_stations": [_ground_station_dict(s) for s in stations],
    }


def upsert_infrastructure_resources(
    session: Session,
    *,
    snapshot: Dict[str, Any],
    ground_stations: Sequence[Dict[str, Any]],
) -> Dict[str, int]:
    """Seed mission-facing InfrastructureResource rows for the fleet + GS."""
    meta = tle_cache.get_orbital_snapshot_metadata(snapshot)
    truth = TruthStatus(meta["truth_status"])
    retrieved = None
    if meta.get("retrieved_at"):
        retrieved = tle_cache.parse_iso_utc(str(meta["retrieved_at"]))

    sat_count = 0
    for sat in snapshot.get("satellites") or []:
        external_id = sat["id"]
        row = session.scalars(
            select(InfrastructureResource).where(
                InfrastructureResource.provider_name == "nomos-fleet",
                InfrastructureResource.external_resource_id == external_id,
            )
        ).one_or_none()
        if row is None:
            row = InfrastructureResource(
                id=uuid.uuid4(),
                provider_name="nomos-fleet",
                resource_type=InfrastructureResourceType.SATELLITE.value,
                external_resource_id=external_id,
            )
            session.add(row)
        row.name = sat["name"]
        row.location = None
        row.capabilities = {
            "norad_id": sat["norad_id"],
            "downlink_rate_mbps": sat["downlink_rate_mbps"],
            "tle_epoch": sat["tle_epoch"],
        }
        row.constraints = {}
        row.pricing = None
        row.access_level = AccessLevel.PUBLIC_INFORMATION.value
        row.source_metadata = {
            "snapshot_id": meta["snapshot_id"],
            "source": meta["source"],
            "source_url": meta.get("source_url"),
            "tle_line1": sat["tle_line1"],
            "tle_line2": sat["tle_line2"],
        }
        row.truth_status = truth
        row.data_freshness_at = retrieved
        row.active = True
        sat_count += 1

    gs_count = 0
    for station in ground_stations:
        external_id = station["id"]
        provider = station.get("provider") or "unknown"
        row = session.scalars(
            select(InfrastructureResource).where(
                InfrastructureResource.provider_name == provider,
                InfrastructureResource.external_resource_id == external_id,
            )
        ).one_or_none()
        if row is None:
            row = InfrastructureResource(
                id=uuid.uuid4(),
                provider_name=provider,
                resource_type=InfrastructureResourceType.GROUND_STATION.value,
                external_resource_id=external_id,
            )
            session.add(row)
        lon = float(station["longitude"])
        lat = float(station["latitude"])
        row.name = station["name"]
        row.location = WKTElement(f"POINT({lon} {lat})", srid=4326)
        row.capabilities = {
            "min_elevation_deg": station.get("min_elevation_deg", 10.0),
            "downlink_mbps": station.get("downlink_mbps"),
            "altitude_m": station.get("altitude_m", 0),
        }
        row.constraints = {
            "latency_minutes": station.get("latency_minutes"),
            "availability": station.get("availability"),
        }
        row.pricing = None
        row.access_level = AccessLevel.PUBLIC_INFORMATION.value
        row.source_metadata = {
            **GS_COORDINATE_METADATA,
            "public_location_label": station.get("location"),
        }
        row.truth_status = TruthStatus.PROVIDER_REPORTED
        row.data_freshness_at = None
        row.active = True
        gs_count += 1

    session.flush()
    return {"satellites": sat_count, "ground_stations": gs_count}
