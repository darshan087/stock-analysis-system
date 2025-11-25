"""Tests for Flask application"""

import pytest
from src.app.app import create_app


@pytest.fixture
def client():
    """Create Flask test client"""
    app = create_app()
    app.config["TESTING"] = True
    
    with app.test_client() as client:
        yield client


def test_index(client):
    """Test index endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.get_json()


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_predict_missing_features(client):
    """Test predict endpoint without features"""
    response = client.post("/api/predict", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()
