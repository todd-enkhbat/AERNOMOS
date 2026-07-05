from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.routing_decision import RoutingDecision


T = TypeVar("T", bound="RoutingResponse")


@_attrs_define
class RoutingResponse:
    """
    Example:
        {'routing_decision': {'candidate_scores': [{'availability_score': 0.97, 'available': True, 'compliance_score':
            1.0, 'contact_score': 0.88, 'cost_score': 0.74, 'eligible': True, 'est_downlink_mb': 42.0, 'estimated_cost_usd':
            84.0, 'estimated_latency_minutes': 38.0, 'hard_constraint_failures': [], 'latency_score': 0.92,
            'model_support_score': 1.0, 'next_aos_utc': '2026-07-05T14:27:30+00:00', 'next_contact_minutes': 27.5,
            'next_max_elevation_deg': 63.4, 'node_id': 'sim_leo_01', 'preference_score': 1.0, 'reasons': ['Onboard
            ship_detection model eliminates raw-scene downlink.', 'Next Svalbard contact in 28 minutes fits the fastest
            priority.'], 'score': 0.87, 'selected_ground_station_id': 'gs_ksat_svalbard', 'weights': {'availability': 15,
            'compliance': 5, 'contact': 10, 'cost': 10, 'latency': 25, 'model_support': 25, 'preference': 10}}],
            'confidence': 0.87, 'config_version': '2026.07.05-1', 'decided_at_utc': '2026-07-05T14:00:01+00:00',
            'decision_hash': '5d9e0b2a7c41f386', 'estimated_cost_usd': 84.0, 'estimated_latency_minutes': 38.0,
            'fallback_node_id': 'aws_us_east_gpu', 'id': 'route_5b8e2f7c9d01', 'input_hash': 'a3f1c6e29b8d4c07', 'job_id':
            'job_9f2c41d3a8b7', 'reasons': ['sim_leo_01 scored highest for fastest priority with an onboard model.',
            'Fallback aws_us_east_gpu retained in case the contact window slips.'], 'seed': 42,
            'selected_ground_station_id': 'gs_ksat_svalbard', 'selected_node_id': 'sim_leo_01', 'tle_snapshot_id':
            'celestrak-2026-07-05'}}

    Attributes:
        routing_decision (RoutingDecision):
    """

    routing_decision: "RoutingDecision"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        routing_decision = self.routing_decision.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "routing_decision": routing_decision,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.routing_decision import RoutingDecision

        d = dict(src_dict)
        routing_decision = RoutingDecision.from_dict(d.pop("routing_decision"))

        routing_response = cls(
            routing_decision=routing_decision,
        )

        routing_response.additional_properties = d
        return routing_response

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
