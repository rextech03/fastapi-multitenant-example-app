import os
from contextlib import contextmanager
from datetime import datetime, time, timedelta
from typing import List, Optional, Union

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
from sqlalchemy.orm import Session, joinedload, relationship, sessionmaker

# from app.api.users import user_router
from app.schemas.schemas import Book, StandardResponse, User, UserLoginIn, UserLoginOut

# from app.models.models import User


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


class Books(Base):
    __tablename__ = "books"

    id = sa.Column(sa.Integer, primary_key=True, nullable=False)
    title = sa.Column(sa.String(256), nullable=False, index=True, unique=True)
    author = sa.Column(sa.String(256), nullable=False, unique=True)


class Roles(Base):
    __tablename__ = "roles"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    role_name = sa.Column(sa.VARCHAR(length=100), autoincrement=False, nullable=True)
    role_description = sa.Column(sa.VARCHAR(length=100), autoincrement=False, nullable=True)
    users_FK = relationship("Users", back_populates="role_FK")


class SharedUsers(Base):
    __tablename__ = "shared_users"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    # uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    email = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True, unique=True)
    tenant_id = sa.Column(sa.INTEGER(), autoincrement=False, nullable=True)
    is_active = sa.Column(sa.BOOLEAN(), autoincrement=False, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    __table_args__ = {"schema": "shared"}


class Users(Base):
    __tablename__ = "users"
    id = sa.Column(sa.INTEGER(), sa.Identity(), primary_key=True, autoincrement=True, nullable=False)
    # uuid = sa.Column(UUID(as_uuid=True), autoincrement=False, nullable=True)
    email = sa.Column(sa.VARCHAR(length=256), autoincrement=False, nullable=True, unique=True)
    first_name = sa.Column(sa.VARCHAR(length=100), autoincrement=False, nullable=True)
    last_name = sa.Column(sa.VARCHAR(length=100), autoincrement=False, nullable=True)
    user_role_id = sa.Column(sa.INTEGER(), sa.ForeignKey("roles.id"), autoincrement=False, nullable=True)
    created_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)
    updated_at = sa.Column(sa.TIMESTAMP(timezone=True), autoincrement=False, nullable=True)

    role_FK = relationship("Roles", back_populates="users_FK")


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


def get_public_db():
    with with_db("shared") as db:
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


@app.get("/books", response_model=List[Book])  #
def read_user(*, db: Session = Depends(get_db)):
    db_book = db.execute(select(Books)).scalars().all()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.get("/books/{book_id}", response_model=Book)  #
def read_user(*, db: Session = Depends(get_db), book_id: int):
    db_book = db.execute(select(Books).where(Book.id == book_id)).scalar_one_or_none()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.post("/books", response_model=Book)  #
def read_user(*, db: Session = Depends(get_db)):

    faker = Faker()

    new_book = Books(
        title=faker.catch_phrase(),
        author=faker.name(),
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


@app.delete("/books/{book_id}", response_model=StandardResponse)  #
def read_user(*, db: Session = Depends(get_db), book_id: int):

    db_book = db.execute(select(Books).where(Book.id == book_id)).scalar_one_or_none()
    db.delete(db_book)
    db.commit()

    return {"ok": True}


@app.get("/users")
async def user_get_all(*, db: Session = Depends(get_db)):
    db_user = db.execute(select(Users)).scalars().all()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_user


@app.post("/users")  # , response_model=User
def read_user(*, db: Session = Depends(get_db)):

    faker = Faker()

    new_user = Users(
        email=faker.email(),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        user_role_id=1,
        created_at=datetime.utcnow(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/login")  # , response_model=UserLoginOut
async def auth_login(*, shared_db: Session = Depends(get_public_db), users: UserLoginIn, req: Request):
    ua_string = req.headers["User-Agent"]
    # browser_lang = req.headers["accept-language"]

    try:
        res = UserLoginIn.from_orm(users)

        db_shared_user = shared_db.execute(
            select(SharedUsers).where(SharedUsers.email == res.email).where(SharedUsers.is_active == True)
        ).scalar_one_or_none()

        db_shared_tenant = shared_db.execute(
            select(Tenant).where(Tenant.id == db_shared_user.tenant_id)
        ).scalar_one_or_none()

        print("#####", db_shared_user.tenant_id, db_shared_tenant.schema)

        if db_shared_user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # with db.session.connection(execution_options={"schema_translate_map":{"tenant":tenant_schema}}):

        # ----------------
        schema_translate_map = dict(tenant=db_shared_tenant.schema)
        connectable = engine.execution_options(schema_translate_map=schema_translate_map)
        with Session(autocommit=False, autoflush=False, bind=connectable) as db:
            db_user = db.execute(select(Users).where(Users.id == 1)).scalar_one_or_none()

        # update_package = {
        #     "updated_at": datetime.utcnow(),
        # }

        # for key, value in update_package.items():
        #     setattr(db_user, key, value)
        # db.add(db_user)
        # db.commit()
        # db.refresh(db_user)

    except Exception as err:
        print(err)
        raise HTTPException(status_code=404, detail="User not found")

    return db_user


@app.post("/roles")  # , response_model=User
def read_user(*, db: Session = Depends(get_db)):

    faker = Faker()

    new_user = Users(
        email=faker.email(),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        user_role_id=1,
        created_at=datetime.utcnow(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# app.include_router(
#     user_router,
#     prefix="/user",
#     tags=["USER"],
# )
