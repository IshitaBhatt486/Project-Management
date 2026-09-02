from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.models import Activity


class ActivityRepository:
    def list(self, db: Session, limit: int = 20) -> list[Activity]:
        return list(
            db.scalars(
                select(Activity).order_by(Activity.created_at.desc()).limit(limit)
            )
        )