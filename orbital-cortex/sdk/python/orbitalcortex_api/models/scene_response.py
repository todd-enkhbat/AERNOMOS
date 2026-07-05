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
    from ..models.scene_response_scene_type_0 import SceneResponseSceneType0


T = TypeVar("T", bound="SceneResponse")


@_attrs_define
class SceneResponse:
    """
    Example:
        {'scene': {'aoi': {'coordinates': [[[-74.3, 40.3], [-73.5, 40.3], [-73.5, 41.0], [-74.3, 41.0], [-74.3, 40.3]]],
            'type': 'Polygon'}, 'captured_utc': '2026-06-15T10:42:00+00:00', 'cog_url':
            'mock://scenes/ny_harbor/backscatter.tif', 'id': 'scene_6e2a9c4f1b8d', 'job_id': 'job_9f2c41d3a8b7', 'mode': 'IW
            GRD', 'provenance': 'Canned Sentinel-1 IW GRD chip over New York Harbor. Offline SNAP-style processing pin; not
            live SAR.', 'resolution_m': 10.0, 'sensor': 'Sentinel-1', 'source': 'simulator/ny_harbor_scene', 'stac_item_id':
            'S1A_IW_GRDH_NY_HARBOR_DEMO'}}

    Attributes:
        scene (Union['SceneResponseSceneType0', None, Unset]):
    """

    scene: Union["SceneResponseSceneType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.scene_response_scene_type_0 import SceneResponseSceneType0

        scene: Union[None, Unset, dict[str, Any]]
        if isinstance(self.scene, Unset):
            scene = UNSET
        elif isinstance(self.scene, SceneResponseSceneType0):
            scene = self.scene.to_dict()
        else:
            scene = self.scene

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if scene is not UNSET:
            field_dict["scene"] = scene

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.scene_response_scene_type_0 import SceneResponseSceneType0

        d = dict(src_dict)

        def _parse_scene(data: object) -> Union["SceneResponseSceneType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                scene_type_0 = SceneResponseSceneType0.from_dict(data)

                return scene_type_0
            except:  # noqa: E722
                pass
            return cast(Union["SceneResponseSceneType0", None, Unset], data)

        scene = _parse_scene(d.pop("scene", UNSET))

        scene_response = cls(
            scene=scene,
        )

        scene_response.additional_properties = d
        return scene_response

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
