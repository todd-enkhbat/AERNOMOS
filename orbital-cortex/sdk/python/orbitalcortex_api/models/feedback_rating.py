from enum import Enum


class FeedbackRating(str, Enum):
    NO = "no"
    PARTLY = "partly"
    YES = "yes"

    def __str__(self) -> str:
        return str(self.value)
