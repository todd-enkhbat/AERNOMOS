from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ReplayResponse")


@_attrs_define
class ReplayResponse:
    """
    Attributes:
        config_version (str):
        input_hash (str):
        match (bool):
        replay_decision_hash (str):
        stored_decision_hash (str):
    """

    config_version: str
    input_hash: str
    match: bool
    replay_decision_hash: str
    stored_decision_hash: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        config_version = self.config_version

        input_hash = self.input_hash

        match = self.match

        replay_decision_hash = self.replay_decision_hash

        stored_decision_hash = self.stored_decision_hash

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "config_version": config_version,
                "input_hash": input_hash,
                "match": match,
                "replay_decision_hash": replay_decision_hash,
                "stored_decision_hash": stored_decision_hash,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        config_version = d.pop("config_version")

        input_hash = d.pop("input_hash")

        match = d.pop("match")

        replay_decision_hash = d.pop("replay_decision_hash")

        stored_decision_hash = d.pop("stored_decision_hash")

        replay_response = cls(
            config_version=config_version,
            input_hash=input_hash,
            match=match,
            replay_decision_hash=replay_decision_hash,
            stored_decision_hash=stored_decision_hash,
        )

        replay_response.additional_properties = d
        return replay_response

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
