"""Seed Postgres reference data: compute nodes, ground stations, satellites.

Also the demo-reset CLI (F4):

    python -m app.seed            # reseed reference data only
    python -m app.seed --reset    # additionally wipe all job data first

With APP_ENV=production, --reset refuses to run unless --force is passed,
so a fat-fingered local command can't wipe the hosted demo.
"""

from __future__ import annotations

import argparse
import json
from typing import Any, Dict, Iterable, List, Optional

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.orm import ComputeNode, GroundStation, Job, Satellite
from app.db.session import REPO_ROOT
from app.db.truth import AccessLevel
from app.services import tle_cache
from app.services.mission_infrastructure import (
    GS_COORDINATE_METADATA,
    upsert_infrastructure_resources,
)
from app.services.provider_registry import ingest_providers_from_config

SIMULATOR_DIR = REPO_ROOT / "simulator"


def _read_json_file(name: str) -> List[Dict[str, Any]]:
    path = SIMULATOR_DIR / name
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON list")
    return data


def apply_orbital_snapshot(session: Session, snapshot: Dict[str, Any]) -> None:
    """Persist annotated TLE snapshot onto Satellite rows + InfrastructureResource."""
    meta = tle_cache.get_orbital_snapshot_metadata(snapshot)
    for sat in snapshot["satellites"]:
        record = session.get(Satellite, sat["id"])
        if record is None:
            record = Satellite(id=sat["id"])
            session.add(record)
        record.name = sat["name"]
        record.norad_id = int(sat["norad_id"])
        record.tle_line1 = sat["tle_line1"]
        record.tle_line2 = sat["tle_line2"]
        record.tle_epoch = sat["tle_epoch"]
        record.source = meta["source"]
        record.snapshot_id = meta["snapshot_id"]
        record.downlink_rate_mbps = float(sat["downlink_rate_mbps"])
        record.retrieved_at = meta.get("retrieved_at")
    session.flush()


def seed_database(session: Session) -> Dict[str, int]:
    ground_stations = _read_json_file("ground_stations.json")
    compute_nodes = _read_json_file("sample_nodes.json")
    snapshot = tle_cache.resolve_orbital_snapshot(prefer_live=get_settings().live_tle)

    _seed_ground_stations(session, ground_stations)
    apply_orbital_snapshot(session, snapshot)
    # Satellites must exist before compute-node rows reference them (FK).
    session.flush()
    _seed_compute_nodes(session, compute_nodes)
    infra_counts = upsert_infrastructure_resources(
        session, snapshot=snapshot, ground_stations=ground_stations
    )
    provider_registry = ingest_providers_from_config(session)
    from app.core.missions import ensure_example_missions
    from app.core.storage import ensure_curated_job_examples

    example_missions = ensure_example_missions(session)
    example_jobs = ensure_curated_job_examples(session, limit=3)
    example_plans = ensure_example_plans(session)
    from app.execution.fixtures import ensure_execution_fixtures

    ensure_execution_fixtures()
    session.commit()
    return {
        "compute_nodes": len(compute_nodes),
        "ground_stations": len(ground_stations),
        "satellites": len(snapshot["satellites"]),
        "infrastructure_satellites": infra_counts["satellites"],
        "infrastructure_ground_stations": infra_counts["ground_stations"],
        "infrastructure_providers": provider_registry["ingested"],
        "example_missions": example_missions,
        "example_jobs": example_jobs,
        "example_plans": example_plans,
    }


