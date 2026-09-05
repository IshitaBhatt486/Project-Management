from datetime import date, datetime, timezone

from sqlalchemy import select

from backend.db.models import Activity, Project, Task
from backend.db.session import SessionLocal


def seed() -> None:
    with SessionLocal() as db:
        if db.scalar(select(Project.id).limit(1)) is not None:
            return

        product = Project(
            name="Product launch",
            key="LAUNCH",
            description="Coordinate the work for the next product release.",
            color="indigo",
        )
        operations = Project(
            name="Operations",
            key="OPS",
            description="Keep the team and customer experience running smoothly.",
            color="amber",
        )
        db.add_all([product, operations])
        db.flush()
        db.add_all(
            [
                Task(
                    project_id=product.id,
                    title="Finalize onboarding flow",
                    description="Review the last open questions with design.",
                    status="in_progress",
                    priority="high",
                    assignee="Maya Chen",
                    due_date=date(2026, 9, 8),
                ),
                Task(
                    project_id=product.id,
                    title="Write release notes",
                    description="Prepare a concise changelog for the launch email.",
                    status="todo",
                    priority="medium",
                    assignee="Noah Williams",
                    due_date=date(2026, 9, 12),
                ),
                Task(
                    project_id=operations.id,
                    title="Audit support macros",
                    description="Remove outdated responses before the next campaign.",
                    status="done",
                    priority="low",
                    assignee="Maya Chen",
                    due_date=date(2026, 9, 2),
                ),
                Activity(
                    project_id=product.id,
                    kind="task_updated",
                    message="Maya moved Finalize onboarding flow to In progress",
                    project_name=product.name,
                    created_at=datetime.now(timezone.utc),
                ),
                Activity(
                    project_id=operations.id,
                    kind="task_completed",
                    message="Maya completed Audit support macros",
                    project_name=operations.name,
                    created_at=datetime.now(timezone.utc),
                ),
            ]
        )
        db.commit()


if __name__ == "__main__":
    seed()
