import argparse
import os

import alembic
import alembic.config  # pylint: disable=E0401
import alembic.migration  # pylint: disable=E0401
import alembic.runtime.environment  # pylint: disable=E0401
import alembic.script  # pylint: disable=E0401
import alembic.util  # pylint: disable=E0401
from alembic.config import Config


def main(tenant="a"):
    print(os.path.abspath(__file__))
    print("Running initial migration")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.normpath(os.path.join(current_dir, ".."))
    directory = os.path.join(package_dir, "migrations")

    config = Config(os.path.join(package_dir, "alembic.ini"))
    config.set_main_option("script_location", directory.replace("%", "%%"))
    config.cmd_opts = argparse.Namespace()
    setattr(config.cmd_opts, "x", [])
    config.cmd_opts.x.append("tenant=" + tenant)

    alembic.command.upgrade(config, "head", sql=None, tag=None)


main()

# if __name__ == "__main__":
#     typer.run(main)
