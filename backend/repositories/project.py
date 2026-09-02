from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.db.models import Project, Task
from backend.schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository:
    def list(self, db: Session) -> list[Project]:
        return list(db.scalars(select(Project).order_by(Project.created_at.desc())))

    def get(self, db: Session, project_id: int) -> Project | None:
        return db.get(Project, project_id)

    def create(self, db: Session, payload: ProjectCreate) -> Project:
        project = Project(**payload.model_dump())
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    def update(self, db: Session, project: Project, payload: ProjectUpdate) -> Project:
        for field, value in payload.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(project, field, value)
        db.commit()
        db.refresh(project)
        return project

    def counts(self, db: Session, project_id: int) -> tuple[int, int]:
        task_count, completed_count = db.execute(
            select(
                func.count(Task.id),
                func.count(Task.id).filter(Task.status == "done"),
            ).where(Task.project_id == project_id)
        ).one()
        return int(task_count), int(completed_count)