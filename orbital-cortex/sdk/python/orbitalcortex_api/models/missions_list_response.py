from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.mission_out import MissionOut


T = TypeVar("T", bound="MissionsListResponse")


@_attrs_define
class MissionsListResponse:
    """
    Attributes:
        missions (list[MissionOut]):
    """

    missions: list[MissionOut]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        missions = []
        for missions_item_data in self.missions:
            missions_item = missions_item_data.to_dict()
            missions.append(missions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "missions": missions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mission_out import MissionOut

        d = dict(src_dict)
        missions = []
        _missions = d.pop("missions")
        for missions_item_data in _missions:
            missions_item = MissionOut.from_dict(missions_item_data)

            missions.append(missions_item)

        missions_list_response = cls(
            missions=missions,
        )

        missions_list_response.additional_properties = d
        return missions_list_response

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
