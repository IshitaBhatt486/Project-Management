from sqlalchemy.orm import Session

from backend.db.models import Project
from backend.repositories.project_member import ProjectMemberRepository
from backend.repositories.project import ProjectRepository
import re

from backend.schemas.project import ProjectCreate, ProjectList, ProjectRead, ProjectUpdate


class ProjectService:
    def __init__(self, repository: ProjectRepository | None = None) -> None:
        self.repository = repository or ProjectRepository()
        self.member_repository = ProjectMemberRepository()

    def _read(self, db: Session, project: Project) -> ProjectRead:
        task_count, completed_count = self.repository.counts(db, project.id)
        return ProjectRead.model_validate(
            {
                **project.__dict__,
                "task_count": task_count,
                "completed_task_count": completed_count,
            }
        )

    def list(
        self,
        db: Session,
        owner_id: int,
        search: str | None,
        status: str | None,
        page: int,
        page_size: int,
    ) -> ProjectList:
        projects, total = self.repository.list(
            db, owner_id, search, status, page, page_size
        )
        return ProjectList(
            items=[self._read(db, item) for item in projects],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get(self, db: Session, project_id: int, owner_id: int) -> ProjectRead | None:
        project = self.repository.get(db, project_id, owner_id)
        return self._read(db, project) if project else None

    def _key_for(self, db: Session, payload: ProjectCreate) -> str:
        requested = payload.key.strip().upper() if payload.key else ""
        base = requested or "".join(re.findall(r"[A-Z0-9]", payload.name.upper()))[:8]
        base = base or "PROJECT"
        candidate = base[:12]
        suffix = 2
        while self.repository.key_exists(db, candidate):
            suffix_text = str(suffix)
            candidate = f"{base[:12-len(suffix_text)]}{suffix_text}"
            suffix += 1
        return candidate

    def create(self, db: Session, payload: ProjectCreate, owner_id: int) -> ProjectRead:
        key = self._key_for(db, payload)
        project = self.repository.create(db, payload, owner_id, key)
        self.member_repository.create(db, project.id, owner_id, "owner")
        return self._read(db, project)

    def update(
        self, db: Session, project_id: int, owner_id: int, payload: ProjectUpdate
    ) -> ProjectRead | None:
        project = self.repository.get(db, project_id, owner_id)
        return self._read(db, self.repository.update(db, project, payload)) if project else None

    def archive(self, db: Session, project_id: int, owner_id: int) -> ProjectRead | None:
        return self.update(
            db,
            project_id,
            owner_id,
            ProjectUpdate(status="archived"),
        )

    def delete(self, db: Session, project_id: int, owner_id: int) -> bool:
        project = self.repository.get(db, project_id, owner_id)
        if not project:
            return False
        self.repository.delete(db, project)
        return True