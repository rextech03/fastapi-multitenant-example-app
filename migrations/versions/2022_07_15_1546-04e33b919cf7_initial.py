"""Initial

Revision ID: 04e33b919cf7
Revises: 
Create Date: 2022-07-15 15:46:40.927592

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "04e33b919cf7"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("author", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema=None,
    )


def downgrade() -> None:
    op.drop_table(
        "books",
        schema=None,
    )
