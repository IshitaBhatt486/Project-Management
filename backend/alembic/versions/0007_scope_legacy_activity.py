"""Attach legacy dashboard activity rows to projects for access control."""

from alembic import op
import sqlalchemy as sa


revision = "0007_scope_legacy_activity"
down_revision = "0006_query_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("activity", sa.Column("project_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_activity_project_id_projects",
        "activity",
        "projects",
        ["project_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.execute(
        sa.text(
            "UPDATE activity SET project_id = ("
            "SELECT MIN(projects.id) FROM projects "
            "WHERE projects.name = activity.project_name"
            ") WHERE project_id IS NULL"
        )
    )
    op.create_index("ix_activity_project_created_at", "activity", ["project_id", "created_at", "id"])


def downgrade() -> None:
    op.drop_index("ix_activity_project_created_at", table_name="activity")
    op.drop_constraint("fk_activity_project_id_projects", "activity", type_="foreignkey")
    op.drop_column("activity", "project_id")
