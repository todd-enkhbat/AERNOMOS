from enum import StrEnum


class JobCreatePriority(StrEnum):
    CHEAPEST = "cheapest"
    FASTEST = "fastest"
    MOST_RELIABLE = "most_reliable"

    def __str__(self) -> str:
        return str(self.value)
