import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseSettings

# PROJECT_DIR = Path(__file__).parent.parent

# print(PROJECT_DIR)


class Settings(BaseSettings):
    environment: str = os.getenv("APP_ENV")

    db_host: str = os.getenv("DB_HOST")
    db_port: str = os.getenv("DB_PORT")
    db_name: str = os.getenv("DB_DATABASE")
    db_user: str = os.getenv("DB_USERNAME")
    db_password: str = os.getenv("DB_PASSWORD")

    DEFAULT_SQLALCHEMY_DATABASE_URI: str = ""

    db_testing: str = os.getenv("DATABASE_TEST_URL")

    class Config:
        env_prefix = ""
        env_file_encoding = "utf-8"
        env_file = ".env"


@lru_cache()
def get_settings() -> BaseSettings:
    return Settings()
