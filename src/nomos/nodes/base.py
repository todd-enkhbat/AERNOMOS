"""Abstract node interface.

Every orbital compute node — quantum, GPU, whatever comes online next —
implements this same interface. That's the point of the router: it
doesn't care what kind of node it's talking to, only whether the node
is available and can handle the job type.

No specific node (T-REX or otherwise) is wired into the skeleton yet.
Real integrations get built as subclasses of Node later.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import Job, JobResult


class Node(ABC):
    """Base class any orbital compute node must implement."""

    name: str
    capabilities: set[str]

    @abstractmethod
    def is_available(self) -> bool:
        """Whether this node can accept a job right now.

        Real implementations will check range windows / visibility here.
        For now, simulated nodes just return a fixed or randomized value.
        """

    def supports(self, job_type: str) -> bool:
        return job_type in self.capabilities

    @abstractmethod
    def run(self, job: Job) -> JobResult:
        """Execute the job and return a result. Must not raise for
        expected failure modes — those should come back as a FAILED
        JobResult so the router/logger can record them cleanly."""
