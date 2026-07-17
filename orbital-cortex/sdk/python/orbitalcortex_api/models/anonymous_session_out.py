from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AnonymousSessionOut")


@_attrs_define
class AnonymousSessionOut:
    """
    Attributes:
        created_at (str):
        expires_at (str):
        id (str):
        last_seen_at (str):
        converted_user_id (None | str | Unset):
    """

    created_at: str
    expires_at: str
    id: str
    last_seen_at: str
    converted_user_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at

        expires_at = self.expires_at

        id = self.id

        last_seen_at = self.last_seen_at

        converted_user_id: None | str | Unset
        if isinstance(self.converted_user_id, Unset):
            converted_user_id = UNSET
        else:
            converted_user_id = self.converted_user_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "expires_at": expires_at,
                "id": id,
                "last_seen_at": last_seen_at,
            }
        )
        if converted_user_id is not UNSET:
            field_dict["converted_user_id"] = converted_user_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_at = d.pop("created_at")

        expires_at = d.pop("expires_at")

        id = d.pop("id")

        last_seen_at = d.pop("last_seen_at")

        def _parse_converted_user_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        converted_user_id = _parse_converted_user_id(d.pop("converted_user_id", UNSET))

        anonymous_session_out = cls(
            created_at=created_at,
            expires_at=expires_at,
            id=id,
            last_seen_at=last_seen_at,
            converted_user_id=converted_user_id,
        )

        anonymous_session_out.additional_properties = d
        return anonymous_session_out

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
