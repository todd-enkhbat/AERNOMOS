"""Private mission and share-link routes."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.catalog import service as catalog_service
from app.catalog.errors import (
    CatalogError,
    CatalogNotFoundError,
    CatalogRateLimitedError,
    CatalogUnavailableError,
)
from app.core import missions as mission_store
from app.core.config import get_settings
from app.db import get_db
from app.db.mission_orm import AnonymousSession, Mission, MissionExport, MissionPlan, ShareLink
from app.deps.auth import (
    get_mission_for_read,
    get_owned_mission,
    require_anonymous_session,
)
from app.exports import service as export_service
from app.exports.json_document import build_mission_export_json
from app.models.errors import ErrorResponse
from app.models.mission import (
    CatalogCandidatesResponse,
    DiscoverRequest,
    MissionCreate,
    MissionInfrastructureResponse,
    MissionJsonExportResponse,
    MissionPdfExportResponse,
    MissionPlanDetailResponse,
    MissionPlansGenerateResponse,
    MissionPlansListResponse,
    MissionResponse,
    MissionsListResponse,
    ShareLinkCreate,
    ShareLinkListResponse,
    ShareLinkResponse,
    ShareResolveResponse,
)
from app.planner import PLANNER_CONFIG_VERSION
from app.planner import engine as planner_engine
from app.services import mission_infrastructure as infra_service

router = APIRouter(prefix="/v1", tags=["missions"])


def _api_error(status: int, code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status,
        detail={"error": {"code": code, "message": message}},
    )


def _parse_optional_dt(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise _api_error(422, "validation_error", f"Invalid datetime: {value}") from exc


def _catalog_http_error(exc: CatalogError) -> HTTPException:
    if isinstance(exc, CatalogRateLimitedError):
        return _api_error(503, exc.code, exc.message)
    if isinstance(exc, CatalogNotFoundError):
        return _api_error(502, exc.code, exc.message)
    if isinstance(exc, CatalogUnavailableError):
        return _api_error(503, exc.code, exc.message)
    return _api_error(503, getattr(exc, "code", "catalog_error"), str(exc))


@router.get(
    "/missions/examples",
    response_model=MissionsListResponse,
    summary="List curated public example missions",
    description=(
        "Returns missions explicitly marked as public examples. These are "
        "not private user submissions and are safe to show without a session."
    ),
)
def list_examples(db: Session = Depends(get_db)) -> Dict[str, Any]:
    rows = mission_store.list_example_missions(db)
    return {
        "missions": [mission_store.mission_to_dict(db, row) for row in rows],
    }


@router.get(
    "/missions",
    response_model=MissionsListResponse,
    summary="List missions for the current private session",
    responses={
        401: {"model": ErrorResponse, "description": "Missing or expired session"},
    },
)
def list_missions(
    request: Request,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    owner = require_anonymous_session(request, db)
    rows = mission_store.list_session_missions(db, owner.id)
    db.commit()
    return {
        "missions": [mission_store.mission_to_dict(db, row) for row in rows],
    }


@router.post(
    "/missions",
    response_model=MissionResponse,
    status_code=201,
    summary="Create a private mission for the current session",
    responses={
        401: {"model": ErrorResponse, "description": "Missing or expired session"},
        422: {"model": ErrorResponse, "description": "Invalid mission payload"},
    },
)
def create_mission(
    payload: MissionCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    owner = require_anonymous_session(request, db)
    data = payload.model_dump()
    data["start_time"] = _parse_optional_dt(payload.start_time)
    data["end_time"] = _parse_optional_dt(payload.end_time)
    data["deadline"] = _parse_optional_dt(payload.deadline)
    try:
        mission = mission_store.create_mission(db, owner=owner, payload=data)
    except ValueError as exc:
        raise _api_error(422, "validation_error", str(exc)) from exc
    db.commit()
    db.refresh(mission)
    return {"mission": mission_store.mission_to_dict(db, mission)}


@router.get(
    "/missions/{mission_id}",
    response_model=MissionResponse,
    summary="Read a mission (owner session or valid share token)",
    responses={
        401: {"model": ErrorResponse, "description": "Auth required"},
        403: {"model": ErrorResponse, "description": "Forbidden or invalid share token"},
        404: {"model": ErrorResponse, "description": "Mission not found"},
    },
)
def get_mission(
    mission: Mission = Depends(get_mission_for_read),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    db.commit()
    return {"mission": mission_store.mission_to_dict(db, mission)}


@router.post(
    "/missions/{mission_id}/discover",
    response_model=CatalogCandidatesResponse,
    summary="Discover real STAC catalog scenes for a mission AOI",
    description=(
        "Searches Microsoft Planetary Computer (Sentinel-1 GRD by default) over the "
        "mission area of interest and date range, then persists MissionDataCandidate "
        "rows with provenance. Never invents catalog items; upstream failures return "
        "typed catalog_* errors."
    ),
    responses={
        401: {"model": ErrorResponse, "description": "Missing session"},
        403: {"model": ErrorResponse, "description": "Not the mission owner"},
        404: {"model": ErrorResponse, "description": "Mission not found"},
        502: {"model": ErrorResponse, "description": "Catalog item/collection not found"},
        503: {
            "model": ErrorResponse,
            "description": "Catalog unavailable or rate-limited",
        },
    },
)
def discover_mission_catalog(
    mission: Mission = Depends(get_owned_mission),
    db: Session = Depends(get_db),
    payload: Optional[DiscoverRequest] = Body(default=None),
) -> Dict[str, Any]:
    body = payload or DiscoverRequest()
    try:
        rows = catalog_service.discover_for_mission(
            db,
            mission,
            start=_parse_optional_dt(body.start_time),
            end=_parse_optional_dt(body.end_time),
            collections=body.collections,
            limit=body.limit,
        )
    except CatalogError as exc:
        raise _catalog_http_error(exc) from exc
    db.commit()
    return {
        "candidates": [catalog_service.candidate_to_dict(db, row) for row in rows],
    }


@router.get(
    "/missions/{mission_id}/candidates",
    response_model=CatalogCandidatesResponse,
    summary="List persisted catalog candidates for a mission",
    responses={
        401: {"model": ErrorResponse, "description": "Auth required"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Mission not found"},
    },
)
def list_mission_candidates(
    mission: Mission = Depends(get_mission_for_read),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    rows = catalog_service.list_candidates(db, mission.id)
    db.commit()
    return {
        "candidates": [catalog_service.candidate_to_dict(db, row) for row in rows],
    }


@router.get(
    "/missions/{mission_id}/infrastructure",
    response_model=MissionInfrastructureResponse,
    summary="Mission-relevant satellites, ground stations, and orbital snapshot provenance",
    description=(
        "Returns only fleet satellites matching the mission's catalog candidates "
        "or data-source preferences (never the full tracked catalog), plus public "
        "ground stations and the TLE snapshot metadata used for contact windows."
    ),
    responses={
        401: {"model": ErrorResponse, "description": "Auth required"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Mission not found"},
    },
)
def get_mission_infrastructure(
    mission: Mission = Depends(get_mission_for_read),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    payload = infra_service.get_mission_infrastructure(
        db, mission, record_evidence=False
    )
    db.commit()
    return payload


@router.post(
    "/missions/{mission_id}/plans",
    response_model=MissionPlansGenerateResponse,
    status_code=201,
    summary="Generate source-backed mission plans",
    description=(
        "Runs the structured feasibility planner (no LLM). Each call appends a new "
        "version batch of MissionPlan rows; prior recommended flags are cleared. "
        "Same mission inputs + source snapshot → deterministic hashes and ranking."
    ),
    responses={
        401: {"model": ErrorResponse, "description": "Missing session"},
        403: {"model": ErrorResponse, "description": "Not the mission owner"},
        404: {"model": ErrorResponse, "description": "Mission not found"},
    },
)
def generate_mission_plans(
    mission: Mission = Depends(get_owned_mission),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    rows = planner_engine.generate_plans_for_mission(db, mission)
    db.commit()
    plans = [
        planner_engine.plan_to_dict(db, row, include_steps=True, include_evidence=True)
        for row in rows
    ]
    recommended_id = next(
        (p["id"] for p in plans if p.get("recommended")),
        None,
    )
    return {
        "plans": plans,
        "recommended_plan_id": recommended_id,
        "generation_strategy": (
            "append_versions — each POST appends a new version batch; "
            "prior recommended flags are cleared."
        ),
        "planner_config_version": PLANNER_CONFIG_VERSION,
    }


@router.get(
    "/missions/{mission_id}/plans",
    response_model=MissionPlansListResponse,
    summary="List generated mission plans",
    responses={
        401: {"model": ErrorResponse, "description": "Auth required"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Mission not found"},
    },
)
def list_mission_plans(
    mission: Mission = Depends(get_mission_for_read),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    rows = db.scalars(
        select(MissionPlan)
        .where(MissionPlan.mission_id == mission.id)
        .order_by(MissionPlan.version.asc())
    ).all()
    db.commit()
    return {
        "plans": [planner_engine.plan_to_dict(db, row) for row in rows],
        "generation_strategy": (
            "append_versions — each POST appends a new version batch; "
            "prior recommended flags are cleared."
        ),
    }


@router.get(
    "/missions/{mission_id}/plans/{plan_id}",
    response_model=MissionPlanDetailResponse,
    summary="Mission plan detail with steps and evidence",
    responses={
        401: {"model": ErrorResponse, "description": "Auth required"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Plan not found"},
    },
)
def get_mission_plan(
    plan_id: str,
    mission: Mission = Depends(get_mission_for_read),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    try:
        pid = UUID(plan_id)
    except ValueError as exc:
        raise _api_error(404, "plan_not_found", "Plan not found.") from exc
    row = db.get(MissionPlan, pid)
    if row is None or row.mission_id != mission.id:
        raise _api_error(404, "plan_not_found", "Plan not found.")
    db.commit()
    return {
        "plan": planner_engine.plan_to_dict(
            db, row, include_steps=True, include_evidence=True
        ),
    }


@router.post(
    "/missions/{mission_id}/share-links",
    response_model=ShareLinkResponse,
    status_code=201,
    summary="Create a private share link for a mission you own",
    description=(
        "Returns the raw share token once. Only the SHA-256 hash is stored. "
        "Pass the token as `X-Nomos-Share-Token` or `share_token` query param."
    ),
    responses={
        401: {"model": ErrorResponse, "description": "Missing session"},
        403: {"model": ErrorResponse, "description": "Not the mission owner"},
        404: {"model": ErrorResponse, "description": "Mission not found"},
    },
)
def create_share_link(
    payload: ShareLinkCreate,
    mission: Mission = Depends(get_owned_mission),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    expires_at = _parse_optional_dt(payload.expires_at)
    link, raw = mission_store.create_share_link(
        db,
        mission,
        settings=get_settings(),
        expires_at=expires_at,
        permissions=payload.permissions,
    )
    db.commit()
    return {
        "share_link": mission_store.share_link_to_dict(link, include_token=raw),
    }


@router.post(
    "/missions/{mission_id}/share-links/{share_link_id}/revoke",
    response_model=ShareLinkResponse,
    summary="Revoke a share link you own",
    responses={
        401: {"model": ErrorResponse, "description": "Missing session"},
        403: {"model": ErrorResponse, "description": "Not the mission owner"},
        404: {"model": ErrorResponse, "description": "Share link not found"},
    },
)
def revoke_share_link(
    share_link_id: str,
    mission: Mission = Depends(get_owned_mission),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    try:
        link_id = mission_store.parse_mission_id(share_link_id)
    except ValueError as exc:
        raise _api_error(404, "share_link_not_found", "Share link not found.") from exc

    link = db.get(ShareLink, link_id)
    if link is None or link.mission_id != mission.id:
        raise _api_error(404, "share_link_not_found", "Share link not found.")

    mission_store.revoke_share_link(link)
    db.commit()
    return {"share_link": mission_store.share_link_to_dict(link)}


@router.get(
    "/missions/{mission_id}/share-links",
    response_model=ShareLinkListResponse,
    summary="List share links for a mission you own",
    responses={
        401: {"model": ErrorResponse, "description": "Missing session"},
        403: {"model": ErrorResponse, "description": "Not the mission owner"},
        404: {"model": ErrorResponse, "description": "Mission not found"},
    },
)
def list_share_links(
    mission: Mission = Depends(get_owned_mission),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    rows = db.scalars(
        select(ShareLink)
        .where(ShareLink.mission_id == mission.id)
        .order_by(ShareLink.created_at.desc())
    ).all()
    db.commit()
    return {
        "share_links": [mission_store.share_link_to_dict(row) for row in rows],
    }


@router.get(
    "/share/{token}",
    response_model=ShareResolveResponse,
    summary="Resolve a private share token to its mission",
    description=(
        "Returns only the mission_id and link metadata for a valid token. "
        "Invalid, expired, or revoked tokens return 403 with no mission payload."
    ),
    responses={
        403: {"model": ErrorResponse, "description": "Invalid / expired / revoked"},
    },
)
def resolve_share_token(
    token: str,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    link = mission_store.get_active_share_link(db, token)
    if link is None:
        raise _api_error(
            403,
            "share_token_invalid",
            "Share link is invalid, expired, or revoked.",
        )
    db.commit()
    return {
        "mission_id": str(link.mission_id),
        "permissions": link.permissions or ["read"],
        "expires_at": link.expires_at.isoformat() if link.expires_at else None,
    }


@router.get(
    "/missions/{mission_id}/exports/json",
    response_model=MissionJsonExportResponse,
    summary="Download versioned mission brief JSON",
    responses={
        401: {"model": ErrorResponse, "description": "Auth required"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Mission not found"},
    },
)
def export_mission_json(
    mission: Mission = Depends(get_mission_for_read),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    document = build_mission_export_json(db, mission)
    db.commit()
    return document


@router.post(
    "/missions/{mission_id}/exports/pdf",
    response_model=MissionPdfExportResponse,
    status_code=201,
    summary="Generate a PDF mission brief",
    description=(
        "Owner-only. Creates an export job and generates the PDF (sync for MVP). "
        "Returns a signed download URL when ready. Large jobs may be processed by "
        "the ARQ worker via generate_mission_pdf_export."
    ),
    responses={
        401: {"model": ErrorResponse, "description": "Missing session"},
        403: {"model": ErrorResponse, "description": "Not the mission owner"},
        404: {"model": ErrorResponse, "description": "Mission not found"},
    },
)
def create_pdf_export(
    mission: Mission = Depends(get_owned_mission),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    row = export_service.create_and_generate_pdf_export(db, mission)
    db.commit()
    return {"export": export_service.export_to_dict(row)}


@router.get(
    "/missions/{mission_id}/exports/pdf",
    response_model=MissionPdfExportResponse,
    summary="Latest PDF export status / signed download URL",
    responses={
        401: {"model": ErrorResponse, "description": "Missing session"},
        403: {"model": ErrorResponse, "description": "Not the mission owner"},
        404: {"model": ErrorResponse, "description": "No export found"},
    },
)
def get_latest_pdf_export(
    mission: Mission = Depends(get_owned_mission),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    row = export_service.get_latest_pdf_export(db, mission.id)
    if row is None:
        raise _api_error(404, "export_not_found", "No PDF export found for this mission.")
    db.commit()
    return {"export": export_service.export_to_dict(row)}


@router.get(
    "/missions/{mission_id}/exports/pdf/{export_id}",
    response_model=MissionPdfExportResponse,
    summary="PDF export status by id",
    responses={
        401: {"model": ErrorResponse, "description": "Missing session"},
        403: {"model": ErrorResponse, "description": "Not the mission owner"},
        404: {"model": ErrorResponse, "description": "Export not found"},
    },
)
def get_pdf_export(
    export_id: str,
    mission: Mission = Depends(get_owned_mission),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    try:
        eid = mission_store.parse_mission_id(export_id)
    except ValueError as exc:
        raise _api_error(404, "export_not_found", "Export not found.") from exc
    row = export_service.get_export(db, eid)
    if row is None or row.mission_id != mission.id:
        raise _api_error(404, "export_not_found", "Export not found.")
    db.commit()
    return {"export": export_service.export_to_dict(row)}


# Keep owner type referenced for mypy/docs.
_ = AnonymousSession
_ = MissionExport
