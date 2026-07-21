"""Privacy-safe product and planning analytics (Phase O)."""

from app.analytics.emitter import AnalyticsPayloadError, emit_event
from app.analytics.schemas import EventName, PlanningFailureReason

__all__ = [
    "AnalyticsPayloadError",
    "EventName",
    "PlanningFailureReason",
    "emit_event",
]
