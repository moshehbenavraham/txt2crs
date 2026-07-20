"""Drop the temporary donor item table.

Revision ID: a7d9c2e4f601
Revises: fe56fa70289e
Create Date: 2026-07-20 00:00:00.000000

The upgrade intentionally removes donor rows after the durable jobs API has
replaced this temporary domain. Downgrade restores the complete previous
schema so the prior application version can start, but it cannot reconstruct
the intentionally deleted rows.
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "a7d9c2e4f601"
down_revision = "fe56fa70289e"
branch_labels = None
depends_on = None

ITEM_OWNER_FOREIGN_KEY = "item_owner_id_fkey"
ITEM_OWNER_INDEX = "ix_item_owner_id"
ITEM_PRIMARY_KEY = "item_pkey"


def upgrade() -> None:
    """Remove the donor table and every intentionally retired donor row."""

    op.drop_table("item")


def downgrade() -> None:
    """Recreate the final donor schema without claiming row recovery."""

    op.create_table(
        "item",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("source_url", sa.String(length=2048), nullable=True),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("content_type", sa.String(length=50), nullable=True),
        sa.Column("item_metadata", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "owner_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["user.id"],
            name=ITEM_OWNER_FOREIGN_KEY,
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=ITEM_PRIMARY_KEY),
    )
    op.create_index(
        ITEM_OWNER_INDEX,
        "item",
        ["owner_id"],
        unique=False,
    )
