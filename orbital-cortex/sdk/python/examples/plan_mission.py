"""Plan a private mission end to end with the Nomos Orbital SDK.

Customer terminology only — no ORM/model names. Mirrors the three-line example
from the docs:

    mission = client.missions.create(...)
    plan = client.missions.generate_plan(mission["id"])
    report = client.missions.export_pdf(mission["id"])
"""

from __future__ import annotations

import json

from orbitalcortex import (
    Client,
    NoCatalogData,
    NoFeasiblePlan,
    UnauthorizedMission,
    UpstreamProviderUnavailable,
)


def main() -> None:
    client = Client(base_url="http://127.0.0.1:8000")

    # A private anonymous session is created automatically (no login).
    mission = client.missions.create(
        title="Harbor monitoring",
        objective_type="analyze_imagery",
        area_of_interest={"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]},
        notes="Exploratory: do not submit proprietary information in the demo.",
    )
    print("Mission:", mission["id"])

    try:
        candidates = client.missions.discover(mission["id"])
        print(f"Found {len(candidates)} real catalog candidate(s).")
    except NoCatalogData:
        print("No public catalog data for this area/time.")
    except UpstreamProviderUnavailable as exc:
        print(f"Catalog provider unavailable: {exc.provider_name}")

    try:
        plan = client.missions.generate_plan(mission["id"])
        print("Recommended plan:", plan["id"], "-", plan.get("summary"))
    except NoFeasiblePlan:
        print("No feasible plan; inspecting rejection reasons instead.")
        for p in client.missions.list_plans(mission["id"]):
            print(" -", p.get("feasibility_status"), p.get("summary"))
        return

    report = client.missions.export_pdf(mission["id"])
    print("PDF export status:", report["status"])
    if report.get("download_url"):
        print("Download:", report["download_url"])

    document = client.missions.export_json(mission["id"])
    print("JSON brief schema_version:", document.get("schema_version"))
    print(json.dumps({"mission_id": mission["id"]}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except UnauthorizedMission as exc:
        print(f"Authorization error [{exc.status_code} {exc.code}]: {exc}")
        raise
