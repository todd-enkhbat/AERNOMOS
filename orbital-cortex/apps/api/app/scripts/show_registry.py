"""Print registry-backed InfrastructureResource rows grouped by integration_status."""

from __future__ import annotations

import sys
from collections import defaultdict

from app.db.session import SessionLocal, get_engine
from app.services.provider_registry import registry_rows_for_display


def _truncate(value: object, width: int) -> str:
    text = "" if value is None else str(value)
    if len(text) <= width:
        return text
    return text[: max(0, width - 3)] + "..."


def main() -> int:
    session = SessionLocal(bind=get_engine())
    try:
        rows = registry_rows_for_display(session)
    finally:
        session.close()

    if not rows:
        print("No registry-backed infrastructure resources found.")
        print("Run: python -m app.scripts.ingest_providers")
        return 1

    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        status = str(row.get("integration_status") or "unknown")
        grouped[status].append(row)

    print("Infrastructure provider registry")
    print("=" * 72)
    for status in sorted(grouped.keys()):
        print(f"\n[{status}]")
        print(f"{'Provider':<24} {'Truth':<16} {'Source URL'}")
        print("-" * 72)
        for row in grouped[status]:
            print(
                f"{_truncate(row.get('provider_name'), 24):<24} "
                f"{_truncate(row.get('registry_truth_status'), 16):<16} "
                f"{row.get('source_url') or '(simulated — no URL)'}"
            )
    print(f"\nTotal registry entries: {len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
