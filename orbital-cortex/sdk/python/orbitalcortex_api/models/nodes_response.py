from collections.abc import Mapping
from typing import Any, TypeVar, Optional, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast

if TYPE_CHECKING:
  from ..models.compute_node import ComputeNode
  from ..models.ground_station import GroundStation





T = TypeVar("T", bound="NodesResponse")



@_attrs_define
class NodesResponse:
    """ 
        Attributes:
            compute_nodes (list['ComputeNode']):
            ground_stations (list['GroundStation']):
     """

    compute_nodes: list['ComputeNode']
    ground_stations: list['GroundStation']
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.compute_node import ComputeNode
        from ..models.ground_station import GroundStation
        compute_nodes = []
        for compute_nodes_item_data in self.compute_nodes:
            compute_nodes_item = compute_nodes_item_data.to_dict()
            compute_nodes.append(compute_nodes_item)



        ground_stations = []
        for ground_stations_item_data in self.ground_stations:
            ground_stations_item = ground_stations_item_data.to_dict()
            ground_stations.append(ground_stations_item)




        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "compute_nodes": compute_nodes,
            "ground_stations": ground_stations,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.compute_node import ComputeNode
        from ..models.ground_station import GroundStation
        d = dict(src_dict)
        compute_nodes = []
        _compute_nodes = d.pop("compute_nodes")
        for compute_nodes_item_data in (_compute_nodes):
            compute_nodes_item = ComputeNode.from_dict(compute_nodes_item_data)



            compute_nodes.append(compute_nodes_item)


        ground_stations = []
        _ground_stations = d.pop("ground_stations")
        for ground_stations_item_data in (_ground_stations):
            ground_stations_item = GroundStation.from_dict(ground_stations_item_data)



            ground_stations.append(ground_stations_item)


        nodes_response = cls(
            compute_nodes=compute_nodes,
            ground_stations=ground_stations,
        )


        nodes_response.additional_properties = d
        return nodes_response

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
