# project/tests/conftest.py

import pytest

# from app.config import get_settings
# from app.db import Base, get_session

# from app.main import create_application
# from fastapi.testclient import TestClient
# from sqlalchemy import MetaData, Session, create_engine
# from sqlalchemy.orm import Session
# from starlette.testclient import TestClient

# def get_settings_override():
#     return Settings(testing=1, database_url=os.environ.get("DATABASE_TEST_URL"))


# @pytest.fixture
# def aws_credentials():
#     """Mocked AWS Credentials for moto."""
#     os.environ["AWS_ACCESS_KEY_ID"] = "testing"
#     os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
#     os.environ["AWS_SECURITY_TOKEN"] = "testing"
#     os.environ["AWS_SESSION_TOKEN"] = "testing"


# @pytest.fixture(name="session")
# def session_fixture():
#     engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
#     # engine = create_engine("sqlite:///testing.db", connect_args={"check_same_thread": False})
#     Base.metadata.create_all(bind=engine)
#     with Session(engine) as session:
#         yield session


# @pytest.fixture(name="client")
# def client_fixture(session: Session):
#     def get_session_override():
#         return session

#     def get_auth_override():
#         return {"user": 1, "account": 2}

#     app = create_application()

#     app.dependency_overrides[get_session] = get_session_override
#     # app.dependency_overrides[has_token] = get_auth_override

#     client = TestClient(app)
#     yield client
#     app.dependency_overrides.clear()
