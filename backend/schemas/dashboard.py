from datetime import datetime

from pydantic import AliasGenerator, BaseModel, ConfigDict


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


class DashboardSummary(BaseModel):
    project_count: int
    open_task_count: int
    completed_task_count: int
    in_progress_task_count: int
    overdue_task_count: int

    model_config = ConfigDict(
        alias_generator=camel_case,
        populate_by_name=True,
    )


class ActivityRead(BaseModel):
    id: int
    kind: str
    message: str
    project_name: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=camel_case,
        populate_by_name=True,
    )