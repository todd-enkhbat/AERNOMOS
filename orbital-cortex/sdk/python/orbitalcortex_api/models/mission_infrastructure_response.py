from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mission_ground_station_out import MissionGroundStationOut
    from ..models.mission_satellite_out import MissionSatelliteOut
    from ..models.orbital_snapshot_out import OrbitalSnapshotOut


T = TypeVar("T", bound="MissionInfrastructureResponse")


@_attrs_define
class MissionInfrastructureResponse:
    """
    Attributes:
        mission_id (str):
        orbital_snapshot (OrbitalSnapshotOut):
        ground_stations (list[MissionGroundStationOut] | Unset):
        satellites (list[MissionSatelliteOut] | Unset):
    """

    mission_id: str
    orbital_snapshot: OrbitalSnapshotOut
    ground_stations: list[MissionGroundStationOut] | Unset = UNSET
    satellites: list[MissionSatelliteOut] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        mission_id = self.mission_id

        orbital_snapshot = self.orbital_snapshot.to_dict()

        ground_stations: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.ground_stations, Unset):
            ground_stations = []
            for ground_stations_item_data in self.ground_stations:
                ground_stations_item = ground_stations_item_data.to_dict()
                ground_stations.append(ground_stations_item)

        satellites: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.satellites, Unset):
            satellites = []
            for satellites_item_data in self.satellites:
                satellites_item = satellites_item_data.to_dict()
                satellites.append(satellites_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "mission_id": mission_id,
                "orbital_snapshot": orbital_snapshot,
            }
        )
        if ground_stations is not UNSET:
            field_dict["ground_stations"] = ground_stations
        if satellites is not UNSET:
            field_dict["satellites"] = satellites

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mission_ground_station_out import MissionGroundStationOut
        from ..models.mission_satellite_out import MissionSatelliteOut
        from ..models.orbital_snapshot_out import OrbitalSnapshotOut

        d = dict(src_dict)
        mission_id = d.pop("mission_id")

        orbital_snapshot = OrbitalSnapshotOut.from_dict(d.pop("orbital_snapshot"))

        _ground_stations = d.pop("ground_stations", UNSET)
        ground_stations: list[MissionGroundStationOut] | Unset = UNSET
        if _ground_stations is not UNSET:
            ground_stations = []
            for ground_stations_item_data in _ground_stations:
                ground_stations_item = MissionGroundStationOut.from_dict(
                    ground_stations_item_data
                )

                ground_stations.append(ground_stations_item)

        _satellites = d.pop("satellites", UNSET)
        satellites: list[MissionSatelliteOut] | Unset = UNSET
        if _satellites is not UNSET:
            satellites = []
            for satellites_item_data in _satellites:
                satellites_item = MissionSatelliteOut.from_dict(satellites_item_data)

                satellites.append(satellites_item)

        mission_infrastructure_response = cls(
            mission_id=mission_id,
            orbital_snapshot=orbital_snapshot,
            ground_stations=ground_stations,
            satellites=satellites,
        )

        mission_infrastructure_response.additional_properties = d
        return mission_infrastructure_response

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
