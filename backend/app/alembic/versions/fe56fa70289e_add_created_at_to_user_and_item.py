"""Add created_at to User and Item.

Revision ID: fe56fa70289e
Revises: 6f1d0f1e9b9b
Create Date: 2026-07-17 00:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "fe56fa70289e"
down_revision = "6f1d0f1e9b9b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "item",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "user",
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user", "created_at")
    op.drop_column("item", "created_at")
