from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.observed_metrics import ObservedMetrics


T = TypeVar("T", bound="ExecutionResult")


@_attrs_define
class ExecutionResult:
    """
    Attributes:
        external_job_id (str):
        observed (ObservedMetrics):
        output_ref (str):
    """

    external_job_id: str
    observed: ObservedMetrics
    output_ref: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        external_job_id = self.external_job_id

        observed = self.observed.to_dict()

        output_ref = self.output_ref

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "external_job_id": external_job_id,
                "observed": observed,
                "output_ref": output_ref,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.observed_metrics import ObservedMetrics

        d = dict(src_dict)
        external_job_id = d.pop("external_job_id")

        observed = ObservedMetrics.from_dict(d.pop("observed"))

        output_ref = d.pop("output_ref")

        execution_result = cls(
            external_job_id=external_job_id,
            observed=observed,
            output_ref=output_ref,
        )

        execution_result.additional_properties = d
        return execution_result

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
