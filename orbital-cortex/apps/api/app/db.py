"""SQLite configuration for the local Orbital Cortex API."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Iterator


APP_DIR = Path(__file__).resolve().parent
API_DIR = APP_DIR.parent
REPO_ROOT = APP_DIR.parents[2]
DEFAULT_DB_PATH = API_DIR / "orbital_cortex.sqlite3"


def database_path() -> Path:
    configured = os.environ.get("ORBITAL_CORTEX_DB_PATH")
    if configured:
        return Path(configured).expanduser().resolve()
    return DEFAULT_DB_PATH


def connect() -> sqlite3.Connection:
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(path), check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_db() -> Iterator[sqlite3.Connection]:
    connection = connect()
    try:
        yield connection
    finally:
        connection.close()


def initialize_database() -> None:
    connection = connect()
    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                job_type TEXT NOT NULL,
                area_of_interest_json TEXT NOT NULL,
                sensor TEXT NOT NULL,
                priority TEXT NOT NULL,
                compute_preference TEXT NOT NULL,
                max_cost_usd REAL NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                selected_route_id TEXT
            );

            CREATE TABLE IF NOT EXISTS compute_nodes (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                location TEXT NOT NULL,
                orbit TEXT,
                gpu_class TEXT NOT NULL,
                supported_models_json TEXT NOT NULL,
                storage_gb INTEGER NOT NULL,
                downlink_mbps INTEGER NOT NULL,
                power_state TEXT NOT NULL,
                availability REAL NOT NULL,
                compliance_tags_json TEXT NOT NULL,
                base_cost_usd REAL NOT NULL,
                latency_minutes REAL NOT NULL,
                next_contact_minutes REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS ground_stations (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                latency_minutes REAL NOT NULL,
                downlink_mbps INTEGER NOT NULL,
                availability REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS routing_decisions (
                id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL UNIQUE,
                selected_node_id TEXT NOT NULL,
                selected_ground_station_id TEXT,
                fallback_node_id TEXT,
                estimated_latency_minutes REAL NOT NULL,
                estimated_cost_usd REAL NOT NULL,
                confidence REAL NOT NULL,
                reasons_json TEXT NOT NULL,
                candidate_scores_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS job_events (
                id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_job_events_job_id
                ON job_events(job_id);

            CREATE TABLE IF NOT EXISTS results (
                id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL UNIQUE,
                summary TEXT NOT NULL,
                confidence REAL NOT NULL,
                geojson_json TEXT NOT NULL,
                output_files_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(job_id) REFERENCES jobs(id) ON DELETE CASCADE
            );
            """
        )
        connection.commit()
    finally:
        connection.close()
