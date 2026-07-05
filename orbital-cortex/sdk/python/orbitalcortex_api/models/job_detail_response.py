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
    from ..models.routing_decision import RoutingDecision


T = TypeVar("T", bound="JobDetailResponse")


@_attrs_define
class JobDetailResponse:
    """
    Example:
        {'job': {'area_of_interest': {'coordinates': [-74.3, 40.3, -73.5, 41.0], 'type': 'bbox'}, 'compute_preference':
            'orbital_if_available', 'created_at': '2026-07-05T14:00:00+00:00', 'id': 'job_9f2c41d3a8b7', 'job_type':
            'ship_detection', 'max_cost_usd': 500.0, 'priority': 'fastest', 'schema_version': 1, 'selected_route_id':
            'route_5b8e2f7c9d01', 'sensor': 'SAR', 'status': 'complete', 'updated_at': '2026-07-05T14:00:09+00:00'},
            'result_summary': 'Detected 17 vessels in New York Harbor.', 'routing_decision': {'candidate_scores':
            [{'availability_score': 0.97, 'available': True, 'compliance_score': 1.0, 'contact_score': 0.88, 'cost_score':
            0.74, 'eligible': True, 'est_downlink_mb': 42.0, 'estimated_cost_usd': 84.0, 'estimated_latency_minutes': 38.0,
            'hard_constraint_failures': [], 'latency_score': 0.92, 'model_support_score': 1.0, 'next_aos_utc':
            '2026-07-05T14:27:30+00:00', 'next_contact_minutes': 27.5, 'next_max_elevation_deg': 63.4, 'node_id':
            'sim_leo_01', 'preference_score': 1.0, 'reasons': ['Onboard ship_detection model eliminates raw-scene
            downlink.', 'Next Svalbard contact in 28 minutes fits the fastest priority.'], 'score': 0.87,
            'selected_ground_station_id': 'gs_ksat_svalbard', 'weights': {'availability': 15, 'compliance': 5, 'contact':
            10, 'cost': 10, 'latency': 25, 'model_support': 25, 'preference': 10}}], 'confidence': 0.87, 'config_version':
            '2026.07.05-1', 'decided_at_utc': '2026-07-05T14:00:01+00:00', 'decision_hash': '5d9e0b2a7c41f386',
            'estimated_cost_usd': 84.0, 'estimated_latency_minutes': 38.0, 'fallback_node_id': 'aws_us_east_gpu', 'id':
            'route_5b8e2f7c9d01', 'input_hash': 'a3f1c6e29b8d4c07', 'job_id': 'job_9f2c41d3a8b7', 'reasons': ['sim_leo_01
            scored highest for fastest priority with an onboard model.', 'Fallback aws_us_east_gpu retained in case the
            contact window slips.'], 'seed': 42, 'selected_ground_station_id': 'gs_ksat_svalbard', 'selected_node_id':
            'sim_leo_01', 'tle_snapshot_id': 'celestrak-2026-07-05'}}

    Attributes:
        job (Job):
        result_summary (Union[None, Unset, str]):
        routing_decision (Union['RoutingDecision', None, Unset]):
    """

    job: "Job"
    result_summary: Union[None, Unset, str] = UNSET
    routing_decision: Union["RoutingDecision", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.routing_decision import RoutingDecision

        job = self.job.to_dict()

        result_summary: Union[None, Unset, str]
        if isinstance(self.result_summary, Unset):
            result_summary = UNSET
        else:
            result_summary = self.result_summary

        routing_decision: Union[None, Unset, dict[str, Any]]
        if isinstance(self.routing_decision, Unset):
            routing_decision = UNSET
        elif isinstance(self.routing_decision, RoutingDecision):
            routing_decision = self.routing_decision.to_dict()
        else:
            routing_decision = self.routing_decision

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "job": job,
            }
        )
        if result_summary is not UNSET:
            field_dict["result_summary"] = result_summary
        if routing_decision is not UNSET:
            field_dict["routing_decision"] = routing_decision

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.job import Job
        from ..models.routing_decision import RoutingDecision

        d = dict(src_dict)
        job = Job.from_dict(d.pop("job"))

        def _parse_result_summary(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        result_summary = _parse_result_summary(d.pop("result_summary", UNSET))

        def _parse_routing_decision(
            data: object,
        ) -> Union["RoutingDecision", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_decision_type_0 = RoutingDecision.from_dict(data)

                return routing_decision_type_0
            except:  # noqa: E722
                pass
            return cast(Union["RoutingDecision", None, Unset], data)

        routing_decision = _parse_routing_decision(d.pop("routing_decision", UNSET))

        job_detail_response = cls(
            job=job,
            result_summary=result_summary,
            routing_decision=routing_decision,
        )

        job_detail_response.additional_properties = d
        return job_detail_response

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
