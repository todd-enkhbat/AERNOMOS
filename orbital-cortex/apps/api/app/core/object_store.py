"""Object storage for result artifacts (F1).

Postgres stores only object keys; bytes live in S3-compatible storage
(Cloudflare R2 in production — zero egress) and are served via signed URLs.

Two backends behind one interface:
- S3ObjectStore: boto3 against R2/S3 when S3_BUCKET is configured.
- LocalObjectStore: filesystem fallback for dev/tests. Signed URLs point at
  GET /v1/artifacts/{key} with an expiring HMAC token, mirroring presigned
  S3 semantics so the rest of the app never branches on backend.
"""

from __future__ import annotations

import hashlib
import hmac
import time
from pathlib import Path
from typing import Optional, Protocol
from urllib.parse import quote

from app.core.config import Settings, get_settings


class ObjectStore(Protocol):
    def put_bytes(self, key: str, data: bytes, content_type: str) -> None:
        ...

    def get_bytes(self, key: str) -> Optional[bytes]:
        ...

    def signed_url(self, key: str) -> str:
        ...


class S3ObjectStore:
    def __init__(self, settings: Settings) -> None:
        import boto3

        self._bucket = settings.s3_bucket
        self._expiry_s = settings.signed_url_expiry_s
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url or None,
            region_name=settings.s3_region,
            aws_access_key_id=settings.s3_access_key_id or None,
            aws_secret_access_key=settings.s3_secret_access_key or None,
        )

    def put_bytes(self, key: str, data: bytes, content_type: str) -> None:
        self._client.put_object(
            Bucket=self._bucket, Key=key, Body=data, ContentType=content_type
        )

    def get_bytes(self, key: str) -> Optional[bytes]:
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
        except self._client.exceptions.NoSuchKey:
            return None
        return response["Body"].read()

    def signed_url(self, key: str) -> str:
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=self._expiry_s,
        )


def _local_signature(secret: str, key: str, expires: int) -> str:
    message = f"{key}|{expires}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()


class LocalObjectStore:
    def __init__(self, settings: Settings) -> None:
        self._root = Path(settings.artifact_dir)
        self._secret = settings.artifact_signing_secret
        self._expiry_s = settings.signed_url_expiry_s
        self._base_url = settings.public_base_url.rstrip("/")

    def _path(self, key: str) -> Path:
        path = (self._root / key).resolve()
        # Keys come from our own code, but never allow traversal outside root.
        if not str(path).startswith(str(self._root.resolve())):
            raise ValueError(f"artifact key escapes storage root: {key}")
        return path

    def put_bytes(self, key: str, data: bytes, content_type: str) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def get_bytes(self, key: str) -> Optional[bytes]:
        path = self._path(key)
        if not path.is_file():
            return None
        return path.read_bytes()

    def signed_url(self, key: str) -> str:
        expires = int(time.time()) + self._expiry_s
        signature = _local_signature(self._secret, key, expires)
        return (
            f"{self._base_url}/v1/artifacts/{quote(key)}"
            f"?expires={expires}&signature={signature}"
        )

    def verify(self, key: str, expires: int, signature: str) -> bool:
        if expires < int(time.time()):
            return False
        expected = _local_signature(self._secret, key, expires)
        return hmac.compare_digest(expected, signature)


def get_object_store() -> ObjectStore:
    settings = get_settings()
    if settings.s3_bucket:
        return S3ObjectStore(settings)
    return LocalObjectStore(settings)


def content_type_for(key: str) -> str:
    if key.endswith(".geojson"):
        return "application/geo+json"
    if key.endswith(".json"):
        return "application/json"
    if key.endswith(".tif") or key.endswith(".tiff"):
        return "image/tiff"
    return "application/octet-stream"
