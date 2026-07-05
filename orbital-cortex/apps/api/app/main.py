"""FastAPI application entrypoint for the Orbital Cortex control plane."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config as AlembicConfig
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db import SessionLocal, get_engine
from app.routes import jobs, nodes, registry, results, routing
from app.seed import seed_database

API_DIR = Path(__file__).resolve().parents[1]


def run_migrations() -> None:
    alembic_config = AlembicConfig(str(API_DIR / "alembic.ini"))
    alembic_config.set_main_option("script_location", str(API_DIR / "migrations"))
    command.upgrade(alembic_config, "head")


def warm_pass_cache_if_empty() -> None:
    """Bare-dev fallback: if no worker has populated upcoming contact
    windows, compute them once at boot so routing has real pass data."""
    from app.core.storage import utc_now
    from app.services.contact_windows import list_windows, precompute_windows
    from app.core.config import get_settings

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
    yield


app = FastAPI(
    title="Orbital Cortex API",
    version="0.1.0",
    description="Local simulated orbital compute orchestration control plane.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "orbital-cortex-api"}


app.include_router(jobs.router)
app.include_router(nodes.router)
app.include_router(registry.router)
app.include_router(routing.router)
app.include_router(results.router)
