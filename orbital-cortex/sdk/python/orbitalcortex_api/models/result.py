from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    cast,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.result_geojson import ResultGeojson


T = TypeVar("T", bound="Result")


@_attrs_define
class Result:
    """
    Attributes:
        confidence (float):
        geojson (ResultGeojson):
        id (str):
        job_id (str):
        output_files (list[str]):
        summary (str):
    """

    confidence: float
    geojson: "ResultGeojson"
    id: str
    job_id: str
    output_files: list[str]
    summary: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        confidence = self.confidence

        geojson = self.geojson.to_dict()

        id = self.id

        job_id = self.job_id

        output_files = self.output_files

        summary = self.summary

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "confidence": confidence,
                "geojson": geojson,
                "id": id,
                "job_id": job_id,
                "output_files": output_files,
                "summary": summary,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.result_geojson import ResultGeojson

        d = dict(src_dict)
        confidence = d.pop("confidence")

        geojson = ResultGeojson.from_dict(d.pop("geojson"))

        id = d.pop("id")

        job_id = d.pop("job_id")

        output_files = cast(list[str], d.pop("output_files"))

        summary = d.pop("summary")

        result = cls(
            confidence=confidence,
            geojson=geojson,
            id=id,
            job_id=job_id,
            output_files=output_files,
            summary=summary,
        )

        result.additional_properties = d
        return result

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
