"""Typed API error models — the shape every error handler returns."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "job_not_found",
                    "message": "No job exists for id job_000000000000.",
                    "details": None,
                }
            }
        }
    )

    error: ErrorDetail
