"""Phase Q: Python SDK missions namespace, typed errors, and doc integrity.

Runs the exact three-line SDK example end to end against the real API (in-process
FastAPI TestClient acting as the local API instance), triggers three typed error
conditions against the real API, and asserts the docs/registry stay in sync and
every Phase Q doc is linked from AGENTS.md.
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import pytest

os.environ.setdefault("DATABASE_URL", "postgresql://localhost:5433/orbital_cortex")
os.environ["REDIS_URL"] = "redis://127.0.0.1:1/0"
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ.setdefault("APP_ENV", "development")

# Make the SDK importable without installing it.
_REPO = Path(__file__).resolve().parents[4]
_SDK_PATH = _REPO / "orbital-cortex" / "sdk" / "python"
if str(_SDK_PATH) not in sys.path:
    sys.path.insert(0, str(_SDK_PATH))

from fastapi.testclient import TestClient  # noqa: E402
from geoalchemy2.elements import WKTElement  # noqa: E402
from orbitalcortex import (  # noqa: E402
    Client,
    ExpiredShareLink,
    InvalidGeographicInput,
    UnauthorizedMission,
)

from app.db import SessionLocal, get_engine  # noqa: E402
from app.db.mission_orm import MissionDataCandidate  # noqa: E402
from app.db.truth import TruthStatus  # noqa: E402
from app.main import app, run_migrations  # noqa: E402

# New York Harbor bbox reused across the suite.
NY_HARBOR = {"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]}
NY_HARBOR_WKT = "POLYGON((-74.3 40.3, -73.5 40.3, -73.5 41.0, -74.3 41.0, -74.3 40.3))"


class _TestClientTransport:
    """Bridge the SDK Transport protocol to a FastAPI TestClient.

    The TestClient keeps its own cookie jar, so the private session cookie from
    POST /v1/sessions persists across mission requests exactly as it would over
    real HTTP. Errors are mapped through the SDK's own error_from_response so the
    typed-exception behavior under test is the real production behavior.
    """

    def __init__(self, test_client: TestClient) -> None:
        self._client = test_client

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Dict[str, str],
        timeout: float,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        from orbitalcortex.exceptions import error_from_response

        parsed = urlparse(url)
        path = parsed.path + (f"?{parsed.query}" if parsed.query else "")
        response = self._client.request(
            method, path, headers=headers, json=json_body
        )
        if response.status_code >= 400:
            payload = response.json() if response.content else {}
            error = payload.get("error", {}) if isinstance(payload, dict) else {}
            raise error_from_response(
                status_code=response.status_code,
                code=error.get("code", "api_error"),
                message=error.get("message", ""),
                response=payload if isinstance(payload, dict) else {},
            )
        if not response.content:
            return {}
        return response.json()


@pytest.fixture()
def api() -> TestClient:
    run_migrations()
    with TestClient(app) as client:
        yield client


def _sdk_client() -> Client:
    """A fresh SDK client bound to its own session/cookie jar."""
    return Client(base_url="http://testserver", transport=_TestClientTransport(TestClient(app)))


def _seed_candidate_covering(mission_id: str) -> None:
    """Insert a SIMULATED candidate scene covering the mission AOI so the planner
    can recommend a feasible existing-imagery -> cloud plan (mirrors the curated
    example seed; this is test setup, not SDK patching)."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    session = SessionLocal(bind=get_engine())
    try:
        session.add(
            MissionDataCandidate(
                id=uuid.uuid4(),
                mission_id=uuid.UUID(mission_id),
                source_provider="nomos-test-fixture",
                collection="sentinel-1-grd",
                external_item_id=f"test-scene-{mission_id}",
                acquisition_time=now,
                footprint=WKTElement(NY_HARBOR_WKT, srid=4326),
                asset_metadata={"test_fixture": True},
                estimated_size_bytes=500 * 1024 * 1024,
                source_url=None,
                source_timestamp=now,
                truth_status=TruthStatus.SIMULATED,
                created_at=now,
            )
        )
        session.commit()
    finally:
        session.close()


