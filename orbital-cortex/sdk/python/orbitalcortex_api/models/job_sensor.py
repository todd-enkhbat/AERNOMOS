from enum import Enum


class JobSensor(str, Enum):
    ANY = "any"
    HYPERSPECTRAL = "hyperspectral"
    OPTICAL = "optical"
    SAR = "SAR"

    def __str__(self) -> str:
        return str(self.value)
