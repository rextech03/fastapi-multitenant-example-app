"""Init shared data

Revision ID: f3ffe4615512
Revises: 
Create Date: 2022-07-14 19:34:53.231907

"""
import uuid

import sqlalchemy as sa
from alembic import op
from migrations.tenant import for_each_tenant_schema
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = "f3ffe4615512"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA shared")
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", UUID(as_uuid=True), default=uuid.uuid4, unique=True),
        sa.Column("name", sa.String(128), nullable=True),
        sa.Column("schema", sa.String(128), nullable=True),
        sa.Column("schema_header_id", sa.String(128), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="shared",
    )

    op.create_table(
        "shared_users",
        sa.Column("id", sa.Integer(), sa.Identity(), autoincrement=True, nullable=False),
        sa.Column("uuid", UUID(as_uuid=True), default=uuid.uuid4, unique=True),
        sa.Column("email", sa.String(128), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), default=func.now()),
        sa.PrimaryKeyConstraint("id"),
        schema="shared",
    )

    op.execute("CREATE SCHEMA tenant_default")

    query = sa.text(
        "INSERT INTO shared.tenants (name, schema, schema_header_id) " "VALUES (:name, :schema, :schema_header_id)"
    ).bindparams(name="default", schema="tenant_default", schema_header_id="127.0.0.1")
    op.execute(query)


def downgrade() -> None:
    op.execute("DROP SCHEMA shared")

    op.execute("DROP SCHEMA tenant_default")
