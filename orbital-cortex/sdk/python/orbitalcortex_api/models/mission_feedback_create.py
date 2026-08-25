from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..models.feedback_rating import FeedbackRating
from ..types import UNSET, Unset

T = TypeVar("T", bound="MissionFeedbackCreate")


@_attrs_define
class MissionFeedbackCreate:
    """
    Attributes:
        rating (FeedbackRating):
        comment (None | str | Unset):
    """

    rating: FeedbackRating
    comment: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        rating = self.rating.value

        comment: None | str | Unset
        if isinstance(self.comment, Unset):
            comment = UNSET
        else:
            comment = self.comment

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "rating": rating,
            }
        )
        if comment is not UNSET:
            field_dict["comment"] = comment

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        rating = FeedbackRating(d.pop("rating"))

        def _parse_comment(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        comment = _parse_comment(d.pop("comment", UNSET))

        mission_feedback_create = cls(
            rating=rating,
            comment=comment,
        )

        return mission_feedback_create
