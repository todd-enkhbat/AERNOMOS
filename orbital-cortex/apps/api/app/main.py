"""FastAPI application entrypoint for the Nomos Orbital control plane."""

from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from app.core.config import cors_origin_list, get_settings
from app.core.logging import configure_logging, get_logger
from app.core.ratelimit import limiter
from app.db import SessionLocal, get_engine
from app.db.migrate import run_migrations
from app.routes import artifacts, jobs, missions, nodes, registry, results, routing, sessions
from app.seed import seed_database

API_DIR = Path(__file__).resolve().parents[1]

configure_logging()
logger = get_logger()

settings = get_settings()
if settings.sentry_dsn:
    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.app_env,
        traces_sample_rate=0.1,
    )


def warm_pass_cache_if_empty() -> None:
    """Bare-dev fallback: if no worker has populated upcoming contact
    windows, compute them once at boot so routing has real pass data."""
    from app.core.storage import utc_now
    from app.services.contact_windows import list_windows, precompute_windows

    session = SessionLocal(bind=get_engine())
    try:
        upcoming = list_windows(session, after_utc=utc_now(), limit=1)
        if not upcoming:
            precompute_windows(session, horizon_hours=get_settings().pass_horizon_hours)
            session.commit()
    finally:
        session.close()


@asynccontextmanager
async def lifespan(app):  # type: ignore[no-untyped-def]
    run_migrations()
    session = SessionLocal(bind=get_engine())
    try:
        seed_database(session)
    finally:
        session.close()
    warm_pass_cache_if_empty()
    logger.info("startup_complete", env=settings.app_env)
    yield


OPENAPI_TAGS = [
    {"name": "sessions", "description": "Private anonymous sessions (cookie-scoped)."},
    {
        "name": "missions",
        "description": "Private mission plans scoped to anonymous sessions or share tokens.",
    },
    {"name": "jobs", "description": "Submit and track EO analysis jobs."},
    {
        "name": "routing",
        "description": "Explainable routing decisions and deterministic replay.",
    },
    {"name": "results", "description": "Result manifests and signed artifact URLs."},
    {"name": "nodes", "description": "Simulated compute-node registry."},
    {
        "name": "registry",
        "description": "Ground stations, satellites (pinned TLEs), and SGP4 contact windows.",
    },
    {"name": "artifacts", "description": "Signed-URL artifact serving (local backend)."},
    {"name": "health", "description": "Liveness and readiness probes."},
]

app = FastAPI(
    title="Nomos Orbital API",
    version="0.1.0",
    description=(
        "Orbital compute orchestration control plane for space-data AI jobs. "
        "Civilian/commercial maritime domain awareness only; simulated and "
        "real data are labeled per record."
    ),
    lifespan=lifespan,
    openapi_tags=OPENAPI_TAGS,
)

app.state.limiter = limiter

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origin_list(settings),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context(request, call_next):  # type: ignore[no-untyped-def]
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("request_failed")
        structlog.contextvars.clear_contextvars()
        raise
    duration_ms = round((time.perf_counter() - started) * 1000, 1)
    logger.info(
        "request_completed",
        status_code=response.status_code,
        duration_ms=duration_ms,
    )
    structlog.contextvars.clear_contextvars()
    response.headers["x-request-id"] = request_id
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):  # type: ignore[no-untyped-def]
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "http_error",
                "message": str(exc.detail),
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):  # type: ignore[no-untyped-def]
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed.",
                "details": jsonable_encoder(exc.errors()),
            }
        },
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):  # type: ignore[no-untyped-def]
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": "rate_limited",
                "message": f"Rate limit exceeded: {exc.detail}.",
            }
        },
    )


@app.get("/health", tags=["health"], include_in_schema=False)
def health() -> dict:
    # Legacy alias kept for older SDK versions; use /healthz.
    return {"status": "ok", "service": "nomos-orbital-api"}


@app.get("/healthz", tags=["health"], summary="Liveness probe")
def healthz() -> dict:
    return {"status": "ok", "service": "nomos-orbital-api"}


@app.get(
    "/readyz",
    tags=["health"],
    summary="Readiness probe",
    description=(
        "503 until the database answers. Redis is reported but optional: "
        "without it, jobs queue and run via the manual dev path."
    ),
)
def readyz() -> JSONResponse:
    from app.core.queue import ping_redis

    checks = {"database": False, "redis": False}
    try:
        session = SessionLocal(bind=get_engine())
        try:
            session.execute(text("SELECT 1"))
            checks["database"] = True
        finally:
            session.close()
    except Exception:
        pass
    checks["redis"] = ping_redis()

    ready = checks["database"]
    return JSONResponse(
        status_code=200 if ready else 503,
        content={
            "status": "ready" if ready else "unavailable",
            "checks": checks,
        },
    )


app.include_router(sessions.router)
app.include_router(missions.router)
app.include_router(jobs.router)
app.include_router(nodes.router)
app.include_router(registry.router)
app.include_router(routing.router)
app.include_router(results.router)
app.include_router(artifacts.router)