def test_sdk_three_line_example_end_to_end(api: TestClient) -> None:
    """The exact three-line example completes without manual patching."""
    client = _sdk_client()

    mission = client.missions.create(
        title="Harbor monitoring",
        objective_type="analyze_imagery",
        area_of_interest=NY_HARBOR,
    )
    assert mission["id"]
    # Customer terminology only — no ORM/model field names leak out.
    assert "anonymous_session_id" in mission  # customer-safe id, not a raw row

    _seed_candidate_covering(mission["id"])

    plan = client.missions.generate_plan(mission["id"])
    assert plan["id"]
    assert plan.get("recommended") is True

    report = client.missions.export_pdf(mission["id"])
    assert report["id"]
    assert report["status"] in {"ready", "queued", "failed"}
    print(
        "SDK example OK -> mission",
        mission["id"],
        "| plan",
        plan["id"],
        "| pdf status",
        report["status"],
        "| download_url set:",
        bool(report.get("download_url")),
    )


def test_error_mapping_unauthorized_mission(api: TestClient) -> None:
    owner = _sdk_client()
    mission = owner.missions.create(
        title="Private A",
        objective_type="analyze_imagery",
        area_of_interest=NY_HARBOR,
    )

    stranger = _sdk_client()  # different session / cookie jar
    stranger.ensure_session()  # has a valid session, but does not own the mission
    with pytest.raises(UnauthorizedMission) as excinfo:
        stranger.missions.retrieve(mission["id"])
    assert excinfo.value.status_code == 403
    assert excinfo.value.code == "mission_forbidden"
    print("UnauthorizedMission ->", repr(excinfo.value))


def test_error_mapping_expired_share_link(api: TestClient) -> None:
    owner = _sdk_client()
    mission = owner.missions.create(
        title="Share me",
        objective_type="analyze_imagery",
        area_of_interest=NY_HARBOR,
    )
    link = owner.missions.create_share_link(mission["id"])
    token = link["token"]
    assert token

    # Revoke it, then a stranger tries to use the (now invalid) token.
    owner._request(
        "POST",
        f"/v1/missions/{mission['id']}/share-links/{link['id']}/revoke",
    )

    stranger = _sdk_client()
    with pytest.raises(ExpiredShareLink) as excinfo:
        stranger.missions.retrieve(mission["id"], share_token=token)
    assert excinfo.value.status_code == 403
    assert excinfo.value.code == "share_token_invalid"
    print("ExpiredShareLink ->", repr(excinfo.value))


def test_error_mapping_invalid_geographic_input(api: TestClient) -> None:
    client = _sdk_client()
    # Point-like / zero-area bbox is invalid geographic input.
    bad_aoi = {"type": "bbox", "coordinates": [-74.0, 40.0, -74.0, 40.0]}
    with pytest.raises(InvalidGeographicInput) as excinfo:
        client.missions.create(
            title="Bad geo",
            objective_type="analyze_imagery",
            area_of_interest=bad_aoi,
        )
    assert excinfo.value.status_code == 422
    assert excinfo.value.code == "validation_error"
    print("InvalidGeographicInput ->", repr(excinfo.value))


def test_data_sources_doc_drift_check() -> None:
    """The doc-drift script exits 0 (data-sources.md matches the registry)."""
    from app.scripts import check_data_sources_drift

    assert check_data_sources_drift.main() == 0


def test_all_phase_q_docs_linked_from_agents() -> None:
    agents = (_REPO / "AGENTS.md").read_text(encoding="utf-8")
    docs = [
        "mission-planner-overview.md",
        "data-sources.md",
        "truth-statuses.md",
        "planning-engine.md",
        "privacy-model.md",
        "provider-integrations.md",
        "demo-limitations.md",
        "accelerator-demo-script.md",
    ]
    missing = [d for d in docs if d not in agents]
    assert not missing, f"docs not linked from AGENTS.md: {missing}"
