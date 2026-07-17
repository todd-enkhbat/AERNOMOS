from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ShareLinkOut")


@_attrs_define
class ShareLinkOut:
    """
    Attributes:
        created_at (str):
        id (str):
        mission_id (str):
        expires_at (None | str | Unset):
        permissions (list[Any] | Unset):
        revoked_at (None | str | Unset):
        token (None | str | Unset):
    """

    created_at: str
    id: str
    mission_id: str
    expires_at: None | str | Unset = UNSET
    permissions: list[Any] | Unset = UNSET
    revoked_at: None | str | Unset = UNSET
    token: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at

        id = self.id

        mission_id = self.mission_id

        expires_at: None | str | Unset
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        else:
            expires_at = self.expires_at

        permissions: list[Any] | Unset = UNSET
        if not isinstance(self.permissions, Unset):
            permissions = self.permissions

        revoked_at: None | str | Unset
        if isinstance(self.revoked_at, Unset):
            revoked_at = UNSET
        else:
            revoked_at = self.revoked_at

        token: None | str | Unset
        if isinstance(self.token, Unset):
            token = UNSET
        else:
            token = self.token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "id": id,
                "mission_id": mission_id,
            }
        )
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at
        if permissions is not UNSET:
            field_dict["permissions"] = permissions
        if revoked_at is not UNSET:
            field_dict["revoked_at"] = revoked_at
        if token is not UNSET:
            field_dict["token"] = token

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_at = d.pop("created_at")

        id = d.pop("id")

        mission_id = d.pop("mission_id")

        def _parse_expires_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        expires_at = _parse_expires_at(d.pop("expires_at", UNSET))

        permissions = cast(list[Any], d.pop("permissions", UNSET))

        def _parse_revoked_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        revoked_at = _parse_revoked_at(d.pop("revoked_at", UNSET))

        def _parse_token(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        token = _parse_token(d.pop("token", UNSET))

        share_link_out = cls(
            created_at=created_at,
            id=id,
            mission_id=mission_id,
            expires_at=expires_at,
            permissions=permissions,
            revoked_at=revoked_at,
            token=token,
        )

        share_link_out.additional_properties = d
        return share_link_out

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
