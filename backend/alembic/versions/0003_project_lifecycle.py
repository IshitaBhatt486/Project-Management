"""Add project ownership, status, and update timestamps."""

from alembic import op
import sqlalchemy as sa

revision = "0003_project_lifecycle"
down_revision = "0002_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column("owner_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "projects",
        sa.Column(
            "status",
            sa.String(length=24),
            nullable=False,
            server_default="active",
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_projects_owner_id", "projects", ["owner_id"])
    op.create_index("ix_projects_status", "projects", ["status"])
    op.create_foreign_key(
        "fk_projects_owner_id_users",
        "projects",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.execute(
        sa.text(
            "UPDATE projects "
            "SET owner_id = (SELECT id FROM users ORDER BY id LIMIT 1) "
            "WHERE owner_id IS NULL"
        )
    )


def downgrade() -> None:
    op.drop_constraint("fk_projects_owner_id_users", "projects", type_="foreignkey")
    op.drop_index("ix_projects_status", table_name="projects")
    op.drop_index("ix_projects_owner_id", table_name="projects")
    op.drop_column("projects", "updated_at")
    op.drop_column("projects", "status")
    op.drop_column("projects", "owner_id")