from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mission_plan_out import MissionPlanOut


T = TypeVar("T", bound="MissionPlansGenerateResponse")


@_attrs_define
class MissionPlansGenerateResponse:
    """
    Attributes:
        planner_config_version (str):
        plans (list[MissionPlanOut]):
        generation_strategy (str | Unset):  Default: 'append_versions — each POST appends a new version batch; prior
            recommended flags are cleared.'.
        recommended_plan_id (None | str | Unset):
    """

    planner_config_version: str
    plans: list[MissionPlanOut]
    generation_strategy: str | Unset = (
        "append_versions — each POST appends a new version batch; prior recommended flags are cleared."
    )
    recommended_plan_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        planner_config_version = self.planner_config_version

        plans = []
        for plans_item_data in self.plans:
            plans_item = plans_item_data.to_dict()
            plans.append(plans_item)

        generation_strategy = self.generation_strategy

        recommended_plan_id: None | str | Unset
        if isinstance(self.recommended_plan_id, Unset):
            recommended_plan_id = UNSET
        else:
            recommended_plan_id = self.recommended_plan_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "planner_config_version": planner_config_version,
                "plans": plans,
            }
        )
        if generation_strategy is not UNSET:
            field_dict["generation_strategy"] = generation_strategy
        if recommended_plan_id is not UNSET:
            field_dict["recommended_plan_id"] = recommended_plan_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mission_plan_out import MissionPlanOut

        d = dict(src_dict)
        planner_config_version = d.pop("planner_config_version")

        plans = []
        _plans = d.pop("plans")
        for plans_item_data in _plans:
            plans_item = MissionPlanOut.from_dict(plans_item_data)

            plans.append(plans_item)

        generation_strategy = d.pop("generation_strategy", UNSET)

        def _parse_recommended_plan_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        recommended_plan_id = _parse_recommended_plan_id(
            d.pop("recommended_plan_id", UNSET)
        )

        mission_plans_generate_response = cls(
            planner_config_version=planner_config_version,
            plans=plans,
            generation_strategy=generation_strategy,
            recommended_plan_id=recommended_plan_id,
        )

        mission_plans_generate_response.additional_properties = d
        return mission_plans_generate_response

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
