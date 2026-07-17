"""Candidate plan pattern generators.

Always emit structured shells for the four supported patterns when relevant.
Generators do not invent catalog scenes or pricing.
"""

from __future__ import annotations

from typing import List, Optional

from app.db.truth import TruthStatus
from app.planner.types import (
    DraftPlan,
    DraftStep,
    FeasibilityStatus,
    MissionPlannerContext,
    PlanPattern,
)
from app.services import provider_registry


def generate_candidate_plans(ctx: MissionPlannerContext) -> List[DraftPlan]:
    """Generate deterministic candidate shells (typically 4)."""
    best = _best_candidate(ctx)
    window = ctx.contact_windows[0] if ctx.contact_windows else None
    plans = [
        _imagery_cloud(ctx, best),
        _imagery_edge(ctx, best),
        _satellite_ground_cloud(ctx, best, window),
        _onboard(ctx, window),
    ]
    return plans


def _best_candidate(ctx: MissionPlannerContext) -> Optional[dict]:
    if not ctx.catalog_snapshot:
        return None
    # Prefer highest AOI coverage, then most recent acquisition, then stable id.
    def key(item: dict) -> tuple:
        cid = str(item.get("id") or "")
        coverage = float(ctx.coverage_by_candidate.get(cid, 0.0))
        acquired = str(item.get("acquisition_time") or "")
        return (-coverage, acquired == "", acquired, cid)

    return sorted(ctx.catalog_snapshot, key=key)[0]


def _provider_step_metadata(provider: dict) -> dict:
    return {
        "registry_resource_id": provider.get("id"),
        "integration_status": provider.get("integration_status"),
        "registry_truth_status": provider.get("registry_truth_status"),
        "source_url": provider.get("source_url"),
        "is_simulated": bool(provider.get("is_simulated")),
        "is_public_info_only": bool(provider.get("is_public_info_only")),
        "is_connected": bool(provider.get("is_connected")),
        "provider_selection_reason": provider.get("selection_reason"),
    }


def _step_truth_for_provider(provider: dict) -> str:
    if provider.get("is_simulated"):
        return TruthStatus.SIMULATED.value
    if provider.get("is_connected"):
        return TruthStatus.PROVIDER_REPORTED.value
    if provider.get("is_public_info_only"):
        return TruthStatus.PROVIDER_REPORTED.value
    return TruthStatus.ESTIMATED.value


def _cloud_provider(ctx: MissionPlannerContext) -> dict:
    resources = ctx.registry_resources.get("cloud") or []
    selected = provider_registry.select_provider(resources, prefer_non_simulated=False)
    if selected:
        return selected
    return {
        "id": None,
        "provider_name": "customer-cloud",
        "integration_status": "unavailable",
        "registry_truth_status": "UNAVAILABLE",
        "source_url": None,
        "is_simulated": False,
        "is_public_info_only": False,
        "is_connected": False,
    }


def _edge_provider(ctx: MissionPlannerContext) -> dict:
    resources = ctx.registry_resources.get("edge") or []
    selected = provider_registry.select_provider(
        resources,
        preferred_name=ctx.preferred_compute_location,
        prefer_non_simulated=True,
    )
    if selected:
        return selected
    fallback = ctx.preferred_compute_location or "customer-edge"
    return {
        "id": None,
        "provider_name": fallback,
        "integration_status": "unavailable",
        "registry_truth_status": "UNAVAILABLE",
        "source_url": None,
        "is_simulated": False,
        "is_public_info_only": False,
        "is_connected": False,
    }


