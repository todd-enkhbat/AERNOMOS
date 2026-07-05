import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nomos import JobStatus, NomosClient, SimulatedNode  # noqa: E402
from nomos.job_log import JobLogger  # noqa: E402
from nomos.router import NoAvailableNodeError, Router  # noqa: E402


def make_client(tmp_path, **node_kwargs):
    node = SimulatedNode(name="sim-node-1", capabilities={"generic-compute"}, **node_kwargs)
    logger = JobLogger(log_path=tmp_path / "jobs.jsonl")
    return NomosClient(nodes=[node], logger=logger), logger


def test_job_submits_routes_and_completes(tmp_path):
    client, logger = make_client(tmp_path, failure_rate=0.0)

    result = client.submit_job("generic-compute", {"n": 1})

    assert result.status == JobStatus.COMPLETED
    assert result.node_name == "sim-node-1"
    assert result.output == {"echo": {"n": 1}, "simulated": True}

    events = [e["event"] for e in logger.read_all()]
    assert events == ["submitted", "routed", "completed"]


def test_unsupported_job_type_fails_cleanly(tmp_path):
    client, logger = make_client(tmp_path)

    result = client.submit_job("quantum-annealing", {})

    assert result.status == JobStatus.FAILED
    assert "no registered node supports" in result.error

    events = [e["event"] for e in logger.read_all()]
    assert events == ["submitted", "failed"]


def test_router_raises_when_no_node_available(tmp_path):
    node = SimulatedNode(
        name="sim-node-1",
        capabilities={"generic-compute"},
        always_available=False,
        seed=1,
    )
    from nomos.models import Job

    router = Router([node])
    # Force unavailability regardless of the node's own randomness.
    node.is_available = lambda: False  # type: ignore[method-assign]

    try:
        router.select_node(Job(job_type="generic-compute"))
        assert False, "expected NoAvailableNodeError"
    except NoAvailableNodeError:
        pass


def test_simulated_failure_path_logs_failed(tmp_path):
    client, logger = make_client(tmp_path, failure_rate=1.0, seed=42)

    result = client.submit_job("generic-compute", {})

    assert result.status == JobStatus.FAILED
    assert result.node_name == "sim-node-1"

    events = [e["event"] for e in logger.read_all()]
    assert events == ["submitted", "routed", "failed"]
