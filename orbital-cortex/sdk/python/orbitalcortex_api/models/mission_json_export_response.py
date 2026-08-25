from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.mission_json_export_response_disclosures import (
        MissionJsonExportResponseDisclosures,
    )
    from ..models.mission_json_export_response_geographic_summary import (
        MissionJsonExportResponseGeographicSummary,
    )
    from ..models.mission_json_export_response_mission_input import (
        MissionJsonExportResponseMissionInput,
    )
    from ..models.mission_json_export_response_selected_plan_type_0 import (
        MissionJsonExportResponseSelectedPlanType0,
    )
    from ..models.mission_json_export_response_source_snapshots import (
        MissionJsonExportResponseSourceSnapshots,
    )
    from ..models.mission_json_export_response_truth_statuses import (
        MissionJsonExportResponseTruthStatuses,
    )


T = TypeVar("T", bound="MissionJsonExportResponse")


@_attrs_define
class MissionJsonExportResponse:
    """Versioned mission brief JSON (schema_version required).

    Attributes:
        document_type (str):
        generated_at (str):
        mission_input (MissionJsonExportResponseMissionInput):
        schema_version (int):
        assumptions (list[Any] | Unset):
        candidate_plans (list[Any] | Unset):
        disclosures (MissionJsonExportResponseDisclosures | Unset):
        geographic_summary (MissionJsonExportResponseGeographicSummary | Unset):
        missing_integrations (list[Any] | Unset):
        next_actions (list[Any] | Unset):
        rejection_reasons (list[Any] | Unset):
        selected_plan (MissionJsonExportResponseSelectedPlanType0 | None | Unset):
        source_evidence (list[Any] | Unset):
        source_snapshots (MissionJsonExportResponseSourceSnapshots | Unset):
        truth_statuses (MissionJsonExportResponseTruthStatuses | Unset):
    """

    document_type: str
    generated_at: str
    mission_input: MissionJsonExportResponseMissionInput
    schema_version: int
    assumptions: list[Any] | Unset = UNSET
    candidate_plans: list[Any] | Unset = UNSET
    disclosures: MissionJsonExportResponseDisclosures | Unset = UNSET
    geographic_summary: MissionJsonExportResponseGeographicSummary | Unset = UNSET
    missing_integrations: list[Any] | Unset = UNSET
    next_actions: list[Any] | Unset = UNSET
    rejection_reasons: list[Any] | Unset = UNSET
    selected_plan: MissionJsonExportResponseSelectedPlanType0 | None | Unset = UNSET
    source_evidence: list[Any] | Unset = UNSET
    source_snapshots: MissionJsonExportResponseSourceSnapshots | Unset = UNSET
    truth_statuses: MissionJsonExportResponseTruthStatuses | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.mission_json_export_response_selected_plan_type_0 import (
            MissionJsonExportResponseSelectedPlanType0,
        )

        document_type = self.document_type

        generated_at = self.generated_at

        mission_input = self.mission_input.to_dict()

        schema_version = self.schema_version

        assumptions: list[Any] | Unset = UNSET
        if not isinstance(self.assumptions, Unset):
            assumptions = self.assumptions

        candidate_plans: list[Any] | Unset = UNSET
        if not isinstance(self.candidate_plans, Unset):
            candidate_plans = self.candidate_plans

        disclosures: dict[str, Any] | Unset = UNSET
        if not isinstance(self.disclosures, Unset):
            disclosures = self.disclosures.to_dict()

        geographic_summary: dict[str, Any] | Unset = UNSET
        if not isinstance(self.geographic_summary, Unset):
            geographic_summary = self.geographic_summary.to_dict()

        missing_integrations: list[Any] | Unset = UNSET
        if not isinstance(self.missing_integrations, Unset):
            missing_integrations = self.missing_integrations

        next_actions: list[Any] | Unset = UNSET
        if not isinstance(self.next_actions, Unset):
            next_actions = self.next_actions

        rejection_reasons: list[Any] | Unset = UNSET
        if not isinstance(self.rejection_reasons, Unset):
            rejection_reasons = self.rejection_reasons

        selected_plan: dict[str, Any] | None | Unset
        if isinstance(self.selected_plan, Unset):
            selected_plan = UNSET
        elif isinstance(self.selected_plan, MissionJsonExportResponseSelectedPlanType0):
            selected_plan = self.selected_plan.to_dict()
        else:
            selected_plan = self.selected_plan

        source_evidence: list[Any] | Unset = UNSET
        if not isinstance(self.source_evidence, Unset):
            source_evidence = self.source_evidence

        source_snapshots: dict[str, Any] | Unset = UNSET
        if not isinstance(self.source_snapshots, Unset):
            source_snapshots = self.source_snapshots.to_dict()

        truth_statuses: dict[str, Any] | Unset = UNSET
        if not isinstance(self.truth_statuses, Unset):
            truth_statuses = self.truth_statuses.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "document_type": document_type,
                "generated_at": generated_at,
                "mission_input": mission_input,
                "schema_version": schema_version,
            }
        )
        if assumptions is not UNSET:
            field_dict["assumptions"] = assumptions
        if candidate_plans is not UNSET:
            field_dict["candidate_plans"] = candidate_plans
        if disclosures is not UNSET:
            field_dict["disclosures"] = disclosures
        if geographic_summary is not UNSET:
            field_dict["geographic_summary"] = geographic_summary
        if missing_integrations is not UNSET:
            field_dict["missing_integrations"] = missing_integrations
        if next_actions is not UNSET:
            field_dict["next_actions"] = next_actions
        if rejection_reasons is not UNSET:
            field_dict["rejection_reasons"] = rejection_reasons
        if selected_plan is not UNSET:
            field_dict["selected_plan"] = selected_plan
        if source_evidence is not UNSET:
            field_dict["source_evidence"] = source_evidence
        if source_snapshots is not UNSET:
            field_dict["source_snapshots"] = source_snapshots
        if truth_statuses is not UNSET:
            field_dict["truth_statuses"] = truth_statuses

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.mission_json_export_response_disclosures import (
            MissionJsonExportResponseDisclosures,
        )
        from ..models.mission_json_export_response_geographic_summary import (
            MissionJsonExportResponseGeographicSummary,
        )
        from ..models.mission_json_export_response_mission_input import (
            MissionJsonExportResponseMissionInput,
        )
        from ..models.mission_json_export_response_selected_plan_type_0 import (
            MissionJsonExportResponseSelectedPlanType0,
        )
        from ..models.mission_json_export_response_source_snapshots import (
            MissionJsonExportResponseSourceSnapshots,
        )
        from ..models.mission_json_export_response_truth_statuses import (
            MissionJsonExportResponseTruthStatuses,
        )

        d = dict(src_dict)
        document_type = d.pop("document_type")

        generated_at = d.pop("generated_at")

        mission_input = MissionJsonExportResponseMissionInput.from_dict(
            d.pop("mission_input")
        )

        schema_version = d.pop("schema_version")

        assumptions = cast(list[Any], d.pop("assumptions", UNSET))

        candidate_plans = cast(list[Any], d.pop("candidate_plans", UNSET))

        _disclosures = d.pop("disclosures", UNSET)
        disclosures: MissionJsonExportResponseDisclosures | Unset
        if isinstance(_disclosures, Unset):
            disclosures = UNSET
        else:
            disclosures = MissionJsonExportResponseDisclosures.from_dict(_disclosures)

        _geographic_summary = d.pop("geographic_summary", UNSET)
        geographic_summary: MissionJsonExportResponseGeographicSummary | Unset
        if isinstance(_geographic_summary, Unset):
            geographic_summary = UNSET
        else:
            geographic_summary = MissionJsonExportResponseGeographicSummary.from_dict(
                _geographic_summary
            )

        missing_integrations = cast(list[Any], d.pop("missing_integrations", UNSET))

        next_actions = cast(list[Any], d.pop("next_actions", UNSET))

        rejection_reasons = cast(list[Any], d.pop("rejection_reasons", UNSET))

        def _parse_selected_plan(
            data: object,
        ) -> MissionJsonExportResponseSelectedPlanType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                selected_plan_type_0 = (
                    MissionJsonExportResponseSelectedPlanType0.from_dict(data)
                )

                return selected_plan_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MissionJsonExportResponseSelectedPlanType0 | None | Unset, data)

        selected_plan = _parse_selected_plan(d.pop("selected_plan", UNSET))

        source_evidence = cast(list[Any], d.pop("source_evidence", UNSET))

        _source_snapshots = d.pop("source_snapshots", UNSET)
        source_snapshots: MissionJsonExportResponseSourceSnapshots | Unset
        if isinstance(_source_snapshots, Unset):
            source_snapshots = UNSET
        else:
            source_snapshots = MissionJsonExportResponseSourceSnapshots.from_dict(
                _source_snapshots
            )

        _truth_statuses = d.pop("truth_statuses", UNSET)
        truth_statuses: MissionJsonExportResponseTruthStatuses | Unset
        if isinstance(_truth_statuses, Unset):
            truth_statuses = UNSET
        else:
            truth_statuses = MissionJsonExportResponseTruthStatuses.from_dict(
                _truth_statuses
            )

        mission_json_export_response = cls(
            document_type=document_type,
            generated_at=generated_at,
            mission_input=mission_input,
            schema_version=schema_version,
            assumptions=assumptions,
            candidate_plans=candidate_plans,
            disclosures=disclosures,
            geographic_summary=geographic_summary,
            missing_integrations=missing_integrations,
            next_actions=next_actions,
            rejection_reasons=rejection_reasons,
            selected_plan=selected_plan,
            source_evidence=source_evidence,
            source_snapshots=source_snapshots,
            truth_statuses=truth_statuses,
        )

        mission_json_export_response.additional_properties = d
        return mission_json_export_response

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
