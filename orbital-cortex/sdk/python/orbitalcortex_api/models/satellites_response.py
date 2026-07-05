from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.satellite import Satellite


T = TypeVar("T", bound="SatellitesResponse")


@_attrs_define
class SatellitesResponse:
    """
    Attributes:
        satellites (list[Satellite]):
    """

    satellites: list[Satellite]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        satellites = []
        for satellites_item_data in self.satellites:
            satellites_item = satellites_item_data.to_dict()
            satellites.append(satellites_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "satellites": satellites,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.satellite import Satellite

        d = dict(src_dict)
        satellites = []
        _satellites = d.pop("satellites")
        for satellites_item_data in _satellites:
            satellites_item = Satellite.from_dict(satellites_item_data)

            satellites.append(satellites_item)

        satellites_response = cls(
            satellites=satellites,
        )

        satellites_response.additional_properties = d
        return satellites_response

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
