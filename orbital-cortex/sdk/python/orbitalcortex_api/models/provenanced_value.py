from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.truth_status import TruthStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="ProvenancedValue")


@_attrs_define
class ProvenancedValue:
    """
    Attributes:
        truth_status (TruthStatus):
        value (Any):
        effective_at (None | str | Unset):
        explanation (None | str | Unset):
        freshness (None | str | Unset):
        method (None | str | Unset):
        retrieved_at (None | str | Unset):
        source (None | str | Unset):
    """

    truth_status: TruthStatus
    value: Any
    effective_at: None | str | Unset = UNSET
    explanation: None | str | Unset = UNSET
    freshness: None | str | Unset = UNSET
    method: None | str | Unset = UNSET
    retrieved_at: None | str | Unset = UNSET
    source: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        truth_status = self.truth_status.value

        value = self.value

        effective_at: None | str | Unset
        if isinstance(self.effective_at, Unset):
            effective_at = UNSET
        else:
            effective_at = self.effective_at

        explanation: None | str | Unset
        if isinstance(self.explanation, Unset):
            explanation = UNSET
        else:
            explanation = self.explanation

        freshness: None | str | Unset
        if isinstance(self.freshness, Unset):
            freshness = UNSET
        else:
            freshness = self.freshness

        method: None | str | Unset
        if isinstance(self.method, Unset):
            method = UNSET
        else:
            method = self.method

        retrieved_at: None | str | Unset
        if isinstance(self.retrieved_at, Unset):
            retrieved_at = UNSET
        else:
            retrieved_at = self.retrieved_at

        source: None | str | Unset
        if isinstance(self.source, Unset):
            source = UNSET
        else:
            source = self.source

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "truth_status": truth_status,
                "value": value,
            }
        )
        if effective_at is not UNSET:
            field_dict["effective_at"] = effective_at
        if explanation is not UNSET:
            field_dict["explanation"] = explanation
        if freshness is not UNSET:
            field_dict["freshness"] = freshness
        if method is not UNSET:
            field_dict["method"] = method
        if retrieved_at is not UNSET:
            field_dict["retrieved_at"] = retrieved_at
        if source is not UNSET:
            field_dict["source"] = source

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        truth_status = TruthStatus(d.pop("truth_status"))

        value = d.pop("value")

        def _parse_effective_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        effective_at = _parse_effective_at(d.pop("effective_at", UNSET))

        def _parse_explanation(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        explanation = _parse_explanation(d.pop("explanation", UNSET))

        def _parse_freshness(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        freshness = _parse_freshness(d.pop("freshness", UNSET))

        def _parse_method(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        method = _parse_method(d.pop("method", UNSET))

        def _parse_retrieved_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        retrieved_at = _parse_retrieved_at(d.pop("retrieved_at", UNSET))

        def _parse_source(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source = _parse_source(d.pop("source", UNSET))

        provenanced_value = cls(
            truth_status=truth_status,
            value=value,
            effective_at=effective_at,
            explanation=explanation,
            freshness=freshness,
            method=method,
            retrieved_at=retrieved_at,
            source=source,
        )

        provenanced_value.additional_properties = d
        return provenanced_value

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
