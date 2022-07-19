import os

from app.config import get_settings
from app.db import engine
from app.main import app, get_db
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import MetaData, create_engine, select
from sqlalchemy.orm import Session

# client = TestClient(app)


def test_get_books():
    load_dotenv("./app/.env")
    db_user = os.getenv("DB_USERNAME")
    db_host: str = os.getenv("DB_HOST")
    db_name: str = os.getenv("DB_DATABASE")
    db_user: str = os.getenv("DB_USERNAME")
    db_password: str = os.getenv("DB_PASSWORD")

    engine = create_engine(
        f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:5438/{db_name}",
        echo=True,
        pool_pre_ping=True,
        pool_recycle=280,
    )
    schema_translate_map = dict(tenant="a")
    connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    with Session(autocommit=False, autoflush=False, bind=connectable, future=True) as session:

        def get_session_override():
            return session  #

        app.dependency_overrides[get_db] = get_session_override  #

        client = TestClient(app)

        response = client.get("/books", headers={"host": "a"})
        app.dependency_overrides.clear()
        data = response.json()
        # assert data == 1
        assert response.status_code == 200


def test_add_books():
    load_dotenv("./app/.env")
    db_user = os.getenv("DB_USERNAME")
    db_host: str = os.getenv("DB_HOST")
    db_name: str = os.getenv("DB_DATABASE")
    db_user: str = os.getenv("DB_USERNAME")
    db_password: str = os.getenv("DB_PASSWORD")

    engine = create_engine(
        f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:5438/{db_name}",
        echo=True,
        pool_pre_ping=True,
        pool_recycle=280,
    )
    schema_translate_map = dict(tenant="a")
    connectable = engine.execution_options(schema_translate_map=schema_translate_map)
    with Session(autocommit=False, autoflush=False, bind=connectable, future=True) as session:

        def get_session_override():
            return session  #

        app.dependency_overrides[get_db] = get_session_override  #

        client = TestClient(app)

        response = client.post("/books", json={}, headers={"host": "a"})
        app.dependency_overrides.clear()
        data = response.json()
        # assert data == {"id": 1, "title": "Horizontal tangible structure", "author": "Adam Jones"}
        assert response.status_code == 200
