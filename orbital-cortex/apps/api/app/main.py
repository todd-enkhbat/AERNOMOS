"""FastAPI application entrypoint for the Orbital Cortex control plane."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db import connect, initialize_database
from app.routes import jobs, nodes, results, routing
from app.seed import seed_database


@asynccontextmanager
async def lifespan(app):  # type: ignore[no-untyped-def]
    initialize_database()
    connection = connect()
    try:
        seed_database(connection)
    finally:
        connection.close()
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
                "details": exc.errors(),
            }
        },
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "orbital-cortex-api"}


app.include_router(jobs.router)
app.include_router(nodes.router)
app.include_router(routing.router)
app.include_router(results.router)
