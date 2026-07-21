"""Persist and generate mission PDF exports."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.object_store import get_object_store
from app.db.mission_orm import Mission, MissionExport
from app.exports.json_document import build_mission_export_json
from app.exports.pdf import render_mission_brief_pdf

logger = logging.getLogger(__name__)

EXPORT_TYPE_PDF = "pdf"
STATUS_QUEUED = "queued"
STATUS_READY = "ready"
STATUS_FAILED = "failed"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def export_to_dict(
    row: MissionExport, *, download_url: Optional[str] = None
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "id": str(row.id),
        "mission_id": str(row.mission_id),
        "export_type": row.export_type,
        "status": row.status,
        "artifact_key": row.artifact_key,
        "error_message": row.error_message,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "completed_at": row.completed_at.isoformat() if row.completed_at else None,
    }
    if download_url is not None:
        payload["download_url"] = download_url
    elif row.status == STATUS_READY and row.artifact_key:
        payload["download_url"] = get_object_store().signed_url(row.artifact_key)
    else:
        payload["download_url"] = None
    return payload


def get_export(db: Session, export_id: uuid.UUID) -> Optional[MissionExport]:
    return db.get(MissionExport, export_id)


def get_latest_pdf_export(db: Session, mission_id: uuid.UUID) -> Optional[MissionExport]:
    return db.scalars(
        select(MissionExport)
        .where(
            MissionExport.mission_id == mission_id,
            MissionExport.export_type == EXPORT_TYPE_PDF,
        )
        .order_by(MissionExport.created_at.desc())
    ).first()


def create_pdf_export_row(db: Session, mission: Mission) -> MissionExport:
    now = utc_now()
    row = MissionExport(
        id=uuid.uuid4(),
        mission_id=mission.id,
        export_type=EXPORT_TYPE_PDF,
        status=STATUS_QUEUED,
        artifact_key=None,
        error_message=None,
        created_at=now,
        completed_at=None,
    )
    db.add(row)
    db.flush()
    return row


def generate_pdf_export(db: Session, export_id: uuid.UUID) -> MissionExport:
    """Render PDF, upload to object store, mark ready/failed."""
    row = get_export(db, export_id)
    if row is None:
        raise ValueError(f"export not found: {export_id}")
    mission = db.get(Mission, row.mission_id)
    if mission is None:
        row.status = STATUS_FAILED
        row.error_message = "Mission not found"
        row.completed_at = utc_now()
        db.flush()
        return row

    try:
        document = build_mission_export_json(db, mission)
        pdf_bytes = render_mission_brief_pdf(document)
        key = f"missions/{mission.id}/exports/{row.id}.pdf"
        get_object_store().put_bytes(key, pdf_bytes, "application/pdf")
        row.artifact_key = key
        row.status = STATUS_READY
        row.error_message = None
        row.completed_at = utc_now()
    except Exception as exc:
        logger.exception("PDF export %s failed", export_id)
        row.status = STATUS_FAILED
        row.error_message = str(exc)[:2000]
        row.completed_at = utc_now()
    db.flush()
    return row


def create_and_generate_pdf_export(db: Session, mission: Mission) -> MissionExport:
    """MVP path: create row and generate synchronously (fast for typical briefs)."""
    row = create_pdf_export_row(db, mission)
    return generate_pdf_export(db, row.id)
