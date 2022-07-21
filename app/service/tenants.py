import argparse
import os
import traceback
from uuid import uuid4

import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from app.db import SQLALCHEMY_DATABASE_URL, get_db, with_db
from app.models.shared_models import Tenant
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session


def alembic_upgrade_head(tenant_name, revision="head"):
    # set the paths values
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        package_dir = os.path.normpath(os.path.join(current_dir, "..", ".."))  # TODO find better way: str(Path.cwd())
        directory = os.path.join(package_dir, "migrations")

        print("D:", current_dir)
        print("D:", directory)

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
        revision = revision
        sql = False
        tag = None
        # command.stamp(config, revision, sql=sql, tag=tag)

        # upgrade command
        command.upgrade(config, revision, sql=sql, tag=tag)
    except Exception as e:
        print(e)
        print(traceback.format_exc())


def tenant_create(name: str, schema: str, host: str) -> None:

    with with_db("public") as db:
        # context = MigrationContext.configure(db.connection())
        # script = alembic.script.ScriptDirectory.from_config(alembic_config)
        # print("#####", context.get_current_revision(), script.get_current_head())
        # if context.get_current_revision() != script.get_current_head():
        # raise RuntimeError("Database is not up-to-date. Execute migrations before adding new tenants.")
        db_tenant = db.execute(select(Tenant).where(Tenant.schema == schema)).scalar_one_or_none()
        if db_tenant is not None:
            raise HTTPException(status_code=404, detail="Tenant already exists!")

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