def ensure_example_plans(session: Session) -> int:
    """Give each curated example mission a persisted, read-only plan set.

    Each example ships with one authored reference scene labeled SIMULATED so
    the planner can produce a feasible recommended brief with an honest truth
    mix (SIMULATED scene, CALCULATED orbital math, ESTIMATED transfers,
    UNAVAILABLE cost/tasking). Idempotent: the SIMULATED candidate is keyed by a
    stable UUID and plans are generated only when a mission has none, so reboots
    and demo resets never duplicate or overwrite curated plans.
    """
    from datetime import timedelta

    from geoalchemy2.elements import WKTElement

    from app.core.missions import (
        CURATED_EXAMPLE_MISSIONS,
        example_candidate_id,
        example_mission_id,
        utc_now,
    )
    from app.db.mission_orm import Mission, MissionDataCandidate, MissionPlan
    from app.db.truth import TruthStatus
    from app.planner.engine import generate_plans_for_mission

    now = utc_now()
    generated = 0
    for spec in CURATED_EXAMPLE_MISSIONS:
        slug = str(spec["slug"])
        mission_id = example_mission_id(slug)
        mission = session.get(Mission, mission_id)
        if mission is None:
            continue

        candidate_id = example_candidate_id(slug)
        if session.get(MissionDataCandidate, candidate_id) is None:
            session.add(
                MissionDataCandidate(
                    id=candidate_id,
                    mission_id=mission_id,
                    source_provider="nomos-curated-example",
                    collection=str(spec.get("collection") or "sentinel-1-grd"),
                    external_item_id=f"example-scene-{slug}",
                    acquisition_time=now - timedelta(days=3),
                    footprint=WKTElement(str(spec["wkt"]), srid=4326),
                    asset_metadata={
                        "curated_example": True,
                        "note": (
                            "Authored reference scene for a curated public example. "
                            "Not a live catalog discovery result."
                        ),
                    },
                    estimated_size_bytes=900 * 1024 * 1024,
                    source_url=None,
                    source_timestamp=now,
                    truth_status=TruthStatus.SIMULATED,
                    created_at=now,
                )
            )
            session.flush()

        has_plan = (
            session.scalar(
                select(func.count())
                .select_from(MissionPlan)
                .where(MissionPlan.mission_id == mission_id)
            )
            or 0
        )
        if not has_plan:
            generate_plans_for_mission(session, mission, now_utc=now)
            generated += 1

    session.flush()
    return generated


def _seed_compute_nodes(
    session: Session,
    nodes: Iterable[Dict[str, Any]],
) -> None:
    for node in nodes:
        record = session.get(ComputeNode, node["id"])
        if record is None:
            record = ComputeNode(id=node["id"])
            session.add(record)
        record.name = node["name"]
        record.type = node["type"]
        record.location = node["location"]
        record.orbit = node.get("orbit")
        record.gpu_class = node["gpu_class"]
        record.supported_models_json = node["supported_models"]
        record.storage_gb = int(node["storage_gb"])
        record.downlink_mbps = int(node["downlink_mbps"])
        record.power_state = node["power_state"]
        record.availability = float(node["availability"])
        record.compliance_tags_json = node["compliance_tags"]
        record.base_cost_usd = float(node["base_cost_usd"])
        record.latency_minutes = float(node["latency_minutes"])
        record.satellite_id = node.get("satellite_id")


def reset_demo_data(session: Session) -> int:
    """Delete visitor jobs only; preserve curated example jobs.

    Events, results, routing decisions, scenes, and detections cascade via
    their FKs. Reference data and ``is_example`` missions are left in place;
    ``seed_database`` upserts curated example missions afterward.
    """
    count = (
        session.scalar(
            select(func.count()).select_from(Job).where(Job.is_example.is_(False))
        )
        or 0
    )
    session.execute(delete(Job).where(Job.is_example.is_(False)))
    session.commit()
    return int(count)


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        prog="python -m app.seed",
        description="Reseed reference data; optionally reset demo job data.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help=(
            "wipe visitor job data (jobs, events, results, routing, scenes); "
            "preserves curated is_example jobs and missions"
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="required for --reset when APP_ENV=production",
    )
    args = parser.parse_args(argv)

    settings = get_settings()
    if args.reset and settings.app_env == "production" and not args.force:
        raise SystemExit(
            "Refusing --reset with APP_ENV=production. Pass --force if this "
            "really is the disposable demo environment."
        )

    from app.db import SessionLocal, get_engine
    from app.db.migrate import run_migrations

    run_migrations()
    session = SessionLocal(bind=get_engine())
    try:
        jobs_deleted = reset_demo_data(session) if args.reset else 0
        counts = seed_database(session)
    finally:
        session.close()
    print(json.dumps({"jobs_deleted": jobs_deleted, "seeded": counts}))


def _seed_ground_stations(
    session: Session,
    ground_stations: Iterable[Dict[str, Any]],
) -> None:
    for station in ground_stations:
        record = session.get(GroundStation, station["id"])
        if record is None:
            record = GroundStation(id=station["id"])
            session.add(record)
        record.name = station["name"]
        record.location = station["location"]
        record.provider = station.get("provider", "")
        record.latitude = float(station["latitude"])
        record.longitude = float(station["longitude"])
        record.altitude_m = float(station.get("altitude_m", 0))
        record.min_elevation_deg = float(station.get("min_elevation_deg", 10.0))
        record.latency_minutes = float(station["latency_minutes"])
        record.downlink_mbps = int(station["downlink_mbps"])
        record.availability = float(station["availability"])
        record.access_level = AccessLevel.PUBLIC_INFORMATION.value
        record.source_metadata = dict(GS_COORDINATE_METADATA)


if __name__ == "__main__":
    main()
