from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset







T = TypeVar("T", bound="ContactWindow")



@_attrs_define
class ContactWindow:
    """ 
        Attributes:
            aos_utc (str):
            culminate_utc (str):
            date (str):
            duration_s (float):
            est_downlink_mb (float):
            ground_station_id (str):
            id (str):
            los_utc (str):
            max_elevation_deg (float):
            satellite_id (str):
     """

    aos_utc: str
    culminate_utc: str
    date: str
    duration_s: float
    est_downlink_mb: float
    ground_station_id: str
    id: str
    los_utc: str
    max_elevation_deg: float
    satellite_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        aos_utc = self.aos_utc

        culminate_utc = self.culminate_utc

        date = self.date

        duration_s = self.duration_s

        est_downlink_mb = self.est_downlink_mb

        ground_station_id = self.ground_station_id

        id = self.id

        los_utc = self.los_utc

        max_elevation_deg = self.max_elevation_deg

        satellite_id = self.satellite_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
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
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        aos_utc = d.pop("aos_utc")

        culminate_utc = d.pop("culminate_utc")

        date = d.pop("date")

        duration_s = d.pop("duration_s")

        est_downlink_mb = d.pop("est_downlink_mb")

        ground_station_id = d.pop("ground_station_id")

        id = d.pop("id")

        los_utc = d.pop("los_utc")

        max_elevation_deg = d.pop("max_elevation_deg")

        satellite_id = d.pop("satellite_id")

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
