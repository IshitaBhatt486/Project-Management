from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.api.dependencies import get_current_user
from backend.db.models import User
from backend.db.session import get_db
from backend.schemas.dashboard import ActivityRead, DashboardSummary
from backend.services.dashboard import DashboardService

router = APIRouter(tags=["dashboard"])
service = DashboardService()


@router.get("/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> DashboardSummary:
    return service.summary(db, user.id)


@router.get("/activity", response_model=list[ActivityRead])
def list_activity(
    project_name: str | None = Query(default=None, max_length=120, alias="projectName"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ActivityRead]:
    return service.activity(db, user.id, project_name)
