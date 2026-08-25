from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.job import Job
    from ..models.routing_decision import RoutingDecision


T = TypeVar("T", bound="JobCreateResponse")


@_attrs_define
class JobCreateResponse:
    """
    Attributes:
        job (Job):
        access_token (None | str | Unset):
        routing_decision (None | RoutingDecision | Unset):
    """

    job: Job
    access_token: None | str | Unset = UNSET
    routing_decision: None | RoutingDecision | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.routing_decision import RoutingDecision

        job = self.job.to_dict()

        access_token: None | str | Unset
        if isinstance(self.access_token, Unset):
            access_token = UNSET
        else:
            access_token = self.access_token

        routing_decision: dict[str, Any] | None | Unset
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
        if access_token is not UNSET:
            field_dict["access_token"] = access_token
        if routing_decision is not UNSET:
            field_dict["routing_decision"] = routing_decision

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.job import Job
        from ..models.routing_decision import RoutingDecision

        d = dict(src_dict)
        job = Job.from_dict(d.pop("job"))

        def _parse_access_token(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        access_token = _parse_access_token(d.pop("access_token", UNSET))

        def _parse_routing_decision(data: object) -> None | RoutingDecision | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                routing_decision_type_0 = RoutingDecision.from_dict(data)

                return routing_decision_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RoutingDecision | Unset, data)

        routing_decision = _parse_routing_decision(d.pop("routing_decision", UNSET))

        job_create_response = cls(
            job=job,
            access_token=access_token,
            routing_decision=routing_decision,
        )

        job_create_response.additional_properties = d
        return job_create_response

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
