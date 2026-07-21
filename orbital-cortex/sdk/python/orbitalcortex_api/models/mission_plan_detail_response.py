from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.mission_plan_out import MissionPlanOut


T = TypeVar("T", bound="MissionPlanDetailResponse")


@_attrs_define
class MissionPlanDetailResponse:
    """
    Attributes:
        plan (MissionPlanOut):
    """

    plan: MissionPlanOut
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        plan = self.plan.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "plan": plan,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mission_plan_out import MissionPlanOut

        d = dict(src_dict)
        plan = MissionPlanOut.from_dict(d.pop("plan"))

        mission_plan_detail_response = cls(
            plan=plan,
        )

        mission_plan_detail_response.additional_properties = d
        return mission_plan_detail_response

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
