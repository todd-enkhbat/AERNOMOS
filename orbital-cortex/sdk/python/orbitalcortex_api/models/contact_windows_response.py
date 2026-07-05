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
    from ..models.contact_window import ContactWindow


T = TypeVar("T", bound="ContactWindowsResponse")


@_attrs_define
class ContactWindowsResponse:
    """
    Example:
        {'contact_windows': [{'aos_utc': '2026-07-05T14:27:30+00:00', 'culminate_utc': '2026-07-05T14:32:10+00:00',
            'date': '2026-07-05', 'duration_s': 555.0, 'est_downlink_mb': 42.0, 'ground_station_id': 'gs_ksat_svalbard',
            'id': 'cw_7a1b3c5d9e2f', 'los_utc': '2026-07-05T14:36:45+00:00', 'max_elevation_deg': 63.4, 'satellite_id':
            'sat_sentinel_1a'}], 'next_cursor': 'MjAyNi0wNy0wNVQxNDoyNzozMCswMDowMHxjd183YTFiM2M1ZDllMmY='}

    Attributes:
        contact_windows (list['ContactWindow']):
        next_cursor (Union[None, Unset, str]):
    """

    contact_windows: list["ContactWindow"]
    next_cursor: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        contact_windows = []
        for contact_windows_item_data in self.contact_windows:
            contact_windows_item = contact_windows_item_data.to_dict()
            contact_windows.append(contact_windows_item)

        next_cursor: Union[None, Unset, str]
        if isinstance(self.next_cursor, Unset):
            next_cursor = UNSET
        else:
            next_cursor = self.next_cursor

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "contact_windows": contact_windows,
            }
        )
        if next_cursor is not UNSET:
            field_dict["next_cursor"] = next_cursor

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.contact_window import ContactWindow

        d = dict(src_dict)
        contact_windows = []
        _contact_windows = d.pop("contact_windows")
        for contact_windows_item_data in _contact_windows:
            contact_windows_item = ContactWindow.from_dict(contact_windows_item_data)

            contact_windows.append(contact_windows_item)

        def _parse_next_cursor(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        next_cursor = _parse_next_cursor(d.pop("next_cursor", UNSET))

        contact_windows_response = cls(
            contact_windows=contact_windows,
            next_cursor=next_cursor,
        )

        contact_windows_response.additional_properties = d
        return contact_windows_response

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
