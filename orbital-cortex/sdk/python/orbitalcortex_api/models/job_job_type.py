from enum import StrEnum


class JobJobType(StrEnum):
    CROP_HEALTH = "crop_health"
    DISASTER_RESPONSE = "disaster_response"
    SHIP_DETECTION = "ship_detection"

    def __str__(self) -> str:
        return str(self.value)
