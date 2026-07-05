"""Job event model definitions."""

from __future__ import annotations

from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field


class JobEvent(BaseModel):
    id: str
    job_id: str
    event_type: str
    message: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    ts_utc: str


class JobEventsResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "events": [
                    {
                        "id": "evt_1d4f8a2c6b3e",
                        "job_id": "job_9f2c41d3a8b7",
                        "event_type": "route_selected",
                        "message": (
                            "Selected sim_leo_01 at 87% route confidence; "
                            "latency 38 minutes, cost $84.00, fallback "
                            "aws_us_east_gpu."
                        ),
                        "payload": {
                            "status_from": "queued",
                            "status_to": "routing",
                            "routing_decision_id": "route_5b8e2f7c9d01",
                            "selected_node_id": "sim_leo_01",
                            "confidence": 0.87,
                        },
                        "ts_utc": "2026-07-05T14:00:01+00:00",
                    }
                ]
            }
        }
    )

    events: List[JobEvent]
