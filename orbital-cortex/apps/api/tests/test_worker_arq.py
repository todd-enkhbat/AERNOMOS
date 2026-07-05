"""End-to-end: a job runs queued -> routing -> executing -> downlinking ->
complete through the real ARQ worker machinery.

Redis is replaced by fakeredis (same redis.asyncio wire behavior), so the
genuine ARQ path — enqueue_job, worker polling, deserialization, execute_job —
runs in-process without a server. Only the TCP transport is fake.
"""

import os

os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:1/0")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")

import asyncio

from arq.connections import ArqRedis
from arq.worker import Worker
from fakeredis import aioredis as fake_aioredis
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db import SessionLocal, get_engine
from app.main import app, run_migrations
from app.workers.executor import execute_job

PAYLOAD = {
    "job_type": "ship_detection",
    "area_of_interest": {"type": "bbox", "coordinates": [-74.3, 40.3, -73.5, 41.0]},
    "sensor": "SAR",
    "priority": "fastest",
    "compute_preference": "orbital_if_available",
    "max_cost_usd": 500,
}


def _reset_job_data() -> None:
    run_migrations()
    session = SessionLocal(bind=get_engine())
    try:
        session.execute(text("DELETE FROM jobs"))
        session.commit()
    finally:
        session.close()


async def _drain_queue_with_worker(job_id: str, monkeypatch) -> None:
    # arq logs `INFO Server` stats at startup; fakeredis has no INFO command.
    # Only the log line is skipped — the job path is untouched.
    async def _quiet_log_redis_info(redis, log_func) -> None:
        return None

    monkeypatch.setattr("arq.worker.log_redis_info", _quiet_log_redis_info)

    fake = fake_aioredis.FakeRedis()
    arq_redis = ArqRedis(connection_pool=fake.connection_pool)
    enqueued = await arq_redis.enqueue_job("execute_job", job_id)
    assert enqueued is not None
    worker = Worker(
        functions=[execute_job],
        redis_pool=arq_redis,
        burst=True,
        poll_delay=0.05,
        handle_signals=False,
    )
    try:
        await worker.main()
    finally:
        await worker.close()


def test_job_completes_end_to_end_via_arq_worker(monkeypatch):
    _reset_job_data()

    with TestClient(app) as client:
        created = client.post("/v1/jobs", json=PAYLOAD)
        assert created.status_code == 201
        job_id = created.json()["job"]["id"]

        # conftest points REDIS_URL at an unreachable port, so the API-side
        # enqueue fails and the job waits in `queued` for a worker.
        assert client.get(f"/v1/jobs/{job_id}").json()["job"]["status"] == "queued"

        asyncio.run(_drain_queue_with_worker(job_id, monkeypatch))

        job = client.get(f"/v1/jobs/{job_id}").json()["job"]
        assert job["status"] == "complete"

        # The event trail records every state-machine transition in order.
        events = client.get(f"/v1/jobs/{job_id}/events").json()["events"]
        transitions = [
            (e["payload"]["status_from"], e["payload"]["status_to"])
            for e in events
            if e["payload"] and "status_to" in e["payload"]
        ]
        assert transitions == [
            ("queued", "routing"),
            ("routing", "executing"),
            ("executing", "downlinking"),
            ("downlinking", "complete"),
        ]

        # Every read surface returns valid data for the completed job.
        routing = client.get(f"/v1/jobs/{job_id}/routing")
        assert routing.status_code == 200
        decision = routing.json()["routing_decision"]
        assert decision["selected_node_id"]
        assert decision["candidate_scores"]

        detections = client.get(f"/v1/jobs/{job_id}/detections")
        assert detections.status_code == 200
        collection = detections.json()
        assert collection["type"] == "FeatureCollection"
        assert collection["features"]

        scene = client.get(f"/v1/jobs/{job_id}/scene")
        assert scene.status_code == 200
        scene_body = scene.json()["scene"]
        assert scene_body["stac_item_id"]
        assert scene_body["aoi"]["type"] == "Polygon"

        replay = client.post(f"/v1/jobs/{job_id}/replay")
        assert replay.status_code == 200
        assert replay.json()["match"] is True
