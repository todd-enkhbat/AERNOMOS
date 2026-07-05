from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.job import Job
    from ..models.result import Result


T = TypeVar("T", bound="SimulateRunResponse")


@_attrs_define
class SimulateRunResponse:
    """
    Example:
        {'events_created': 8, 'job': {'area_of_interest': {'coordinates': [-74.3, 40.3, -73.5, 41.0], 'type': 'bbox'},
            'compute_preference': 'orbital_if_available', 'created_at': '2026-07-05T14:00:00+00:00', 'id':
            'job_9f2c41d3a8b7', 'job_type': 'ship_detection', 'max_cost_usd': 500.0, 'priority': 'fastest',
            'schema_version': 1, 'selected_route_id': 'route_5b8e2f7c9d01', 'sensor': 'SAR', 'status': 'complete',
            'updated_at': '2026-07-05T14:00:09+00:00'}, 'result': {'confidence': 0.91, 'geojson': {'features': [{'geometry':
            {'coordinates': [-74.045, 40.63], 'type': 'Point'}, 'properties': {'class': 'cargo', 'confidence': 0.94,
            'simulated': True}, 'type': 'Feature'}], 'type': 'FeatureCollection'}, 'id': 'res_3c7d91e5b2a4', 'job_id':
            'job_9f2c41d3a8b7', 'output_files': ['results/job_9f2c41d3a8b7/detections.geojson',
            'results/job_9f2c41d3a8b7/summary.json'], 'summary': 'Detected 17 vessels in New York Harbor.'}}

    Attributes:
        events_created (int):
        job (Job):
        result (Union['Result', None, Unset]):
    """

    events_created: int
    job: "Job"
    result: Union["Result", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.result import Result

        events_created = self.events_created

        job = self.job.to_dict()

        result: Union[None, Unset, dict[str, Any]]
        if isinstance(self.result, Unset):
            result = UNSET
        elif isinstance(self.result, Result):
            result = self.result.to_dict()
        else:
            result = self.result

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "events_created": events_created,
                "job": job,
            }
        )
        if result is not UNSET:
            field_dict["result"] = result

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.job import Job
        from ..models.result import Result

        d = dict(src_dict)
        events_created = d.pop("events_created")

        job = Job.from_dict(d.pop("job"))

        def _parse_result(data: object) -> Union["Result", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                result_type_0 = Result.from_dict(data)

                return result_type_0
            except:  # noqa: E722
                pass
            return cast(Union["Result", None, Unset], data)

        result = _parse_result(d.pop("result", UNSET))

        simulate_run_response = cls(
            events_created=events_created,
            job=job,
            result=result,
        )

        simulate_run_response.additional_properties = d
        return simulate_run_response

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
