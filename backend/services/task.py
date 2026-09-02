from sqlalchemy.orm import Session

from backend.db.models import Task
from backend.repositories.task import TaskRepository
from backend.schemas.task import TaskCreate, TaskRead, TaskUpdate


class TaskService:
    def __init__(self, repository: TaskRepository | None = None) -> None:
        self.repository = repository or TaskRepository()

    def list(
        self, db: Session, project_id: int | None = None, status: str | None = None
    ) -> list[TaskRead]:
        return [TaskRead.model_validate(item) for item in self.repository.list(db, project_id, status)]

    def create(self, db: Session, payload: TaskCreate) -> TaskRead:
        return TaskRead.model_validate(self.repository.create(db, payload))

    def update(self, db: Session, task_id: int, payload: TaskUpdate) -> TaskRead | None:
        task = self.repository.get(db, task_id)
        return TaskRead.model_validate(self.repository.update(db, task, payload)) if task else None

    def delete(self, db: Session, task_id: int) -> bool:
        task = self.repository.get(db, task_id)
        if not task:
            return False
        self.repository.delete(db, task)
        return True