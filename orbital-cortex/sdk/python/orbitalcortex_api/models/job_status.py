from enum import Enum

class JobStatus(str, Enum):
    COMPLETE = "complete"
    DOWNLINKING = "downlinking"
    EXECUTING = "executing"
    FAILED = "failed"
    QUEUED = "queued"
    ROUTING = "routing"

    def __str__(self) -> str:
        return str(self.value)
