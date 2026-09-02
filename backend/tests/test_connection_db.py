from app.main import app
from fastapi.testclient import TestClient


def test_connection_db():
    with TestClient(app) as client:
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": 1}
