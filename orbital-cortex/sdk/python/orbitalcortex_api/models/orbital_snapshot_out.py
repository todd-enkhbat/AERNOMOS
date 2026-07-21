from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OrbitalSnapshotOut")


@_attrs_define
class OrbitalSnapshotOut:
    """
    Attributes:
        snapshot_id (str):
        source (str):
        truth_status (str):
        epochs (list[Any] | Unset):
        freshness (None | str | Unset):
        retrieved_at (None | str | Unset):
        source_url (None | str | Unset):
        stale_epoch_days (int | Unset):  Default: 7.
        used_pinned_fallback (bool | Unset):  Default: False.
    """

    snapshot_id: str
    source: str
    truth_status: str
    epochs: list[Any] | Unset = UNSET
    freshness: None | str | Unset = UNSET
    retrieved_at: None | str | Unset = UNSET
    source_url: None | str | Unset = UNSET
    stale_epoch_days: int | Unset = 7
    used_pinned_fallback: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        snapshot_id = self.snapshot_id

        source = self.source

        truth_status = self.truth_status

        epochs: list[Any] | Unset = UNSET
        if not isinstance(self.epochs, Unset):
            epochs = self.epochs

        freshness: None | str | Unset
        if isinstance(self.freshness, Unset):
            freshness = UNSET
        else:
            freshness = self.freshness

        retrieved_at: None | str | Unset
        if isinstance(self.retrieved_at, Unset):
            retrieved_at = UNSET
        else:
            retrieved_at = self.retrieved_at

        source_url: None | str | Unset
        if isinstance(self.source_url, Unset):
            source_url = UNSET
        else:
            source_url = self.source_url

        stale_epoch_days = self.stale_epoch_days

        used_pinned_fallback = self.used_pinned_fallback

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "snapshot_id": snapshot_id,
                "source": source,
                "truth_status": truth_status,
            }
        )
        if epochs is not UNSET:
            field_dict["epochs"] = epochs
        if freshness is not UNSET:
            field_dict["freshness"] = freshness
        if retrieved_at is not UNSET:
            field_dict["retrieved_at"] = retrieved_at
        if source_url is not UNSET:
            field_dict["source_url"] = source_url
        if stale_epoch_days is not UNSET:
            field_dict["stale_epoch_days"] = stale_epoch_days
        if used_pinned_fallback is not UNSET:
            field_dict["used_pinned_fallback"] = used_pinned_fallback

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        snapshot_id = d.pop("snapshot_id")

        source = d.pop("source")

        truth_status = d.pop("truth_status")

        epochs = cast(list[Any], d.pop("epochs", UNSET))

        def _parse_freshness(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        freshness = _parse_freshness(d.pop("freshness", UNSET))

        def _parse_retrieved_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        retrieved_at = _parse_retrieved_at(d.pop("retrieved_at", UNSET))

        def _parse_source_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source_url = _parse_source_url(d.pop("source_url", UNSET))

        stale_epoch_days = d.pop("stale_epoch_days", UNSET)

        used_pinned_fallback = d.pop("used_pinned_fallback", UNSET)

        orbital_snapshot_out = cls(
            snapshot_id=snapshot_id,
            source=source,
            truth_status=truth_status,
            epochs=epochs,
            freshness=freshness,
            retrieved_at=retrieved_at,
            source_url=source_url,
            stale_epoch_days=stale_epoch_days,
            used_pinned_fallback=used_pinned_fallback,
        )

        orbital_snapshot_out.additional_properties = d
        return orbital_snapshot_out

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
