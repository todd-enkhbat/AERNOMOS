from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.source_evidence_out_raw_value import SourceEvidenceOutRawValue
    from ..models.source_evidence_out_transformed_value import (
        SourceEvidenceOutTransformedValue,
    )


T = TypeVar("T", bound="SourceEvidenceOut")


@_attrs_define
class SourceEvidenceOut:
    """
    Attributes:
        id (str):
        mission_id (str):
        source_name (str):
        source_type (str):
        truth_status (str):
        effective_at (None | str | Unset):
        mission_plan_id (None | str | Unset):
        mission_plan_step_id (None | str | Unset):
        raw_value (SourceEvidenceOutRawValue | Unset):
        retrieved_at (None | str | Unset):
        source_url (None | str | Unset):
        transformation_method (None | str | Unset):
        transformed_value (SourceEvidenceOutTransformedValue | Unset):
    """

    id: str
    mission_id: str
    source_name: str
    source_type: str
    truth_status: str
    effective_at: None | str | Unset = UNSET
    mission_plan_id: None | str | Unset = UNSET
    mission_plan_step_id: None | str | Unset = UNSET
    raw_value: SourceEvidenceOutRawValue | Unset = UNSET
    retrieved_at: None | str | Unset = UNSET
    source_url: None | str | Unset = UNSET
    transformation_method: None | str | Unset = UNSET
    transformed_value: SourceEvidenceOutTransformedValue | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        mission_id = self.mission_id

        source_name = self.source_name

        source_type = self.source_type

        truth_status = self.truth_status

        effective_at: None | str | Unset
        if isinstance(self.effective_at, Unset):
            effective_at = UNSET
        else:
            effective_at = self.effective_at

        mission_plan_id: None | str | Unset
        if isinstance(self.mission_plan_id, Unset):
            mission_plan_id = UNSET
        else:
            mission_plan_id = self.mission_plan_id

        mission_plan_step_id: None | str | Unset
        if isinstance(self.mission_plan_step_id, Unset):
            mission_plan_step_id = UNSET
        else:
            mission_plan_step_id = self.mission_plan_step_id

        raw_value: dict[str, Any] | Unset = UNSET
        if not isinstance(self.raw_value, Unset):
            raw_value = self.raw_value.to_dict()

        retrieved_at: None | str | Unset
        if isinstance(self.retrieved_at, Unset):
            retrieved_at = UNSET
        else:
            retrieved_at = self.retrieved_at

        source_url: None | str | Unset
        if isinstance(self.source_url, Unset):
            source_url = UNSET
        else:
            source_url = self.source_url

        transformation_method: None | str | Unset
        if isinstance(self.transformation_method, Unset):
            transformation_method = UNSET
        else:
            transformation_method = self.transformation_method

        transformed_value: dict[str, Any] | Unset = UNSET
        if not isinstance(self.transformed_value, Unset):
            transformed_value = self.transformed_value.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "mission_id": mission_id,
                "source_name": source_name,
                "source_type": source_type,
                "truth_status": truth_status,
            }
        )
        if effective_at is not UNSET:
            field_dict["effective_at"] = effective_at
        if mission_plan_id is not UNSET:
            field_dict["mission_plan_id"] = mission_plan_id
        if mission_plan_step_id is not UNSET:
            field_dict["mission_plan_step_id"] = mission_plan_step_id
        if raw_value is not UNSET:
            field_dict["raw_value"] = raw_value
        if retrieved_at is not UNSET:
            field_dict["retrieved_at"] = retrieved_at
        if source_url is not UNSET:
            field_dict["source_url"] = source_url
        if transformation_method is not UNSET:
            field_dict["transformation_method"] = transformation_method
        if transformed_value is not UNSET:
            field_dict["transformed_value"] = transformed_value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.source_evidence_out_raw_value import SourceEvidenceOutRawValue
        from ..models.source_evidence_out_transformed_value import (
            SourceEvidenceOutTransformedValue,
        )

        d = dict(src_dict)
        id = d.pop("id")

        mission_id = d.pop("mission_id")

        source_name = d.pop("source_name")

        source_type = d.pop("source_type")

        truth_status = d.pop("truth_status")

        def _parse_effective_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        effective_at = _parse_effective_at(d.pop("effective_at", UNSET))

        def _parse_mission_plan_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        mission_plan_id = _parse_mission_plan_id(d.pop("mission_plan_id", UNSET))

        def _parse_mission_plan_step_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        mission_plan_step_id = _parse_mission_plan_step_id(
            d.pop("mission_plan_step_id", UNSET)
        )

        _raw_value = d.pop("raw_value", UNSET)
        raw_value: SourceEvidenceOutRawValue | Unset
        if isinstance(_raw_value, Unset):
            raw_value = UNSET
        else:
            raw_value = SourceEvidenceOutRawValue.from_dict(_raw_value)

        def _parse_retrieved_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        retrieved_at = _parse_retrieved_at(d.pop("retrieved_at", UNSET))

        def _parse_source_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source_url = _parse_source_url(d.pop("source_url", UNSET))

        def _parse_transformation_method(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        transformation_method = _parse_transformation_method(
            d.pop("transformation_method", UNSET)
        )

        _transformed_value = d.pop("transformed_value", UNSET)
        transformed_value: SourceEvidenceOutTransformedValue | Unset
        if isinstance(_transformed_value, Unset):
            transformed_value = UNSET
        else:
            transformed_value = SourceEvidenceOutTransformedValue.from_dict(
                _transformed_value
            )

        source_evidence_out = cls(
            id=id,
            mission_id=mission_id,
            source_name=source_name,
            source_type=source_type,
            truth_status=truth_status,
            effective_at=effective_at,
            mission_plan_id=mission_plan_id,
            mission_plan_step_id=mission_plan_step_id,
            raw_value=raw_value,
            retrieved_at=retrieved_at,
            source_url=source_url,
            transformation_method=transformation_method,
            transformed_value=transformed_value,
        )

        source_evidence_out.additional_properties = d
        return source_evidence_out

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
