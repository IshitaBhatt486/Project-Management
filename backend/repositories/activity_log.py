from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.db.models import ActivityLog, Project, User


class ActivityLogRepository:
    def create(
        self,
        db: Session,
        project_id: int,
        user_id: int,
        action: str,
        metadata: dict,
    ) -> ActivityLog:
        log = ActivityLog(
            project_id=project_id,
            user_id=user_id,
            action=action,
            metadata_json=metadata,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    def list(
        self, db: Session, project_id: int, page: int, page_size: int
    ) -> tuple[list[tuple[ActivityLog, str, str]], int]:
        total = int(
            db.scalar(
                select(func.count(ActivityLog.id)).where(
                    ActivityLog.project_id == project_id
                )
            )
            or 0
        )
        rows = db.execute(
            select(ActivityLog, User.name, Project.name)
            .join(User, User.id == ActivityLog.user_id)
            .join(Project, Project.id == ActivityLog.project_id)
            .where(ActivityLog.project_id == project_id)
            .order_by(ActivityLog.created_at.desc(), ActivityLog.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        return [(log, actor_name, project_name) for log, actor_name, project_name in rows], total