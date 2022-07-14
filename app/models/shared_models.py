import sqlalchemy as sa
from sqlalchemy import MetaData, create_engine, func, select, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, joinedload, relationship, sessionmaker

metadata = sa.MetaData(schema="shared")
Base = declarative_base(metadata=metadata)


class Tenant(Base):
    __tablename__ = "tenants"

    id = sa.Column("id", sa.Integer, primary_key=True, nullable=False)
    name = sa.Column("name", sa.String(256), nullable=False, index=True, unique=True)
    schema = sa.Column("schema", sa.String(256), nullable=False, unique=True)
    host = sa.Column("host", sa.String(256), nullable=False, unique=True)

    __table_args__ = {"schema": "shared"}


class SharedUser(Base):
    __tablename__ = "shared_users"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    # uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    email = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True, unique=True)
    tenant_id = sa.Column(sa.INTEGER(), autoincrement=False, nullable=True)
    is_active = sa.Column(sa.BOOLEAN(), autoincrement=False, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    __table_args__ = {"schema": "shared"}