def _imagery_cloud(ctx: MissionPlannerContext, candidate: Optional[dict]) -> DraftPlan:
    provider = (candidate or {}).get("source_provider") or "catalog"
    item_id = (candidate or {}).get("external_item_id") or "unavailable"
    candidate_id = (candidate or {}).get("id")
    cloud = _cloud_provider(ctx)
    cloud_name = str(cloud.get("provider_name") or "customer-cloud")
    cloud_meta = _provider_step_metadata(cloud)
    cloud_truth = _step_truth_for_provider(cloud)
    steps = [
        DraftStep(
            sequence=1,
            step_type="select_catalog_scene",
            provider_name=provider,
            title="Select catalog scene",
            description=f"Use existing STAC item {item_id} covering the mission AOI.",
            truth_status=(
                (candidate or {}).get("truth_status") or TruthStatus.UNAVAILABLE.value
            ),
            feasibility_status=FeasibilityStatus.FEASIBLE.value,
            input_artifact="mission_aoi",
            output_artifact=f"catalog:{item_id}",
            source_metadata={"candidate_id": candidate_id, "external_item_id": item_id},
        ),
        DraftStep(
            sequence=2,
            step_type="retrieve_asset",
            provider_name=provider,
            title="Retrieve asset",
            description="Fetch the scene asset from the public catalog provider.",
            truth_status=TruthStatus.ESTIMATED.value,
            feasibility_status=FeasibilityStatus.FEASIBLE.value,
            input_artifact=f"catalog:{item_id}",
            output_artifact="staged_scene",
        ),
        DraftStep(
            sequence=3,
            step_type="transfer",
            provider_name=cloud_name,
            title="Transfer to cloud storage",
            description="Move the staged scene into cloud or customer object storage.",
            truth_status=TruthStatus.ESTIMATED.value,
            feasibility_status=FeasibilityStatus.FEASIBLE.value,
            input_artifact="staged_scene",
            output_artifact="cloud_scene",
            resource_id=str(cloud["id"]) if cloud.get("id") else None,
            source_metadata=cloud_meta,
        ),
        DraftStep(
            sequence=4,
            step_type="cloud_process",
            provider_name=cloud_name,
            title="Process in cloud",
            description="Run the mission analysis on cloud compute and return the result.",
            truth_status=cloud_truth,
            feasibility_status=FeasibilityStatus.FEASIBLE.value,
            input_artifact="cloud_scene",
            output_artifact="analysis_result",
            resource_id=str(cloud["id"]) if cloud.get("id") else None,
            source_metadata=cloud_meta,
        ),
    ]
    assumptions = [
        {
            "key": "catalog_asset_retrievable",
            "detail": "Assumes STAC asset hrefs remain reachable (SAS signing deferred).",
        },
    ]
    if cloud.get("is_simulated"):
        assumptions.append(
            {
                "key": "simulated_cloud_provider",
                "detail": (
                    f"Cloud compute step uses registry entry '{cloud_name}' "
                    "labeled SIMULATED — not a live provider connection."
                ),
            }
        )
    elif cloud.get("is_public_info_only"):
        assumptions.append(
            {
                "key": "public_cloud_info_only",
                "detail": (
                    f"Cloud provider '{cloud_name}' is public-source information only; "
                    "Nomos has not verified live availability."
                ),
            }
        )
    else:
        assumptions.append(
            {
                "key": "cloud_compute_available",
                "detail": "Assumes a customer or Nomos cloud environment can run the model.",
            }
        )
    return DraftPlan(
        pattern=PlanPattern.EXISTING_IMAGERY_CLOUD,
        summary="Existing imagery → cloud processing",
        steps=steps,
        candidate_id=candidate_id,
        assumptions=assumptions,
    )


def _imagery_edge(ctx: MissionPlannerContext, candidate: Optional[dict]) -> DraftPlan:
    provider = (candidate or {}).get("source_provider") or "catalog"
    item_id = (candidate or {}).get("external_item_id") or "unavailable"
    candidate_id = (candidate or {}).get("id")
    edge = _edge_provider(ctx)
    edge_name = str(edge.get("provider_name") or "customer-edge")
    edge_meta = _provider_step_metadata(edge)
    edge_truth = _step_truth_for_provider(edge)
    steps = [
        DraftStep(
            sequence=1,
            step_type="select_catalog_scene",
            provider_name=provider,
            title="Select catalog scene",
            description=f"Use existing STAC item {item_id} covering the mission AOI.",
            truth_status=(
                (candidate or {}).get("truth_status") or TruthStatus.UNAVAILABLE.value
            ),
            feasibility_status=FeasibilityStatus.FEASIBLE.value,
            input_artifact="mission_aoi",
            output_artifact=f"catalog:{item_id}",
            source_metadata={"candidate_id": candidate_id, "external_item_id": item_id},
        ),
        DraftStep(
            sequence=2,
            step_type="retrieve_asset",
            provider_name=provider,
            title="Retrieve asset",
            description="Fetch the scene asset from the public catalog provider.",
            truth_status=TruthStatus.ESTIMATED.value,
            feasibility_status=FeasibilityStatus.FEASIBLE.value,
            input_artifact=f"catalog:{item_id}",
            output_artifact="staged_scene",
        ),
        DraftStep(
            sequence=3,
            step_type="transfer",
            provider_name=edge_name,
            title="Transfer to customer edge",
            description=f"Move the staged scene to registry provider '{edge_name}'.",
            truth_status=TruthStatus.ESTIMATED.value,
            feasibility_status=FeasibilityStatus.FEASIBLE.value,
            input_artifact="staged_scene",
            output_artifact="edge_scene",
            resource_id=str(edge["id"]) if edge.get("id") else None,
            source_metadata=edge_meta,
        ),
        DraftStep(
            sequence=4,
            step_type="edge_process",
            provider_name=edge_name,
            title="Process on customer edge",
            description=(
                "Run analysis on the selected edge compute resource "
                "from the provider registry."
            ),
            truth_status=edge_truth,
            feasibility_status=FeasibilityStatus.FEASIBLE.value,
            input_artifact="edge_scene",
            output_artifact="analysis_result",
            resource_id=str(edge["id"]) if edge.get("id") else None,
            source_metadata=edge_meta,
        ),
    ]
    assumptions: List[dict] = []
    if edge.get("is_simulated"):
        assumptions.append(
            {
                "key": "simulated_edge_provider",
                "detail": (
                    f"Edge compute step uses registry entry '{edge_name}' "
                    "labeled SIMULATED — not a live provider connection."
                ),
            }
        )
    elif edge.get("is_public_info_only"):
        assumptions.append(
            {
                "key": "public_edge_info_only",
                "detail": (
                    f"Edge provider '{edge_name}' is public-source information only "
                    f"(integration_status={edge.get('integration_status')}). "
                    "Live sandbox or partner access is still required."
                ),
            }
        )
        if edge.get("source_url"):
            assumptions.append(
                {
                    "key": "edge_source_citation",
                    "detail": f"Public provider facts sourced from {edge.get('source_url')}.",
                }
            )
    else:
        assumptions.append(
            {
                "key": "customer_edge_reachable",
                "detail": (
                    "Assumes the customer edge environment can receive "
                    "and process the scene."
                ),
            }
        )
    return DraftPlan(
        pattern=PlanPattern.EXISTING_IMAGERY_EDGE,
        summary="Existing imagery → customer edge processing",
        steps=steps,
        candidate_id=candidate_id,
        assumptions=assumptions,
    )


