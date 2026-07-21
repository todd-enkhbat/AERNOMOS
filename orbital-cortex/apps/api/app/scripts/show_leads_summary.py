"""Print feedback and design-partner lead counts for traction review."""

from __future__ import annotations

import json
import sys

from app.db.session import SessionLocal, get_engine
from app.leads.service import compute_leads_summary


def _print_table(summary: dict) -> None:
    print("Nomos Orbital — leads summary")
    print("=" * 72)
    print(f"Generated at: {summary.get('generated_at')}")
    print()

    feedback = summary.get("feedback") or {}
    by_rating = feedback.get("by_rating") or {}
    print("[Feedback]")
    print(f"  total                {feedback.get('total')}")
    print(f"  yes                  {by_rating.get('yes', 0)}")
    print(f"  partly               {by_rating.get('partly', 0)}")
    print(f"  no                   {by_rating.get('no', 0)}")
    print()

    leads = summary.get("design_partner_requests") or {}
    print("[Design-partner requests]")
    print(f"  total                {leads.get('total')}")
    print()
    print("  By organization")
    orgs = leads.get("by_organization") or {}
    if not orgs:
        print("    (none)")
    else:
        for org, count in orgs.items():
            print(f"    {org:<40} {count}")
    print()
    print("  By mission type")
    types = leads.get("by_mission_type") or {}
    if not types:
        print("    (none)")
    else:
        for mission_type, count in types.items():
            print(f"    {mission_type:<40} {count}")


def main() -> int:
    session = SessionLocal(bind=get_engine())
    try:
        summary = compute_leads_summary(session)
    finally:
        session.close()
    _print_table(summary)
    if "--json" in sys.argv:
        print()
        print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
