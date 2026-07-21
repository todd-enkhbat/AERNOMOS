from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mission_plan_out import MissionPlanOut


T = TypeVar("T", bound="MissionPlansListResponse")


@_attrs_define
class MissionPlansListResponse:
    """
    Attributes:
        plans (list[MissionPlanOut]):
        generation_strategy (str | Unset):  Default: 'append_versions — each POST appends a new version batch; prior
            recommended flags are cleared.'.
    """

    plans: list[MissionPlanOut]
    generation_strategy: str | Unset = (
        "append_versions — each POST appends a new version batch; prior recommended flags are cleared."
    )
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        plans = []
        for plans_item_data in self.plans:
            plans_item = plans_item_data.to_dict()
            plans.append(plans_item)

        generation_strategy = self.generation_strategy

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "plans": plans,
            }
        )
        if generation_strategy is not UNSET:
            field_dict["generation_strategy"] = generation_strategy

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mission_plan_out import MissionPlanOut

        d = dict(src_dict)
        plans = []
        _plans = d.pop("plans")
        for plans_item_data in _plans:
            plans_item = MissionPlanOut.from_dict(plans_item_data)

            plans.append(plans_item)

        generation_strategy = d.pop("generation_strategy", UNSET)

        mission_plans_list_response = cls(
            plans=plans,
            generation_strategy=generation_strategy,
        )

        mission_plans_list_response.additional_properties = d
        return mission_plans_list_response

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
