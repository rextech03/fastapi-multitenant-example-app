# project/tests/conftest.py

import os

import pytest
from app.config import Settings, get_settings
from app.db import Base, engine, get_db
from app.main import create_application
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

# from starlette.testclient import TestClient


def get_settings_override():
    return Settings(testing=1, db_testing='os.environ.get("DATABASE_TEST_URL")')


# @pytest.fixture
# def aws_credentials():
#     """Mocked AWS Credentials for moto."""
#     os.environ["AWS_ACCESS_KEY_ID"] = "testing"
#     os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
#     os.environ["AWS_SECURITY_TOKEN"] = "testing"
#     os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture(name="session")
def session_fixture():
    load_dotenv("./app/.env")
    db_user = os.getenv("DB_USERNAME")
    db_host: str = os.getenv("DB_HOST")
    db_name: str = os.getenv("DB_DATABASE")
    db_user: str = os.getenv("DB_USERNAME")
    db_password: str = os.getenv("DB_PASSWORD")
    SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@192.166.219.228:5438/postgres"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, pool_pre_ping=True, pool_recycle=280)

    schema_translate_map = dict(tenant="a")
    connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    # Base.metadata.create_all(bind=engine)
    # Base = declarative_base(metadata=metadata)
    with Session(bind=connectable) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        schema_translate_map = dict(tenant="a")
        connectable = engine.execution_options(schema_translate_map=schema_translate_map)
        with Session(autocommit=False, autoflush=False, bind=connectable, future=True) as db:
            return db

    # def get_auth_override():
    #     return {"user": 1, "account": 2}

    app = create_application()

    # app.dependency_overrides[get_db] = get_session_override
    # app.dependency_overrides[has_token] = get_auth_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
