import unittest

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.core.rate_limit import SlidingWindowRateLimiter
from backend.db.base import Base
from backend.db.models import Project, ProjectMember, User
from backend.schemas.project import ProjectCreate
from backend.schemas.task import TaskCreate
from backend.services.project_access import require_project_role


class SecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.user = User(name="Viewer", email="viewer@example.com", password_hash="test")
        self.owner = User(name="Owner", email="owner@example.com", password_hash="test")
        self.db.add_all([self.user, self.owner])
        self.db.flush()
        self.project = Project(name="Private", key="PVT", owner_id=self.owner.id)
        self.db.add(self.project)
        self.db.flush()
        self.db.add_all(
            [
                ProjectMember(project_id=self.project.id, user_id=self.owner.id, role="owner"),
                ProjectMember(project_id=self.project.id, user_id=self.user.id, role="viewer"),
            ]
        )
        self.db.commit()

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def test_viewer_cannot_mutate_project(self) -> None:
        with self.assertRaises(HTTPException) as raised:
            require_project_role(
                self.db, self.project.id, self.user.id, {"owner", "admin"}
            )
        self.assertEqual(raised.exception.status_code, 403)

    def test_task_enums_and_blank_titles_are_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            TaskCreate(project_id=self.project.id, title="   ")
        with self.assertRaises(ValidationError):
            TaskCreate(
                project_id=self.project.id,
                title="Valid",
                status="not-a-status",
            )

    def test_unknown_project_fields_are_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            ProjectCreate.model_validate(
                {"name": "Project", "key": "PRJ", "owner_id": self.user.id}
            )

    def test_authentication_rate_limit(self) -> None:
        limiter = SlidingWindowRateLimiter(attempts=2, window_seconds=60)
        limiter.check("client")
        limiter.check("client")
        with self.assertRaises(HTTPException) as raised:
            limiter.check("client")
        self.assertEqual(raised.exception.status_code, 429)
        self.assertIn("Retry-After", raised.exception.headers)


if __name__ == "__main__":
    unittest.main()
