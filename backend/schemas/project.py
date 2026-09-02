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


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    key: str = Field(min_length=1, max_length=12)
    description: str = ""
    color: str = "indigo"

    model_config = api_model_config


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    color: str | None = None

    model_config = api_model_config


class ProjectRead(ProjectBase):
    id: int
    task_count: int = 0
    completed_task_count: int = 0

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=camel_case,
        populate_by_name=True,
    )