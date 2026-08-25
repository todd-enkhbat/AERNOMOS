from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mission_ground_station_out_source_metadata import (
        MissionGroundStationOutSourceMetadata,
    )
    from ..models.provenanced_value import ProvenancedValue


T = TypeVar("T", bound="MissionGroundStationOut")


@_attrs_define
class MissionGroundStationOut:
    """
    Attributes:
        altitude_m (ProvenancedValue):
        availability (ProvenancedValue):
        downlink_mbps (ProvenancedValue):
        id (str):
        latency_minutes (ProvenancedValue):
        latitude (ProvenancedValue):
        location (str):
        longitude (ProvenancedValue):
        min_elevation_deg (ProvenancedValue):
        name (str):
        access_level (str | Unset):  Default: 'public_information'.
        coordinate_truth_status (str | Unset):  Default: 'PROVIDER_REPORTED'.
        ops_params_truth_status (str | Unset):  Default: 'SIMULATED'.
        provider (str | Unset):  Default: ''.
        resource_type (str | Unset):  Default: 'ground_station'.
        source_metadata (MissionGroundStationOutSourceMetadata | Unset):
        truth_status (str | Unset):  Default: 'PROVIDER_REPORTED'.
    """

    altitude_m: ProvenancedValue
    availability: ProvenancedValue
    downlink_mbps: ProvenancedValue
    id: str
    latency_minutes: ProvenancedValue
    latitude: ProvenancedValue
    location: str
    longitude: ProvenancedValue
    min_elevation_deg: ProvenancedValue
    name: str
    access_level: str | Unset = "public_information"
    coordinate_truth_status: str | Unset = "PROVIDER_REPORTED"
    ops_params_truth_status: str | Unset = "SIMULATED"
    provider: str | Unset = ""
    resource_type: str | Unset = "ground_station"
    source_metadata: MissionGroundStationOutSourceMetadata | Unset = UNSET
    truth_status: str | Unset = "PROVIDER_REPORTED"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        altitude_m = self.altitude_m.to_dict()

        availability = self.availability.to_dict()

        downlink_mbps = self.downlink_mbps.to_dict()

        id = self.id

        latency_minutes = self.latency_minutes.to_dict()

        latitude = self.latitude.to_dict()

        location = self.location

        longitude = self.longitude.to_dict()

        min_elevation_deg = self.min_elevation_deg.to_dict()

        name = self.name

        access_level = self.access_level

        coordinate_truth_status = self.coordinate_truth_status

        ops_params_truth_status = self.ops_params_truth_status

        provider = self.provider

        resource_type = self.resource_type

        source_metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.source_metadata, Unset):
            source_metadata = self.source_metadata.to_dict()

        truth_status = self.truth_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "altitude_m": altitude_m,
                "availability": availability,
                "downlink_mbps": downlink_mbps,
                "id": id,
                "latency_minutes": latency_minutes,
                "latitude": latitude,
                "location": location,
                "longitude": longitude,
                "min_elevation_deg": min_elevation_deg,
                "name": name,
            }
        )
        if access_level is not UNSET:
            field_dict["access_level"] = access_level
        if coordinate_truth_status is not UNSET:
            field_dict["coordinate_truth_status"] = coordinate_truth_status
        if ops_params_truth_status is not UNSET:
            field_dict["ops_params_truth_status"] = ops_params_truth_status
        if provider is not UNSET:
            field_dict["provider"] = provider
        if resource_type is not UNSET:
            field_dict["resource_type"] = resource_type
        if source_metadata is not UNSET:
            field_dict["source_metadata"] = source_metadata
        if truth_status is not UNSET:
            field_dict["truth_status"] = truth_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mission_ground_station_out_source_metadata import (
            MissionGroundStationOutSourceMetadata,
        )
        from ..models.provenanced_value import ProvenancedValue

        d = dict(src_dict)
        altitude_m = ProvenancedValue.from_dict(d.pop("altitude_m"))

        availability = ProvenancedValue.from_dict(d.pop("availability"))

        downlink_mbps = ProvenancedValue.from_dict(d.pop("downlink_mbps"))

        id = d.pop("id")

        latency_minutes = ProvenancedValue.from_dict(d.pop("latency_minutes"))

        latitude = ProvenancedValue.from_dict(d.pop("latitude"))

        location = d.pop("location")

        longitude = ProvenancedValue.from_dict(d.pop("longitude"))

        min_elevation_deg = ProvenancedValue.from_dict(d.pop("min_elevation_deg"))

        name = d.pop("name")

        access_level = d.pop("access_level", UNSET)

        coordinate_truth_status = d.pop("coordinate_truth_status", UNSET)

        ops_params_truth_status = d.pop("ops_params_truth_status", UNSET)

        provider = d.pop("provider", UNSET)

        resource_type = d.pop("resource_type", UNSET)

        _source_metadata = d.pop("source_metadata", UNSET)
        source_metadata: MissionGroundStationOutSourceMetadata | Unset
        if isinstance(_source_metadata, Unset):
            source_metadata = UNSET
        else:
            source_metadata = MissionGroundStationOutSourceMetadata.from_dict(
                _source_metadata
            )

        truth_status = d.pop("truth_status", UNSET)

        mission_ground_station_out = cls(
            altitude_m=altitude_m,
            availability=availability,
            downlink_mbps=downlink_mbps,
            id=id,
            latency_minutes=latency_minutes,
            latitude=latitude,
            location=location,
            longitude=longitude,
            min_elevation_deg=min_elevation_deg,
            name=name,
            access_level=access_level,
            coordinate_truth_status=coordinate_truth_status,
            ops_params_truth_status=ops_params_truth_status,
            provider=provider,
            resource_type=resource_type,
            source_metadata=source_metadata,
            truth_status=truth_status,
        )

        mission_ground_station_out.additional_properties = d
        return mission_ground_station_out

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
