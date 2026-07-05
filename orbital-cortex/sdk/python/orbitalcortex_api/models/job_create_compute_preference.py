from enum import Enum

class JobCreateComputePreference(str, Enum):
    CHEAPEST = "cheapest"
    FASTEST = "fastest"
    GROUND_ONLY = "ground_only"
    ORBITAL_IF_AVAILABLE = "orbital_if_available"

    def __str__(self) -> str:
        return str(self.value)
