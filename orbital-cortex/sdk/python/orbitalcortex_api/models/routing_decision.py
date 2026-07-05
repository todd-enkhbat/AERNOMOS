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
  from ..models.candidate_score import CandidateScore





T = TypeVar("T", bound="RoutingDecision")



@_attrs_define
class RoutingDecision:
    """ 
        Attributes:
            candidate_scores (list['CandidateScore']):
            confidence (float):
            estimated_cost_usd (float):
            estimated_latency_minutes (float):
            id (str):
            job_id (str):
            reasons (list[str]):
            selected_node_id (str):
            config_version (Union[None, Unset, str]):
            decided_at_utc (Union[None, Unset, str]):
            decision_hash (Union[None, Unset, str]):
            fallback_node_id (Union[None, Unset, str]):
            input_hash (Union[None, Unset, str]):
            seed (Union[None, Unset, int]):
            selected_ground_station_id (Union[None, Unset, str]):
            tle_snapshot_id (Union[None, Unset, str]):
     """

    candidate_scores: list['CandidateScore']
    confidence: float
    estimated_cost_usd: float
    estimated_latency_minutes: float
    id: str
    job_id: str
    reasons: list[str]
    selected_node_id: str
    config_version: Union[None, Unset, str] = UNSET
    decided_at_utc: Union[None, Unset, str] = UNSET
    decision_hash: Union[None, Unset, str] = UNSET
    fallback_node_id: Union[None, Unset, str] = UNSET
    input_hash: Union[None, Unset, str] = UNSET
    seed: Union[None, Unset, int] = UNSET
    selected_ground_station_id: Union[None, Unset, str] = UNSET
    tle_snapshot_id: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.candidate_score import CandidateScore
        candidate_scores = []
        for candidate_scores_item_data in self.candidate_scores:
            candidate_scores_item = candidate_scores_item_data.to_dict()
            candidate_scores.append(candidate_scores_item)



        confidence = self.confidence

        estimated_cost_usd = self.estimated_cost_usd

        estimated_latency_minutes = self.estimated_latency_minutes

        id = self.id

        job_id = self.job_id

        reasons = self.reasons



        selected_node_id = self.selected_node_id

        config_version: Union[None, Unset, str]
        if isinstance(self.config_version, Unset):
            config_version = UNSET
        else:
            config_version = self.config_version

        decided_at_utc: Union[None, Unset, str]
        if isinstance(self.decided_at_utc, Unset):
            decided_at_utc = UNSET
        else:
            decided_at_utc = self.decided_at_utc

        decision_hash: Union[None, Unset, str]
        if isinstance(self.decision_hash, Unset):
            decision_hash = UNSET
        else:
            decision_hash = self.decision_hash

        fallback_node_id: Union[None, Unset, str]
        if isinstance(self.fallback_node_id, Unset):
            fallback_node_id = UNSET
        else:
            fallback_node_id = self.fallback_node_id

        input_hash: Union[None, Unset, str]
        if isinstance(self.input_hash, Unset):
            input_hash = UNSET
        else:
            input_hash = self.input_hash

        seed: Union[None, Unset, int]
        if isinstance(self.seed, Unset):
            seed = UNSET
        else:
            seed = self.seed

        selected_ground_station_id: Union[None, Unset, str]
        if isinstance(self.selected_ground_station_id, Unset):
            selected_ground_station_id = UNSET
        else:
            selected_ground_station_id = self.selected_ground_station_id

        tle_snapshot_id: Union[None, Unset, str]
        if isinstance(self.tle_snapshot_id, Unset):
            tle_snapshot_id = UNSET
        else:
            tle_snapshot_id = self.tle_snapshot_id


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "candidate_scores": candidate_scores,
            "confidence": confidence,
            "estimated_cost_usd": estimated_cost_usd,
            "estimated_latency_minutes": estimated_latency_minutes,
            "id": id,
            "job_id": job_id,
            "reasons": reasons,
            "selected_node_id": selected_node_id,
        })
        if config_version is not UNSET:
            field_dict["config_version"] = config_version
        if decided_at_utc is not UNSET:
            field_dict["decided_at_utc"] = decided_at_utc
        if decision_hash is not UNSET:
            field_dict["decision_hash"] = decision_hash
        if fallback_node_id is not UNSET:
            field_dict["fallback_node_id"] = fallback_node_id
        if input_hash is not UNSET:
            field_dict["input_hash"] = input_hash
        if seed is not UNSET:
            field_dict["seed"] = seed
        if selected_ground_station_id is not UNSET:
            field_dict["selected_ground_station_id"] = selected_ground_station_id
        if tle_snapshot_id is not UNSET:
            field_dict["tle_snapshot_id"] = tle_snapshot_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.candidate_score import CandidateScore
        d = dict(src_dict)
        candidate_scores = []
        _candidate_scores = d.pop("candidate_scores")
        for candidate_scores_item_data in (_candidate_scores):
            candidate_scores_item = CandidateScore.from_dict(candidate_scores_item_data)



            candidate_scores.append(candidate_scores_item)


        confidence = d.pop("confidence")

        estimated_cost_usd = d.pop("estimated_cost_usd")

        estimated_latency_minutes = d.pop("estimated_latency_minutes")

        id = d.pop("id")

        job_id = d.pop("job_id")

        reasons = cast(list[str], d.pop("reasons"))


        selected_node_id = d.pop("selected_node_id")

        def _parse_config_version(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        config_version = _parse_config_version(d.pop("config_version", UNSET))


        def _parse_decided_at_utc(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        decided_at_utc = _parse_decided_at_utc(d.pop("decided_at_utc", UNSET))


        def _parse_decision_hash(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        decision_hash = _parse_decision_hash(d.pop("decision_hash", UNSET))


        def _parse_fallback_node_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        fallback_node_id = _parse_fallback_node_id(d.pop("fallback_node_id", UNSET))


        def _parse_input_hash(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        input_hash = _parse_input_hash(d.pop("input_hash", UNSET))


        def _parse_seed(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        seed = _parse_seed(d.pop("seed", UNSET))


        def _parse_selected_ground_station_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        selected_ground_station_id = _parse_selected_ground_station_id(d.pop("selected_ground_station_id", UNSET))


        def _parse_tle_snapshot_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        tle_snapshot_id = _parse_tle_snapshot_id(d.pop("tle_snapshot_id", UNSET))


        routing_decision = cls(
            candidate_scores=candidate_scores,
            confidence=confidence,
            estimated_cost_usd=estimated_cost_usd,
            estimated_latency_minutes=estimated_latency_minutes,
            id=id,
            job_id=job_id,
            reasons=reasons,
            selected_node_id=selected_node_id,
            config_version=config_version,
            decided_at_utc=decided_at_utc,
            decision_hash=decision_hash,
            fallback_node_id=fallback_node_id,
            input_hash=input_hash,
            seed=seed,
            selected_ground_station_id=selected_ground_station_id,
            tle_snapshot_id=tle_snapshot_id,
        )


        routing_decision.additional_properties = d
        return routing_decision

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
