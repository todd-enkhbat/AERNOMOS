from enum import StrEnum


class JobStatus(StrEnum):
    COMPLETE = "complete"
    DOWNLINKING = "downlinking"
    EXECUTING = "executing"
    FAILED = "failed"
    QUEUED = "queued"
    ROUTING = "routing"

    def __str__(self) -> str:
        return str(self.value)
