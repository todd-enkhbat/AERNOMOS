from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import cast, Union
from typing import Union

if TYPE_CHECKING:
  from ..models.scene_response_scene_type_0 import SceneResponseSceneType0





T = TypeVar("T", bound="SceneResponse")



@_attrs_define
class SceneResponse:
    """ 
        Attributes:
            scene (Union['SceneResponseSceneType0', None, Unset]):
     """

    scene: Union['SceneResponseSceneType0', None, Unset] = UNSET
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
        field_dict.update({
        })
        if scene is not UNSET:
            field_dict["scene"] = scene

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.scene_response_scene_type_0 import SceneResponseSceneType0
        d = dict(src_dict)
        def _parse_scene(data: object) -> Union['SceneResponseSceneType0', None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                scene_type_0 = SceneResponseSceneType0.from_dict(data)



                return scene_type_0
            except: # noqa: E722
                pass
            return cast(Union['SceneResponseSceneType0', None, Unset], data)

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
