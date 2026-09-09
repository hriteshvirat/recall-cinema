import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "RECALL"

def test_media_static_mount():
    # Verify sample_data can be accessed
    response = client.get("/media/sample_data/kitchen_mystery_demo.mp4")
    # Should be 200 since we just generated the video
    assert response.status_code == 200
