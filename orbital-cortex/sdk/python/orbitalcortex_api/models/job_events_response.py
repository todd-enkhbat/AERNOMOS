from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.job_event import JobEvent


T = TypeVar("T", bound="JobEventsResponse")


@_attrs_define
class JobEventsResponse:
    """
    Example:
        {'events': [{'event_type': 'route_selected', 'id': 'evt_1d4f8a2c6b3e', 'job_id': 'job_9f2c41d3a8b7', 'message':
            'Selected sim_leo_01 at 87% route confidence; latency 38 minutes, cost $84.00, fallback aws_us_east_gpu.',
            'payload': {'confidence': 0.87, 'routing_decision_id': 'route_5b8e2f7c9d01', 'selected_node_id': 'sim_leo_01',
            'status_from': 'queued', 'status_to': 'routing'}, 'ts_utc': '2026-07-05T14:00:01+00:00'}]}

    Attributes:
        events (list['JobEvent']):
    """

    events: list["JobEvent"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        events = []
        for events_item_data in self.events:
            events_item = events_item_data.to_dict()
            events.append(events_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "events": events,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.job_event import JobEvent

        d = dict(src_dict)
        events = []
        _events = d.pop("events")
        for events_item_data in _events:
            events_item = JobEvent.from_dict(events_item_data)

            events.append(events_item)

        job_events_response = cls(
            events=events,
        )

        job_events_response.additional_properties = d
        return job_events_response

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
