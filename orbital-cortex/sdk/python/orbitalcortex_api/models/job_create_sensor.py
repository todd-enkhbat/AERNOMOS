from enum import Enum


class JobCreateSensor(str, Enum):
    ANY = "any"
    HYPERSPECTRAL = "hyperspectral"
    OPTICAL = "optical"
    SAR = "SAR"

    def __str__(self) -> str:
        return str(self.value)
