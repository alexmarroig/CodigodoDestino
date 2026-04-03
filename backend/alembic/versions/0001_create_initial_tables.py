"""create initial tables

Revision ID: 0001_create_initial_tables
Revises:
Create Date: 2026-04-02 00:00:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_create_initial_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    json_type = (
        postgresql.JSONB(astext_type=sa.Text())
        if bind.dialect.name == "postgresql"
        else sa.JSON()
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "map_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("input_data", json_type, nullable=False),
        sa.Column("result", json_type, nullable=False),
        sa.Column("engine_version", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_map_requests_user_id", "map_requests", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_map_requests_user_id", table_name="map_requests")
    op.drop_table("map_requests")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
