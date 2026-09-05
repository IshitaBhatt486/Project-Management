from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.db.models import ProjectMember, User
from backend.repositories.project_member import ProjectMemberRepository
from backend.repositories.user import UserRepository
from backend.schemas.member import MemberInvite, MemberRead, MemberRoleUpdate
from backend.services.activity_log import ActivityLogService
from backend.services.project_access import require_membership, require_project_role


class ProjectMemberService:
    def __init__(
        self,
        repository: ProjectMemberRepository | None = None,
        user_repository: UserRepository | None = None,
        activity_logs: ActivityLogService | None = None,
    ) -> None:
        self.repository = repository or ProjectMemberRepository()
        self.user_repository = user_repository or UserRepository()
        self.activity_logs = activity_logs or ActivityLogService()

    def _read(self, member: ProjectMember, user: User) -> MemberRead:
        return MemberRead(
            id=member.id,
            project_id=member.project_id,
            user_id=user.id,
            name=user.name,
            email=user.email,
            role=member.role,
        )

    def list(self, db: Session, project_id: int, actor_id: int) -> list[MemberRead]:
        require_membership(db, project_id, actor_id)
        return [
            self._read(member, user)
            for member, user in self.repository.list(db, project_id)
        ]

    def invite(
        self, db: Session, project_id: int, actor_id: int, payload: MemberInvite
    ) -> MemberRead:
        actor = require_project_role(db, project_id, actor_id, {"owner", "admin"})
        if actor.role == "admin" and payload.role == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only invite members or viewers",
            )
        user = self.user_repository.get_by_email(db, str(payload.email).lower())
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No registered user found with that email",
            )
        if self.repository.get_by_user(db, project_id, user.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="That user is already a project member",
            )
        member = self.repository.create(db, project_id, user.id, payload.role)
        self.activity_logs.record(
            db,
            project_id,
            actor_id,
            "user_invited",
            {
                "user_id": user.id,
                "user_name": user.name,
                "user_email": user.email,
                "role": payload.role,
            },
        )
        return self._read(member, user)

    def update_role(
        self,
        db: Session,
        project_id: int,
        member_id: int,
        actor_id: int,
        payload: MemberRoleUpdate,
    ) -> MemberRead:
        require_project_role(db, project_id, actor_id, {"owner"})
        target = self.repository.get(db, project_id, member_id)
        if target is None:
            raise HTTPException(status_code=404, detail="Member not found")
        member, user = target
        if member.role == "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The project owner role cannot be changed",
            )
        previous_role = member.role
        updated = self.repository.update(db, member, payload.role)
        self.activity_logs.record(
            db,
            project_id,
            actor_id,
            "role_changed",
            {
                "user_id": user.id,
                "user_name": user.name,
                "previous_role": previous_role,
                "role": updated.role,
            },
        )
        return self._read(updated, user)

    def remove(
        self, db: Session, project_id: int, member_id: int, actor_id: int
    ) -> None:
        require_project_role(db, project_id, actor_id, {"owner"})
        target = self.repository.get(db, project_id, member_id)
        if target is None:
            raise HTTPException(status_code=404, detail="Member not found")
        member, user = target
        if member.role == "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The project owner cannot be removed",
            )
        self.activity_logs.record(
            db,
            project_id,
            actor_id,
            "user_removed",
            {
                "user_id": user.id,
                "user_name": user.name,
                "user_email": user.email,
                "role": member.role,
            },
        )
        self.repository.delete(db, member)
