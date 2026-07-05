from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.job_compute_preference import JobComputePreference
from ..models.job_job_type import JobJobType
from ..models.job_priority import JobPriority
from ..models.job_sensor import JobSensor
from ..models.job_status import JobStatus
from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union

if TYPE_CHECKING:
  from ..models.area_of_interest import AreaOfInterest





T = TypeVar("T", bound="Job")



@_attrs_define
class Job:
    """ 
        Attributes:
            area_of_interest (AreaOfInterest):
            compute_preference (JobComputePreference):
            created_at (str):
            id (str):
            job_type (JobJobType):
            max_cost_usd (float):
            priority (JobPriority):
            sensor (JobSensor):
            status (JobStatus):
            updated_at (str):
            schema_version (Union[Unset, int]):  Default: 1.
            selected_route_id (Union[None, Unset, str]):
     """

    area_of_interest: 'AreaOfInterest'
    compute_preference: JobComputePreference
    created_at: str
    id: str
    job_type: JobJobType
    max_cost_usd: float
    priority: JobPriority
    sensor: JobSensor
    status: JobStatus
    updated_at: str
    schema_version: Union[Unset, int] = 1
    selected_route_id: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.area_of_interest import AreaOfInterest
        area_of_interest = self.area_of_interest.to_dict()

        compute_preference = self.compute_preference.value

        created_at = self.created_at

        id = self.id

        job_type = self.job_type.value

        max_cost_usd = self.max_cost_usd

        priority = self.priority.value

        sensor = self.sensor.value

        status = self.status.value

        updated_at = self.updated_at

        schema_version = self.schema_version

        selected_route_id: Union[None, Unset, str]
        if isinstance(self.selected_route_id, Unset):
            selected_route_id = UNSET
        else:
            selected_route_id = self.selected_route_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "area_of_interest": area_of_interest,
            "compute_preference": compute_preference,
            "created_at": created_at,
            "id": id,
            "job_type": job_type,
            "max_cost_usd": max_cost_usd,
            "priority": priority,
            "sensor": sensor,
            "status": status,
            "updated_at": updated_at,
        })
        if schema_version is not UNSET:
            field_dict["schema_version"] = schema_version
        if selected_route_id is not UNSET:
            field_dict["selected_route_id"] = selected_route_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.area_of_interest import AreaOfInterest
        d = dict(src_dict)
        area_of_interest = AreaOfInterest.from_dict(d.pop("area_of_interest"))




        compute_preference = JobComputePreference(d.pop("compute_preference"))




        created_at = d.pop("created_at")

        id = d.pop("id")

        job_type = JobJobType(d.pop("job_type"))




        max_cost_usd = d.pop("max_cost_usd")

        priority = JobPriority(d.pop("priority"))




        sensor = JobSensor(d.pop("sensor"))




        status = JobStatus(d.pop("status"))




        updated_at = d.pop("updated_at")

        schema_version = d.pop("schema_version", UNSET)

        def _parse_selected_route_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        selected_route_id = _parse_selected_route_id(d.pop("selected_route_id", UNSET))


        job = cls(
            area_of_interest=area_of_interest,
            compute_preference=compute_preference,
            created_at=created_at,
            id=id,
            job_type=job_type,
            max_cost_usd=max_cost_usd,
            priority=priority,
            sensor=sensor,
            status=status,
            updated_at=updated_at,
            schema_version=schema_version,
            selected_route_id=selected_route_id,
        )


        job.additional_properties = d
        return job

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
