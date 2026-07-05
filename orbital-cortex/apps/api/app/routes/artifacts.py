"""Signed-URL artifact serving for the local object-store backend.

Production (R2/S3) serves presigned URLs directly from the bucket; this
route only exists so the filesystem backend has the same signed-URL
contract in dev and tests.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Response

from app.core.object_store import LocalObjectStore, content_type_for, get_object_store
from app.models.errors import ErrorResponse

router = APIRouter(prefix="/v1", tags=["artifacts"])


@router.get(
    "/artifacts/{key:path}",
    summary="Fetch an artifact via a signed URL (local backend only)",
    responses={
        403: {"model": ErrorResponse, "description": "Bad or expired signature"},
        404: {"model": ErrorResponse, "description": "Artifact not found"},
    },
)
def get_artifact(
    key: str,
    expires: int = Query(...),
    signature: str = Query(...),
) -> Response:
    store = get_object_store()
    if not isinstance(store, LocalObjectStore):
        raise _api_error(
            404,
            "artifact_route_disabled",
            "Artifacts are served directly from object storage in this environment.",
        )
    if not store.verify(key, expires, signature):
        raise _api_error(403, "invalid_signature", "Signature is invalid or expired.")
    data = store.get_bytes(key)
    if data is None:
        raise _api_error(404, "artifact_not_found", f"No artifact exists at {key}.")
    return Response(content=data, media_type=content_type_for(key))


def _api_error(status_code: int, code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail={"error": {"code": code, "message": message}},
    )
