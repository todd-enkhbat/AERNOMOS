from enum import Enum

class JobCreateJobType(str, Enum):
    CROP_HEALTH = "crop_health"
    DISASTER_RESPONSE = "disaster_response"
    SHIP_DETECTION = "ship_detection"

    def __str__(self) -> str:
        return str(self.value)
