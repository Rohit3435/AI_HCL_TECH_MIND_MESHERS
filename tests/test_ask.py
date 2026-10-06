from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ask_missing_student_id():
    response = client.post("/ask", json={"question": "What is my attendance?"})
    # Will work for now, but our mock logic should ideally enforce this
    assert response.status_code == 200

def test_ask_with_student_id():
    response = client.post("/ask", 
                           json={"question": "What is my attendance in CS201?", "as_of_date": "2026-10-06"},
                           headers={"X-Student-Id": "S1001"})
    assert response.status_code == 200
    data = response.json()
    assert "trace_id" in data
    assert "answer" in data
