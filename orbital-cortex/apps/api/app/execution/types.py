"""Execution data contracts — defined exactly once, imported everywhere.

Every module in the execution path (provider, runner, worker, routes, tests)
must import these shapes instead of redefining them.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

ExecutionStatusLiteral = Literal["queued", "running", "succeeded", "failed"]

STATUS_QUEUED = "queued"
STATUS_RUNNING = "running"
STATUS_SUCCEEDED = "succeeded"
STATUS_FAILED = "failed"

TASK_CROP_GEOTIFF = "crop_geotiff"
TASK_THUMBNAIL = "thumbnail"
SUPPORTED_TASK_TYPES = [TASK_CROP_GEOTIFF, TASK_THUMBNAIL]

# Plan-step types that may be executed by the local CPU provider.
EXECUTABLE_STEP_TYPES = frozenset({"cloud_process", "edge_process"})

# Persisted MissionPlanStep.execution_status values.
STEP_EXECUTION_PLANNED = "planned"
STEP_EXECUTION_RUNNING = "running"
STEP_EXECUTION_EXECUTED = "executed"
STEP_EXECUTION_FAILED = "failed"


class ExecutionError(Exception):
    """Base class for execution failures with a human-readable message."""


class ExecutionValidationError(ExecutionError):
    """Invalid task input (bad task_type, disallowed input_ref, bad params)."""


class ExecutionStateError(ExecutionError):
    """Operation not valid for the job's current state."""


class ProviderCapabilities(BaseModel):
    provider_id: str
    supported_task_types: List[str]
    max_input_bytes: int
    max_execution_seconds: int


class ExecutionTask(BaseModel):
    task_type: str  # "crop_geotiff" | "thumbnail"
    input_ref: str  # "fixture:<name>" or "artifact:<object-store-key>"
    params: Dict[str, Any] = Field(default_factory=dict)


class ExecutionEstimate(BaseModel):
    estimated_seconds: float
    estimated_cost_usd: float  # 0.0 for local CPU; kept for future providers


class ExternalJob(BaseModel):
    external_job_id: str
    idempotency_key: str
    status: ExecutionStatusLiteral


class ExternalJobStatus(BaseModel):
    external_job_id: str
    status: ExecutionStatusLiteral
    error: Optional[str] = None


class ObservedMetrics(BaseModel):
    transfer_seconds: float
    execution_seconds: float
    input_bytes: int
    output_bytes: int
    storage_location: str


class ExecutionResult(BaseModel):
    external_job_id: str
    output_ref: str  # "artifact:<object-store-key>"
    observed: ObservedMetrics


# --- API request / response wrappers (same single-definition module) -------


class ExecuteStepRequest(BaseModel):
    step_id: str
    task_type: str
    input_ref: str
    params: Dict[str, Any] = Field(default_factory=dict)
    # Optional; a deterministic key is derived from (plan, step, task) when
    # omitted so client retries of the same request are idempotent.
    idempotency_key: Optional[str] = Field(default=None, max_length=128)


class ExecuteStepResponse(BaseModel):
    job: ExternalJob
    estimate: ExecutionEstimate
    plan_step_id: str
    provider_id: str


class ExecutionStatusResponse(BaseModel):
    job: ExternalJobStatus
    task_type: str
    plan_step_id: Optional[str] = None
    # Present only when the job succeeded. Observed values are measured
    # (OBSERVED); they are never estimated or stubbed.
    result: Optional[ExecutionResult] = None
    observed_truth_status: Optional[str] = None
    download_url: Optional[str] = None
