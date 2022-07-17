import argparse
import os
import traceback
from contextlib import contextmanager
from typing import List
from uuid import uuid4

import alembic  # pylint: disable=E0401
import alembic.config  # pylint: disable=E0401
import alembic.migration  # pylint: disable=E0401
import alembic.runtime.environment  # pylint: disable=E0401
import alembic.script  # pylint: disable=E0401
import alembic.util  # pylint: disable=E0401
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from dotenv import find_dotenv, load_dotenv
from faker import Faker
from fastapi import Depends, FastAPI, HTTPException, Request
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, joinedload, relationship, sessionmaker

from app.api.auth import auth_router
from app.api.users import user_router
from app.db import (
    SQLALCHEMY_DATABASE_URL,
    get_db,
    get_tenant_specific_metadata,
    with_db,
)
from app.models.models import Book
from app.models.shared_models import Tenant
from app.schemas.schemas import BookBase, StandardResponse


def alembic_upgrade_head(tenant_name):
    # set the paths values
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        package_dir = os.path.normpath(os.path.join(current_dir, ".."))
        directory = os.path.join(package_dir, "migrations")

        # create Alembic config and feed it with paths
        config = Config(os.path.join(package_dir, "alembic.ini"))
        config.set_main_option("script_location", directory.replace("%", "%%"))
        config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)
        config.cmd_opts = argparse.Namespace()  # arguments stub

        # If it is required to pass -x parameters to alembic
        x_arg = "tenant=" + tenant_name  # "dry_run=" + "True"
        if not hasattr(config.cmd_opts, "x"):
            if x_arg is not None:
                setattr(config.cmd_opts, "x", [])
                if isinstance(x_arg, list) or isinstance(x_arg, tuple):
                    for x in x_arg:
                        config.cmd_opts.x.append(x)
                else:
                    config.cmd_opts.x.append(x_arg)
            else:
                setattr(config.cmd_opts, "x", None)

        # prepare and run the command
        revision = "head"
        sql = False
        tag = None
        # command.stamp(config, revision, sql=sql, tag=tag)

        # upgrade command
        command.upgrade(config, revision, sql=sql, tag=tag)
    except Exception as e:
        print(e)
        print(traceback.format_exc())


# def _get_alembic_config():
#     from alembic.config import Config

#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     package_dir = os.path.normpath(os.path.join(current_dir, ".."))
#     directory = os.path.join(package_dir, "migrations")
#     config = Config(os.path.join(package_dir, "alembic.ini"))
#     config.set_main_option("script_location", directory.replace("%", "%%"))  # directory.replace('%', '%%')
#     config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)
#     return config


# alembic_config = _get_alembic_config()


def tenant_create(name: str, schema: str, host: str) -> None:
    with with_db(schema) as db:
        # context = MigrationContext.configure(db.connection())
        # script = alembic.script.ScriptDirectory.from_config(alembic_config)
        # print("#####", context.get_current_revision(), script.get_current_head())
        # if context.get_current_revision() != script.get_current_head():
        # raise RuntimeError("Database is not up-to-date. Execute migrations before adding new tenants.")

        tenant = Tenant(
            uuid=uuid4(),
            name=name,
            schema=schema,
            schema_header_id=host,
        )
        db.add(tenant)

        db.execute(sa.schema.CreateSchema(schema))
        db.commit()

    # get_tenant_specific_metadata().create_all(bind=db.connection())


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
    print("OK")
    tenant_create(name, schema, host)
    print("OK1")
    # alembic_upgrade_head(schema)
    # print("OK2")
    return {"name": name, "schema": schema, "host": host}


@app.get("/upgrade")
def read_item(schema: str):
    alembic_upgrade_head(schema)
    return {"ok": True}


# Books CRUD


@app.get("/books", response_model=List[BookBase])  #
def read_user(*, db: Session = Depends(get_db)):
    db_book = db.execute(select(Book)).scalars().all()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.get("/books/{book_id}", response_model=BookBase)  #
def read_user(*, db: Session = Depends(get_db), book_id: int):
    db_book = db.execute(select(Book).where(Book.id == book_id)).scalar_one_or_none()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book


@app.post("/books", response_model=BookBase)  #
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


app.include_router(
    auth_router,
    prefix="/auth",
    tags=["USER"],
)

app.include_router(
    user_router,
    prefix="/users",
    tags=["USER"],
)
