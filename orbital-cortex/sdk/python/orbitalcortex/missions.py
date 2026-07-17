"""Mission-planner resource.

Customer-friendly wrapper over the private mission workflow. Inputs and outputs
are plain JSON-native dicts using **customer terminology** (mission, plan,
candidate, share link) — callers never touch ORM models or database rows.

    mission = client.missions.create(
        title="Harbor monitoring",
        objective_type="analyze_imagery",
        area_of_interest={"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]},
    )
    plan = client.missions.generate_plan(mission["id"])
    report = client.missions.export_pdf(mission["id"])
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence

from orbitalcortex.exceptions import NoFeasiblePlan, StaleOrbitalData

if TYPE_CHECKING:
    from orbitalcortex.client import Client

Json = Dict[str, Any]


class MissionsResource:
    def __init__(self, client: "Client") -> None:
        self._client = client

    # -- creation / retrieval ------------------------------------------------ #

    def create(
        self,
        *,
        title: str,
        objective_type: str,
        area_of_interest: Json,
        status: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        deadline: Optional[str] = None,
        max_cost_usd: Optional[float] = None,
        max_data_volume_mb: Optional[float] = None,
        preferred_compute_location: Optional[str] = None,
        allowed_regions: Optional[Sequence[Any]] = None,
        data_source_preference: Optional[Sequence[Any]] = None,
        notes: Optional[str] = None,
        organization_name: Optional[str] = None,
        use_case: Optional[str] = None,
        data_residency: Optional[str] = None,
    ) -> Json:
        """Create a private mission for the current anonymous session.

        Ensures a private session exists first (no login required). Raises
        :class:`InvalidGeographicInput` if the area of interest is rejected.
        """
        self._client.ensure_session()
        body: Json = {
            "title": title,
            "objective_type": objective_type,
            "area_of_interest": area_of_interest,
        }
        optional = {
            "status": status,
            "start_time": start_time,
            "end_time": end_time,
            "deadline": deadline,
            "max_cost_usd": max_cost_usd,
            "max_data_volume_mb": max_data_volume_mb,
            "preferred_compute_location": preferred_compute_location,
            "allowed_regions": list(allowed_regions) if allowed_regions else None,
            "data_source_preference": (
                list(data_source_preference) if data_source_preference else None
            ),
            "notes": notes,
            "organization_name": organization_name,
            "use_case": use_case,
            "data_residency": data_residency,
        }
        body.update({k: v for k, v in optional.items() if v is not None})
        response = self._client._request("POST", "/v1/missions", json_body=body)
        return response["mission"]

    def retrieve(self, mission_id: str, *, share_token: Optional[str] = None) -> Json:
        """Read a mission by id (owner session, or a valid share token)."""
        path = f"/v1/missions/{mission_id}"
        headers = {"X-Nomos-Share-Token": share_token} if share_token else None
        response = self._client._request("GET", path, extra_headers=headers)
        return response["mission"]

    def list(self) -> List[Json]:
        """List missions owned by the current private session."""
        self._client.ensure_session()
        response = self._client._request("GET", "/v1/missions")
        return response.get("missions", [])

    def list_examples(self) -> List[Json]:
        """List curated public example missions (no session required)."""
        response = self._client._request("GET", "/v1/missions/examples")
        return response.get("missions", [])

    # -- catalog discovery --------------------------------------------------- #

    def discover(
        self,
        mission_id: str,
        *,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        collections: Optional[Sequence[str]] = None,
        limit: Optional[int] = None,
    ) -> List[Json]:
        """Search real public catalogs and persist candidate scenes.

        Raises :class:`NoCatalogData` when the upstream collection is not found,
        or :class:`UpstreamProviderUnavailable` when the catalog is down or
        rate-limited.
        """
        body: Json = {}
        if start_time is not None:
            body["start_time"] = start_time
        if end_time is not None:
            body["end_time"] = end_time
        if collections is not None:
            body["collections"] = list(collections)
        if limit is not None:
            body["limit"] = limit
        response = self._client._request(
            "POST",
            f"/v1/missions/{mission_id}/discover",
            json_body=body or None,
        )
        return response.get("candidates", [])

    def candidates(self, mission_id: str) -> List[Json]:
        """List persisted catalog candidates for a mission."""
        response = self._client._request(
            "GET", f"/v1/missions/{mission_id}/candidates"
        )
        return response.get("candidates", [])

    def infrastructure(
        self, mission_id: str, *, raise_on_stale: bool = False
    ) -> Json:
        """Mission-relevant satellites, ground stations, and orbital snapshot.

        With ``raise_on_stale=True``, raises :class:`StaleOrbitalData` when the
        orbital snapshot truth status is ``STALE`` (e.g. the live TLE source was
        unreachable and a pinned snapshot was used).
        """
        response = self._client._request(
            "GET", f"/v1/missions/{mission_id}/infrastructure"
        )
        snapshot = response.get("orbital_snapshot", {}) or {}
        if raise_on_stale and snapshot.get("truth_status") == "STALE":
            raise StaleOrbitalData(
                "Orbital data is stale: "
                f"{snapshot.get('freshness') or 'epoch older than freshness window'}.",
                response={"orbital_snapshot": snapshot},
                age_hours=_snapshot_age_hours(snapshot),
            )
        return response

    # -- planning ------------------------------------------------------------ #

    def generate_plan(self, mission_id: str, *, require_feasible: bool = True) -> Json:
        """Generate source-backed plans and return the recommended plan.

        Raises :class:`NoFeasiblePlan` when ``require_feasible`` is true and the
        planner recommends no feasible plan (all candidates were rejected or
        conditional).
        """
        response = self._client._request(
            "POST", f"/v1/missions/{mission_id}/plans"
        )
        plans = response.get("plans", [])
        recommended_id = response.get("recommended_plan_id")
        recommended = next(
            (p for p in plans if p.get("id") == recommended_id),
            None,
        )
        if recommended is None:
            recommended = next(
                (p for p in plans if p.get("recommended")),
                None,
            )
        if recommended is None:
            if require_feasible:
                raise NoFeasiblePlan(
                    "The planner produced no feasible recommended plan for this "
                    "mission. Inspect list_plans() for rejection reasons.",
                    status_code=201,
                    code="no_feasible_plan",
                    response=response,
                )
            recommended = plans[0] if plans else {}
        return recommended

    def list_plans(self, mission_id: str) -> List[Json]:
        """List all generated plans for a mission."""
        response = self._client._request(
            "GET", f"/v1/missions/{mission_id}/plans"
        )
        return response.get("plans", [])

    def get_plan(self, mission_id: str, plan_id: str) -> Json:
        """Read a single plan with steps and source evidence."""
        response = self._client._request(
            "GET", f"/v1/missions/{mission_id}/plans/{plan_id}"
        )
        return response["plan"]

    # -- exports / sharing --------------------------------------------------- #

    def export_pdf(self, mission_id: str) -> Json:
        """Generate a PDF mission brief and return the export record.

        The returned dict includes ``status`` and, when ready, a
        ``download_url``.
        """
        response = self._client._request(
            "POST", f"/v1/missions/{mission_id}/exports/pdf"
        )
        return response["export"]

    def latest_pdf(self, mission_id: str) -> Json:
        """Latest PDF export status / signed download URL."""
        response = self._client._request(
            "GET", f"/v1/missions/{mission_id}/exports/pdf"
        )
        return response["export"]

    def export_json(self, mission_id: str) -> Json:
        """Download the versioned mission brief JSON document."""
        return self._client._request(
            "GET", f"/v1/missions/{mission_id}/exports/json"
        )

    def create_share_link(
        self,
        mission_id: str,
        *,
        expires_at: Optional[str] = None,
        permissions: Optional[Sequence[str]] = None,
    ) -> Json:
        """Create a private share link. The raw token is returned once."""
        body: Json = {"permissions": list(permissions) if permissions else ["read"]}
        if expires_at is not None:
            body["expires_at"] = expires_at
        response = self._client._request(
            "POST", f"/v1/missions/{mission_id}/share-links", json_body=body
        )
        return response["share_link"]


def _snapshot_age_hours(snapshot: Json) -> Optional[float]:
    """Best-effort age (hours) of a STALE orbital snapshot from retrieved_at."""
    from datetime import datetime, timezone

    retrieved = snapshot.get("retrieved_at")
    if not retrieved:
        return None
    try:
        ts = datetime.fromisoformat(str(retrieved).replace("Z", "+00:00"))
    except ValueError:
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    delta = datetime.now(timezone.utc) - ts
    return round(delta.total_seconds() / 3600.0, 2)
