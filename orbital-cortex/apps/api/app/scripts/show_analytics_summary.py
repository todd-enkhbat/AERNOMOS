"""Print the same operational summary as GET /v1/admin/analytics/summary."""

from __future__ import annotations

import json
import sys

from app.analytics.metrics import compute_analytics_summary
from app.db.session import SessionLocal, get_engine


def _print_table(summary: dict) -> None:
    print("Nomos Orbital — analytics summary")
    print("=" * 72)
    print(f"Generated at: {summary.get('generated_at')}")
    print()

    traction = summary.get("traction") or {}
    print("[Traction]")
    print(f"  missions_started     {traction.get('missions_started')}")
    print(f"  plans_generated      {traction.get('plans_generated')}")
    print(f"  missions_completed   {traction.get('missions_completed')}")
    print(f"  completion_rate      {traction.get('completion_rate')}")
    print(f"  example_views        {traction.get('example_views')}")
    print(f"  user_returns         {traction.get('user_returns')}")
    print()

    catalog = summary.get("catalog") or {}
    print("[Catalog]")
    print(f"  searches             {catalog.get('searches')}")
    print(f"  failures             {catalog.get('failures')}")
    print(f"  avg_search_seconds   {catalog.get('avg_search_seconds')}")
    print(f"  p50_search_seconds   {catalog.get('p50_search_seconds')}")
    print(f"  p95_search_seconds   {catalog.get('p95_search_seconds')}")
    print()

    planner = summary.get("planner") or {}
    print("[Planner]")
    print(f"  generations          {planner.get('generations')}")
    print(f"  avg_generation_sec   {planner.get('avg_generation_seconds')}")
    print(f"  p50_generation_sec   {planner.get('p50_generation_seconds')}")
    print(f"  p95_generation_sec   {planner.get('p95_generation_seconds')}")
    print()

    print("[Missions by status]")
    for status, count in sorted((summary.get("missions_by_status") or {}).items()):
        print(f"  {status:<20} {count}")
    print()

    exports = summary.get("exports") or {}
    print("[Exports]")
    print(f"  pdf_ready            {exports.get('pdf_ready')}")
    print(f"  failures             {exports.get('failures')}")
    print()

    sharing = summary.get("sharing") or {}
    print("[Sharing]")
    print(f"  links_created        {sharing.get('links_created')}")
    print(f"  links_active         {sharing.get('links_active')}")
    print(f"  plan_shared_events   {sharing.get('plan_shared_events')}")
    print()

    execution = summary.get("execution") or {}
    print("[CPU execution]")
    print(f"  jobs_total           {execution.get('jobs_total')}")
    print(f"  jobs_succeeded       {execution.get('jobs_succeeded')}")
    print(f"  success_rate         {execution.get('success_rate')}")
    print()

    orbital = summary.get("orbital_data") or {}
    print("[Orbital data freshness]")
    print(f"  snapshot_id          {orbital.get('snapshot_id')}")
    print(f"  truth_status         {orbital.get('truth_status')}")
    print(
        "  newest_satellite_update_hours_ago "
        f"{orbital.get('newest_satellite_update_hours_ago')}"
    )


def main() -> int:
    session = SessionLocal(bind=get_engine())
    try:
        summary = compute_analytics_summary(session)
    finally:
        session.close()
    _print_table(summary)
    if "--json" in sys.argv:
        print()
        print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
