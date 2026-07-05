from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.ground_station import GroundStation


T = TypeVar("T", bound="GroundStationsResponse")


@_attrs_define
class GroundStationsResponse:
    """
    Example:
        {'ground_stations': [{'altitude_m': 458.0, 'availability': 0.98, 'downlink_mbps': 600, 'id': 'gs_ksat_svalbard',
            'latency_minutes': 8.0, 'latitude': 78.23, 'location': 'Svalbard, Norway', 'longitude': 15.39,
            'min_elevation_deg': 10.0, 'name': 'KSAT Svalbard', 'provider': 'KSAT'}]}

    Attributes:
        ground_stations (list['GroundStation']):
    """

    ground_stations: list["GroundStation"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ground_stations = []
        for ground_stations_item_data in self.ground_stations:
            ground_stations_item = ground_stations_item_data.to_dict()
            ground_stations.append(ground_stations_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ground_stations": ground_stations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ground_station import GroundStation

        d = dict(src_dict)
        ground_stations = []
        _ground_stations = d.pop("ground_stations")
        for ground_stations_item_data in _ground_stations:
            ground_stations_item = GroundStation.from_dict(ground_stations_item_data)

            ground_stations.append(ground_stations_item)

        ground_stations_response = cls(
            ground_stations=ground_stations,
        )

        ground_stations_response.additional_properties = d
        return ground_stations_response

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
