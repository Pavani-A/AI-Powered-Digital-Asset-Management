from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "ai-dam-api"


def test_database_health():
    response = client.get("/health/database")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["database"] == "postgresql"


def test_qdrant_health():
    response = client.get("/health/qdrant")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["collection"] == "asset_embeddings"
    assert data["vector_size"] == 768
    assert "vectors_count" in data


def test_search():
    response = client.get(
        "/search",
        params={"q": "sunflower", "limit": 5},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "sunflower"
    assert "results" in data
    assert isinstance(data["results"], list)


def test_search_with_file_type_filter():
    response = client.get(
        "/search",
        params={
            "q": "sunflower",
            "limit": 5,
            "file_type": "image",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "sunflower"
    assert "results" in data
    assert isinstance(data["results"], list)