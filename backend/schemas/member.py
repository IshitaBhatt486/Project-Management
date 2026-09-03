from typing import Literal

from pydantic import AliasGenerator, BaseModel, ConfigDict, EmailStr, Field


camel_case = AliasGenerator(
    validation_alias=lambda value: "".join(
        part.capitalize() if index else part
        for index, part in enumerate(value.split("_"))
    ),
    serialization_alias=lambda value: "".join(
        part.capitalize() if index else part
        for index, part in enumerate(value.split("_"))
    ),
)


MemberRole = Literal["owner", "admin", "member", "viewer"]
AssignableMemberRole = Literal["admin", "member", "viewer"]


class MemberInvite(BaseModel):
    email: EmailStr
    role: AssignableMemberRole = "member"


class MemberRoleUpdate(BaseModel):
    role: AssignableMemberRole


class MemberRead(BaseModel):
    id: int
    project_id: int
    user_id: int
    name: str
    email: EmailStr
    role: MemberRole

    model_config = ConfigDict(
        alias_generator=camel_case,
        populate_by_name=True,
    )
