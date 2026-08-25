from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.provenanced_value import ProvenancedValue


T = TypeVar("T", bound="ContactWindow")


@_attrs_define
class ContactWindow:
    """
    Attributes:
        aos_utc (ProvenancedValue):
        culminate_utc (ProvenancedValue):
        date (str):
        duration_s (ProvenancedValue):
        est_downlink_mb (ProvenancedValue):
        ground_station_id (str):
        id (str):
        los_utc (ProvenancedValue):
        max_elevation_deg (ProvenancedValue):
        satellite_id (str):
        calculation_method (str | Unset):  Default: 'SGP4/Skyfield.find_events'.
        tle_snapshot_id (str | Unset):  Default: ''.
        truth_status (str | Unset):  Default: 'CALCULATED'.
    """

    aos_utc: ProvenancedValue
    culminate_utc: ProvenancedValue
    date: str
    duration_s: ProvenancedValue
    est_downlink_mb: ProvenancedValue
    ground_station_id: str
    id: str
    los_utc: ProvenancedValue
    max_elevation_deg: ProvenancedValue
    satellite_id: str
    calculation_method: str | Unset = "SGP4/Skyfield.find_events"
    tle_snapshot_id: str | Unset = ""
    truth_status: str | Unset = "CALCULATED"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        aos_utc = self.aos_utc.to_dict()

        culminate_utc = self.culminate_utc.to_dict()

        date = self.date

        duration_s = self.duration_s.to_dict()

        est_downlink_mb = self.est_downlink_mb.to_dict()

        ground_station_id = self.ground_station_id

        id = self.id

        los_utc = self.los_utc.to_dict()

        max_elevation_deg = self.max_elevation_deg.to_dict()

        satellite_id = self.satellite_id

        calculation_method = self.calculation_method

        tle_snapshot_id = self.tle_snapshot_id

        truth_status = self.truth_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "aos_utc": aos_utc,
                "culminate_utc": culminate_utc,
                "date": date,
                "duration_s": duration_s,
                "est_downlink_mb": est_downlink_mb,
                "ground_station_id": ground_station_id,
                "id": id,
                "los_utc": los_utc,
                "max_elevation_deg": max_elevation_deg,
                "satellite_id": satellite_id,
            }
        )
        if calculation_method is not UNSET:
            field_dict["calculation_method"] = calculation_method
        if tle_snapshot_id is not UNSET:
            field_dict["tle_snapshot_id"] = tle_snapshot_id
        if truth_status is not UNSET:
            field_dict["truth_status"] = truth_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.provenanced_value import ProvenancedValue

        d = dict(src_dict)
        aos_utc = ProvenancedValue.from_dict(d.pop("aos_utc"))

        culminate_utc = ProvenancedValue.from_dict(d.pop("culminate_utc"))

        date = d.pop("date")

        duration_s = ProvenancedValue.from_dict(d.pop("duration_s"))

        est_downlink_mb = ProvenancedValue.from_dict(d.pop("est_downlink_mb"))

        ground_station_id = d.pop("ground_station_id")

        id = d.pop("id")

        los_utc = ProvenancedValue.from_dict(d.pop("los_utc"))

        max_elevation_deg = ProvenancedValue.from_dict(d.pop("max_elevation_deg"))

        satellite_id = d.pop("satellite_id")

        calculation_method = d.pop("calculation_method", UNSET)

        tle_snapshot_id = d.pop("tle_snapshot_id", UNSET)

        truth_status = d.pop("truth_status", UNSET)

        contact_window = cls(
            aos_utc=aos_utc,
            culminate_utc=culminate_utc,
            date=date,
            duration_s=duration_s,
            est_downlink_mb=est_downlink_mb,
            ground_station_id=ground_station_id,
            id=id,
            los_utc=los_utc,
            max_elevation_deg=max_elevation_deg,
            satellite_id=satellite_id,
            calculation_method=calculation_method,
            tle_snapshot_id=tle_snapshot_id,
            truth_status=truth_status,
        )

        contact_window.additional_properties = d
        return contact_window

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
