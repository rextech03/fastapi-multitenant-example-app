import os
from contextlib import contextmanager
from typing import Optional, Union

import alembic  # pylint: disable=E0401
import alembic.config  # pylint: disable=E0401
import alembic.migration  # pylint: disable=E0401
import alembic.runtime.environment  # pylint: disable=E0401
import alembic.script  # pylint: disable=E0401
import alembic.util  # pylint: disable=E0401
import sqlalchemy as sa
from alembic.runtime.migration import MigrationContext
from dotenv import find_dotenv, load_dotenv
from faker import Faker
from fastapi import Depends, FastAPI, HTTPException, Request
from loguru import logger
from sqlalchemy import MetaData, create_engine, func, select, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.schemas.schemas import Books, StandardResponse

load_dotenv(".env")

db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("DB_PORT")
db_username = os.environ.get("DB_USERNAME")
db_password = os.environ.get("DB_PASSWORD")

# logger.add("./app/logs.log", format="{time} - {level} - {message}", level="DEBUG", backtrace=False, diagnose=True)

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{db_username}:{db_password}@{db_host}:5438/postgres"

# db = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, pool_pre_ping=True, pool_recycle=280)
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, pool_pre_ping=True, pool_recycle=280)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()
metadata = sa.MetaData(schema="tenant")
Base = declarative_base(metadata=metadata)


class Tenant(Base):
    __tablename__ = "tenants"

    id = sa.Column("id", sa.Integer, primary_key=True, nullable=False)
    name = sa.Column("name", sa.String(256), nullable=False, index=True, unique=True)
    schema = sa.Column("schema", sa.String(256), nullable=False, unique=True)
    host = sa.Column("host", sa.String(256), nullable=False, unique=True)

    __table_args__ = {"schema": "shared"}


class Book(Base):
    __tablename__ = "books"

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    title = sa.Column(sa.String(256), nullable=False, index=True, unique=True)
    author = sa.Column(sa.String(256), nullable=False, unique=True)


def get_shared_metadata():
    meta = MetaData()
    for table in Base.metadata.tables.values():
        if table.schema != "tenant":
            table.tometadata(meta)
    return meta


def get_tenant_specific_metadata():
    meta = MetaData(schema="tenant")
    for table in Base.metadata.tables.values():
        if table.schema == "tenant":
            table.tometadata(meta)
    return meta

    #  -------------------


class TenantNotFoundError(Exception):
    pass


def get_tenant(req: Request) -> Tenant:
    host_without_port = req.headers["host"].split(":", 1)[0]

    with with_db(None) as db:
        tenant = db.execute(select(Tenant).where(Tenant.host == host_without_port)).scalar_one_or_none()

    if tenant is None:
        raise TenantNotFoundError()

    return tenant


def get_db(tenant: Tenant = Depends(get_tenant)):
    with with_db(tenant.schema) as db:
        yield db
    # --------------------


@contextmanager
def with_db(tenant_schema: Optional[str]):
    if tenant_schema:
        schema_translate_map = dict(tenant=tenant_schema)
    else:
        schema_translate_map = None

    connectable = engine.execution_options(schema_translate_map=schema_translate_map)

    try:
        db = Session(autocommit=False, autoflush=False, bind=connectable)
        yield db
    finally:
        db.close()


def _get_alembic_config():
    from alembic.config import Config

    current_dir = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.normpath(os.path.join(current_dir, ".."))
    directory = os.path.join(package_dir, "migrations")
    config = Config(os.path.join(package_dir, "alembic.ini"))
    config.set_main_option("script_location", directory.replace("%", "%%"))  # directory.replace('%', '%%')
    config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)
    return config


alembic_config = _get_alembic_config()


def tenant_create(name: str, schema: str, host: str) -> None:
    with with_db(schema) as db:
        context = MigrationContext.configure(db.connection())
        script = alembic.script.ScriptDirectory.from_config(alembic_config)
        if context.get_current_revision() != script.get_current_head():
            raise RuntimeError("Database is not up-to-date. Execute migrations before adding new tenants.")

        tenant = Tenant(
            name=name,
            host=host,
            schema=schema,
        )
        db.add(tenant)

        db.execute(sa.schema.CreateSchema(schema))
        get_tenant_specific_metadata().create_all(bind=db.connection())

        db.commit()


# -------------------------------------------------------

app = FastAPI()


@app.on_event("startup")
async def startup():
    logger.info("🚀 Starting up and initializing app...")
    # with engine.begin() as db:
    #     context = MigrationContext.configure(db)
    #     if context.get_current_revision() is not None:
    #         print("Database already exists.")
    #         return
    #
    #     db.execute(sa.schema.CreateSchema("shared"))
    #     get_shared_metadata().create_all(bind=db)

    # alembic_config.attributes["connection"] = db
    # command.stamp(alembic_config, "head", purge=True)

    # db.execute(sa.schema.CreateSchema("shared"))
    # get_shared_metadata().create_all(bind=db)

    # Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/create")
def read_item(name: str, schema: str, host: str):
    print("#######")
    tenant_create(name, schema, host)
    print("$$$$$")
    return {"name": name, "schema": schema, "host": host}


# Books CRUD


@app.get("/books", response_model=list[Books])  #
def read_user(*, db: Session = Depends(get_db)):
    db_user = db.execute(select(Book)).scalars().all()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_user


@app.get("/books/{book_id}", response_model=Books)  #
def read_user(*, db: Session = Depends(get_db), book_id: int):
    db_user = db.execute(select(Book).where(Book.id == book_id)).scalar_one_or_none()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_user


@app.post("/books", response_model=Books)  #
def read_user(*, db: Session = Depends(get_db)):

    faker = Faker()

    new_book = Book(
        title=faker.catch_phrase(),
        author=faker.name(),
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


@app.delete("/books/{book_id}", response_model=StandardResponse)  #
def read_user(*, db: Session = Depends(get_db), book_id: int):

    db_book = db.execute(select(Book).where(Book.id == book_id)).scalar_one_or_none()
    db.delete(db_book)
    db.commit()

    return {"ok": True}