def _satellite_ground_cloud(
    ctx: MissionPlannerContext,
    candidate: Optional[dict],
    window: Optional[dict],
) -> DraftPlan:
    sat_id = (window or {}).get("satellite_id") or "fleet-satellite"
    gs_id = (window or {}).get("ground_station_id") or "ground-station"
    window_id = (window or {}).get("id")
    cloud = _cloud_provider(ctx)
    cloud_name = str(cloud.get("provider_name") or "customer-cloud")
    cloud_meta = _provider_step_metadata(cloud)
    cloud_truth = _step_truth_for_provider(cloud)
    steps = [
        DraftStep(
            sequence=1,
            step_type="acquire",
            provider_name=sat_id,
            title="Satellite acquisition",
            description=(
                "Task a new acquisition over the AOI. Not executable without a "
                "connected tasking API."
            ),
            truth_status=TruthStatus.UNAVAILABLE.value,
            feasibility_status=FeasibilityStatus.CONDITIONAL.value,
            rejection_reason="No tasking API connected",
            output_artifact="raw_acquisition",
            source_metadata={"integration": "tasking_api", "status": "unavailable"},
        ),
        DraftStep(
            sequence=2,
            step_type="wait_contact",
            provider_name=gs_id,
            title="Wait for contact window",
            description=(
                f"Next eligible contact window for {sat_id} via {gs_id}."
                if window
                else "No cached contact window in the planning horizon."
            ),
            truth_status=(
                TruthStatus.CALCULATED.value if window else TruthStatus.UNAVAILABLE.value
            ),
            feasibility_status=(
                FeasibilityStatus.FEASIBLE.value
                if window
                else FeasibilityStatus.REJECTED.value
            ),
            rejection_reason=None if window else "No contact window available",
            source_metadata={
                "contact_window_id": window_id,
                "tle_snapshot_id": ctx.tle_snapshot_id,
                "orbital_truth_status": ctx.orbital_truth_status,
            },
        ),
        DraftStep(
            sequence=3,
            step_type="downlink",
            provider_name=gs_id,
            title="Downlink via ground station",
            description="Transfer acquired data through the ground station.",
            truth_status=TruthStatus.ESTIMATED.value,
            feasibility_status=FeasibilityStatus.CONDITIONAL.value,
            input_artifact="raw_acquisition",
            output_artifact="ground_scene",
        ),
        DraftStep(
            sequence=4,
            step_type="transfer",
            provider_name=cloud_name,
            title="Transfer to cloud",
            description="Move downlinked data into cloud storage for processing.",
            truth_status=TruthStatus.ESTIMATED.value,
            feasibility_status=FeasibilityStatus.FEASIBLE.value,
            input_artifact="ground_scene",
            output_artifact="cloud_scene",
            resource_id=str(cloud["id"]) if cloud.get("id") else None,
            source_metadata=cloud_meta,
        ),
        DraftStep(
            sequence=5,
            step_type="cloud_process",
            provider_name=cloud_name,
            title="Process in cloud",
            description="Run analysis on cloud compute and return the result.",
            truth_status=cloud_truth,
            feasibility_status=FeasibilityStatus.FEASIBLE.value,
            input_artifact="cloud_scene",
            output_artifact="analysis_result",
            resource_id=str(cloud["id"]) if cloud.get("id") else None,
            source_metadata=cloud_meta,
        ),
    ]
    assumptions = [
        {
            "key": "tasking_not_executed",
            "detail": "Plan does not claim tasking or reservation was executed.",
        }
    ]
    if ctx.orbital_truth_status == TruthStatus.STALE.value:
        assumptions.append(
            {
                "key": "stale_orbital_data",
                "detail": (
                    f"Contact windows use TLE snapshot '{ctx.tle_snapshot_id}' "
                    "labeled STALE; geometry may be outdated."
                ),
            }
        )
    return DraftPlan(
        pattern=PlanPattern.SATELLITE_GROUND_CLOUD,
        summary="Satellite acquisition → ground station → cloud processing",
        steps=steps,
        candidate_id=(candidate or {}).get("id"),
        contact_window_id=window_id,
        tle_snapshot_id=ctx.tle_snapshot_id,
        orbital_truth_status=ctx.orbital_truth_status,
        assumptions=assumptions,
    )


