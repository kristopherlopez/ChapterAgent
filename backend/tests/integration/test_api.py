"""Integration tests for the API endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.api.app import app


@pytest.fixture
def client():
    return TestClient(app)


class TestSolutionsAPI:
    def test_list_solutions(self, client):
        response = client.get("/api/solutions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Check shape matches SolutionSummary
        first = data[0]
        assert "id" in first
        assert "name" in first
        assert "health" in first

    def test_get_solution_detail(self, client):
        response = client.get("/api/solutions/rag-policy-qa")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "rag-policy-qa"
        assert "guardrails" in data
        assert "evaluation" in data
        assert "complianceGate" in data

    def test_get_nonexistent_solution(self, client):
        response = client.get("/api/solutions/nonexistent")
        assert response.status_code == 404


class TestComplianceAPI:
    def test_dashboard(self, client):
        response = client.get("/api/compliance/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "passing" in data
        assert "failing" in data
        assert "total" in data
        assert data["total"] >= 1


class TestEvidenceAPI:
    def test_get_evidence(self, client):
        response = client.get("/api/evidence/rag-policy-qa")
        assert response.status_code == 200
        data = response.json()
        assert data["solution_id"] == "rag-policy-qa"
        assert "gate_results" in data
        assert "policy_evidence_map" in data

    def test_download_evidence(self, client):
        response = client.get("/api/evidence/rag-policy-qa/download")
        assert response.status_code == 200
        assert "attachment" in response.headers.get("content-disposition", "")

    def test_evidence_not_found(self, client):
        response = client.get("/api/evidence/nonexistent")
        assert response.status_code == 404


class TestTracesAPI:
    def test_get_traces(self, client):
        response = client.get("/api/traces/rag-policy-qa")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "step" in data[0]
        assert "label" in data[0]

    def test_list_scenarios(self, client):
        response = client.get("/api/traces/rag-policy-qa/scenarios")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


class TestScorecardAPI:
    def test_get_scorecard(self, client):
        response = client.get("/api/scorecard")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0]["framework"] == "Claude Agent SDK"
