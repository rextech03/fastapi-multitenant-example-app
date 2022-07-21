"""Add Permissions entries

Revision ID: 9efdd94249a5
Revises: e3aad4a7daff
Create Date: 2022-07-20 14:58:50.431864

"""
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = "9efdd94249a5"
down_revision = "e3aad4a7daff"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # query = sa.text(
    #     "INSERT INTO permissions (uuid, account_id,	name, title, description) "
    #     "VALUES (:uuid, :account_id, :name, :title, :description)"
    # ).bindparams(uuid=uuid4(), account_id=1, name="USER_ADD", title="Add user", description="Add user permission")
    # op.execute(
    #     query,
    #     # schema=None,
    # )

    permissions = table(
        "permissions",
        sa.Column("id", sa.INTEGER(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), autoincrement=False, nullable=True),
        sa.Column("name", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column("title", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column("description", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    )

    op.bulk_insert(
        permissions,
        [
            {
                "uuid": uuid4(),
                "name": "USER_ADD",
                "title": "Add user",
                "description": "Add user permission",
            },
            {
                "uuid": uuid4(),
                "name": "USER_DELETE",
                "title": "Dlete user",
                "description": "Delete user permission",
            },
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM permissions WHERE name IN ('USER_ADD', 'USER_DELETE')", execution_options=None)
