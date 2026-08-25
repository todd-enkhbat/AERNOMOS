from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.execution_result import ExecutionResult
    from ..models.external_job_status import ExternalJobStatus


T = TypeVar("T", bound="ExecutionStatusResponse")


@_attrs_define
class ExecutionStatusResponse:
    """
    Attributes:
        job (ExternalJobStatus):
        task_type (str):
        download_url (None | str | Unset):
        observed_truth_status (None | str | Unset):
        plan_step_id (None | str | Unset):
        result (ExecutionResult | None | Unset):
    """

    job: ExternalJobStatus
    task_type: str
    download_url: None | str | Unset = UNSET
    observed_truth_status: None | str | Unset = UNSET
    plan_step_id: None | str | Unset = UNSET
    result: ExecutionResult | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.execution_result import ExecutionResult

        job = self.job.to_dict()

        task_type = self.task_type

        download_url: None | str | Unset
        if isinstance(self.download_url, Unset):
            download_url = UNSET
        else:
            download_url = self.download_url

        observed_truth_status: None | str | Unset
        if isinstance(self.observed_truth_status, Unset):
            observed_truth_status = UNSET
        else:
            observed_truth_status = self.observed_truth_status

        plan_step_id: None | str | Unset
        if isinstance(self.plan_step_id, Unset):
            plan_step_id = UNSET
        else:
            plan_step_id = self.plan_step_id

        result: dict[str, Any] | None | Unset
        if isinstance(self.result, Unset):
            result = UNSET
        elif isinstance(self.result, ExecutionResult):
            result = self.result.to_dict()
        else:
            result = self.result

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "job": job,
                "task_type": task_type,
            }
        )
        if download_url is not UNSET:
            field_dict["download_url"] = download_url
        if observed_truth_status is not UNSET:
            field_dict["observed_truth_status"] = observed_truth_status
        if plan_step_id is not UNSET:
            field_dict["plan_step_id"] = plan_step_id
        if result is not UNSET:
            field_dict["result"] = result

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.execution_result import ExecutionResult
        from ..models.external_job_status import ExternalJobStatus

        d = dict(src_dict)
        job = ExternalJobStatus.from_dict(d.pop("job"))

        task_type = d.pop("task_type")

        def _parse_download_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        download_url = _parse_download_url(d.pop("download_url", UNSET))

        def _parse_observed_truth_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        observed_truth_status = _parse_observed_truth_status(
            d.pop("observed_truth_status", UNSET)
        )

        def _parse_plan_step_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        plan_step_id = _parse_plan_step_id(d.pop("plan_step_id", UNSET))

        def _parse_result(data: object) -> ExecutionResult | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                result_type_0 = ExecutionResult.from_dict(data)

                return result_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ExecutionResult | None | Unset, data)

        result = _parse_result(d.pop("result", UNSET))

        execution_status_response = cls(
            job=job,
            task_type=task_type,
            download_url=download_url,
            observed_truth_status=observed_truth_status,
            plan_step_id=plan_step_id,
            result=result,
        )

        execution_status_response.additional_properties = d
        return execution_status_response

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
