from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.api.dependencies import get_current_user
from backend.db.models import User
from backend.db.session import get_db
from backend.schemas.dashboard import ActivityLogList
from backend.services.activity_log import ActivityLogService


router = APIRouter(
    prefix="/projects/{project_id}/activity", tags=["activity"]
)
service = ActivityLogService()


@router.get("", response_model=ActivityLogList)
def list_project_activity(
    project_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50, alias="pageSize"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ActivityLogList:
    return service.list(db, project_id, user.id, page, page_size)