from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ObservedMetrics")


@_attrs_define
class ObservedMetrics:
    """
    Attributes:
        execution_seconds (float):
        input_bytes (int):
        output_bytes (int):
        storage_location (str):
        transfer_seconds (float):
    """

    execution_seconds: float
    input_bytes: int
    output_bytes: int
    storage_location: str
    transfer_seconds: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        execution_seconds = self.execution_seconds

        input_bytes = self.input_bytes

        output_bytes = self.output_bytes

        storage_location = self.storage_location

        transfer_seconds = self.transfer_seconds

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "execution_seconds": execution_seconds,
                "input_bytes": input_bytes,
                "output_bytes": output_bytes,
                "storage_location": storage_location,
                "transfer_seconds": transfer_seconds,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        execution_seconds = d.pop("execution_seconds")

        input_bytes = d.pop("input_bytes")

        output_bytes = d.pop("output_bytes")

        storage_location = d.pop("storage_location")

        transfer_seconds = d.pop("transfer_seconds")

        observed_metrics = cls(
            execution_seconds=execution_seconds,
            input_bytes=input_bytes,
            output_bytes=output_bytes,
            storage_location=storage_location,
            transfer_seconds=transfer_seconds,
        )

        observed_metrics.additional_properties = d
        return observed_metrics

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
