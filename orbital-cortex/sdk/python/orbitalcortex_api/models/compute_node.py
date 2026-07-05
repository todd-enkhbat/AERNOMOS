from collections.abc import Mapping
from typing import (
    Any,
    TypeVar,
    Union,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.compute_node_type import ComputeNodeType
from ..types import UNSET, Unset

T = TypeVar("T", bound="ComputeNode")


@_attrs_define
class ComputeNode:
    """
    Attributes:
        availability (float):
        base_cost_usd (float):
        compliance_tags (list[str]):
        downlink_mbps (int):
        gpu_class (str):
        id (str):
        latency_minutes (float):
        location (str):
        name (str):
        power_state (str):
        storage_gb (int):
        supported_models (list[str]):
        type_ (ComputeNodeType):
        orbit (Union[None, Unset, str]):
        satellite_id (Union[None, Unset, str]):
    """

    availability: float
    base_cost_usd: float
    compliance_tags: list[str]
    downlink_mbps: int
    gpu_class: str
    id: str
    latency_minutes: float
    location: str
    name: str
    power_state: str
    storage_gb: int
    supported_models: list[str]
    type_: ComputeNodeType
    orbit: Union[None, Unset, str] = UNSET
    satellite_id: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        availability = self.availability

        base_cost_usd = self.base_cost_usd

        compliance_tags = self.compliance_tags

        downlink_mbps = self.downlink_mbps

        gpu_class = self.gpu_class

        id = self.id

        latency_minutes = self.latency_minutes

        location = self.location

        name = self.name

        power_state = self.power_state

        storage_gb = self.storage_gb

        supported_models = self.supported_models

        type_ = self.type_.value

        orbit: Union[None, Unset, str]
        if isinstance(self.orbit, Unset):
            orbit = UNSET
        else:
            orbit = self.orbit

        satellite_id: Union[None, Unset, str]
        if isinstance(self.satellite_id, Unset):
            satellite_id = UNSET
        else:
            satellite_id = self.satellite_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "availability": availability,
                "base_cost_usd": base_cost_usd,
                "compliance_tags": compliance_tags,
                "downlink_mbps": downlink_mbps,
                "gpu_class": gpu_class,
                "id": id,
                "latency_minutes": latency_minutes,
                "location": location,
                "name": name,
                "power_state": power_state,
                "storage_gb": storage_gb,
                "supported_models": supported_models,
                "type": type_,
            }
        )
        if orbit is not UNSET:
            field_dict["orbit"] = orbit
        if satellite_id is not UNSET:
            field_dict["satellite_id"] = satellite_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        availability = d.pop("availability")

        base_cost_usd = d.pop("base_cost_usd")

        compliance_tags = cast(list[str], d.pop("compliance_tags"))

        downlink_mbps = d.pop("downlink_mbps")

        gpu_class = d.pop("gpu_class")

        id = d.pop("id")

        latency_minutes = d.pop("latency_minutes")

        location = d.pop("location")

        name = d.pop("name")

        power_state = d.pop("power_state")

        storage_gb = d.pop("storage_gb")

        supported_models = cast(list[str], d.pop("supported_models"))

        type_ = ComputeNodeType(d.pop("type"))

        def _parse_orbit(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        orbit = _parse_orbit(d.pop("orbit", UNSET))

        def _parse_satellite_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        satellite_id = _parse_satellite_id(d.pop("satellite_id", UNSET))

        compute_node = cls(
            availability=availability,
            base_cost_usd=base_cost_usd,
            compliance_tags=compliance_tags,
            downlink_mbps=downlink_mbps,
            gpu_class=gpu_class,
            id=id,
            latency_minutes=latency_minutes,
            location=location,
            name=name,
            power_state=power_state,
            storage_gb=storage_gb,
            supported_models=supported_models,
            type_=type_,
            orbit=orbit,
            satellite_id=satellite_id,
        )

        compute_node.additional_properties = d
        return compute_node

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
