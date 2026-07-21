"""Phase H: orbital provenance, staleness, and mission-specific infrastructure."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from unittest.mock import patch

from fastapi.testclient import TestClient
from geoalchemy2.elements import WKTElement
from sqlalchemy import delete, select

from app.db import SessionLocal, get_engine
from app.db.mission_orm import Mission, MissionDataCandidate, SourceEvidence
from app.db.orm import ContactWindow, GroundStation, Satellite
from app.db.truth import AccessLevel, TruthStatus
from app.main import app, run_migrations
from app.services import tle_cache
from app.services.contact_windows import compute_passes, precompute_windows
from app.services.mission_infrastructure import (
    record_orbital_snapshot_evidence,
    satellite_ids_for_collections,
    select_satellites_for_mission,
)


def _utcnow() -> datetime:
    return datetime(2026, 7, 16, 12, 0, 0, tzinfo=timezone.utc)


def test_stale_detection_when_epoch_older_than_threshold():
    now = _utcnow()
    old_epoch = now - timedelta(days=tle_cache.STALE_EPOCH_DAYS + 1)
    status = tle_cache.classify_orbital_truth_status(
        source_id=tle_cache.SOURCE_CELESTRAK_GP,
        epochs=[old_epoch],
        now=now,
    )
    assert status == TruthStatus.STALE


def test_fresh_live_celestrak_is_provider_reported():
    now = _utcnow()
    fresh = now - timedelta(days=1)
    status = tle_cache.classify_orbital_truth_status(
        source_id=tle_cache.SOURCE_CELESTRAK_GP,
        epochs=[fresh],
        now=now,
    )
    assert status == TruthStatus.PROVIDER_REPORTED


def test_pinned_fallback_labeled_stale():
    now = _utcnow()
    status = tle_cache.classify_orbital_truth_status(
        source_id=tle_cache.SOURCE_PINNED_SNAPSHOT,
        epochs=[now - timedelta(days=1)],
        now=now,
        used_pinned_fallback=True,
    )
    assert status == TruthStatus.STALE


def test_resolve_falls_back_to_pinned_on_live_failure():
    def _boom() -> Dict[str, Any]:
        raise RuntimeError("celestrak unavailable")

    with patch.object(tle_cache, "fetch_live_snapshot", side_effect=_boom):
        snap = tle_cache.resolve_orbital_snapshot(prefer_live=True, now=_utcnow())

    assert snap["used_pinned_fallback"] is True
    assert snap["source_id"] == tle_cache.SOURCE_PINNED_SNAPSHOT
    assert snap["truth_status"] == TruthStatus.STALE.value
    assert snap["snapshot_id"].startswith("celestrak-")
    meta = tle_cache.get_orbital_snapshot_metadata(snap, now=_utcnow())
    assert meta["source"] == tle_cache.SOURCE_PINNED_SNAPSHOT
    assert meta["truth_status"] == TruthStatus.STALE.value
    assert meta["used_pinned_fallback"] is True


def test_contact_window_reproducible_for_same_snapshot():
    pinned = tle_cache.load_snapshot()
    s1a = next(s for s in pinned["satellites"] if s["id"] == "sat_sentinel_1a")
    epoch = datetime.fromisoformat(s1a["tle_epoch"])
    first = compute_passes(
        s1a["tle_line1"],
        s1a["tle_line2"],
        s1a["name"],
        78.2297,
        15.3975,
        450.0,
        10.0,
        epoch,
        24.0,
    )
    second = compute_passes(
        s1a["tle_line1"],
        s1a["tle_line2"],
        s1a["name"],
        78.2297,
        15.3975,
        450.0,
        10.0,
        epoch,
        24.0,
    )
    assert first == second
    assert first


def test_mission_specific_selection_excludes_unrelated_sats():
    s1_ids = satellite_ids_for_collections(["sentinel-1-grd"])
    assert s1_ids == {"sat_sentinel_1a", "sat_sentinel_1c"}
    assert "sat_capella_14" not in s1_ids
    assert "sat_iceye_x2" not in s1_ids

    capella_ids = satellite_ids_for_collections(["capella-slc"])
    assert "sat_capella_14" in capella_ids
    assert "sat_sentinel_1a" not in capella_ids


def test_precompute_stores_tle_snapshot_id_and_gs_metadata():
    run_migrations()
    session = SessionLocal(bind=get_engine())
    try:
        from app.seed import seed_database

        seed_database(session)
        sats = session.scalars(select(Satellite)).all()
        assert sats
        snapshot_id = sats[0].snapshot_id
        # Clear windows then recompute for a fixed start near TLE epoch.
        session.execute(delete(ContactWindow))
        session.flush()
        epoch = datetime.fromisoformat(sats[0].tle_epoch)
        created = precompute_windows(session, start_utc=epoch, horizon_hours=24.0)
        session.commit()
        assert created > 0
        windows = session.scalars(select(ContactWindow).limit(5)).all()
        assert windows
        for window in windows:
            assert window.tle_snapshot_id == snapshot_id

        stations = session.scalars(select(GroundStation)).all()
        assert stations
        for station in stations:
            assert station.access_level == AccessLevel.PUBLIC_INFORMATION.value
            assert station.source_metadata.get("ops_params_truth_status") == (
                TruthStatus.SIMULATED.value
            )
    finally:
        session.close()


def test_mission_infrastructure_endpoint_and_evidence_helper():
    run_migrations()
    with TestClient(app) as client:
        created_session = client.post("/v1/sessions")
        assert created_session.status_code in (200, 201)

        mission_resp = client.post(
            "/v1/missions",
            json={
                "title": "Harbor SAR plan",
                "objective_type": "ship_detection",
                "area_of_interest": {
                    "type": "bbox",
                    "coordinates": [-74.3, 40.3, -73.5, 41.0],
                },
                "data_source_preference": ["sentinel-1-grd"],
            },
        )
        assert mission_resp.status_code == 201
        mission_id = mission_resp.json()["mission"]["id"]

        # Prefer candidate-driven selection: insert a Sentinel-1 candidate.
        db = SessionLocal(bind=get_engine())
        try:
            mission = db.get(Mission, mission_id)
            assert mission is not None
            db.add(
                MissionDataCandidate(
                    mission_id=mission.id,
                    source_provider="microsoft-planetary-computer",
                    collection="sentinel-1-grd",
                    external_item_id="test-s1-item",
                    acquisition_time=_utcnow(),
                    footprint=WKTElement(
                        "POLYGON((-74.1 40.6, -73.9 40.6, -73.9 40.8, -74.1 40.8, -74.1 40.6))",
                        srid=4326,
                    ),
                    asset_metadata={},
                    estimated_size_bytes=1_000_000,
                    source_url="https://example.test/item",
                    source_timestamp=_utcnow(),
                    truth_status=TruthStatus.PROVIDER_REPORTED,
                )
            )
            db.commit()

            selected = select_satellites_for_mission(db, mission)
            ids = {s.id for s in selected}
            assert ids == {"sat_sentinel_1a", "sat_sentinel_1c"}
            assert "sat_iceye_x2" not in ids

            meta = tle_cache.metadata_from_db_satellites(
                list(db.scalars(select(Satellite)).all())
            )
            evidence = record_orbital_snapshot_evidence(
                db, mission_id=mission.id, snapshot_meta=meta
            )
            db.commit()
            assert evidence.truth_status in (TruthStatus.STALE, TruthStatus.PROVIDER_REPORTED)
            assert evidence.source_type == "orbital_tle_snapshot"
            stored = db.get(SourceEvidence, evidence.id)
            assert stored is not None
        finally:
            db.close()

        infra = client.get(f"/v1/missions/{mission_id}/infrastructure")
        assert infra.status_code == 200
        body = infra.json()
        assert body["mission_id"] == mission_id
        assert body["orbital_snapshot"]["snapshot_id"]
        assert body["orbital_snapshot"]["truth_status"] in {
            TruthStatus.STALE.value,
            TruthStatus.PROVIDER_REPORTED.value,
            TruthStatus.UNAVAILABLE.value,
        }
        assert body["orbital_snapshot"]["freshness"] in {"fresh", "stale", "unknown"}
        sat_ids = {s["id"] for s in body["satellites"]}
        assert sat_ids == {"sat_sentinel_1a", "sat_sentinel_1c"}
        assert body["satellites"][0]["tle_epoch"]["truth_status"] in {
            TruthStatus.STALE.value,
            TruthStatus.PROVIDER_REPORTED.value,
        }
        gs = body["ground_stations"][0]
        assert gs["latitude"]["truth_status"] == "PROVIDER_REPORTED"
        assert gs["latency_minutes"]["truth_status"] == "SIMULATED"
        assert all(gs["access_level"] == "public_information" for gs in body["ground_stations"])
        assert body["ground_stations"]


def test_get_orbital_snapshot_metadata_shape():
    meta = tle_cache.get_orbital_snapshot_metadata(now=_utcnow())
    assert set(meta) >= {
        "snapshot_id",
        "source",
        "epochs",
        "truth_status",
        "retrieved_at",
    }
    assert meta["stale_epoch_days"] == tle_cache.STALE_EPOCH_DAYS
