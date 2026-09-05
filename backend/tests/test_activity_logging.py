import unittest

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.db.base import Base
from backend.db.models import ActivityLog, User
from backend.schemas.member import MemberInvite
from backend.schemas.project import ProjectCreate, ProjectUpdate
from backend.services.activity_log import ActivityLogService
from backend.services.project import ProjectService
from backend.services.project_member import ProjectMemberService
from backend.services.dashboard import DashboardService
from backend.schemas.task import TaskCreate
from backend.services.task import TaskService


class ActivityLoggingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.owner = self._user("Sarah", "sarah@example.com")
        self.invitee = self._user("John", "john@example.com")
        self.projects = ProjectService()
        self.members = ProjectMemberService()
        self.activity = ActivityLogService()

    def tearDown(self) -> None:
        self.db.close()
        self.engine.dispose()

    def _user(self, name: str, email: str) -> User:
        user = User(name=name, email=email, password_hash="test")
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def _project(self):
        return self.projects.create(
            self.db,
            ProjectCreate(name="Apollo", key="APL"),
            self.owner.id,
        )

    def _actions(self, project_id: int) -> list[str]:
        return list(
            self.db.scalars(
                select(ActivityLog.action)
                .where(ActivityLog.project_id == project_id)
                .order_by(ActivityLog.id)
            )
        )

    def test_creating_project_creates_activity_log(self) -> None:
        project = self._project()

        self.assertEqual(self._actions(project.id), ["project_created"])

    def test_editing_project_creates_activity_log(self) -> None:
        project = self._project()

        self.projects.update(
            self.db,
            project.id,
            self.owner.id,
            ProjectUpdate(status="on_hold"),
        )

        self.assertEqual(
            self._actions(project.id), ["project_created", "project_updated"]
        )

    def test_inviting_user_creates_activity_log(self) -> None:
        project = self._project()

        self.members.invite(
            self.db,
            project.id,
            self.owner.id,
            MemberInvite(email=self.invitee.email, role="member"),
        )

        logs = list(
            self.db.scalars(
                select(ActivityLog)
                .where(ActivityLog.project_id == project.id)
                .order_by(ActivityLog.id)
            )
        )
        self.assertEqual([log.action for log in logs], ["project_created", "user_invited"])
        self.assertEqual(logs[-1].metadata_json["user_name"], "John")

    def test_activity_order_is_most_recent_first(self) -> None:
        project = self._project()
        self.projects.update(
            self.db, project.id, self.owner.id, ProjectUpdate(name="Apollo 2")
        )
        self.projects.update(
            self.db, project.id, self.owner.id, ProjectUpdate(status="completed")
        )

        result = self.activity.list(self.db, project.id, self.owner.id, 1, 10)

        self.assertEqual(
            [item.id for item in result.items],
            sorted((item.id for item in result.items), reverse=True),
        )

    def test_activity_pagination(self) -> None:
        project = self._project()
        for name in ("Apollo 2", "Apollo 3", "Apollo 4", "Apollo 5"):
            self.projects.update(
                self.db, project.id, self.owner.id, ProjectUpdate(name=name)
            )

        first = self.activity.list(self.db, project.id, self.owner.id, 1, 2)
        second = self.activity.list(self.db, project.id, self.owner.id, 2, 2)
        third = self.activity.list(self.db, project.id, self.owner.id, 3, 2)

        self.assertEqual(first.total, 5)
        self.assertEqual(len(first.items), 2)
        self.assertEqual(len(second.items), 2)
        self.assertEqual(len(third.items), 1)
        self.assertTrue(first.items[-1].id > second.items[0].id)

    def test_dashboard_is_scoped_to_current_user(self) -> None:
        other = self._user("Alex", "alex@example.com")
        own_project = self._project()
        other_project = self.projects.create(
            self.db, ProjectCreate(name="Private", key="PVT"), other.id
        )
        TaskService().create(
            self.db,
            TaskCreate(project_id=other_project.id, title="Private task"),
            other.id,
        )

        summary = DashboardService().summary(self.db, self.owner.id)

        self.assertEqual(summary.project_count, 1)
        self.assertEqual(summary.open_task_count, 0)
        self.assertNotEqual(own_project.id, other_project.id)

    def test_removed_member_is_logged_and_loses_access(self) -> None:
        project = self._project()
        invited = self.members.invite(
            self.db,
            project.id,
            self.owner.id,
            MemberInvite(email=self.invitee.email, role="viewer"),
        )

        self.members.remove(self.db, project.id, invited.id, self.owner.id)

        self.assertEqual(self._actions(project.id)[-1], "user_removed")
        self.assertIsNone(
            self.members.repository.get_by_user(self.db, project.id, self.invitee.id)
        )


if __name__ == "__main__":
    unittest.main()