def _onboard(ctx: MissionPlannerContext, window: Optional[dict]) -> DraftPlan:
    sat_id = (window or {}).get("satellite_id") or "fleet-satellite"
    window_id = (window or {}).get("id")
    orbital = provider_registry.select_provider(
        ctx.registry_resources.get("orbital_compute") or [],
        prefer_non_simulated=True,
    )
    onboard_name = (
        str(orbital.get("provider_name"))
        if orbital and not orbital.get("is_simulated")
        else sat_id
    )
    onboard_meta = _provider_step_metadata(orbital) if orbital else {}
    steps = [
        DraftStep(
            sequence=1,
            step_type="acquire",
            provider_name=sat_id,
            title="Satellite acquisition",
            description="Acquire imagery onboard for immediate processing.",
            truth_status=TruthStatus.UNAVAILABLE.value,
            feasibility_status=FeasibilityStatus.REJECTED.value,
            rejection_reason="No tasking / onboard provider connected",
            output_artifact="raw_acquisition",
        ),
        DraftStep(
            sequence=2,
            step_type="onboard_process",
            provider_name=onboard_name,
            title="Onboard model execution",
            description="Run inference on orbital compute. No real onboard provider exists today.",
            truth_status=TruthStatus.UNAVAILABLE.value,
            feasibility_status=FeasibilityStatus.REJECTED.value,
            rejection_reason="onboard_provider_unavailable",
            input_artifact="raw_acquisition",
            output_artifact="onboard_result",
            resource_id=str(orbital["id"]) if orbital and orbital.get("id") else None,
            source_metadata=onboard_meta,
        ),
        DraftStep(
            sequence=3,
            step_type="wait_contact",
            provider_name=(window or {}).get("ground_station_id") or "ground-station",
            title="Prioritized downlink",
            description="Downlink prioritized results on the next contact window.",
            truth_status=(
                TruthStatus.CALCULATED.value if window else TruthStatus.UNAVAILABLE.value
            ),
            feasibility_status=(
                FeasibilityStatus.FEASIBLE.value
                if window
                else FeasibilityStatus.REJECTED.value
            ),
            source_metadata={
                "contact_window_id": window_id,
                "tle_snapshot_id": ctx.tle_snapshot_id,
                "orbital_truth_status": ctx.orbital_truth_status,
            },
        ),
        DraftStep(
            sequence=4,
            step_type="delivery",
            provider_name="customer-cloud",
            title="Deliver result",
            description="Deliver the prioritized result to the customer.",
            truth_status=TruthStatus.ESTIMATED.value,
            feasibility_status=FeasibilityStatus.FEASIBLE.value,
            input_artifact="onboard_result",
            output_artifact="analysis_result",
        ),
    ]
    return DraftPlan(
        pattern=PlanPattern.ONBOARD_PROCESSING,
        summary="Onboard processing → prioritized downlink → delivery",
        steps=steps,
        contact_window_id=window_id,
        tle_snapshot_id=ctx.tle_snapshot_id,
        orbital_truth_status=ctx.orbital_truth_status,
        assumptions=[
            {
                "key": "onboard_provider_missing",
                "detail": "No real onboard processing provider is integrated.",
            }
        ],
    )
