from enum import StrEnum


class FeedbackRating(StrEnum):
    NO = "no"
    PARTLY = "partly"
    YES = "yes"

    def __str__(self) -> str:
        return str(self.value)
