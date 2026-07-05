from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.job_create_compute_preference import JobCreateComputePreference
from ..models.job_create_job_type import JobCreateJobType
from ..models.job_create_priority import JobCreatePriority
from ..models.job_create_sensor import JobCreateSensor
from ..types import UNSET, Unset
from typing import cast
from typing import Literal, Union, cast

if TYPE_CHECKING:
  from ..models.area_of_interest import AreaOfInterest





T = TypeVar("T", bound="JobCreate")



@_attrs_define
class JobCreate:
    """ 
        Attributes:
            area_of_interest (AreaOfInterest):
            compute_preference (JobCreateComputePreference):
            job_type (JobCreateJobType):
            max_cost_usd (float):
            priority (JobCreatePriority):
            sensor (JobCreateSensor):
            schema_version (Union[Literal[1], Unset]):  Default: 1.
     """

    area_of_interest: 'AreaOfInterest'
    compute_preference: JobCreateComputePreference
    job_type: JobCreateJobType
    max_cost_usd: float
    priority: JobCreatePriority
    sensor: JobCreateSensor
    schema_version: Union[Literal[1], Unset] = 1
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.area_of_interest import AreaOfInterest
        area_of_interest = self.area_of_interest.to_dict()

        compute_preference = self.compute_preference.value

        job_type = self.job_type.value

        max_cost_usd = self.max_cost_usd

        priority = self.priority.value

        sensor = self.sensor.value

        schema_version = self.schema_version


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "area_of_interest": area_of_interest,
            "compute_preference": compute_preference,
            "job_type": job_type,
            "max_cost_usd": max_cost_usd,
            "priority": priority,
            "sensor": sensor,
        })
        if schema_version is not UNSET:
            field_dict["schema_version"] = schema_version

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.area_of_interest import AreaOfInterest
        d = dict(src_dict)
        area_of_interest = AreaOfInterest.from_dict(d.pop("area_of_interest"))




        compute_preference = JobCreateComputePreference(d.pop("compute_preference"))




        job_type = JobCreateJobType(d.pop("job_type"))




        max_cost_usd = d.pop("max_cost_usd")

        priority = JobCreatePriority(d.pop("priority"))




        sensor = JobCreateSensor(d.pop("sensor"))




        schema_version = cast(Union[Literal[1], Unset] , d.pop("schema_version", UNSET))
        if schema_version != 1and not isinstance(schema_version, Unset):
            raise ValueError(f"schema_version must match const 1, got '{schema_version}'")

        job_create = cls(
            area_of_interest=area_of_interest,
            compute_preference=compute_preference,
            job_type=job_type,
            max_cost_usd=max_cost_usd,
            priority=priority,
            sensor=sensor,
            schema_version=schema_version,
        )


        job_create.additional_properties = d
        return job_create

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
