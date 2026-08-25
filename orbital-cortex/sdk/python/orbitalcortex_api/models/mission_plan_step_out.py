from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mission_plan_step_out_source_metadata import (
        MissionPlanStepOutSourceMetadata,
    )


T = TypeVar("T", bound="MissionPlanStepOut")


@_attrs_define
class MissionPlanStepOut:
    """
    Attributes:
        description (str):
        feasibility_status (str):
        id (str):
        mission_plan_id (str):
        provider_name (str):
        sequence (int):
        step_type (str):
        title (str):
        truth_status (str):
        duration_seconds (float | None | Unset):
        end_time (None | str | Unset):
        estimated_cost_usd (float | None | Unset):
        executed_at (None | str | Unset):
        execution_status (str | Unset):  Default: 'planned'.
        input_artifact (None | str | Unset):
        output_artifact (None | str | Unset):
        rejection_reason (None | str | Unset):
        resource_id (None | str | Unset):
        source_metadata (MissionPlanStepOutSourceMetadata | Unset):
        start_time (None | str | Unset):
    """

    description: str
    feasibility_status: str
    id: str
    mission_plan_id: str
    provider_name: str
    sequence: int
    step_type: str
    title: str
    truth_status: str
    duration_seconds: float | None | Unset = UNSET
    end_time: None | str | Unset = UNSET
    estimated_cost_usd: float | None | Unset = UNSET
    executed_at: None | str | Unset = UNSET
    execution_status: str | Unset = "planned"
    input_artifact: None | str | Unset = UNSET
    output_artifact: None | str | Unset = UNSET
    rejection_reason: None | str | Unset = UNSET
    resource_id: None | str | Unset = UNSET
    source_metadata: MissionPlanStepOutSourceMetadata | Unset = UNSET
    start_time: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description = self.description

        feasibility_status = self.feasibility_status

        id = self.id

        mission_plan_id = self.mission_plan_id

        provider_name = self.provider_name

        sequence = self.sequence

        step_type = self.step_type

        title = self.title

        truth_status = self.truth_status

        duration_seconds: float | None | Unset
        if isinstance(self.duration_seconds, Unset):
            duration_seconds = UNSET
        else:
            duration_seconds = self.duration_seconds

        end_time: None | str | Unset
        if isinstance(self.end_time, Unset):
            end_time = UNSET
        else:
            end_time = self.end_time

        estimated_cost_usd: float | None | Unset
        if isinstance(self.estimated_cost_usd, Unset):
            estimated_cost_usd = UNSET
        else:
            estimated_cost_usd = self.estimated_cost_usd

        executed_at: None | str | Unset
        if isinstance(self.executed_at, Unset):
            executed_at = UNSET
        else:
            executed_at = self.executed_at

        execution_status = self.execution_status

        input_artifact: None | str | Unset
        if isinstance(self.input_artifact, Unset):
            input_artifact = UNSET
        else:
            input_artifact = self.input_artifact

        output_artifact: None | str | Unset
        if isinstance(self.output_artifact, Unset):
            output_artifact = UNSET
        else:
            output_artifact = self.output_artifact

        rejection_reason: None | str | Unset
        if isinstance(self.rejection_reason, Unset):
            rejection_reason = UNSET
        else:
            rejection_reason = self.rejection_reason

        resource_id: None | str | Unset
        if isinstance(self.resource_id, Unset):
            resource_id = UNSET
        else:
            resource_id = self.resource_id

        source_metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.source_metadata, Unset):
            source_metadata = self.source_metadata.to_dict()

        start_time: None | str | Unset
        if isinstance(self.start_time, Unset):
            start_time = UNSET
        else:
            start_time = self.start_time

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "description": description,
                "feasibility_status": feasibility_status,
                "id": id,
                "mission_plan_id": mission_plan_id,
                "provider_name": provider_name,
                "sequence": sequence,
                "step_type": step_type,
                "title": title,
                "truth_status": truth_status,
            }
        )
        if duration_seconds is not UNSET:
            field_dict["duration_seconds"] = duration_seconds
        if end_time is not UNSET:
            field_dict["end_time"] = end_time
        if estimated_cost_usd is not UNSET:
            field_dict["estimated_cost_usd"] = estimated_cost_usd
        if executed_at is not UNSET:
            field_dict["executed_at"] = executed_at
        if execution_status is not UNSET:
            field_dict["execution_status"] = execution_status
        if input_artifact is not UNSET:
            field_dict["input_artifact"] = input_artifact
        if output_artifact is not UNSET:
            field_dict["output_artifact"] = output_artifact
        if rejection_reason is not UNSET:
            field_dict["rejection_reason"] = rejection_reason
        if resource_id is not UNSET:
            field_dict["resource_id"] = resource_id
        if source_metadata is not UNSET:
            field_dict["source_metadata"] = source_metadata
        if start_time is not UNSET:
            field_dict["start_time"] = start_time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mission_plan_step_out_source_metadata import (
            MissionPlanStepOutSourceMetadata,
        )

        d = dict(src_dict)
        description = d.pop("description")

        feasibility_status = d.pop("feasibility_status")

        id = d.pop("id")

        mission_plan_id = d.pop("mission_plan_id")

        provider_name = d.pop("provider_name")

        sequence = d.pop("sequence")

        step_type = d.pop("step_type")

        title = d.pop("title")

        truth_status = d.pop("truth_status")

        def _parse_duration_seconds(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        duration_seconds = _parse_duration_seconds(d.pop("duration_seconds", UNSET))

        def _parse_end_time(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        end_time = _parse_end_time(d.pop("end_time", UNSET))

        def _parse_estimated_cost_usd(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        estimated_cost_usd = _parse_estimated_cost_usd(
            d.pop("estimated_cost_usd", UNSET)
        )

        def _parse_executed_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        executed_at = _parse_executed_at(d.pop("executed_at", UNSET))

        execution_status = d.pop("execution_status", UNSET)

        def _parse_input_artifact(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        input_artifact = _parse_input_artifact(d.pop("input_artifact", UNSET))

        def _parse_output_artifact(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        output_artifact = _parse_output_artifact(d.pop("output_artifact", UNSET))

        def _parse_rejection_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        rejection_reason = _parse_rejection_reason(d.pop("rejection_reason", UNSET))

        def _parse_resource_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        resource_id = _parse_resource_id(d.pop("resource_id", UNSET))

        _source_metadata = d.pop("source_metadata", UNSET)
        source_metadata: MissionPlanStepOutSourceMetadata | Unset
        if isinstance(_source_metadata, Unset):
            source_metadata = UNSET
        else:
            source_metadata = MissionPlanStepOutSourceMetadata.from_dict(
                _source_metadata
            )

        def _parse_start_time(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        start_time = _parse_start_time(d.pop("start_time", UNSET))

        mission_plan_step_out = cls(
            description=description,
            feasibility_status=feasibility_status,
            id=id,
            mission_plan_id=mission_plan_id,
            provider_name=provider_name,
            sequence=sequence,
            step_type=step_type,
            title=title,
            truth_status=truth_status,
            duration_seconds=duration_seconds,
            end_time=end_time,
            estimated_cost_usd=estimated_cost_usd,
            executed_at=executed_at,
            execution_status=execution_status,
            input_artifact=input_artifact,
            output_artifact=output_artifact,
            rejection_reason=rejection_reason,
            resource_id=resource_id,
            source_metadata=source_metadata,
            start_time=start_time,
        )

        mission_plan_step_out.additional_properties = d
        return mission_plan_step_out

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
