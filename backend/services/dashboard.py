from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.db.models import Activity, ProjectMember, Task
from backend.schemas.dashboard import ActivityRead, DashboardSummary


class DashboardService:
    def summary(self, db: Session, user_id: int) -> DashboardSummary:
        project_count = db.scalar(
            select(func.count(ProjectMember.project_id)).where(
                ProjectMember.user_id == user_id
            )
        ) or 0
        open_task_count, completed_count, in_progress_count, overdue_count = db.execute(
            select(
                func.count(Task.id).filter(Task.status != "done"),
                func.count(Task.id).filter(Task.status == "done"),
                func.count(Task.id).filter(Task.status == "in_progress"),
                func.count(Task.id).filter(
                    Task.due_date < date.today(), Task.status != "done"
                ),
            )
            .join(ProjectMember, ProjectMember.project_id == Task.project_id)
            .where(ProjectMember.user_id == user_id)
        ).one()
        return DashboardSummary(
            project_count=project_count,
            open_task_count=open_task_count,
            completed_task_count=completed_count,
            in_progress_task_count=in_progress_count,
            overdue_task_count=overdue_count,
        )

    def activity(
        self, db: Session, user_id: int, project_name: str | None = None
    ) -> list[ActivityRead]:
        query = (
            select(Activity)
            .join(ProjectMember, ProjectMember.project_id == Activity.project_id)
            .where(ProjectMember.user_id == user_id)
        )
        if project_name:
            query = query.where(Activity.project_name == project_name)
        rows = db.scalars(
            query.order_by(Activity.created_at.desc(), Activity.id.desc()).limit(20)
        )
        return [ActivityRead.model_validate(row) for row in rows]
