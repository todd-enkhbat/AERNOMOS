from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.share_link_out import ShareLinkOut


T = TypeVar("T", bound="ShareLinkListResponse")


@_attrs_define
class ShareLinkListResponse:
    """
    Attributes:
        share_links (list[ShareLinkOut]):
    """

    share_links: list[ShareLinkOut]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        share_links = []
        for share_links_item_data in self.share_links:
            share_links_item = share_links_item_data.to_dict()
            share_links.append(share_links_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "share_links": share_links,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.share_link_out import ShareLinkOut

        d = dict(src_dict)
        share_links = []
        _share_links = d.pop("share_links")
        for share_links_item_data in _share_links:
            share_links_item = ShareLinkOut.from_dict(share_links_item_data)

            share_links.append(share_links_item)

        share_link_list_response = cls(
            share_links=share_links,
        )

        share_link_list_response.additional_properties = d
        return share_link_list_response

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
