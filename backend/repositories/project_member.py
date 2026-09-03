from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.models import ProjectMember, User


class ProjectMemberRepository:
    def get_for_user(
        self, db: Session, project_id: int, user_id: int
    ) -> ProjectMember | None:
        return db.scalar(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )

    def list(
        self, db: Session, project_id: int
    ) -> list[tuple[ProjectMember, User]]:
        rows = db.execute(
            select(ProjectMember, User)
            .join(User, User.id == ProjectMember.user_id)
            .where(ProjectMember.project_id == project_id)
            .order_by(ProjectMember.role, User.name)
        ).all()
        return [(member, user) for member, user in rows]

    def get(
        self, db: Session, project_id: int, member_id: int
    ) -> tuple[ProjectMember, User] | None:
        row = db.execute(
            select(ProjectMember, User)
            .join(User, User.id == ProjectMember.user_id)
            .where(
                ProjectMember.project_id == project_id,
                ProjectMember.id == member_id,
            )
        ).one_or_none()
        return (row[0], row[1]) if row else None

    def get_by_user(
        self, db: Session, project_id: int, user_id: int
    ) -> ProjectMember | None:
        return self.get_for_user(db, project_id, user_id)

    def create(
        self, db: Session, project_id: int, user_id: int, role: str
    ) -> ProjectMember:
        member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    def update(self, db: Session, member: ProjectMember, role: str) -> ProjectMember:
        member.role = role
        db.commit()
        db.refresh(member)
        return member

    def delete(self, db: Session, member: ProjectMember) -> None:
        db.delete(member)
        db.commit()