"""Data contracts for mission feedback and design-partner requests."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

FEEDBACK_COMMENT_MAX_LEN = 500
HONEYPOT_FIELD = "website"


class FeedbackRating(str, Enum):
    YES = "yes"
    PARTLY = "partly"
    NO = "no"


class MissionFeedback(BaseModel):
    id: UUID
    mission_id: UUID
    session_id_hash: Optional[str] = None
    rating: FeedbackRating
    comment: Optional[str] = None
    created_at: datetime


class DesignPartnerRequest(BaseModel):
    id: UUID
    mission_id: Optional[UUID] = None
    name: str
    work_email: EmailStr
    organization: str
    role: str
    mission_type: str
    requested_integration: str
    permission_to_contact: bool
    created_at: datetime


class MissionFeedbackCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rating: FeedbackRating
    comment: Optional[str] = Field(default=None, max_length=FEEDBACK_COMMENT_MAX_LEN)

    @field_validator("comment")
    @classmethod
    def reject_overlong_comment(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            return None
        if len(stripped) > FEEDBACK_COMMENT_MAX_LEN:
            raise ValueError(
                f"comment must be at most {FEEDBACK_COMMENT_MAX_LEN} characters"
            )
        return stripped


class DesignPartnerRequestCreate(BaseModel):
    """Inbound create body. Honeypot is accepted separately at the route layer."""

    model_config = ConfigDict(extra="forbid")

    mission_id: Optional[UUID] = None
    name: str = Field(min_length=1, max_length=200)
    work_email: EmailStr
    organization: str = Field(min_length=1, max_length=200)
    role: str = Field(min_length=1, max_length=120)
    mission_type: str = Field(min_length=1, max_length=120)
    requested_integration: str = Field(min_length=1, max_length=200)
    permission_to_contact: bool

    @field_validator("permission_to_contact")
    @classmethod
    def require_permission(cls, value: bool) -> bool:
        if value is not True:
            raise ValueError("permission_to_contact must be true to submit")
        return value

    @field_validator(
        "name",
        "organization",
        "role",
        "mission_type",
        "requested_integration",
    )
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("field cannot be blank")
        return stripped


class MissionFeedbackResponse(BaseModel):
    feedback: MissionFeedback


class DesignPartnerRequestResponse(BaseModel):
    request: DesignPartnerRequest


class LeadsExportResponse(BaseModel):
    feedback: list[MissionFeedback]
    design_partner_requests: list[DesignPartnerRequest]
    generated_at: datetime
