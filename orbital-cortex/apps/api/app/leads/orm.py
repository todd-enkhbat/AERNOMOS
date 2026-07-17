"""Private ORM tables for feedback and design-partner leads."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.orm import Base


class MissionFeedbackRow(Base):
    __tablename__ = "mission_feedback"
    __table_args__ = (
        Index("ix_mission_feedback_mission_id", "mission_id"),
        Index("ix_mission_feedback_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("missions.id", ondelete="CASCADE"),
        nullable=False,
    )
    session_id_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    rating: Mapped[str] = mapped_column(String(16), nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class DesignPartnerRequestRow(Base):
    __tablename__ = "design_partner_requests"
    __table_args__ = (
        Index("ix_design_partner_requests_mission_id", "mission_id"),
        Index("ix_design_partner_requests_created_at", "created_at"),
        Index("ix_design_partner_requests_organization", "organization"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    mission_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("missions.id", ondelete="SET NULL"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    work_email: Mapped[str] = mapped_column(String(320), nullable=False)
    organization: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(String(120), nullable=False)
    mission_type: Mapped[str] = mapped_column(String(120), nullable=False)
    requested_integration: Mapped[str] = mapped_column(String(200), nullable=False)
    permission_to_contact: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
