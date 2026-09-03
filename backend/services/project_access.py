from collections.abc import Collection

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.db.models import ProjectMember
from backend.repositories.project_member import ProjectMemberRepository

member_repository = ProjectMemberRepository()


def get_membership(
    db: Session, project_id: int, user_id: int
) -> ProjectMember | None:
    return member_repository.get_for_user(db, project_id, user_id)


def require_membership(db: Session, project_id: int, user_id: int) -> ProjectMember:
    membership = get_membership(db, project_id, user_id)
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return membership


def require_project_role(
    db: Session,
    project_id: int,
    user_id: int,
    allowed_roles: Collection[str],
) -> ProjectMember:
    membership = require_membership(db, project_id, user_id)
    if membership.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    return membership