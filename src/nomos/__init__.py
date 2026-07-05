"""Nomos Orbital — routing and orchestration layer for orbital compute.

MVS skeleton (v0.1): submit -> route -> log, against a single pluggable node.
Node integrations (T-REX or otherwise) are deliberately kept out of this
layer — see nomos.nodes.base.Node for the interface any real node must
implement later.
"""

from .client import NomosClient
from .models import Job, JobResult, JobStatus
from .nodes.base import Node
from .nodes.simulated import SimulatedNode
from .router import NoAvailableNodeError, Router

__all__ = [
    "NomosClient",
    "Job",
    "JobResult",
    "JobStatus",
    "Node",
    "SimulatedNode",
    "Router",
    "NoAvailableNodeError",
]

__version__ = "0.1.0"
