from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.repositories.activity_log import ActivityLogRepository
from backend.schemas.dashboard import ActivityLogList, ActivityLogRead
from backend.services.project_access import require_membership


class ActivityLogService:
    def __init__(
        self, repository: ActivityLogRepository | None = None
    ) -> None:
        self.repository = repository or ActivityLogRepository()

    def record(
        self,
        db: Session,
        project_id: int,
        user_id: int,
        action: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.repository.create(db, project_id, user_id, action, metadata or {})

    def list(
        self,
        db: Session,
        project_id: int,
        user_id: int,
        page: int,
        page_size: int,
    ) -> ActivityLogList:
        require_membership(db, project_id, user_id)
        rows, total = self.repository.list(db, project_id, page, page_size)
        items = [
            ActivityLogRead(
                id=log.id,
                project_id=log.project_id,
                user_id=log.user_id,
                actor_name=actor_name,
                project_name=project_name,
                action=log.action,
                metadata=log.metadata_json,
                message=self._message(log.action, actor_name, log.metadata_json),
                created_at=log.created_at,
            )
            for log, actor_name, project_name in rows
        ]
        return ActivityLogList(
            items=items, total=total, page=page, page_size=page_size
        )

    @staticmethod
    def _message(action: str, actor_name: str, metadata: dict[str, Any]) -> str:
        target_name = metadata.get("user_name") or "a user"
        if action == "project_created":
            return f"{actor_name} created project"
        if action == "project_updated":
            if "status" in metadata.get("changed_fields", []):
                return f"{actor_name} changed project status"
            return f"{actor_name} updated project"
        if action == "project_archived":
            return f"{actor_name} archived project"
        if action == "user_invited":
            return f"{actor_name} invited {target_name}"
        if action == "user_removed":
            return f"{actor_name} removed {target_name}"
        if action == "role_changed":
            return f"{actor_name} changed {target_name}'s role"
        return f"{actor_name} updated project activity"