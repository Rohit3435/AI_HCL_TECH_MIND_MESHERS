from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_sources():
    response = client.get("/sources")
    assert response.status_code == 200
    assert "sources" in response.json()
    assert isinstance(response.json()["sources"], list)
