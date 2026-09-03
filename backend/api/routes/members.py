from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.api.dependencies import get_current_user
from backend.db.models import User
from backend.db.session import get_db
from backend.schemas.member import MemberInvite, MemberRead, MemberRoleUpdate
from backend.services.project_member import ProjectMemberService

router = APIRouter(prefix="/projects/{project_id}/members", tags=["members"])
service = ProjectMemberService()


@router.get("", response_model=list[MemberRead])
def list_members(
    project_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MemberRead]:
    return service.list(db, project_id, user.id)


@router.post("", response_model=MemberRead, status_code=status.HTTP_201_CREATED)
def invite_member(
    project_id: int,
    payload: MemberInvite,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemberRead:
    return service.invite(db, project_id, user.id, payload)


@router.patch("/{member_id}", response_model=MemberRead)
def change_member_role(
    project_id: int,
    member_id: int,
    payload: MemberRoleUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemberRead:
    return service.update_role(db, project_id, member_id, user.id, payload)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    project_id: int,
    member_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    service.remove(db, project_id, member_id, user.id)