from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_audit():
    # Generate a trace first
    ask_resp = client.post("/ask", 
                           json={"question": "What is my attendance?"},
                           headers={"X-Student-Id": "S1001"})
    trace_id = ask_resp.json()["trace_id"]
    
    # Fetch audit
    audit_resp = client.get(f"/audit/{trace_id}")
    assert audit_resp.status_code == 200
    assert audit_resp.json()["trace_id"] == trace_id
