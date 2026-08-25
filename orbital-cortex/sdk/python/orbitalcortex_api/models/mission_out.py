from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mission_out_area_of_interest import MissionOutAreaOfInterest


T = TypeVar("T", bound="MissionOut")


@_attrs_define
class MissionOut:
    """
    Attributes:
        area_of_interest (MissionOutAreaOfInterest):
        created_at (str):
        id (str):
        objective_type (str):
        status (str):
        title (str):
        updated_at (str):
        allowed_regions (list[Any] | Unset):
        anonymous_session_id (None | str | Unset):
        customer_systems (list[Any] | Unset):
        data_source_preference (list[Any] | Unset):
        deadline (None | str | Unset):
        end_time (None | str | Unset):
        is_example (bool | Unset):  Default: False.
        max_cost_usd (float | None | Unset):
        max_data_volume_mb (float | None | Unset):
        notes (None | str | Unset):
        organization_id (None | str | Unset):
        preferred_compute_location (None | str | Unset):
        start_time (None | str | Unset):
    """

    area_of_interest: MissionOutAreaOfInterest
    created_at: str
    id: str
    objective_type: str
    status: str
    title: str
    updated_at: str
    allowed_regions: list[Any] | Unset = UNSET
    anonymous_session_id: None | str | Unset = UNSET
    customer_systems: list[Any] | Unset = UNSET
    data_source_preference: list[Any] | Unset = UNSET
    deadline: None | str | Unset = UNSET
    end_time: None | str | Unset = UNSET
    is_example: bool | Unset = False
    max_cost_usd: float | None | Unset = UNSET
    max_data_volume_mb: float | None | Unset = UNSET
    notes: None | str | Unset = UNSET
    organization_id: None | str | Unset = UNSET
    preferred_compute_location: None | str | Unset = UNSET
    start_time: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        area_of_interest = self.area_of_interest.to_dict()

        created_at = self.created_at

        id = self.id

        objective_type = self.objective_type

        status = self.status

        title = self.title

        updated_at = self.updated_at

        allowed_regions: list[Any] | Unset = UNSET
        if not isinstance(self.allowed_regions, Unset):
            allowed_regions = self.allowed_regions

        anonymous_session_id: None | str | Unset
        if isinstance(self.anonymous_session_id, Unset):
            anonymous_session_id = UNSET
        else:
            anonymous_session_id = self.anonymous_session_id

        customer_systems: list[Any] | Unset = UNSET
        if not isinstance(self.customer_systems, Unset):
            customer_systems = self.customer_systems

        data_source_preference: list[Any] | Unset = UNSET
        if not isinstance(self.data_source_preference, Unset):
            data_source_preference = self.data_source_preference

        deadline: None | str | Unset
        if isinstance(self.deadline, Unset):
            deadline = UNSET
        else:
            deadline = self.deadline

        end_time: None | str | Unset
        if isinstance(self.end_time, Unset):
            end_time = UNSET
        else:
            end_time = self.end_time

        is_example = self.is_example

        max_cost_usd: float | None | Unset
        if isinstance(self.max_cost_usd, Unset):
            max_cost_usd = UNSET
        else:
            max_cost_usd = self.max_cost_usd

        max_data_volume_mb: float | None | Unset
        if isinstance(self.max_data_volume_mb, Unset):
            max_data_volume_mb = UNSET
        else:
            max_data_volume_mb = self.max_data_volume_mb

        notes: None | str | Unset
        if isinstance(self.notes, Unset):
            notes = UNSET
        else:
            notes = self.notes

        organization_id: None | str | Unset
        if isinstance(self.organization_id, Unset):
            organization_id = UNSET
        else:
            organization_id = self.organization_id

        preferred_compute_location: None | str | Unset
        if isinstance(self.preferred_compute_location, Unset):
            preferred_compute_location = UNSET
        else:
            preferred_compute_location = self.preferred_compute_location

        start_time: None | str | Unset
        if isinstance(self.start_time, Unset):
            start_time = UNSET
        else:
            start_time = self.start_time

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "area_of_interest": area_of_interest,
                "created_at": created_at,
                "id": id,
                "objective_type": objective_type,
                "status": status,
                "title": title,
                "updated_at": updated_at,
            }
        )
        if allowed_regions is not UNSET:
            field_dict["allowed_regions"] = allowed_regions
        if anonymous_session_id is not UNSET:
            field_dict["anonymous_session_id"] = anonymous_session_id
        if customer_systems is not UNSET:
            field_dict["customer_systems"] = customer_systems
        if data_source_preference is not UNSET:
            field_dict["data_source_preference"] = data_source_preference
        if deadline is not UNSET:
            field_dict["deadline"] = deadline
        if end_time is not UNSET:
            field_dict["end_time"] = end_time
        if is_example is not UNSET:
            field_dict["is_example"] = is_example
        if max_cost_usd is not UNSET:
            field_dict["max_cost_usd"] = max_cost_usd
        if max_data_volume_mb is not UNSET:
            field_dict["max_data_volume_mb"] = max_data_volume_mb
        if notes is not UNSET:
            field_dict["notes"] = notes
        if organization_id is not UNSET:
            field_dict["organization_id"] = organization_id
        if preferred_compute_location is not UNSET:
            field_dict["preferred_compute_location"] = preferred_compute_location
        if start_time is not UNSET:
            field_dict["start_time"] = start_time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mission_out_area_of_interest import MissionOutAreaOfInterest

        d = dict(src_dict)
        area_of_interest = MissionOutAreaOfInterest.from_dict(d.pop("area_of_interest"))

        created_at = d.pop("created_at")

        id = d.pop("id")

        objective_type = d.pop("objective_type")

        status = d.pop("status")

        title = d.pop("title")

        updated_at = d.pop("updated_at")

        allowed_regions = cast(list[Any], d.pop("allowed_regions", UNSET))

        def _parse_anonymous_session_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        anonymous_session_id = _parse_anonymous_session_id(
            d.pop("anonymous_session_id", UNSET)
        )

        customer_systems = cast(list[Any], d.pop("customer_systems", UNSET))

        data_source_preference = cast(list[Any], d.pop("data_source_preference", UNSET))

        def _parse_deadline(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        deadline = _parse_deadline(d.pop("deadline", UNSET))

        def _parse_end_time(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        end_time = _parse_end_time(d.pop("end_time", UNSET))

        is_example = d.pop("is_example", UNSET)

        def _parse_max_cost_usd(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        max_cost_usd = _parse_max_cost_usd(d.pop("max_cost_usd", UNSET))

        def _parse_max_data_volume_mb(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        max_data_volume_mb = _parse_max_data_volume_mb(
            d.pop("max_data_volume_mb", UNSET)
        )

        def _parse_notes(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        notes = _parse_notes(d.pop("notes", UNSET))

        def _parse_organization_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        organization_id = _parse_organization_id(d.pop("organization_id", UNSET))

        def _parse_preferred_compute_location(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        preferred_compute_location = _parse_preferred_compute_location(
            d.pop("preferred_compute_location", UNSET)
        )

        def _parse_start_time(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        start_time = _parse_start_time(d.pop("start_time", UNSET))

        mission_out = cls(
            area_of_interest=area_of_interest,
            created_at=created_at,
            id=id,
            objective_type=objective_type,
            status=status,
            title=title,
            updated_at=updated_at,
            allowed_regions=allowed_regions,
            anonymous_session_id=anonymous_session_id,
            customer_systems=customer_systems,
            data_source_preference=data_source_preference,
            deadline=deadline,
            end_time=end_time,
            is_example=is_example,
            max_cost_usd=max_cost_usd,
            max_data_volume_mb=max_data_volume_mb,
            notes=notes,
            organization_id=organization_id,
            preferred_compute_location=preferred_compute_location,
            start_time=start_time,
        )

        mission_out.additional_properties = d
        return mission_out

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
