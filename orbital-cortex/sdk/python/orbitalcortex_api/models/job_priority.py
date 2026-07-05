from enum import Enum

class JobPriority(str, Enum):
    CHEAPEST = "cheapest"
    FASTEST = "fastest"
    MOST_RELIABLE = "most_reliable"

    def __str__(self) -> str:
        return str(self.value)
