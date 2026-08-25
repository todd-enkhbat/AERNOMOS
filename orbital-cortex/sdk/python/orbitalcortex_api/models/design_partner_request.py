from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DesignPartnerRequest")


@_attrs_define
class DesignPartnerRequest:
    """
    Attributes:
        created_at (datetime.datetime):
        id (UUID):
        mission_type (str):
        name (str):
        organization (str):
        permission_to_contact (bool):
        requested_integration (str):
        role (str):
        work_email (str):
        mission_id (None | Unset | UUID):
    """

    created_at: datetime.datetime
    id: UUID
    mission_type: str
    name: str
    organization: str
    permission_to_contact: bool
    requested_integration: str
    role: str
    work_email: str
    mission_id: None | Unset | UUID = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at.isoformat()

        id = str(self.id)

        mission_type = self.mission_type

        name = self.name

        organization = self.organization

        permission_to_contact = self.permission_to_contact

        requested_integration = self.requested_integration

        role = self.role

        work_email = self.work_email

        mission_id: None | str | Unset
        if isinstance(self.mission_id, Unset):
            mission_id = UNSET
        elif isinstance(self.mission_id, UUID):
            mission_id = str(self.mission_id)
        else:
            mission_id = self.mission_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "id": id,
                "mission_type": mission_type,
                "name": name,
                "organization": organization,
                "permission_to_contact": permission_to_contact,
                "requested_integration": requested_integration,
                "role": role,
                "work_email": work_email,
            }
        )
        if mission_id is not UNSET:
            field_dict["mission_id"] = mission_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        id = UUID(d.pop("id"))

        mission_type = d.pop("mission_type")

        name = d.pop("name")

        organization = d.pop("organization")

        permission_to_contact = d.pop("permission_to_contact")

        requested_integration = d.pop("requested_integration")

        role = d.pop("role")

        work_email = d.pop("work_email")

        def _parse_mission_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                mission_id_type_0 = UUID(data)

                return mission_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        mission_id = _parse_mission_id(d.pop("mission_id", UNSET))

        design_partner_request = cls(
            created_at=created_at,
            id=id,
            mission_type=mission_type,
            name=name,
            organization=organization,
            permission_to_contact=permission_to_contact,
            requested_integration=requested_integration,
            role=role,
            work_email=work_email,
            mission_id=mission_id,
        )

        design_partner_request.additional_properties = d
        return design_partner_request

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
