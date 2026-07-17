"""SDK exceptions.

Two families live here:

* Legacy control-plane errors (``APIError``, ``TransportError``,
  ``JobTimeoutError``) used by the ``jobs`` / ``routing`` resources.
* Mission-planner typed errors (``NomosError`` and subclasses) used by the
  ``missions`` resource. Each maps to a real API error response — see
  ``orbital-cortex/docs/errors.md`` for the status-code + error-code table.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class OrbitalCortexError(Exception):
    """Base class for every SDK error."""


class APIError(OrbitalCortexError):
    """Raised when the API returns an error response with no more specific
    typed mapping."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        code: str = "api_error",
        response: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.response = response or {}

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(status_code={self.status_code!r}, "
            f"code={self.code!r}, message={str(self)!r})"
        )


class TransportError(OrbitalCortexError):
    """Raised when the SDK cannot reach the API."""


class JobTimeoutError(OrbitalCortexError):
    """Raised when wait_for_job exceeds its deadline before the job
    reaches a terminal state."""

    def __init__(self, message: str, *, job_id: str, last_status: str) -> None:
        super().__init__(message)
        self.job_id = job_id
        self.last_status = last_status


# --------------------------------------------------------------------------- #
# Mission-planner typed errors
# --------------------------------------------------------------------------- #


class NomosError(APIError):
    """Base for all mission SDK errors.

    Subclasses ``APIError`` so callers keep access to ``status_code``, ``code``,
    and the raw ``response`` while catching a specific, customer-meaningful
    exception type instead of a generic HTTP error.
    """


class NoCatalogData(NomosError):
    """No public catalog data was found for the mission's area/time.

    API: ``502 catalog_not_found``.
    """


class NoFeasiblePlan(NomosError):
    """The planner produced no feasible plan for the mission.

    Derived from a real ``201`` plan response whose ``recommended_plan_id`` is
    null and whose plans are all rejected/conditional. See ``errors.md``.
    """


class UpstreamProviderUnavailable(NomosError):
    """An upstream data/infrastructure provider was unavailable or rate-limited.

    API: ``503 catalog_unavailable`` / ``503 catalog_rate_limited``.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        code: str = "catalog_unavailable",
        response: Optional[Dict[str, Any]] = None,
        provider_name: Optional[str] = None,
    ) -> None:
        super().__init__(
            message, status_code=status_code, code=code, response=response
        )
        # Which provider failed, for actionable debugging.
        self.provider_name = provider_name


class UnauthorizedMission(NomosError):
    """The session is missing, or the mission belongs to another session.

    API: ``401 session_required`` / ``403 mission_forbidden``.
    """


class ExpiredShareLink(NomosError):
    """A share token is invalid, expired, or revoked.

    API: ``403 share_token_invalid``.
    """


class StaleOrbitalData(NomosError):
    """Orbital data used for the mission is stale.

    Reserved: the API currently surfaces staleness as a ``STALE`` truth status
    on the infrastructure payload rather than an HTTP error. The SDK raises this
    from :meth:`MissionsResource.infrastructure` when ``raise_on_stale=True``.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 0,
        code: str = "stale_orbital_data",
        response: Optional[Dict[str, Any]] = None,
        age_hours: Optional[float] = None,
    ) -> None:
        super().__init__(
            message, status_code=status_code, code=code, response=response
        )
        # Concrete age of the orbital snapshot, not just "stale".
        self.age_hours = age_hours


class InvalidGeographicInput(NomosError):
    """The area of interest was rejected as invalid geographic input.

    API: ``422 validation_error`` where the failing field is ``area_of_interest``.
    """


class MissionValidationError(NomosError):
    """A request field failed validation (non-geographic).

    API: ``422 validation_error``.
    """


# Direct code → exception mappings (unambiguous cases).
_CODE_TO_ERROR = {
    "session_required": UnauthorizedMission,
    "mission_forbidden": UnauthorizedMission,
    "share_token_invalid": ExpiredShareLink,
    "catalog_not_found": NoCatalogData,
    "catalog_unavailable": UpstreamProviderUnavailable,
    "catalog_rate_limited": UpstreamProviderUnavailable,
    "no_feasible_plan": NoFeasiblePlan,
    "stale_orbital_data": StaleOrbitalData,
}


def _mentions_geographic_input(message: str, error: Dict[str, Any]) -> bool:
    haystacks = [message or ""]
    details = error.get("details")
    if isinstance(details, list):
        for item in details:
            if isinstance(item, dict):
                loc = item.get("loc")
                if isinstance(loc, (list, tuple)):
                    haystacks.extend(str(part) for part in loc)
                haystacks.append(str(item.get("msg", "")))
    provider = error.get("field")
    if provider:
        haystacks.append(str(provider))
    text = " ".join(haystacks).lower()
    return "area_of_interest" in text or "geojson" in text or "aoi" in text


def error_from_response(
    *,
    status_code: int,
    code: str,
    message: str,
    response: Optional[Dict[str, Any]] = None,
) -> APIError:
    """Map an API error envelope to the most specific SDK exception.

    Falls back to :class:`APIError` for codes with no typed mapping so the
    legacy control-plane resources keep their existing behavior.
    """
    payload = response or {}
    error = payload.get("error", {}) if isinstance(payload, dict) else {}

    if code == "validation_error":
        if _mentions_geographic_input(message, error if isinstance(error, dict) else {}):
            return InvalidGeographicInput(
                message, status_code=status_code, code=code, response=payload
            )
        return MissionValidationError(
            message, status_code=status_code, code=code, response=payload
        )

    cls = _CODE_TO_ERROR.get(code)
    if cls is UpstreamProviderUnavailable:
        provider_name = None
        if isinstance(error, dict):
            provider_name = error.get("provider")
        return UpstreamProviderUnavailable(
            message,
            status_code=status_code,
            code=code,
            response=payload,
            provider_name=provider_name,
        )
    if cls is not None:
        return cls(message, status_code=status_code, code=code, response=payload)

    return APIError(message, status_code=status_code, code=code, response=payload)
