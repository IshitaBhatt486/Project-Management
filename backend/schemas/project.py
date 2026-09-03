from datetime import datetime
from typing import Literal

from pydantic import AliasGenerator, BaseModel, ConfigDict, Field, field_validator


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

api_model_config = ConfigDict(
    alias_generator=camel_case,
    populate_by_name=True,
)

ProjectStatus = Literal["active", "on_hold", "completed", "archived"]


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    key: str = Field(min_length=1, max_length=12)
    description: str = Field(default="", max_length=1000)
    color: str = "indigo"

    model_config = api_model_config


class ProjectCreate(ProjectBase):
    key: str | None = Field(default=None, min_length=1, max_length=12)
    status: Literal["active", "on_hold", "completed"] = "active"

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Project name cannot be blank")
        return normalized


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    color: str | None = None
    status: ProjectStatus | None = None

    model_config = api_model_config

    @field_validator("name")
    @classmethod
    def updated_name_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("Project name cannot be blank")
        return normalized


class ProjectRead(ProjectBase):
    id: int
    owner_id: int | None = None
    status: ProjectStatus = "active"
    created_at: datetime
    updated_at: datetime
    task_count: int = 0
    completed_task_count: int = 0

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=camel_case,
        populate_by_name=True,
    )


class ProjectList(BaseModel):
    items: list[ProjectRead]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")

    model_config = ConfigDict(
        alias_generator=camel_case,
        populate_by_name=True,
    )