from sqlalchemy.orm import Session

from backend.db.models import Project
from backend.repositories.project import ProjectRepository
from backend.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate


class ProjectService:
    def __init__(self, repository: ProjectRepository | None = None) -> None:
        self.repository = repository or ProjectRepository()

    def _read(self, db: Session, project: Project) -> ProjectRead:
        task_count, completed_count = self.repository.counts(db, project.id)
        return ProjectRead.model_validate(
            {
                **project.__dict__,
                "task_count": task_count,
                "completed_task_count": completed_count,
            }
        )

    def list(self, db: Session) -> list[ProjectRead]:
        return [self._read(db, item) for item in self.repository.list(db)]

    def get(self, db: Session, project_id: int) -> ProjectRead | None:
        project = self.repository.get(db, project_id)
        return self._read(db, project) if project else None

    def create(self, db: Session, payload: ProjectCreate) -> ProjectRead:
        return self._read(db, self.repository.create(db, payload))

    def update(
        self, db: Session, project_id: int, payload: ProjectUpdate
    ) -> ProjectRead | None:
        project = self.repository.get(db, project_id)
        return self._read(db, self.repository.update(db, project, payload)) if project else None