import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert "vector_store_loaded" in body


def test_query_happy_path(client):
    response = client.post("/query", json={"question": "How long is maternity leave?"})
    assert response.status_code == 200
    body = response.json()
    assert "answer" in body
    assert "sources" in body
    assert isinstance(body["sources"], list)
    assert len(body["answer"]) > 0


def test_query_invalid_input(client):
    response = client.post("/query", json={})
    assert response.status_code == 422

    response = client.post("/query", json={"question": ""})
    assert response.status_code == 422