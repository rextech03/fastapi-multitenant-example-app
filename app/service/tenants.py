import argparse
import os
import traceback

import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from app.db import SQLALCHEMY_DATABASE_URL, with_db


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


def tenant_create(schema: str) -> None:
    try:
        with with_db("public") as db:
            db.execute(sa.schema.CreateSchema(schema))
            db.commit()
    except Exception as e:
        print(e)
