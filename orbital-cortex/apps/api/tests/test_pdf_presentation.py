"""Tests for PDF presentation layer (human-readable labels)."""

from __future__ import annotations

from app.exports.json_document import JSON_SCHEMA_VERSION, TRUTH_STATUS_LEGEND
from app.exports.pdf import render_mission_brief_html
from app.exports.presentation import enrich_for_pdf, format_duration


def _sample_doc() -> dict:
    return {
        "schema_version": JSON_SCHEMA_VERSION,
        "document_type": "nomos_mission_brief",
        "generated_at": "2026-07-17T04:49:00+00:00",
        "mission_input": {
            "id": "a1b2c3d4-e5f6-4000-8000-0000000000aa",
            "title": "NY Harbor maritime awareness",
            "objective_type": "analyze_imagery",
            "status": "exploratory",
            "start_time": "2026-07-01T00:00:00+00:00",
            "end_time": None,
            "deadline": None,
            "notes": "Demo only.",
        },
        "geographic_summary": {
            "geometry_type": "bbox",
            "bbox": [-74.3, 40.3, -73.5, 41.0],
        },
        "selected_plan": {
            "id": "plan-1",
            "version": 4,
            "status": "conditional",
            "recommended": True,
            "summary": "Use existing Sentinel-1 imagery via cloud processing",
            "pattern": "existing_imagery_cloud",
            "estimated_total_time_seconds": 1860,
            "estimated_total_cost_usd": None,
            "plan_hash": "abc123",
            "input_hash": "def456",
            "planner_config_version": "2026.07.17-1",
            "explanation": {
                "why_recommended": "Best public catalog coverage.",
                "executable_now": ["Select catalog scene"],
                "needs_provider": ["Connect tasking API"],
            },
            "steps": [
                {
                    "sequence": 1,
                    "title": "Select catalog scene",
                    "description": "Choose Sentinel-1 GRD",
                    "provider_name": "microsoft-planetary-computer",
                    "feasibility_status": "feasible",
                    "truth_status": "PROVIDER_REPORTED",
                    "rejection_reason": None,
                }
            ],
        },
        "candidate_plans": [
            {
                "version": 4,
                "summary": "Use existing Sentinel-1 imagery via cloud processing",
                "status": "conditional",
                "recommended": True,
                "explanation": {"why_recommended": "Best coverage"},
            }
        ],
        "assumptions": [
            {"kind": "planner_meta", "pattern": "existing_imagery_cloud", "planner_config_version": "2026.07.17-1"},
        ],
        "source_evidence": [
            {
                "source_name": "Microsoft Planetary Computer",
                "source_type": "catalog",
                "truth_status": "PROVIDER_REPORTED",
                "retrieved_at": "2026-07-17T04:40:00+00:00",
            }
        ],
        "truth_statuses": {"legend": TRUTH_STATUS_LEGEND},
        "missing_integrations": ["Satellite tasking / reservation API"],
        "next_actions": ["Connect a satellite tasking provider account"],
        "disclosures": {
            "simulation_boundary": "Planning disclosure text.",
            "simulated_fields_policy": "SIMULATED values are labeled.",
        },
    }


def test_enrich_for_pdf_humanizes_objective_and_providers():
    view = enrich_for_pdf(_sample_doc())
    assert view["mission"]["objective"] == "Analyze satellite imagery"
    assert "Microsoft Planetary Computer" in view["timeline"]["steps"][0]["provider_label"]
    assert "About 31 min" in view["recommendation"]["duration"]
    assert "pricing feed" in view["recommendation"]["cost"].lower()


def test_pdf_html_uses_guided_sections_not_raw_codes():
    html = render_mission_brief_html(_sample_doc())
    assert "Executive summary" in html
    assert "Step-by-step timeline" in html
    assert "Appendix A" in html
    assert "Reviewer notes" in html
    assert "analyze_imagery" not in html
    assert "microsoft-planetary-computer" not in html
    assert "Planning only — not an operational order" in html
    assert "Reviewed by (name / role)" in html


def test_format_duration_edge_cases():
    assert "seconds" in format_duration(45)
    assert "min" in format_duration(1860)
    assert "pricing" not in format_duration(None).lower()
    assert "Not estimated" in format_duration(None)
