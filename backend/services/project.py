import re

from sqlalchemy.orm import Session

from backend.db.models import Project
from backend.repositories.project import ProjectRepository
from backend.repositories.project_member import ProjectMemberRepository
from backend.schemas.project import ProjectCreate, ProjectList, ProjectRead, ProjectUpdate
from backend.services.activity_log import ActivityLogService


class ProjectService:
    def __init__(
        self,
        repository: ProjectRepository | None = None,
        activity_logs: ActivityLogService | None = None,
    ) -> None:
        self.repository = repository or ProjectRepository()
        self.member_repository = ProjectMemberRepository()
        self.activity_logs = activity_logs or ActivityLogService()

    def _read(
        self,
        db: Session,
        project: Project,
        counts: tuple[int, int] | None = None,
    ) -> ProjectRead:
        task_count, completed_count = counts or self.repository.counts(db, project.id)
        return ProjectRead.model_validate(project).model_copy(
            update={
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
        counts = self.repository.counts_for_projects(
            db, [project.id for project in projects]
        )
        return ProjectList(
            items=[self._read(db, item, counts.get(item.id, (0, 0))) for item in projects],
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
        self.activity_logs.record(
            db,
            project.id,
            owner_id,
            "project_created",
            {"project_name": project.name, "project_key": project.key},
        )
        return self._read(db, project)

    def update(
        self, db: Session, project_id: int, owner_id: int, payload: ProjectUpdate
    ) -> ProjectRead | None:
        project = self.repository.get(db, project_id, owner_id)
        if not project:
            return None

        changes = {
            field: value
            for field, value in payload.model_dump(exclude_unset=True).items()
            if value is not None and getattr(project, field) != value
        }
        if not changes:
            return self._read(db, project)

        previous_status = project.status
        updated = self.repository.update(db, project, payload)
        action = (
            "project_archived"
            if updated.status == "archived" and previous_status != "archived"
            else "project_updated"
        )
        metadata = {"changed_fields": list(changes)}
        if "status" in changes:
            metadata["previous_status"] = previous_status
            metadata["status"] = updated.status
        self.activity_logs.record(db, project_id, owner_id, action, metadata)
        return self._read(db, updated)

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
