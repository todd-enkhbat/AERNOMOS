"""Regenerate orbital-cortex/docs/analytics-schema.md from Pydantic allowlists."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import get_args, get_origin

from app.analytics.schemas import PAYLOAD_BY_EVENT, EventName, PlanningFailureReason

REPO_ROOT = Path(__file__).resolve().parents[4]
DOC_PATH = REPO_ROOT / "docs" / "analytics-schema.md"


def _field_type_name(annotation: object) -> str:
    origin = get_origin(annotation)
    if origin is list:
        args = get_args(annotation)
        inner = _field_type_name(args[0]) if args else "any"
        return f"list[{inner}]"
    if hasattr(annotation, "__name__"):
        return annotation.__name__  # type: ignore[union-attr]
    return str(annotation).replace("typing.", "")


def render_markdown() -> str:
    lines = [
        "# Analytics event schema",
        "",
        "Privacy-safe product and planning analytics (Phase O). Storage: Postgres "
        "`analytics_events` table (`event_name`, allowlisted `payload` JSONB, "
        "`created_at`).",
        "",
        "**Allowlist rule:** each event has exactly one Pydantic payload model with "
        "`extra='forbid'`. Unknown keys raise at emit time — never silently dropped.",
        "",
        "**Hashing:** `session_id_hash` uses HMAC-SHA256 with `ANALYTICS_HASH_SALT` "
        "(separate from auth keys). Raw session cookies and share tokens are never "
        "logged.",
        "",
        "**Forbidden everywhere:** `aoi_geometry`, `aoi_polygon`, `mission_notes`, "
        "`raw_query_text`, `session_token`, `share_token`, `user_email`, "
        "`ip_address`, or any unbounded free-form user text.",
        "",
        "Regenerate this file:",
        "",
        "```bash",
        "cd orbital-cortex/apps/api && python -m app.scripts.generate_analytics_schema_doc",
        "```",
        "",
        "## Event names",
        "",
    ]
    for event in EventName:
        lines.append(f"- `{event.value}`")
    lines.extend(
        [
            "",
            "## Planning failure reasons (enum only — no raw exception text)",
            "",
        ]
    )
    for reason in PlanningFailureReason:
        lines.append(f"- `{reason.value}`")
    lines.append("")
    lines.append("## Payload allowlists")
    lines.append("")
    for event, model in PAYLOAD_BY_EVENT.items():
        lines.append(f"### `{event.value}`")
        lines.append("")
        lines.append("| Field | Type |")
        lines.append("| --- | --- |")
        for name, field in model.model_fields.items():
            lines.append(f"| `{name}` | `{_field_type_name(field.annotation)}` |")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(render_markdown(), encoding="utf-8")
    print(f"Wrote {DOC_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
