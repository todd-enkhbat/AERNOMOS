from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.candidate_score_weights import CandidateScoreWeights
    from ..models.hard_constraint_failure import HardConstraintFailure


T = TypeVar("T", bound="CandidateScore")


@_attrs_define
class CandidateScore:
    """
    Attributes:
        availability_score (float):
        available (bool):
        compliance_score (float):
        contact_score (float):
        cost_score (float):
        eligible (bool):
        estimated_cost_usd (float):
        estimated_latency_minutes (float):
        latency_score (float):
        model_support_score (float):
        node_id (str):
        preference_score (float):
        reasons (list[str]):
        score (float):
        binding_constraint (None | str | Unset):
        est_downlink_mb (float | None | Unset):
        hard_constraint_failures (list[HardConstraintFailure] | Unset):
        next_aos_utc (None | str | Unset):
        next_contact_minutes (float | None | Unset):
        next_max_elevation_deg (float | None | Unset):
        selected_ground_station_id (None | str | Unset):
        weights (CandidateScoreWeights | Unset):
    """

    availability_score: float
    available: bool
    compliance_score: float
    contact_score: float
    cost_score: float
    eligible: bool
    estimated_cost_usd: float
    estimated_latency_minutes: float
    latency_score: float
    model_support_score: float
    node_id: str
    preference_score: float
    reasons: list[str]
    score: float
    binding_constraint: None | str | Unset = UNSET
    est_downlink_mb: float | None | Unset = UNSET
    hard_constraint_failures: list[HardConstraintFailure] | Unset = UNSET
    next_aos_utc: None | str | Unset = UNSET
    next_contact_minutes: float | None | Unset = UNSET
    next_max_elevation_deg: float | None | Unset = UNSET
    selected_ground_station_id: None | str | Unset = UNSET
    weights: CandidateScoreWeights | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        availability_score = self.availability_score

        available = self.available

        compliance_score = self.compliance_score

        contact_score = self.contact_score

        cost_score = self.cost_score

        eligible = self.eligible

        estimated_cost_usd = self.estimated_cost_usd

        estimated_latency_minutes = self.estimated_latency_minutes

        latency_score = self.latency_score

        model_support_score = self.model_support_score

        node_id = self.node_id

        preference_score = self.preference_score

        reasons = self.reasons

        score = self.score

        binding_constraint: None | str | Unset
        if isinstance(self.binding_constraint, Unset):
            binding_constraint = UNSET
        else:
            binding_constraint = self.binding_constraint

        est_downlink_mb: float | None | Unset
        if isinstance(self.est_downlink_mb, Unset):
            est_downlink_mb = UNSET
        else:
            est_downlink_mb = self.est_downlink_mb

        hard_constraint_failures: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.hard_constraint_failures, Unset):
            hard_constraint_failures = []
            for hard_constraint_failures_item_data in self.hard_constraint_failures:
                hard_constraint_failures_item = (
                    hard_constraint_failures_item_data.to_dict()
                )
                hard_constraint_failures.append(hard_constraint_failures_item)

        next_aos_utc: None | str | Unset
        if isinstance(self.next_aos_utc, Unset):
            next_aos_utc = UNSET
        else:
            next_aos_utc = self.next_aos_utc

        next_contact_minutes: float | None | Unset
        if isinstance(self.next_contact_minutes, Unset):
            next_contact_minutes = UNSET
        else:
            next_contact_minutes = self.next_contact_minutes

        next_max_elevation_deg: float | None | Unset
        if isinstance(self.next_max_elevation_deg, Unset):
            next_max_elevation_deg = UNSET
        else:
            next_max_elevation_deg = self.next_max_elevation_deg

        selected_ground_station_id: None | str | Unset
        if isinstance(self.selected_ground_station_id, Unset):
            selected_ground_station_id = UNSET
        else:
            selected_ground_station_id = self.selected_ground_station_id

        weights: dict[str, Any] | Unset = UNSET
        if not isinstance(self.weights, Unset):
            weights = self.weights.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "availability_score": availability_score,
                "available": available,
                "compliance_score": compliance_score,
                "contact_score": contact_score,
                "cost_score": cost_score,
                "eligible": eligible,
                "estimated_cost_usd": estimated_cost_usd,
                "estimated_latency_minutes": estimated_latency_minutes,
                "latency_score": latency_score,
                "model_support_score": model_support_score,
                "node_id": node_id,
                "preference_score": preference_score,
                "reasons": reasons,
                "score": score,
            }
        )
        if binding_constraint is not UNSET:
            field_dict["binding_constraint"] = binding_constraint
        if est_downlink_mb is not UNSET:
            field_dict["est_downlink_mb"] = est_downlink_mb
        if hard_constraint_failures is not UNSET:
            field_dict["hard_constraint_failures"] = hard_constraint_failures
        if next_aos_utc is not UNSET:
            field_dict["next_aos_utc"] = next_aos_utc
        if next_contact_minutes is not UNSET:
            field_dict["next_contact_minutes"] = next_contact_minutes
        if next_max_elevation_deg is not UNSET:
            field_dict["next_max_elevation_deg"] = next_max_elevation_deg
        if selected_ground_station_id is not UNSET:
            field_dict["selected_ground_station_id"] = selected_ground_station_id
        if weights is not UNSET:
            field_dict["weights"] = weights

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.candidate_score_weights import CandidateScoreWeights
        from ..models.hard_constraint_failure import HardConstraintFailure

        d = dict(src_dict)
        availability_score = d.pop("availability_score")

        available = d.pop("available")

        compliance_score = d.pop("compliance_score")

        contact_score = d.pop("contact_score")

        cost_score = d.pop("cost_score")

        eligible = d.pop("eligible")

        estimated_cost_usd = d.pop("estimated_cost_usd")

        estimated_latency_minutes = d.pop("estimated_latency_minutes")

        latency_score = d.pop("latency_score")

        model_support_score = d.pop("model_support_score")

        node_id = d.pop("node_id")

        preference_score = d.pop("preference_score")

        reasons = cast(list[str], d.pop("reasons"))

        score = d.pop("score")

        def _parse_binding_constraint(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        binding_constraint = _parse_binding_constraint(
            d.pop("binding_constraint", UNSET)
        )

        def _parse_est_downlink_mb(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        est_downlink_mb = _parse_est_downlink_mb(d.pop("est_downlink_mb", UNSET))

        _hard_constraint_failures = d.pop("hard_constraint_failures", UNSET)
        hard_constraint_failures: list[HardConstraintFailure] | Unset = UNSET
        if _hard_constraint_failures is not UNSET:
            hard_constraint_failures = []
            for hard_constraint_failures_item_data in _hard_constraint_failures:
                hard_constraint_failures_item = HardConstraintFailure.from_dict(
                    hard_constraint_failures_item_data
                )

                hard_constraint_failures.append(hard_constraint_failures_item)

        def _parse_next_aos_utc(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        next_aos_utc = _parse_next_aos_utc(d.pop("next_aos_utc", UNSET))

        def _parse_next_contact_minutes(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        next_contact_minutes = _parse_next_contact_minutes(
            d.pop("next_contact_minutes", UNSET)
        )

        def _parse_next_max_elevation_deg(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        next_max_elevation_deg = _parse_next_max_elevation_deg(
            d.pop("next_max_elevation_deg", UNSET)
        )

        def _parse_selected_ground_station_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        selected_ground_station_id = _parse_selected_ground_station_id(
            d.pop("selected_ground_station_id", UNSET)
        )

        _weights = d.pop("weights", UNSET)
        weights: CandidateScoreWeights | Unset
        if isinstance(_weights, Unset):
            weights = UNSET
        else:
            weights = CandidateScoreWeights.from_dict(_weights)

        candidate_score = cls(
            availability_score=availability_score,
            available=available,
            compliance_score=compliance_score,
            contact_score=contact_score,
            cost_score=cost_score,
            eligible=eligible,
            estimated_cost_usd=estimated_cost_usd,
            estimated_latency_minutes=estimated_latency_minutes,
            latency_score=latency_score,
            model_support_score=model_support_score,
            node_id=node_id,
            preference_score=preference_score,
            reasons=reasons,
            score=score,
            binding_constraint=binding_constraint,
            est_downlink_mb=est_downlink_mb,
            hard_constraint_failures=hard_constraint_failures,
            next_aos_utc=next_aos_utc,
            next_contact_minutes=next_contact_minutes,
            next_max_elevation_deg=next_max_elevation_deg,
            selected_ground_station_id=selected_ground_station_id,
            weights=weights,
        )

        candidate_score.additional_properties = d
        return candidate_score

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
