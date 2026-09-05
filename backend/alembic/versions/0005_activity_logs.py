"""Add project activity logs."""

from alembic import op
import sqlalchemy as sa


revision = "0005_activity_logs"
down_revision = "0004_project_members"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "activity_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("action", sa.String(length=40), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_activity_logs_project_created_at",
        "activity_logs",
        ["project_id", "created_at", "id"],
    )
    op.create_index(
        "ix_activity_logs_user_id",
        "activity_logs",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_activity_logs_user_id", table_name="activity_logs")
    op.drop_index(
        "ix_activity_logs_project_created_at", table_name="activity_logs"
    )
    op.drop_table("activity_logs")