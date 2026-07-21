from enum import Enum


class TruthStatus(str, Enum):
    CALCULATED = "CALCULATED"
    ESTIMATED = "ESTIMATED"
    OBSERVED = "OBSERVED"
    PROVIDER_REPORTED = "PROVIDER_REPORTED"
    SIMULATED = "SIMULATED"
    STALE = "STALE"
    UNAVAILABLE = "UNAVAILABLE"

    def __str__(self) -> str:
        return str(self.value)
