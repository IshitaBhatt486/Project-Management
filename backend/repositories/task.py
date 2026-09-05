from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.models import Project, ProjectMember, Task
from backend.schemas.task import TaskCreate, TaskUpdate


class TaskRepository:
    def list(
        self,
        db: Session,
        owner_id: int,
        project_id: int | None = None,
        status: str | None = None,
    ) -> list[Task]:
        query = (
            select(Task)
            .join(Project)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .where(ProjectMember.user_id == owner_id)
            .order_by(Task.created_at.desc(), Task.id.desc())
        )
        if project_id is not None:
            query = query.where(Task.project_id == project_id)
        if status is not None:
            query = query.where(Task.status == status)
        return list(db.scalars(query))

    def get(self, db: Session, task_id: int, owner_id: int) -> Task | None:
        return db.scalar(
            select(Task)
            .join(Project)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .where(Task.id == task_id, ProjectMember.user_id == owner_id)
        )

    def create(self, db: Session, payload: TaskCreate, owner_id: int) -> Task | None:
        if db.scalar(
            select(Project.id)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .where(
                Project.id == payload.project_id,
                ProjectMember.user_id == owner_id,
            )
        ) is None:
            return None
        task = Task(**payload.model_dump())
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def update(self, db: Session, task: Task, payload: TaskUpdate) -> Task:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(task, field, value)
        db.commit()
        db.refresh(task)
        return task

    def delete(self, db: Session, task: Task) -> None:
        db.delete(task)
        db.commit()
