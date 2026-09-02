from datetime import date

from pydantic import AliasGenerator, BaseModel, ConfigDict, Field


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


class TaskBase(BaseModel):
    project_id: int
    title: str = Field(min_length=1, max_length=240)
    description: str = ""
    status: str = "todo"
    priority: str = "medium"
    assignee: str = ""
    due_date: date | None = None

    model_config = api_model_config


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=240)
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    assignee: str | None = None
    due_date: date | None = None

    model_config = api_model_config


class TaskRead(TaskBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=camel_case,
        populate_by_name=True,
    )