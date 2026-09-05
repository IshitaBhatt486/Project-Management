from datetime import date

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

TaskStatus = Literal["backlog", "todo", "in_progress", "in_review", "done"]
TaskPriority = Literal["low", "medium", "high", "urgent"]


class TaskBase(BaseModel):
    project_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=240)
    description: str = Field(default="", max_length=4000)
    status: TaskStatus = "todo"
    priority: TaskPriority = "medium"
    assignee: str = Field(default="", max_length=120)
    due_date: date | None = None

    model_config = api_model_config

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Task title cannot be blank")
        return value


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=240)
    description: str | None = Field(default=None, max_length=4000)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    assignee: str | None = Field(default=None, max_length=120)
    due_date: date | None = None

    model_config = api_model_config

    @field_validator("title")
    @classmethod
    def updated_title_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Task title cannot be blank")
        return value


class TaskRead(TaskBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=camel_case,
        populate_by_name=True,
    )
