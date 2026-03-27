import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_predict_safe_inverter():
    payload = {
        "inverter_id": "80-1F-12",
        "pv1_voltage": 350.5,
        "kwh_total": 50000.5,
        "temperature": 25.0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "7_day_risk_probability" in data
    assert data["risk_level"] in ["SAFE", "WARNING"]

def test_predict_critical_inverter():
    payload = {
        "inverter_id": "54-10-EC",
        "pv1_voltage": 100.0,  # anomalously low
        "kwh_total": 50000.5,
        "temperature": 45.0    # anomalously high
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "CRITICAL"
    assert "High ambient temperature" in data["top_contributing_features"]
