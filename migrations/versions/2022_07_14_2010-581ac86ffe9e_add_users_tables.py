"""Add Users tables

Revision ID: 581ac86ffe9e
Revises: 080e24511d27
Create Date: 2022-07-14 20:10:56.976794

"""
import sqlalchemy as sa
from alembic import op
from migrations.tenant import for_each_tenant_schema
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "581ac86ffe9e"
down_revision = "080e24511d27"
branch_labels = None
depends_on = None


@for_each_tenant_schema
def upgrade(schema: str) -> None:
    op.create_table(
        "roles",
        sa.Column(
            "id",
            sa.INTEGER(),
            sa.Identity(always=False, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("role_name", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column("role_description", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="roles_pkey"),
        schema=schema,
    )
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.INTEGER(),
            sa.Identity(always=False, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("email", sa.VARCHAR(length=256), autoincrement=False, nullable=True),
        sa.Column("first_name", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column("last_name", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column("user_role_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("created_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(["user_role_id"], ["tenant_default.roles.id"], name="role_fk"),
        sa.PrimaryKeyConstraint("id", name="users_pkey"),
        sa.UniqueConstraint("email", name="users_email_key"),
        schema=schema,
    )
    op.create_table(
        "permissions",
        sa.Column(
            "id",
            sa.INTEGER(),
            sa.Identity(always=False, start=1, increment=1, minvalue=1, maxvalue=2147483647, cycle=False, cache=1),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("uuid", postgresql.UUID(), autoincrement=False, nullable=True),
        sa.Column("account_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("name", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column("title", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.Column("description", sa.VARCHAR(length=100), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name="permissions_pkey"),
        sa.UniqueConstraint("uuid", name="permissions_uuid_key"),
        schema=schema,
    )

    op.create_table(
        "roles_permissions_link",
        sa.Column("role_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("permission_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(
            ["permission_id"], ["tenant_default.permissions.id"], name="roles_permissions_link_fk"
        ),
        sa.ForeignKeyConstraint(["role_id"], ["tenant_default.roles.id"], name="roles_permissions_link_fk_1"),
        sa.PrimaryKeyConstraint("role_id", "permission_id", name="roles_permissions_link_pkey"),
        schema=schema,
    )

    # ### end Alembic commands ###


@for_each_tenant_schema
def downgrade(schema: str) -> None:
    op.drop_table(
        "permissions",
        schema=schema,
    )
    op.drop_table(
        "users",
        schema=schema,
    )
    op.drop_table(
        "roles",
        schema=schema,
    )
    op.drop_table(
        "roles_permissions_link",
        schema=schema,
    )
    # ### end Alembic commands ###
