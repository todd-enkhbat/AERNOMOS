"""Phase B: mission data model — migration, ownership, share-link constraints."""

from __future__ import annotations

import hashlib
import os
import uuid
from datetime import datetime, timedelta, timezone

import pytest
from alembic import command
from alembic.config import Config as AlembicConfig
from geoalchemy2.elements import WKTElement
from sqlalchemy import create_engine, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.db.migrate import API_DIR
from app.db.mission_orm import (
    AnonymousSession,
    Mission,
    ShareLink,
)
from app.db.session import _normalize_url
from app.db.truth import TRUTH_STATUS_VALUES, TruthStatus

os.environ.setdefault(
    "DATABASE_URL", "postgresql://localhost:5433/orbital_cortex"
)
os.environ["REDIS_URL"] = "redis://127.0.0.1:1/0"
os.environ["RATE_LIMIT_ENABLED"] = "false"


MISSION_TABLES = (
    "anonymous_sessions",
    "missions",
    "mission_data_candidates",
    "infrastructure_resources",
    "mission_plans",
    "mission_plan_steps",
    "source_evidence",
    "share_links",
)

AOI_WKT = (
    "POLYGON((-74.3 40.3,-73.5 40.3,-73.5 41.0,-74.3 41.0,-74.3 40.3))"
)


