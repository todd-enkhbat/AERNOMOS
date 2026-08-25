from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.feedback_rating import FeedbackRating
from ..types import UNSET, Unset

T = TypeVar("T", bound="MissionFeedback")


@_attrs_define
class MissionFeedback:
    """
    Attributes:
        created_at (datetime.datetime):
        id (UUID):
        mission_id (UUID):
        rating (FeedbackRating):
        comment (None | str | Unset):
        session_id_hash (None | str | Unset):
    """

    created_at: datetime.datetime
    id: UUID
    mission_id: UUID
    rating: FeedbackRating
    comment: None | str | Unset = UNSET
    session_id_hash: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at.isoformat()

        id = str(self.id)

        mission_id = str(self.mission_id)

        rating = self.rating.value

        comment: None | str | Unset
        if isinstance(self.comment, Unset):
            comment = UNSET
        else:
            comment = self.comment

        session_id_hash: None | str | Unset
        if isinstance(self.session_id_hash, Unset):
            session_id_hash = UNSET
        else:
            session_id_hash = self.session_id_hash

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "id": id,
                "mission_id": mission_id,
                "rating": rating,
            }
        )
        if comment is not UNSET:
            field_dict["comment"] = comment
        if session_id_hash is not UNSET:
            field_dict["session_id_hash"] = session_id_hash

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        id = UUID(d.pop("id"))

        mission_id = UUID(d.pop("mission_id"))

        rating = FeedbackRating(d.pop("rating"))

        def _parse_comment(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        comment = _parse_comment(d.pop("comment", UNSET))

        def _parse_session_id_hash(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        session_id_hash = _parse_session_id_hash(d.pop("session_id_hash", UNSET))

        mission_feedback = cls(
            created_at=created_at,
            id=id,
            mission_id=mission_id,
            rating=rating,
            comment=comment,
            session_id_hash=session_id_hash,
        )

        mission_feedback.additional_properties = d
        return mission_feedback

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
