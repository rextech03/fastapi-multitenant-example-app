from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_get_books(session: Session, client: TestClient):
    response = client.get("/books", headers={"host": "a"})
    data = response.json()
    assert response.status_code == 200


def test_add_books(session: Session, client: TestClient):
    response = client.post("/books", json={}, headers={"host": "a"})
    data = response.json()
    assert response.status_code == 200
