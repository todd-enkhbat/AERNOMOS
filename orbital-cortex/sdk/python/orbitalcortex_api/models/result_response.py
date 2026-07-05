from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.artifact_ref import ArtifactRef
    from ..models.result import Result


T = TypeVar("T", bound="ResultResponse")


@_attrs_define
class ResultResponse:
    """
    Example:
        {'artifacts': [{'key': 'results/job_9f2c41d3a8b7/detections.geojson', 'url': 'https://api.orbital-cortex.example
            /v1/artifacts/results/job_9f2c41d3a8b7/detections.geojson?expires=1783700000&signature=8c1f2ab90d374e6c'}],
            'result': {'confidence': 0.91, 'geojson': {'features': [{'geometry': {'coordinates': [-74.045, 40.63], 'type':
            'Point'}, 'properties': {'class': 'cargo', 'confidence': 0.94, 'simulated': True}, 'type': 'Feature'}], 'type':
            'FeatureCollection'}, 'id': 'res_3c7d91e5b2a4', 'job_id': 'job_9f2c41d3a8b7', 'output_files':
            ['results/job_9f2c41d3a8b7/detections.geojson', 'results/job_9f2c41d3a8b7/summary.json'], 'summary': 'Detected
            17 vessels in New York Harbor.'}}

    Attributes:
        result (Result):
        artifacts (Union[Unset, list['ArtifactRef']]):
    """

    result: "Result"
    artifacts: Union[Unset, list["ArtifactRef"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result = self.result.to_dict()

        artifacts: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.artifacts, Unset):
            artifacts = []
            for artifacts_item_data in self.artifacts:
                artifacts_item = artifacts_item_data.to_dict()
                artifacts.append(artifacts_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "result": result,
            }
        )
        if artifacts is not UNSET:
            field_dict["artifacts"] = artifacts

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.artifact_ref import ArtifactRef
        from ..models.result import Result

        d = dict(src_dict)
        result = Result.from_dict(d.pop("result"))

        artifacts = []
        _artifacts = d.pop("artifacts", UNSET)
        for artifacts_item_data in _artifacts or []:
            artifacts_item = ArtifactRef.from_dict(artifacts_item_data)

            artifacts.append(artifacts_item)

        result_response = cls(
            result=result,
            artifacts=artifacts,
        )

        result_response.additional_properties = d
        return result_response

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
