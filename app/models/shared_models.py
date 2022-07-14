from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import MetaData, create_engine, func, select, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, joinedload, relationship, sessionmaker
from sqlalchemy.sql import func

metadata = sa.MetaData(schema="shared")
Base = declarative_base(metadata=metadata)


class Tenant(Base):
    __tablename__ = "tenants"
    id = sa.Column(sa.Integer(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    uuid = sa.Column(UUID(as_uuid=True), default=uuid4(), unique=True)
    name = sa.Column("name", sa.String(128), nullable=True)
    schema = sa.Column(sa.String(128), nullable=True)
    schema_header_id = sa.Column("schema_header_id", sa.String(128), nullable=True)

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
