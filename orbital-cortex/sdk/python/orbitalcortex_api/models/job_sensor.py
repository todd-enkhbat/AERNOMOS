from enum import StrEnum


class JobSensor(StrEnum):
    ANY = "any"
    HYPERSPECTRAL = "hyperspectral"
    OPTICAL = "optical"
    SAR = "SAR"

    def __str__(self) -> str:
        return str(self.value)
