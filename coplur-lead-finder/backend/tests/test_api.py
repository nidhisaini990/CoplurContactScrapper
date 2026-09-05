import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_leads_mock_mode(monkeypatch):
    monkeypatch.setenv("SEARCH_PROVIDER", "mock")
    monkeypatch.setenv("USE_AI", "false")
    payload = {
        "target_segment": "Engineering Colleges",
        "industry": "Education",
        "location": "India",
        "keywords": ["placement", "employability"],
        "roles": ["Training and Placement Officer"],
        "limit": 10,
        "min_relevance_score": 0,
    }
    response = client.post("/api/leads/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == len(data["leads"])
    assert data["total"] > 0
    scores = [lead["relevance_score"] for lead in data["leads"]]
    assert scores == sorted(scores, reverse=True)


def test_search_leads_respects_min_relevance_score():
    payload = {
        "target_segment": "Engineering Colleges",
        "keywords": [],
        "roles": [],
        "limit": 10,
        "min_relevance_score": 95,
    }
    response = client.post("/api/leads/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    for lead in data["leads"]:
        assert lead["relevance_score"] >= 95


def test_export_csv_sanitizes_formula_injection():
    payload = {
        "leads": [
            {
                "organization_name": "=SUM(A1:A2)",
                "website": "example.com",
                "relevance_score": 90,
            }
        ]
    }
    response = client.post("/api/leads/export", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    body = response.text
    assert "'=SUM(A1:A2)" in body


def test_invalid_search_request_returns_422():
    response = client.post("/api/leads/search", json={"limit": 0})
    assert response.status_code == 422
