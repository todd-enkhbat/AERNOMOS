"""F1: S3/R2 object-store round-trip against a mocked boto3 client.

The local-backend round-trip (upload, signed URL, tamper, expiry) lives in
test_platform.py; this covers the S3ObjectStore code path CI can't reach
with real credentials.
"""

import os

os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:1/0")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

import io
import sys
import types

import pytest

from app.core.config import Settings, get_settings


class FakeS3Client:
    """Mirrors exactly the boto3 S3 surface object_store uses."""

    def __init__(self) -> None:
        self.objects = {}
        self.presigned_calls = []

        class _NoSuchKey(Exception):
            pass

        self.exceptions = types.SimpleNamespace(NoSuchKey=_NoSuchKey)

    def put_object(self, Bucket, Key, Body, ContentType):  # noqa: N803
        self.objects[(Bucket, Key)] = (Body, ContentType)

    def get_object(self, Bucket, Key):  # noqa: N803
        if (Bucket, Key) not in self.objects:
            raise self.exceptions.NoSuchKey()
        body, _ = self.objects[(Bucket, Key)]
        return {"Body": io.BytesIO(body)}

    def generate_presigned_url(self, operation, Params, ExpiresIn):  # noqa: N803
        self.presigned_calls.append((operation, Params, ExpiresIn))
        return (
            f"https://{Params['Bucket']}.r2.example/{Params['Key']}"
            f"?X-Amz-Expires={ExpiresIn}&X-Amz-Signature=fake"
        )


@pytest.fixture
def fake_s3(monkeypatch):
    client = FakeS3Client()
    fake_boto3 = types.SimpleNamespace(client=lambda *args, **kwargs: client)
    monkeypatch.setitem(sys.modules, "boto3", fake_boto3)
    return client


def test_s3_round_trip_and_signed_url(fake_s3):
    from app.core.object_store import S3ObjectStore

    settings = Settings(
        s3_bucket="oc-artifacts",
        s3_endpoint_url="https://account.r2.cloudflarestorage.com",
        s3_access_key_id="test-key-id",
        s3_secret_access_key="test-secret",
        signed_url_expiry_s=900,
    )
    store = S3ObjectStore(settings)

    key = "results/job_test/detections.geojson"
    payload = b'{"type": "FeatureCollection", "features": []}'
    store.put_bytes(key, payload, "application/geo+json")

    stored_body, stored_content_type = fake_s3.objects[("oc-artifacts", key)]
    assert stored_body == payload
    assert stored_content_type == "application/geo+json"

    assert store.get_bytes(key) == payload
    assert store.get_bytes("results/job_test/missing.json") is None

    url = store.signed_url(key)
    assert url.startswith("https://oc-artifacts.r2.example/")
    operation, params, expires_in = fake_s3.presigned_calls[0]
    assert operation == "get_object"
    assert params == {"Bucket": "oc-artifacts", "Key": key}
    assert expires_in == 900


def test_s3_bucket_setting_selects_s3_backend(fake_s3, monkeypatch):
    from app.core import object_store

    monkeypatch.setenv("S3_BUCKET", "oc-artifacts")
    get_settings.cache_clear()
    try:
        store = object_store.get_object_store()
        assert isinstance(store, object_store.S3ObjectStore)
    finally:
        monkeypatch.undo()
        get_settings.cache_clear()


def test_empty_bucket_falls_back_to_local(monkeypatch):
    from app.core import object_store

    monkeypatch.delenv("S3_BUCKET", raising=False)
    get_settings.cache_clear()
    try:
        store = object_store.get_object_store()
        assert isinstance(store, object_store.LocalObjectStore)
    finally:
        monkeypatch.undo()
        get_settings.cache_clear()
