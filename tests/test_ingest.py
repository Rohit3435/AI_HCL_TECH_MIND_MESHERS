from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def test_ingest_document():
    metadata = {"doc_id": "TEST-01", "title": "Test Doc"}
    files = {"file": ("test.pdf", b"dummy content", "application/pdf")}
    data = {"metadata": json.dumps(metadata)}
    
    response = client.post("/ingest", files=files, data=data)
    assert response.status_code == 200
    assert response.json()["status"] == "indexed"
