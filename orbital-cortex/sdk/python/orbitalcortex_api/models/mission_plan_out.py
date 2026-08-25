from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mission_plan_out_estimates_type_0 import MissionPlanOutEstimatesType0
    from ..models.mission_plan_out_explanation_type_0 import (
        MissionPlanOutExplanationType0,
    )
    from ..models.mission_plan_step_out import MissionPlanStepOut
    from ..models.source_evidence_out import SourceEvidenceOut


T = TypeVar("T", bound="MissionPlanOut")


@_attrs_define
class MissionPlanOut:
    """
    Attributes:
        id (str):
        mission_id (str):
        recommended (bool):
        status (str):
        summary (str):
        version (int):
        assumptions (list[Any] | Unset):
        confidence (float | None | Unset):
        created_at (None | str | Unset):
        estimated_total_cost_usd (float | None | Unset):
        estimated_total_time_seconds (float | None | Unset):
        estimates (MissionPlanOutEstimatesType0 | None | Unset):
        evidence (list[SourceEvidenceOut] | None | Unset):
        explanation (MissionPlanOutExplanationType0 | None | Unset):
        feasibility_status (None | str | Unset):
        input_hash (None | str | Unset):
        pattern (None | str | Unset):
        plan_hash (None | str | Unset):
        planner_config_version (None | str | Unset):
        score (float | None | Unset):
        steps (list[MissionPlanStepOut] | None | Unset):
    """

    id: str
    mission_id: str
    recommended: bool
    status: str
    summary: str
    version: int
    assumptions: list[Any] | Unset = UNSET
    confidence: float | None | Unset = UNSET
    created_at: None | str | Unset = UNSET
    estimated_total_cost_usd: float | None | Unset = UNSET
    estimated_total_time_seconds: float | None | Unset = UNSET
    estimates: MissionPlanOutEstimatesType0 | None | Unset = UNSET
    evidence: list[SourceEvidenceOut] | None | Unset = UNSET
    explanation: MissionPlanOutExplanationType0 | None | Unset = UNSET
    feasibility_status: None | str | Unset = UNSET
    input_hash: None | str | Unset = UNSET
    pattern: None | str | Unset = UNSET
    plan_hash: None | str | Unset = UNSET
    planner_config_version: None | str | Unset = UNSET
    score: float | None | Unset = UNSET
    steps: list[MissionPlanStepOut] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.mission_plan_out_estimates_type_0 import (
            MissionPlanOutEstimatesType0,
        )
        from ..models.mission_plan_out_explanation_type_0 import (
            MissionPlanOutExplanationType0,
        )

        id = self.id

        mission_id = self.mission_id

        recommended = self.recommended

        status = self.status

        summary = self.summary

        version = self.version

        assumptions: list[Any] | Unset = UNSET
        if not isinstance(self.assumptions, Unset):
            assumptions = self.assumptions

        confidence: float | None | Unset
        if isinstance(self.confidence, Unset):
            confidence = UNSET
        else:
            confidence = self.confidence

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        else:
            created_at = self.created_at

        estimated_total_cost_usd: float | None | Unset
        if isinstance(self.estimated_total_cost_usd, Unset):
            estimated_total_cost_usd = UNSET
        else:
            estimated_total_cost_usd = self.estimated_total_cost_usd

        estimated_total_time_seconds: float | None | Unset
        if isinstance(self.estimated_total_time_seconds, Unset):
            estimated_total_time_seconds = UNSET
        else:
            estimated_total_time_seconds = self.estimated_total_time_seconds

        estimates: dict[str, Any] | None | Unset
        if isinstance(self.estimates, Unset):
            estimates = UNSET
        elif isinstance(self.estimates, MissionPlanOutEstimatesType0):
            estimates = self.estimates.to_dict()
        else:
            estimates = self.estimates

        evidence: list[dict[str, Any]] | None | Unset
        if isinstance(self.evidence, Unset):
            evidence = UNSET
        elif isinstance(self.evidence, list):
            evidence = []
            for evidence_type_0_item_data in self.evidence:
                evidence_type_0_item = evidence_type_0_item_data.to_dict()
                evidence.append(evidence_type_0_item)

        else:
            evidence = self.evidence

        explanation: dict[str, Any] | None | Unset
        if isinstance(self.explanation, Unset):
            explanation = UNSET
        elif isinstance(self.explanation, MissionPlanOutExplanationType0):
            explanation = self.explanation.to_dict()
        else:
            explanation = self.explanation

        feasibility_status: None | str | Unset
        if isinstance(self.feasibility_status, Unset):
            feasibility_status = UNSET
        else:
            feasibility_status = self.feasibility_status

        input_hash: None | str | Unset
        if isinstance(self.input_hash, Unset):
            input_hash = UNSET
        else:
            input_hash = self.input_hash

        pattern: None | str | Unset
        if isinstance(self.pattern, Unset):
            pattern = UNSET
        else:
            pattern = self.pattern

        plan_hash: None | str | Unset
        if isinstance(self.plan_hash, Unset):
            plan_hash = UNSET
        else:
            plan_hash = self.plan_hash

        planner_config_version: None | str | Unset
        if isinstance(self.planner_config_version, Unset):
            planner_config_version = UNSET
        else:
            planner_config_version = self.planner_config_version

        score: float | None | Unset
        if isinstance(self.score, Unset):
            score = UNSET
        else:
            score = self.score

        steps: list[dict[str, Any]] | None | Unset
        if isinstance(self.steps, Unset):
            steps = UNSET
        elif isinstance(self.steps, list):
            steps = []
            for steps_type_0_item_data in self.steps:
                steps_type_0_item = steps_type_0_item_data.to_dict()
                steps.append(steps_type_0_item)

        else:
            steps = self.steps

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "mission_id": mission_id,
                "recommended": recommended,
                "status": status,
                "summary": summary,
                "version": version,
            }
        )
        if assumptions is not UNSET:
            field_dict["assumptions"] = assumptions
        if confidence is not UNSET:
            field_dict["confidence"] = confidence
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if estimated_total_cost_usd is not UNSET:
            field_dict["estimated_total_cost_usd"] = estimated_total_cost_usd
        if estimated_total_time_seconds is not UNSET:
            field_dict["estimated_total_time_seconds"] = estimated_total_time_seconds
        if estimates is not UNSET:
            field_dict["estimates"] = estimates
        if evidence is not UNSET:
            field_dict["evidence"] = evidence
        if explanation is not UNSET:
            field_dict["explanation"] = explanation
        if feasibility_status is not UNSET:
            field_dict["feasibility_status"] = feasibility_status
        if input_hash is not UNSET:
            field_dict["input_hash"] = input_hash
        if pattern is not UNSET:
            field_dict["pattern"] = pattern
        if plan_hash is not UNSET:
            field_dict["plan_hash"] = plan_hash
        if planner_config_version is not UNSET:
            field_dict["planner_config_version"] = planner_config_version
        if score is not UNSET:
            field_dict["score"] = score
        if steps is not UNSET:
            field_dict["steps"] = steps

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mission_plan_out_estimates_type_0 import (
            MissionPlanOutEstimatesType0,
        )
        from ..models.mission_plan_out_explanation_type_0 import (
            MissionPlanOutExplanationType0,
        )
        from ..models.mission_plan_step_out import MissionPlanStepOut
        from ..models.source_evidence_out import SourceEvidenceOut

        d = dict(src_dict)
        id = d.pop("id")

        mission_id = d.pop("mission_id")

        recommended = d.pop("recommended")

        status = d.pop("status")

        summary = d.pop("summary")

        version = d.pop("version")

        assumptions = cast(list[Any], d.pop("assumptions", UNSET))

        def _parse_confidence(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        confidence = _parse_confidence(d.pop("confidence", UNSET))

        def _parse_created_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        def _parse_estimated_total_cost_usd(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        estimated_total_cost_usd = _parse_estimated_total_cost_usd(
            d.pop("estimated_total_cost_usd", UNSET)
        )

        def _parse_estimated_total_time_seconds(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        estimated_total_time_seconds = _parse_estimated_total_time_seconds(
            d.pop("estimated_total_time_seconds", UNSET)
        )

        def _parse_estimates(
            data: object,
        ) -> MissionPlanOutEstimatesType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                estimates_type_0 = MissionPlanOutEstimatesType0.from_dict(data)

                return estimates_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MissionPlanOutEstimatesType0 | None | Unset, data)

        estimates = _parse_estimates(d.pop("estimates", UNSET))

        def _parse_evidence(data: object) -> list[SourceEvidenceOut] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                evidence_type_0 = []
                _evidence_type_0 = data
                for evidence_type_0_item_data in _evidence_type_0:
                    evidence_type_0_item = SourceEvidenceOut.from_dict(
                        evidence_type_0_item_data
                    )

                    evidence_type_0.append(evidence_type_0_item)

                return evidence_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[SourceEvidenceOut] | None | Unset, data)

        evidence = _parse_evidence(d.pop("evidence", UNSET))

        def _parse_explanation(
            data: object,
        ) -> MissionPlanOutExplanationType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                explanation_type_0 = MissionPlanOutExplanationType0.from_dict(data)

                return explanation_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MissionPlanOutExplanationType0 | None | Unset, data)

        explanation = _parse_explanation(d.pop("explanation", UNSET))

        def _parse_feasibility_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        feasibility_status = _parse_feasibility_status(
            d.pop("feasibility_status", UNSET)
        )

        def _parse_input_hash(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        input_hash = _parse_input_hash(d.pop("input_hash", UNSET))

        def _parse_pattern(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pattern = _parse_pattern(d.pop("pattern", UNSET))

        def _parse_plan_hash(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        plan_hash = _parse_plan_hash(d.pop("plan_hash", UNSET))

        def _parse_planner_config_version(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        planner_config_version = _parse_planner_config_version(
            d.pop("planner_config_version", UNSET)
        )

        def _parse_score(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        score = _parse_score(d.pop("score", UNSET))

        def _parse_steps(data: object) -> list[MissionPlanStepOut] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                steps_type_0 = []
                _steps_type_0 = data
                for steps_type_0_item_data in _steps_type_0:
                    steps_type_0_item = MissionPlanStepOut.from_dict(
                        steps_type_0_item_data
                    )

                    steps_type_0.append(steps_type_0_item)

                return steps_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[MissionPlanStepOut] | None | Unset, data)

        steps = _parse_steps(d.pop("steps", UNSET))

        mission_plan_out = cls(
            id=id,
            mission_id=mission_id,
            recommended=recommended,
            status=status,
            summary=summary,
            version=version,
            assumptions=assumptions,
            confidence=confidence,
            created_at=created_at,
            estimated_total_cost_usd=estimated_total_cost_usd,
            estimated_total_time_seconds=estimated_total_time_seconds,
            estimates=estimates,
            evidence=evidence,
            explanation=explanation,
            feasibility_status=feasibility_status,
            input_hash=input_hash,
            pattern=pattern,
            plan_hash=plan_hash,
            planner_config_version=planner_config_version,
            score=score,
            steps=steps,
        )

        mission_plan_out.additional_properties = d
        return mission_plan_out

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
