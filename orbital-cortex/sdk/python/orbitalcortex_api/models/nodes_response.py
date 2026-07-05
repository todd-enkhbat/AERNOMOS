from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.compute_node import ComputeNode
    from ..models.ground_station import GroundStation


T = TypeVar("T", bound="NodesResponse")


@_attrs_define
class NodesResponse:
    """
    Example:
        {'compute_nodes': [{'availability': 0.97, 'base_cost_usd': 60.0, 'compliance_tags': ['civilian', 'commercial'],
            'downlink_mbps': 400, 'gpu_class': 'edge-tpu-class', 'id': 'sim_leo_01', 'latency_minutes': 30.0, 'location':
            'LEO / sun-synchronous', 'name': 'Simulated LEO SAR node 01', 'orbit': 'SSO ~700 km', 'power_state': 'nominal',
            'satellite_id': 'sat_sentinel_1a', 'storage_gb': 512, 'supported_models': ['ship_detection'], 'type':
            'orbital'}], 'ground_stations': [{'altitude_m': 458.0, 'availability': 0.98, 'downlink_mbps': 600, 'id':
            'gs_ksat_svalbard', 'latency_minutes': 8.0, 'latitude': 78.23, 'location': 'Svalbard, Norway', 'longitude':
            15.39, 'min_elevation_deg': 10.0, 'name': 'KSAT Svalbard', 'provider': 'KSAT'}]}

    Attributes:
        compute_nodes (list['ComputeNode']):
        ground_stations (list['GroundStation']):
    """

    compute_nodes: list["ComputeNode"]
    ground_stations: list["GroundStation"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
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
        field_dict.update(
            {
                "compute_nodes": compute_nodes,
                "ground_stations": ground_stations,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.compute_node import ComputeNode
        from ..models.ground_station import GroundStation

        d = dict(src_dict)
        compute_nodes = []
        _compute_nodes = d.pop("compute_nodes")
        for compute_nodes_item_data in _compute_nodes:
            compute_nodes_item = ComputeNode.from_dict(compute_nodes_item_data)

            compute_nodes.append(compute_nodes_item)

        ground_stations = []
        _ground_stations = d.pop("ground_stations")
        for ground_stations_item_data in _ground_stations:
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
