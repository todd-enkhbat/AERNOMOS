from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MissionExportOut")


@_attrs_define
class MissionExportOut:
    """
    Attributes:
        export_type (str):
        id (str):
        mission_id (str):
        status (str):
        artifact_key (None | str | Unset):
        completed_at (None | str | Unset):
        created_at (None | str | Unset):
        download_url (None | str | Unset):
        error_message (None | str | Unset):
    """

    export_type: str
    id: str
    mission_id: str
    status: str
    artifact_key: None | str | Unset = UNSET
    completed_at: None | str | Unset = UNSET
    created_at: None | str | Unset = UNSET
    download_url: None | str | Unset = UNSET
    error_message: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        export_type = self.export_type

        id = self.id

        mission_id = self.mission_id

        status = self.status

        artifact_key: None | str | Unset
        if isinstance(self.artifact_key, Unset):
            artifact_key = UNSET
        else:
            artifact_key = self.artifact_key

        completed_at: None | str | Unset
        if isinstance(self.completed_at, Unset):
            completed_at = UNSET
        else:
            completed_at = self.completed_at

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        else:
            created_at = self.created_at

        download_url: None | str | Unset
        if isinstance(self.download_url, Unset):
            download_url = UNSET
        else:
            download_url = self.download_url

        error_message: None | str | Unset
        if isinstance(self.error_message, Unset):
            error_message = UNSET
        else:
            error_message = self.error_message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "export_type": export_type,
                "id": id,
                "mission_id": mission_id,
                "status": status,
            }
        )
        if artifact_key is not UNSET:
            field_dict["artifact_key"] = artifact_key
        if completed_at is not UNSET:
            field_dict["completed_at"] = completed_at
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if download_url is not UNSET:
            field_dict["download_url"] = download_url
        if error_message is not UNSET:
            field_dict["error_message"] = error_message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        export_type = d.pop("export_type")

        id = d.pop("id")

        mission_id = d.pop("mission_id")

        status = d.pop("status")

        def _parse_artifact_key(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        artifact_key = _parse_artifact_key(d.pop("artifact_key", UNSET))

        def _parse_completed_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        completed_at = _parse_completed_at(d.pop("completed_at", UNSET))

        def _parse_created_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        def _parse_download_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        download_url = _parse_download_url(d.pop("download_url", UNSET))

        def _parse_error_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error_message = _parse_error_message(d.pop("error_message", UNSET))

        mission_export_out = cls(
            export_type=export_type,
            id=id,
            mission_id=mission_id,
            status=status,
            artifact_key=artifact_key,
            completed_at=completed_at,
            created_at=created_at,
            download_url=download_url,
            error_message=error_message,
        )

        mission_export_out.additional_properties = d
        return mission_export_out

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
