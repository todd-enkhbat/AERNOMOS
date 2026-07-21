from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ExecutionEstimate")


@_attrs_define
class ExecutionEstimate:
    """
    Attributes:
        estimated_cost_usd (float):
        estimated_seconds (float):
    """

    estimated_cost_usd: float
    estimated_seconds: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        estimated_cost_usd = self.estimated_cost_usd

        estimated_seconds = self.estimated_seconds

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "estimated_cost_usd": estimated_cost_usd,
                "estimated_seconds": estimated_seconds,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        estimated_cost_usd = d.pop("estimated_cost_usd")

        estimated_seconds = d.pop("estimated_seconds")

        execution_estimate = cls(
            estimated_cost_usd=estimated_cost_usd,
            estimated_seconds=estimated_seconds,
        )

        execution_estimate.additional_properties = d
        return execution_estimate

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
