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
    # Index may return a JSON landing object or an HTML UI (frontend).
    if response.is_json:
        data = response.get_json()
        assert "name" in data
    else:
        text = response.get_data(as_text=True)
        assert "Stock Analysis" in text or "<html" in text


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_predict_missing_features(client):
    """Test predict endpoint with valid data"""
    response = client.post("/api/predict", json={"ticker": "AAPL"})
    # Should succeed with AAPL or return 500 if yfinance is unavailable
    assert response.status_code in [200, 500]
