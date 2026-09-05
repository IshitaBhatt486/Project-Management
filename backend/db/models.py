from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        Index("ix_projects_status_updated_at", "status", "updated_at", "id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    key: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    color: Mapped[str] = mapped_column(String(24), default="indigo", nullable=False)
    owner_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(24), default="active", nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    tasks: Mapped[list["Task"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    owner: Mapped["User | None"] = relationship(back_populates="projects")
    members: Mapped[list["ProjectMember"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    projects: Mapped[list[Project]] = relationship(back_populates="owner")
    memberships: Mapped[list["ProjectMember"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    activity_logs: Mapped[list["ActivityLog"]] = relationship(back_populates="user")


class ProjectMember(Base):
    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_members_project_user"),
        Index("ix_project_members_user_project", "user_id", "project_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False, default="member")

    project: Mapped[Project] = relationship(back_populates="members")
    user: Mapped[User] = relationship(back_populates="memberships")


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("ix_tasks_project_created_at", "project_id", "created_at", "id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(String(24), default="todo", nullable=False, index=True)
    priority: Mapped[str] = mapped_column(String(16), default="medium", nullable=False)
    assignee: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    project: Mapped[Project] = relationship(back_populates="tasks")


class Activity(Base):
    __tablename__ = "activity"
    __table_args__ = (
        Index("ix_activity_project_created_at", "project_id", "created_at", "id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=True
    )
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    message: Mapped[str] = mapped_column(String(240), nullable=False)
    project_name: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    __table_args__ = (
        Index(
            "ix_activity_logs_project_created_at",
            "project_id",
            "created_at",
            "id",
        ),
        Index("ix_activity_logs_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(40), nullable=False)
    metadata_json: Mapped[dict] = mapped_column(
        "metadata", JSON, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    project: Mapped[Project] = relationship(back_populates="activity_logs")
    user: Mapped[User] = relationship(back_populates="activity_logs")
