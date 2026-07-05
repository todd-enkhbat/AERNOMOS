from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="Satellite")


@_attrs_define
class Satellite:
    """
    Attributes:
        downlink_rate_mbps (float):
        id (str):
        name (str):
        norad_id (int):
        snapshot_id (str):
        source (str):
        tle_epoch (str):
        tle_line1 (str):
        tle_line2 (str):
    """

    downlink_rate_mbps: float
    id: str
    name: str
    norad_id: int
    snapshot_id: str
    source: str
    tle_epoch: str
    tle_line1: str
    tle_line2: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        downlink_rate_mbps = self.downlink_rate_mbps

        id = self.id

        name = self.name

        norad_id = self.norad_id

        snapshot_id = self.snapshot_id

        source = self.source

        tle_epoch = self.tle_epoch

        tle_line1 = self.tle_line1

        tle_line2 = self.tle_line2

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "downlink_rate_mbps": downlink_rate_mbps,
                "id": id,
                "name": name,
                "norad_id": norad_id,
                "snapshot_id": snapshot_id,
                "source": source,
                "tle_epoch": tle_epoch,
                "tle_line1": tle_line1,
                "tle_line2": tle_line2,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        downlink_rate_mbps = d.pop("downlink_rate_mbps")

        id = d.pop("id")

        name = d.pop("name")

        norad_id = d.pop("norad_id")

        snapshot_id = d.pop("snapshot_id")

        source = d.pop("source")

        tle_epoch = d.pop("tle_epoch")

        tle_line1 = d.pop("tle_line1")

        tle_line2 = d.pop("tle_line2")

        satellite = cls(
            downlink_rate_mbps=downlink_rate_mbps,
            id=id,
            name=name,
            norad_id=norad_id,
            snapshot_id=snapshot_id,
            source=source,
            tle_epoch=tle_epoch,
            tle_line1=tle_line1,
            tle_line2=tle_line2,
        )

        satellite.additional_properties = d
        return satellite

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
