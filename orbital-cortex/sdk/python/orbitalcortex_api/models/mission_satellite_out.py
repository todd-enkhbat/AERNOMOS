from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.provenanced_value import ProvenancedValue


T = TypeVar("T", bound="MissionSatelliteOut")


@_attrs_define
class MissionSatelliteOut:
    """
    Attributes:
        downlink_rate_mbps (ProvenancedValue):
        id (str):
        name (str):
        norad_id (int):
        snapshot_id (str):
        source (str):
        tle_epoch (ProvenancedValue):
        truth_status (str):
        access_level (str | Unset):  Default: 'public_information'.
        resource_type (str | Unset):  Default: 'satellite'.
        retrieved_at (None | str | Unset):
    """

    downlink_rate_mbps: ProvenancedValue
    id: str
    name: str
    norad_id: int
    snapshot_id: str
    source: str
    tle_epoch: ProvenancedValue
    truth_status: str
    access_level: str | Unset = "public_information"
    resource_type: str | Unset = "satellite"
    retrieved_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        downlink_rate_mbps = self.downlink_rate_mbps.to_dict()

        id = self.id

        name = self.name

        norad_id = self.norad_id

        snapshot_id = self.snapshot_id

        source = self.source

        tle_epoch = self.tle_epoch.to_dict()

        truth_status = self.truth_status

        access_level = self.access_level

        resource_type = self.resource_type

        retrieved_at: None | str | Unset
        if isinstance(self.retrieved_at, Unset):
            retrieved_at = UNSET
        else:
            retrieved_at = self.retrieved_at

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
                "truth_status": truth_status,
            }
        )
        if access_level is not UNSET:
            field_dict["access_level"] = access_level
        if resource_type is not UNSET:
            field_dict["resource_type"] = resource_type
        if retrieved_at is not UNSET:
            field_dict["retrieved_at"] = retrieved_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.provenanced_value import ProvenancedValue

        d = dict(src_dict)
        downlink_rate_mbps = ProvenancedValue.from_dict(d.pop("downlink_rate_mbps"))

        id = d.pop("id")

        name = d.pop("name")

        norad_id = d.pop("norad_id")

        snapshot_id = d.pop("snapshot_id")

        source = d.pop("source")

        tle_epoch = ProvenancedValue.from_dict(d.pop("tle_epoch"))

        truth_status = d.pop("truth_status")

        access_level = d.pop("access_level", UNSET)

        resource_type = d.pop("resource_type", UNSET)

        def _parse_retrieved_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        retrieved_at = _parse_retrieved_at(d.pop("retrieved_at", UNSET))

        mission_satellite_out = cls(
            downlink_rate_mbps=downlink_rate_mbps,
            id=id,
            name=name,
            norad_id=norad_id,
            snapshot_id=snapshot_id,
            source=source,
            tle_epoch=tle_epoch,
            truth_status=truth_status,
            access_level=access_level,
            resource_type=resource_type,
            retrieved_at=retrieved_at,
        )

        mission_satellite_out.additional_properties = d
        return mission_satellite_out

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
