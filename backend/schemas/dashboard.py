from datetime import datetime
from typing import Any

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


class ActivityLogRead(BaseModel):
    id: int
    project_id: int
    user_id: int
    actor_name: str
    project_name: str
    action: str
    metadata: dict[str, Any]
    message: str
    created_at: datetime

    model_config = ConfigDict(
        alias_generator=camel_case,
        populate_by_name=True,
    )


class ActivityLogList(BaseModel):
    items: list[ActivityLogRead]
    total: int
    page: int
    page_size: int = Field(serialization_alias="pageSize")

    model_config = ConfigDict(
        alias_generator=camel_case,
        populate_by_name=True,
    )