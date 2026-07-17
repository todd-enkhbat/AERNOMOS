"""Human-readable presentation layer for mission brief PDFs."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

OBJECTIVE_LABELS: Dict[str, str] = {
    "analyze_imagery": "Analyze satellite imagery",
    "plan_data_delivery": "Plan data delivery from orbit",
    "compare_processing": "Compare processing options",
    "remote_sensing_workflow": "Remote sensing workflow",
    "other": "Other space-data objective",
    "ship_detection": "Maritime / vessel monitoring",
    "crop_health": "Agricultural monitoring",
    "disaster_response": "Disaster response imagery",
}

MISSION_STATUS_LABELS: Dict[str, str] = {
    "draft": "Draft — not yet committed",
    "exploratory": "Exploratory — options under review",
    "active": "Active planning",
    "example": "Curated public example",
}

PLAN_STATUS_LABELS: Dict[str, str] = {
    "feasible": "Executable now",
    "conditional": "Feasible after provider access",
    "rejected": "Not executable",
}

FEASIBILITY_LABELS: Dict[str, str] = {
    "feasible": "Ready with current public data",
    "conditional": "Blocked on provider access",
    "rejected": "Fails a hard constraint",
}

PATTERN_LABELS: Dict[str, str] = {
    "existing_imagery_cloud": "Use existing catalog imagery → process in cloud",
    "existing_imagery_edge": "Use existing catalog imagery → process at edge",
    "satellite_ground_cloud": "Satellite → ground station → cloud",
    "onboard": "Onboard satellite processing",
}

PROVIDER_LABELS: Dict[str, str] = {
    "microsoft-planetary-computer": "Microsoft Planetary Computer (public STAC catalog)",
    "customer-cloud": "Your designated cloud region",
    "customer-edge": "Your edge / on-prem environment",
    "nomos-fleet": "Nomos reference satellite fleet (public TLE data)",
    "ground-station": "Ground station (public coordinates only)",
}

TRUTH_STATUS_SHORT: Dict[str, str] = {
    "OBSERVED": "Directly measured",
    "CALCULATED": "Calculated by Nomos",
    "PROVIDER_REPORTED": "From upstream provider",
    "ESTIMATED": "Estimated (not guaranteed)",
    "SIMULATED": "Simulated / demo only",
    "STALE": "Real but possibly outdated",
    "UNAVAILABLE": "No source connected",
}

REJECTION_REASON_LABELS: Dict[str, str] = {
    "tasking_api_unavailable": "No live satellite tasking API is connected.",
    "onboard_provider_unavailable": "No onboard processing provider is connected.",
    "cost_unavailable": "Cost cannot be estimated without a pricing data source.",
    "coverage_below_threshold": "Catalog scenes do not sufficiently cover the area.",
    "no_catalog_candidates": "No matching public catalog scenes were found.",
}


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def format_datetime(value: Optional[str]) -> str:
    dt = _parse_iso(value)
    if dt is None:
        return "Not specified"
    return dt.strftime("%B %d, %Y at %H:%M UTC")


def format_date_short(value: Optional[str]) -> str:
    dt = _parse_iso(value)
    if dt is None:
        return "—"
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def format_duration(seconds: Optional[float]) -> str:
    if seconds is None:
        return "Not estimated — no reliable duration model for this path"
    total = int(round(seconds))
    if total < 60:
        return f"About {total} seconds"
    minutes, secs = divmod(total, 60)
    if minutes < 60:
        return f"About {minutes} min {secs} s"
    hours, minutes = divmod(minutes, 60)
    if hours < 48:
        return f"About {hours} h {minutes} min"
    days, hours = divmod(hours, 24)
    return f"About {days} day(s) {hours} h"


def format_cost(usd: Optional[float]) -> str:
    if usd is None:
        return "Not estimated — no commercial pricing feed is connected"
    return f"${usd:,.2f} USD (estimate only)"


def label(mapping: Dict[str, str], key: Optional[str], fallback: Optional[str] = None) -> str:
    if not key:
        return fallback or "Not specified"
    return mapping.get(key, key.replace("_", " ").replace("-", " ").title())


def format_bbox(bbox: Optional[List[float]]) -> str:
    if not bbox or len(bbox) != 4:
        return "Area boundary not available in this export"
    west, south, east, north = bbox
    return (
        f"West {west:.4f}°, South {south:.4f}°, "
        f"East {east:.4f}°, North {north:.4f}° (WGS84)"
    )


def format_geo_narrative(geo: Dict[str, Any]) -> str:
    geom = geo.get("geometry_type")
    if geom == "bbox":
        return (
            "The mission area is defined as a rectangular bounding box. "
            + format_bbox(geo.get("bbox"))
        )
    if geom == "Polygon":
        return (
            "The mission area is a custom polygon. "
            + format_bbox(geo.get("bbox"))
            + " See the interactive map on the Nomos mission page for the exact shape."
        )
    return "The mission area geometry was not included in this export."


def humanize_rejection(code_or_text: Optional[str]) -> str:
    if not code_or_text:
        return ""
    text = str(code_or_text)
    if text in REJECTION_REASON_LABELS:
        return REJECTION_REASON_LABELS[text]
    if "unavailable" in text.lower():
        return text.replace("_", " ").capitalize() + "."
    return text


def _assumption_lines(assumptions: List[Any]) -> List[Dict[str, str]]:
    lines: List[Dict[str, str]] = []
    for item in assumptions or []:
        if not isinstance(item, dict):
            lines.append({"text": str(item), "category": "General"})
            continue
        kind = item.get("kind")
        if kind == "planner_meta":
            pattern = label(PATTERN_LABELS, item.get("pattern"))
            lines.append(
                {
                    "category": "Planning method",
                    "text": (
                        f"Nomos evaluated routes using pattern “{pattern}”. "
                        f"Planner configuration {item.get('planner_config_version', '—')}."
                    ),
                }
            )
            for reason in item.get("rejection_reasons") or []:
                if isinstance(reason, dict):
                    msg = reason.get("message") or humanize_rejection(reason.get("code"))
                else:
                    msg = humanize_rejection(str(reason))
                if msg:
                    lines.append({"category": "Constraint", "text": msg})
            continue
        if item.get("text"):
            lines.append({"category": "Assumption", "text": str(item["text"])})
        elif item.get("message"):
            lines.append({"category": "Assumption", "text": str(item["message"])})
    return lines


def _step_narrative(step: Dict[str, Any]) -> str:
    feas = step.get("feasibility_status") or ""
    if feas == "feasible":
        return "This step can proceed with currently available public data and integrations."
    if feas == "conditional":
        if step.get("rejection_reason"):
            return humanize_rejection(step.get("rejection_reason"))
        return "This step depends on connecting a provider that is not yet available in your account."
    if feas == "rejected":
        return humanize_rejection(step.get("rejection_reason")) or (
            "This step cannot be executed under current constraints."
        )
    return "Review feasibility with your operations team."


def _executive_summary(doc: Dict[str, Any], plan: Optional[Dict[str, Any]]) -> str:
    mission = doc.get("mission_input") or {}
    title = mission.get("title") or "This mission"
    if not plan:
        return (
            f"{title} does not yet have a generated execution plan. "
            "Run plan generation in Nomos before using this document for operational decisions."
        )
    status = plan.get("status") or "unknown"
    status_label = label(PLAN_STATUS_LABELS, status)
    summary = plan.get("summary") or "No summary available."
    why = (plan.get("explanation") or {}).get("why_recommended") or ""
    parts = [
        f"Nomos recommends: {summary}",
        f"Overall readiness: {status_label}.",
    ]
    if why:
        parts.append(why)
    parts.append(
        "This document is a planning artifact. It does not task satellites, "
        "reserve ground stations, or execute workloads unless explicitly marked as connected."
    )
    return " ".join(parts)


def _document_control(doc: Dict[str, Any]) -> Dict[str, str]:
    mission_id = (doc.get("mission_input") or {}).get("id") or "unknown"
    short_id = str(mission_id).split("-")[0].upper()
    generated = format_date_short(doc.get("generated_at"))
    plan = doc.get("selected_plan") or {}
    return {
        "reference": f"NOMOS-BRIEF-{short_id}",
        "generated": generated,
        "schema_version": str(doc.get("schema_version", "1")),
        "mission_id": str(mission_id),
        "plan_id": str(plan.get("id") or "—"),
        "plan_version": str(plan.get("version") or "—"),
    }


def _plan_comparison_rows(plans: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for plan in plans or []:
        rows.append(
            {
                "version": f"v{plan.get('version', '—')}",
                "summary": plan.get("summary") or "—",
                "readiness": label(PLAN_STATUS_LABELS, plan.get("status")),
                "recommended": "Yes — primary recommendation" if plan.get("recommended") else "No",
                "commentary": (
                    (plan.get("explanation") or {}).get("why_recommended")
                    or label(PLAN_STATUS_LABELS, plan.get("status"))
                ),
            }
        )
    return rows


def _source_rows(evidence: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for ev in evidence or []:
        truth = ev.get("truth_status") or "UNAVAILABLE"
        rows.append(
            {
                "name": ev.get("source_name") or "Unknown source",
                "type": (ev.get("source_type") or "data").replace("_", " ").title(),
                "confidence": TRUTH_STATUS_SHORT.get(str(truth), str(truth)),
                "retrieved": format_date_short(ev.get("retrieved_at")),
                "note": (
                    "Use this row to trace where a number or window in the plan originated."
                ),
            }
        )
    return rows


def _missing_integration_rows(items: List[str]) -> List[Dict[str, str]]:
    guidance = {
        "Satellite tasking / reservation API": (
            "Nomos cannot request new satellite collections or reserve spacecraft capacity "
            "until your tasking provider is connected."
        ),
        "Ground-station booking / capacity API": (
            "Ground-station coordinates may appear in the plan, but live booking and "
            "capacity guarantees require a connected ground-segment provider."
        ),
        "Commercial pricing feeds": (
            "Cost figures stay blank intentionally. Nomos will not invent cloud or "
            "downlink prices without a sourced rate card."
        ),
        "Onboard processing provider": (
            "Onboard execution paths remain planning-only until payload and compute "
            "capabilities are registered."
        ),
    }
    rows: List[Dict[str, str]] = []
    for item in items or []:
        rows.append(
            {
                "integration": item,
                "impact": guidance.get(
                    item,
                    "This capability is not connected. Related plan steps remain conditional or unavailable.",
                ),
            }
        )
    return rows


def enrich_for_pdf(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Build a presentation-friendly view model for the Jinja PDF template."""
    mission = doc.get("mission_input") or {}
    geo = doc.get("geographic_summary") or {}
    plan = doc.get("selected_plan")
    explanation = (plan or {}).get("explanation") or {}

    steps: List[Dict[str, Any]] = []
    for step in (plan or {}).get("steps") or []:
        steps.append(
            {
                **step,
                "provider_label": label(PROVIDER_LABELS, step.get("provider_name")),
                "feasibility_label": label(
                    FEASIBILITY_LABELS, step.get("feasibility_status")
                ),
                "truth_label": TRUTH_STATUS_SHORT.get(
                    str(step.get("truth_status") or ""), "Unknown"
                ),
                "narrative": _step_narrative(step),
            }
        )

    return {
        "control": _document_control(doc),
        "purpose": (
            "This Mission Brief translates your Nomos plan into a readable record for "
            "engineering review, partner sharing, and internal compliance. "
            "Read sections 1–7 for decisions; use the appendices for data-confidence "
            "definitions and technical identifiers."
        ),
        "executive_summary": _executive_summary(doc, plan),
        "limitations": {
            "headline": "Planning only — not an operational order",
            "body": doc.get("disclosures", {}).get("simulation_boundary", ""),
            "policy": doc.get("disclosures", {}).get("simulated_fields_policy", ""),
        },
        "mission": {
            "title": mission.get("title") or "Untitled mission",
            "objective": label(OBJECTIVE_LABELS, mission.get("objective_type")),
            "status": label(MISSION_STATUS_LABELS, mission.get("status")),
            "timeframe": {
                "start": format_datetime(mission.get("start_time")),
                "end": format_datetime(mission.get("end_time")),
                "deadline": format_datetime(mission.get("deadline")),
            },
            "notes": mission.get("notes") or "None recorded.",
            "area_narrative": format_geo_narrative(geo),
        },
        "recommendation": {
            "present": plan is not None,
            "headline": (plan or {}).get("summary") or "No recommendation generated",
            "readiness": label(PLAN_STATUS_LABELS, (plan or {}).get("status")),
            "why": explanation.get("why_recommended")
            or "Generate or refresh plans in Nomos to populate this section.",
            "duration": format_duration((plan or {}).get("estimated_total_time_seconds")),
            "cost": format_cost((plan or {}).get("estimated_total_cost_usd")),
            "executable_now": explanation.get("executable_now") or [],
            "needs_provider": explanation.get("needs_provider") or [],
            "pattern": label(
                PATTERN_LABELS,
                (plan or {}).get("pattern"),
                "Not recorded",
            ),
        },
        "timeline": {
            "intro": (
                "The recommended plan unfolds in the order below. Each step lists what "
                "would happen, which system is involved, and whether Nomos can execute "
                "it today or only after additional provider access."
            ),
            "steps": steps,
        },
        "alternatives": {
            "intro": (
                "Nomos evaluated multiple routing patterns. The table compares every "
                "generated version so reviewers can see why the primary recommendation "
                "was selected."
            ),
            "rows": _plan_comparison_rows(doc.get("candidate_plans") or []),
        },
        "assumptions": {
            "intro": (
                "These are the explicit assumptions and constraints Nomos used when "
                "ranking plans. They should be validated with your operations and "
                "compliance teams before any external commitment."
            ),
            "entries": _assumption_lines(doc.get("assumptions") or []),
        },
        "sources": {
            "intro": (
                "Every material value in the brief should trace to a source. The table "
                "lists evidence attached to the recommended plan."
            ),
            "rows": _source_rows(doc.get("source_evidence") or []),
        },
        "missing": {
            "intro": (
                "The following integrations are not connected for this workspace. "
                "Related steps remain conditional or unavailable — Nomos will not "
                "imply live capacity where none exists."
            ),
            "rows": _missing_integration_rows(doc.get("missing_integrations") or []),
        },
        "next_actions": {
            "intro": "Recommended follow-ups before treating this plan as execution-ready:",
            "entries": doc.get("next_actions") or [],
        },
        "truth_legend": doc.get("truth_statuses", {}).get("legend") or [],
        "appendix": {
            "mission_id": mission.get("id"),
            "document_type": doc.get("document_type"),
            "schema_version": doc.get("schema_version"),
            "generated_at": doc.get("generated_at"),
            "plan_hash": (plan or {}).get("plan_hash"),
            "input_hash": (plan or {}).get("input_hash"),
            "planner_config": (plan or {}).get("planner_config_version"),
        },
    }
