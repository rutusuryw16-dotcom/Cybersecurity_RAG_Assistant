import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["cloud_readiness"]["docker_support"] is True


def test_demo_auth():
    response = client.get("/api/v1/auth/demo-token?role=analyst")
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["role"] == "analyst"


def test_investigate_endpoint():
    # Get token
    token = client.get("/api/v1/auth/demo-token?role=analyst").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test RAG investigation
    payload = {
        "query": "Why was 192.0.2.10 flagged for 50 failed logins?",
        "incident_context": "Brute force attack on SSH",
        "top_k": 3
    }
    response = client.post("/api/v1/investigate", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "grounded_answer" in data
    assert "baseline_ungrounded_answer" in data
    assert "citations" in data
    assert data["groundedness_score"] > 0.0
