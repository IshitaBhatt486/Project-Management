from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.schemas.dashboard import ActivityRead, DashboardSummary
from backend.services.dashboard import DashboardService

router = APIRouter(tags=["dashboard"])
service = DashboardService()


@router.get("/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummary:
    return service.summary(db)


@router.get("/activity", response_model=list[ActivityRead])
def list_activity(db: Session = Depends(get_db)) -> list[ActivityRead]:
    return service.activity(db)