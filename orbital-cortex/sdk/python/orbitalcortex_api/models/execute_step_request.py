from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.execute_step_request_params import ExecuteStepRequestParams


T = TypeVar("T", bound="ExecuteStepRequest")


@_attrs_define
class ExecuteStepRequest:
    """
    Attributes:
        input_ref (str):
        step_id (str):
        task_type (str):
        idempotency_key (None | str | Unset):
        params (ExecuteStepRequestParams | Unset):
    """

    input_ref: str
    step_id: str
    task_type: str
    idempotency_key: None | str | Unset = UNSET
    params: ExecuteStepRequestParams | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        input_ref = self.input_ref

        step_id = self.step_id

        task_type = self.task_type

        idempotency_key: None | str | Unset
        if isinstance(self.idempotency_key, Unset):
            idempotency_key = UNSET
        else:
            idempotency_key = self.idempotency_key

        params: dict[str, Any] | Unset = UNSET
        if not isinstance(self.params, Unset):
            params = self.params.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "input_ref": input_ref,
                "step_id": step_id,
                "task_type": task_type,
            }
        )
        if idempotency_key is not UNSET:
            field_dict["idempotency_key"] = idempotency_key
        if params is not UNSET:
            field_dict["params"] = params

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.execute_step_request_params import ExecuteStepRequestParams

        d = dict(src_dict)
        input_ref = d.pop("input_ref")

        step_id = d.pop("step_id")

        task_type = d.pop("task_type")

        def _parse_idempotency_key(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        idempotency_key = _parse_idempotency_key(d.pop("idempotency_key", UNSET))

        _params = d.pop("params", UNSET)
        params: ExecuteStepRequestParams | Unset
        if isinstance(_params, Unset):
            params = UNSET
        else:
            params = ExecuteStepRequestParams.from_dict(_params)

        execute_step_request = cls(
            input_ref=input_ref,
            step_id=step_id,
            task_type=task_type,
            idempotency_key=idempotency_key,
            params=params,
        )

        execute_step_request.additional_properties = d
        return execute_step_request

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
