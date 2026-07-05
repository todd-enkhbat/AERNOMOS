"""Retry policy shared by the sync and async clients.

GETs retry automatically on transport failures and 5xx responses with
exponential backoff + jitter (tenacity). Non-idempotent requests (POST)
never retry unless the caller opts in explicitly.
"""

from __future__ import annotations

from tenacity import (
    AsyncRetrying,
    Retrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential_jitter,
)

from orbitalcortex.exceptions import APIError, TransportError


def is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, TransportError):
        return True
    return isinstance(exc, APIError) and exc.status_code >= 500


def build_retrying(max_retries: int, backoff_s: float) -> Retrying:
    return Retrying(
        stop=stop_after_attempt(max_retries + 1),
        wait=wait_exponential_jitter(initial=backoff_s, max=4.0),
        retry=retry_if_exception(is_retryable),
        reraise=True,
    )


def build_async_retrying(max_retries: int, backoff_s: float) -> AsyncRetrying:
    return AsyncRetrying(
        stop=stop_after_attempt(max_retries + 1),
        wait=wait_exponential_jitter(initial=backoff_s, max=4.0),
        retry=retry_if_exception(is_retryable),
        reraise=True,
    )
