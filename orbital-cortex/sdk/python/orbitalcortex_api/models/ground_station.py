from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GroundStation")


@_attrs_define
class GroundStation:
    """
    Attributes:
        availability (float):
        downlink_mbps (int):
        id (str):
        latency_minutes (float):
        latitude (float):
        location (str):
        longitude (float):
        name (str):
        altitude_m (float | Unset):  Default: 0.0.
        min_elevation_deg (float | Unset):  Default: 10.0.
        provider (str | Unset):  Default: ''.
    """

    availability: float
    downlink_mbps: int
    id: str
    latency_minutes: float
    latitude: float
    location: str
    longitude: float
    name: str
    altitude_m: float | Unset = 0.0
    min_elevation_deg: float | Unset = 10.0
    provider: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        availability = self.availability

        downlink_mbps = self.downlink_mbps

        id = self.id

        latency_minutes = self.latency_minutes

        latitude = self.latitude

        location = self.location

        longitude = self.longitude

        name = self.name

        altitude_m = self.altitude_m

        min_elevation_deg = self.min_elevation_deg

        provider = self.provider

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "availability": availability,
                "downlink_mbps": downlink_mbps,
                "id": id,
                "latency_minutes": latency_minutes,
                "latitude": latitude,
                "location": location,
                "longitude": longitude,
                "name": name,
            }
        )
        if altitude_m is not UNSET:
            field_dict["altitude_m"] = altitude_m
        if min_elevation_deg is not UNSET:
            field_dict["min_elevation_deg"] = min_elevation_deg
        if provider is not UNSET:
            field_dict["provider"] = provider

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        availability = d.pop("availability")

        downlink_mbps = d.pop("downlink_mbps")

        id = d.pop("id")

        latency_minutes = d.pop("latency_minutes")

        latitude = d.pop("latitude")

        location = d.pop("location")

        longitude = d.pop("longitude")

        name = d.pop("name")

        altitude_m = d.pop("altitude_m", UNSET)

        min_elevation_deg = d.pop("min_elevation_deg", UNSET)

        provider = d.pop("provider", UNSET)

        ground_station = cls(
            availability=availability,
            downlink_mbps=downlink_mbps,
            id=id,
            latency_minutes=latency_minutes,
            latitude=latitude,
            location=location,
            longitude=longitude,
            name=name,
            altitude_m=altitude_m,
            min_elevation_deg=min_elevation_deg,
            provider=provider,
        )

        ground_station.additional_properties = d
        return ground_station

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
