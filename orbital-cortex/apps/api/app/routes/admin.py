"""Internal admin routes (not linked from customer-facing pages)."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.analytics.metrics import compute_analytics_summary
from app.db import get_db
from app.deps.admin import require_admin_token
from app.leads import service as leads_service

router = APIRouter(prefix="/v1/admin", tags=["admin"], include_in_schema=False)


@router.get("/analytics/summary")
def analytics_summary(
    db: Session = Depends(get_db),
    _: None = Depends(require_admin_token),
) -> Dict[str, Any]:
    return compute_analytics_summary(db)


@router.get("/leads/export")
def leads_export(
    db: Session = Depends(get_db),
    _: None = Depends(require_admin_token),
) -> Dict[str, Any]:
    feedback = [
        leads_service.feedback_to_model(row).model_dump(mode="json")
        for row in leads_service.list_all_feedback(db)
    ]
    requests = [
        leads_service.design_partner_to_model(row).model_dump(mode="json")
        for row in leads_service.list_all_design_partner_requests(db)
    ]
    return {
        "feedback": feedback,
        "design_partner_requests": requests,
        "generated_at": leads_service.utc_now().isoformat(),
    }
