from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.catalog_candidate_asset_out import CatalogCandidateAssetOut
    from ..models.catalog_candidate_out_asset_metadata import (
        CatalogCandidateOutAssetMetadata,
    )
    from ..models.catalog_candidate_out_footprint import CatalogCandidateOutFootprint
    from ..models.provenanced_value import ProvenancedValue


T = TypeVar("T", bound="CatalogCandidateOut")


@_attrs_define
class CatalogCandidateOut:
    """
    Attributes:
        acquisition_time (ProvenancedValue):
        collection (str):
        created_at (str):
        external_item_id (str):
        footprint (CatalogCandidateOutFootprint):
        id (str):
        mission_id (str):
        source_provider (str):
        source_timestamp (str):
        truth_status (str):
        asset_metadata (CatalogCandidateOutAssetMetadata | Unset):
        available_assets (list[CatalogCandidateAssetOut] | Unset):
        estimated_size_bytes (None | ProvenancedValue | Unset):
        source_url (None | str | Unset):
    """

    acquisition_time: ProvenancedValue
    collection: str
    created_at: str
    external_item_id: str
    footprint: CatalogCandidateOutFootprint
    id: str
    mission_id: str
    source_provider: str
    source_timestamp: str
    truth_status: str
    asset_metadata: CatalogCandidateOutAssetMetadata | Unset = UNSET
    available_assets: list[CatalogCandidateAssetOut] | Unset = UNSET
    estimated_size_bytes: None | ProvenancedValue | Unset = UNSET
    source_url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.provenanced_value import ProvenancedValue

        acquisition_time = self.acquisition_time.to_dict()

        collection = self.collection

        created_at = self.created_at

        external_item_id = self.external_item_id

        footprint = self.footprint.to_dict()

        id = self.id

        mission_id = self.mission_id

        source_provider = self.source_provider

        source_timestamp = self.source_timestamp

        truth_status = self.truth_status

        asset_metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.asset_metadata, Unset):
            asset_metadata = self.asset_metadata.to_dict()

        available_assets: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.available_assets, Unset):
            available_assets = []
            for available_assets_item_data in self.available_assets:
                available_assets_item = available_assets_item_data.to_dict()
                available_assets.append(available_assets_item)

        estimated_size_bytes: dict[str, Any] | None | Unset
        if isinstance(self.estimated_size_bytes, Unset):
            estimated_size_bytes = UNSET
        elif isinstance(self.estimated_size_bytes, ProvenancedValue):
            estimated_size_bytes = self.estimated_size_bytes.to_dict()
        else:
            estimated_size_bytes = self.estimated_size_bytes

        source_url: None | str | Unset
        if isinstance(self.source_url, Unset):
            source_url = UNSET
        else:
            source_url = self.source_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "acquisition_time": acquisition_time,
                "collection": collection,
                "created_at": created_at,
                "external_item_id": external_item_id,
                "footprint": footprint,
                "id": id,
                "mission_id": mission_id,
                "source_provider": source_provider,
                "source_timestamp": source_timestamp,
                "truth_status": truth_status,
            }
        )
        if asset_metadata is not UNSET:
            field_dict["asset_metadata"] = asset_metadata
        if available_assets is not UNSET:
            field_dict["available_assets"] = available_assets
        if estimated_size_bytes is not UNSET:
            field_dict["estimated_size_bytes"] = estimated_size_bytes
        if source_url is not UNSET:
            field_dict["source_url"] = source_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.catalog_candidate_asset_out import CatalogCandidateAssetOut
        from ..models.catalog_candidate_out_asset_metadata import (
            CatalogCandidateOutAssetMetadata,
        )
        from ..models.catalog_candidate_out_footprint import (
            CatalogCandidateOutFootprint,
        )
        from ..models.provenanced_value import ProvenancedValue

        d = dict(src_dict)
        acquisition_time = ProvenancedValue.from_dict(d.pop("acquisition_time"))

        collection = d.pop("collection")

        created_at = d.pop("created_at")

        external_item_id = d.pop("external_item_id")

        footprint = CatalogCandidateOutFootprint.from_dict(d.pop("footprint"))

        id = d.pop("id")

        mission_id = d.pop("mission_id")

        source_provider = d.pop("source_provider")

        source_timestamp = d.pop("source_timestamp")

        truth_status = d.pop("truth_status")

        _asset_metadata = d.pop("asset_metadata", UNSET)
        asset_metadata: CatalogCandidateOutAssetMetadata | Unset
        if isinstance(_asset_metadata, Unset):
            asset_metadata = UNSET
        else:
            asset_metadata = CatalogCandidateOutAssetMetadata.from_dict(_asset_metadata)

        _available_assets = d.pop("available_assets", UNSET)
        available_assets: list[CatalogCandidateAssetOut] | Unset = UNSET
        if _available_assets is not UNSET:
            available_assets = []
            for available_assets_item_data in _available_assets:
                available_assets_item = CatalogCandidateAssetOut.from_dict(
                    available_assets_item_data
                )

                available_assets.append(available_assets_item)

        def _parse_estimated_size_bytes(
            data: object,
        ) -> None | ProvenancedValue | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                estimated_size_bytes_type_0 = ProvenancedValue.from_dict(data)

                return estimated_size_bytes_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ProvenancedValue | Unset, data)

        estimated_size_bytes = _parse_estimated_size_bytes(
            d.pop("estimated_size_bytes", UNSET)
        )

        def _parse_source_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source_url = _parse_source_url(d.pop("source_url", UNSET))

        catalog_candidate_out = cls(
            acquisition_time=acquisition_time,
            collection=collection,
            created_at=created_at,
            external_item_id=external_item_id,
            footprint=footprint,
            id=id,
            mission_id=mission_id,
            source_provider=source_provider,
            source_timestamp=source_timestamp,
            truth_status=truth_status,
            asset_metadata=asset_metadata,
            available_assets=available_assets,
            estimated_size_bytes=estimated_size_bytes,
            source_url=source_url,
        )

        catalog_candidate_out.additional_properties = d
        return catalog_candidate_out

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
