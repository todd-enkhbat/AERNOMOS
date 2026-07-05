"""F2 hardening behavior: CORS allow-list and the production config guard."""

import os

os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:1/0")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, cors_origin_list, validate_production_settings
from app.main import app

ALLOWED_ORIGIN = "http://localhost:3000"
DISALLOWED_ORIGIN = "https://evil.example"


def test_cors_allows_configured_origin_only():
    with TestClient(app) as client:
        allowed = client.get("/healthz", headers={"Origin": ALLOWED_ORIGIN})
        assert allowed.headers.get("access-control-allow-origin") == ALLOWED_ORIGIN

        denied = client.get("/healthz", headers={"Origin": DISALLOWED_ORIGIN})
        assert "access-control-allow-origin" not in denied.headers


def test_cors_preflight_rejects_unknown_origin():
    with TestClient(app) as client:
        preflight = client.options(
            "/v1/jobs",
            headers={
                "Origin": DISALLOWED_ORIGIN,
                "Access-Control-Request-Method": "POST",
            },
        )
        assert preflight.status_code == 400
        assert "access-control-allow-origin" not in preflight.headers

        allowed = client.options(
            "/v1/jobs",
            headers={
                "Origin": ALLOWED_ORIGIN,
                "Access-Control-Request-Method": "POST",
            },
        )
        assert allowed.status_code == 200
        assert allowed.headers["access-control-allow-origin"] == ALLOWED_ORIGIN


def test_cors_origin_list_parses_explicit_origins():
    settings = Settings(cors_origins="https://app.example.com, https://staging.example.com")
    assert cors_origin_list(settings) == [
        "https://app.example.com",
        "https://staging.example.com",
    ]
    assert "*" not in cors_origin_list(Settings())


def test_production_guard_rejects_dev_signing_secret():
    settings = Settings(
        app_env="production",
        s3_bucket="",
        artifact_signing_secret="dev-only-artifact-secret",
    )
    with pytest.raises(RuntimeError, match="forgeable"):
        validate_production_settings(settings)


def test_production_guard_rejects_wildcard_cors():
    settings = Settings(
        app_env="production",
        s3_bucket="oc-artifacts",
        cors_origins="*",
    )
    with pytest.raises(RuntimeError, match="never '\\*'"):
        validate_production_settings(settings)


def test_production_guard_accepts_hardened_config():
    settings = Settings(
        app_env="production",
        s3_bucket="oc-artifacts",
        cors_origins="https://app.example.com",
    )
    validate_production_settings(settings)


def test_production_guard_accepts_local_backend_with_real_secret():
    settings = Settings(
        app_env="production",
        s3_bucket="",
        artifact_signing_secret="a-genuinely-random-64-char-secret-set-via-fly-secrets",
        cors_origins="https://app.example.com",
    )
    validate_production_settings(settings)


def test_guard_is_inert_in_development():
    validate_production_settings(Settings(app_env="development"))
