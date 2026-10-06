from enum import StrEnum


class ComputeNodeType(StrEnum):
    GROUND_CLOUD = "ground_cloud"
    GROUND_STATION = "ground_station"
    ORBITAL = "orbital"

    def __str__(self) -> str:
        return str(self.value)
