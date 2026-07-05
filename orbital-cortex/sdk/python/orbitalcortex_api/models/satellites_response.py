from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.satellite import Satellite


T = TypeVar("T", bound="SatellitesResponse")


@_attrs_define
class SatellitesResponse:
    """
    Example:
        {'satellites': [{'downlink_rate_mbps': 520.0, 'id': 'sat_sentinel_1a', 'name': 'SENTINEL-1A', 'norad_id': 39634,
            'snapshot_id': 'celestrak-2026-07-05', 'source': 'celestrak', 'tle_epoch': '2026-07-05T12:25:40+00:00',
            'tle_line1': '1 39634U 14016A   26186.51782528  .00000714  00000+0  19052-3 0  9995', 'tle_line2': '2 39634
            98.1813 187.6273 0001341  81.4767 278.6588 14.59198614652873'}]}

    Attributes:
        satellites (list['Satellite']):
    """

    satellites: list["Satellite"]
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
