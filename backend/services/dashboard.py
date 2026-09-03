from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.db.models import Activity, Project, Task
from backend.schemas.dashboard import ActivityRead, DashboardSummary


class DashboardService:
    def summary(self, db: Session) -> DashboardSummary:
        project_count = db.scalar(select(func.count(Project.id))) or 0
        open_task_count = db.scalar(
            select(func.count(Task.id)).where(Task.status != "done")
        ) or 0
        completed_count = db.scalar(
            select(func.count(Task.id)).where(Task.status == "done")
        ) or 0
        in_progress_count = db.scalar(
            select(func.count(Task.id)).where(Task.status == "in_progress")
        ) or 0
        overdue_count = db.scalar(
            select(func.count(Task.id)).where(
                Task.due_date < date.today(), Task.status != "done"
            )
        ) or 0
        return DashboardSummary(
            project_count=project_count,
            open_task_count=open_task_count,
            completed_task_count=completed_count,
            in_progress_task_count=in_progress_count,
            overdue_task_count=overdue_count,
        )

    def activity(
        self, db: Session, project_name: str | None = None
    ) -> list[ActivityRead]:
        query = select(Activity)
        if project_name:
            query = query.where(Activity.project_name == project_name)
        rows = db.scalars(query.order_by(Activity.created_at.desc()).limit(20))
        return [ActivityRead.model_validate(row) for row in rows]