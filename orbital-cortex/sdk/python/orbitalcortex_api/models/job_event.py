from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.job_event_payload import JobEventPayload


T = TypeVar("T", bound="JobEvent")


@_attrs_define
class JobEvent:
    """
    Attributes:
        event_type (str):
        id (str):
        job_id (str):
        message (str):
        ts_utc (str):
        payload (JobEventPayload | Unset):
    """

    event_type: str
    id: str
    job_id: str
    message: str
    ts_utc: str
    payload: JobEventPayload | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        event_type = self.event_type

        id = self.id

        job_id = self.job_id

        message = self.message

        ts_utc = self.ts_utc

        payload: dict[str, Any] | Unset = UNSET
        if not isinstance(self.payload, Unset):
            payload = self.payload.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "event_type": event_type,
                "id": id,
                "job_id": job_id,
                "message": message,
                "ts_utc": ts_utc,
            }
        )
        if payload is not UNSET:
            field_dict["payload"] = payload

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.job_event_payload import JobEventPayload

        d = dict(src_dict)
        event_type = d.pop("event_type")

        id = d.pop("id")

        job_id = d.pop("job_id")

        message = d.pop("message")

        ts_utc = d.pop("ts_utc")

        _payload = d.pop("payload", UNSET)
        payload: JobEventPayload | Unset
        if isinstance(_payload, Unset):
            payload = UNSET
        else:
            payload = JobEventPayload.from_dict(_payload)

        job_event = cls(
            event_type=event_type,
            id=id,
            job_id=job_id,
            message=message,
            ts_utc=ts_utc,
            payload=payload,
        )

        job_event.additional_properties = d
        return job_event

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