def _alembic_config(database_url: str) -> AlembicConfig:
    config = AlembicConfig(str(API_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(API_DIR / "migrations"))
    config.set_main_option("sqlalchemy.url", _normalize_url(database_url))
    return config


def _database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL is not set")
    return url


def _token_hash(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine(_normalize_url(_database_url()), pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        engine.dispose()


def test_truth_status_vocabulary() -> None:
    assert TruthStatus.OBSERVED.value == "OBSERVED"
    assert set(TRUTH_STATUS_VALUES) == {
        "OBSERVED",
        "CALCULATED",
        "PROVIDER_REPORTED",
        "ESTIMATED",
        "SIMULATED",
        "STALE",
        "UNAVAILABLE",
    }


def test_mission_migration_up_and_down() -> None:
    database_url = _database_url()
    config = _alembic_config(database_url)
    engine = create_engine(_normalize_url(database_url), pool_pre_ping=True)

    command.upgrade(config, "head")
    with engine.connect() as conn:
        for table in MISSION_TABLES:
            exists = conn.execute(
                text("SELECT to_regclass(:name)"), {"name": f"public.{table}"}
            ).scalar()
            assert exists is not None, f"missing table {table}"
            assert str(exists).endswith(table)

        # Legacy demo path tables must still exist after the additive migration.
        for table in ("jobs", "scenes", "detections", "routing_decisions"):
            exists = conn.execute(
                text("SELECT to_regclass(:name)"), {"name": f"public.{table}"}
            ).scalar()
            assert exists is not None, f"legacy table missing: {table}"
            assert str(exists).endswith(table)

        gist = conn.execute(
            text(
                """
                SELECT indexname FROM pg_indexes
                WHERE tablename = 'missions' AND indexname = 'ix_missions_area_of_interest'
                """
            )
        ).scalar()
        assert gist == "ix_missions_area_of_interest"

    command.downgrade(config, "e1f2a3b4c5d6")
    with engine.connect() as conn:
        for table in MISSION_TABLES:
            exists = conn.execute(
                text("SELECT to_regclass(:name)"), {"name": f"public.{table}"}
            ).scalar()
            assert exists is None, f"table still present after downgrade: {table}"

        # Demo tables untouched by downgrade of mission revision.
        jobs = conn.execute(
            text("SELECT to_regclass('public.jobs')")
        ).scalar()
        assert jobs is not None
        assert str(jobs).endswith("jobs")

    command.upgrade(config, "head")
    engine.dispose()


def test_mission_ownership_isolated_by_session(db_session: Session) -> None:
    command.upgrade(_alembic_config(_database_url()), "head")

    now = _utcnow()
    session_a = AnonymousSession(
        id=uuid.uuid4(),
        session_token_hash=_token_hash("session-a-token"),
        expires_at=now + timedelta(days=7),
    )
    session_b = AnonymousSession(
        id=uuid.uuid4(),
        session_token_hash=_token_hash("session-b-token"),
        expires_at=now + timedelta(days=7),
    )
    db_session.add_all([session_a, session_b])
    db_session.flush()

    mission_a = Mission(
        id=uuid.uuid4(),
        anonymous_session_id=session_a.id,
        title="Session A mission",
        objective_type="ship_detection",
        status="draft",
        area_of_interest=WKTElement(AOI_WKT, srid=4326),
    )
    mission_b = Mission(
        id=uuid.uuid4(),
        anonymous_session_id=session_b.id,
        title="Session B mission",
        objective_type="ship_detection",
        status="draft",
        area_of_interest=WKTElement(AOI_WKT, srid=4326),
    )
    org_id = uuid.uuid4()
    mission_org = Mission(
        id=uuid.uuid4(),
        organization_id=org_id,
        title="Org mission",
        objective_type="crop_health",
        status="draft",
        area_of_interest=WKTElement(AOI_WKT, srid=4326),
    )
    db_session.add_all([mission_a, mission_b, mission_org])
    db_session.commit()

    owned_by_a = db_session.scalars(
        select(Mission).where(Mission.anonymous_session_id == session_a.id)
    ).all()
    assert {m.id for m in owned_by_a} == {mission_a.id}

    owned_by_b = db_session.scalars(
        select(Mission).where(Mission.anonymous_session_id == session_b.id)
    ).all()
    assert {m.id for m in owned_by_b} == {mission_b.id}

    owned_by_org = db_session.scalars(
        select(Mission).where(Mission.organization_id == org_id)
    ).all()
    assert {m.id for m in owned_by_org} == {mission_org.id}

    # Ownerless mission rejected by CHECK constraint.
    orphan = Mission(
        id=uuid.uuid4(),
        title="Orphan",
        objective_type="ship_detection",
        status="draft",
        area_of_interest=WKTElement(AOI_WKT, srid=4326),
    )
    db_session.add(orphan)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_share_link_model_constraints(db_session: Session) -> None:
    command.upgrade(_alembic_config(_database_url()), "head")

    now = _utcnow()
    anon = AnonymousSession(
        id=uuid.uuid4(),
        session_token_hash=_token_hash("share-session-token"),
        expires_at=now + timedelta(days=7),
    )
    db_session.add(anon)
    db_session.flush()

    mission = Mission(
        id=uuid.uuid4(),
        anonymous_session_id=anon.id,
        title="Shareable mission",
        objective_type="ship_detection",
        status="draft",
        area_of_interest=WKTElement(AOI_WKT, srid=4326),
    )
    db_session.add(mission)
    db_session.flush()

    token_hash = _token_hash("share-token-raw")
    link = ShareLink(
        id=uuid.uuid4(),
        mission_id=mission.id,
        token_hash=token_hash,
        permissions=["read"],
    )
    db_session.add(link)
    db_session.commit()

    # Lookup by token hash (Phase C will gate API access this way).
    found = db_session.scalars(
        select(ShareLink).where(
            ShareLink.token_hash == token_hash,
            ShareLink.revoked_at.is_(None),
        )
    ).one()
    assert found.mission_id == mission.id

    # Duplicate token hash rejected.
    duplicate = ShareLink(
        id=uuid.uuid4(),
        mission_id=mission.id,
        token_hash=token_hash,
        permissions=["read"],
    )
    db_session.add(duplicate)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # expires_at before created_at rejected.
    bad_expiry = ShareLink(
        id=uuid.uuid4(),
        mission_id=mission.id,
        token_hash=_token_hash("bad-expiry"),
        created_at=now,
        expires_at=now - timedelta(hours=1),
        permissions=["read"],
    )
    db_session.add(bad_expiry)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Revoked links are excluded from active lookup.
    found.revoked_at = _utcnow()
    db_session.commit()
    active = db_session.scalars(
        select(ShareLink).where(
            ShareLink.token_hash == token_hash,
            ShareLink.revoked_at.is_(None),
        )
    ).all()
    assert active == []


def test_legacy_jobs_table_still_writable(db_session: Session) -> None:
    """Additive mission migration must not break the demo Job path."""
    command.upgrade(_alembic_config(_database_url()), "head")

    job_id = f"job_{uuid.uuid4().hex[:12]}"
    now = _utcnow().isoformat().replace("+00:00", "Z")
    db_session.execute(
        text(
            """
            INSERT INTO jobs (
                id, schema_version, job_type, area_of_interest_json, sensor,
                priority, compute_preference, max_cost_usd, status,
                created_at, updated_at
            ) VALUES (
                :id, 1, 'ship_detection', CAST(:aoi AS jsonb), 'SAR',
                'fastest', 'orbital_if_available', 100.0, 'queued',
                :created_at, :updated_at
            )
            """
        ),
        {
            "id": job_id,
            "aoi": '{"type":"bbox","coordinates":[-74.3,40.3,-73.5,41.0]}',
            "created_at": now,
            "updated_at": now,
        },
    )
    db_session.commit()
    count = db_session.execute(
        text("SELECT count(*) FROM jobs WHERE id = :id"), {"id": job_id}
    ).scalar()
    assert count == 1
    db_session.execute(text("DELETE FROM jobs WHERE id = :id"), {"id": job_id})
    db_session.commit()
