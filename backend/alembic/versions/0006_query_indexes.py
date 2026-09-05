"""Add composite indexes for common dashboard and list queries."""

from alembic import op


revision = "0006_query_indexes"
down_revision = "0005_activity_logs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_projects_status_updated_at",
        "projects",
        ["status", "updated_at", "id"],
    )
    op.create_index(
        "ix_tasks_project_created_at",
        "tasks",
        ["project_id", "created_at", "id"],
    )
    op.create_index(
        "ix_project_members_user_project",
        "project_members",
        ["user_id", "project_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_project_members_user_project", table_name="project_members")
    op.drop_index("ix_tasks_project_created_at", table_name="tasks")
    op.drop_index("ix_projects_status_updated_at", table_name="projects")
