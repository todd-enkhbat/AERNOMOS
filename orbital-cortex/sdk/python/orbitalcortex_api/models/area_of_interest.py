from collections.abc import Mapping
from typing import (
    Any,
    Literal,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AreaOfInterest")


@_attrs_define
class AreaOfInterest:
    """
    Attributes:
        coordinates (list[float]):
        type_ (Literal['bbox']):
    """

    coordinates: list[float]
    type_: Literal["bbox"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        coordinates = self.coordinates

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "coordinates": coordinates,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        coordinates = cast(list[float], d.pop("coordinates"))

        type_ = cast(Literal["bbox"], d.pop("type"))
        if type_ != "bbox":
            raise ValueError(f"type must match const 'bbox', got '{type_}'")

        area_of_interest = cls(
            coordinates=coordinates,
            type_=type_,
        )

        area_of_interest.additional_properties = d
        return area_of_interest

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
