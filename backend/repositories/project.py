from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from backend.db.models import Project, ProjectMember, Task
from backend.schemas.project import ProjectCreate, ProjectUpdate


class ProjectRepository:
    def list(
        self,
        db: Session,
        owner_id: int,
        search: str | None,
        status: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Project], int]:
        conditions = [ProjectMember.user_id == owner_id]
        if search:
            pattern = f"%{search.strip().lower()}%"
            conditions.append(
                or_(
                    func.lower(Project.name).like(pattern),
                    func.lower(Project.key).like(pattern),
                    func.lower(Project.description).like(pattern),
                )
            )
        if status:
            conditions.append(Project.status == status)
        else:
            conditions.append(Project.status != "archived")
        base_query = select(Project).join(ProjectMember).where(*conditions)
        total = int(db.scalar(select(func.count()).select_from(base_query.subquery())) or 0)
        projects = list(
            db.scalars(
                base_query.order_by(Project.updated_at.desc(), Project.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        return projects, total

    def get(self, db: Session, project_id: int, owner_id: int) -> Project | None:
        return db.scalar(
            select(Project)
            .join(ProjectMember)
            .where(
                Project.id == project_id,
                ProjectMember.user_id == owner_id,
            )
        )

    def key_exists(self, db: Session, key: str) -> bool:
        return db.scalar(select(Project.id).where(Project.key == key)) is not None

    def create(self, db: Session, payload: ProjectCreate, owner_id: int, key: str) -> Project:
        project = Project(
            **payload.model_dump(exclude={"key"}),
            key=key,
            owner_id=owner_id,
        )
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

    def delete(self, db: Session, project: Project) -> None:
        db.delete(project)
        db.commit()

    def counts(self, db: Session, project_id: int) -> tuple[int, int]:
        task_count, completed_count = db.execute(
            select(
                func.count(Task.id),
                func.count(Task.id).filter(Task.status == "done"),
            ).where(Task.project_id == project_id)
        ).one()
        return int(task_count), int(completed_count)