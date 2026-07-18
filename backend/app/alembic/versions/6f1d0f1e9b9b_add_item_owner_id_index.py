"""Add index for item owner lookups

Revision ID: 6f1d0f1e9b9b
Revises: 4ac9cd0948d7
Create Date: 2026-02-20 00:00:00.000000

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "6f1d0f1e9b9b"
down_revision = "4ac9cd0948d7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(op.f("ix_item_owner_id"), "item", ["owner_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_item_owner_id"), table_name="item")
