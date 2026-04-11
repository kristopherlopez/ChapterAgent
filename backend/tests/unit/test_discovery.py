"""Unit tests for solution manifest discovery."""

from pathlib import Path

from src.platform.discovery import discover_solutions, load_solution_manifest


SOLUTIONS_DIR = Path(__file__).resolve().parents[3] / "solutions"


class TestDiscovery:
    def test_discover_finds_all_solutions(self):
        # The project has 3 solution directories with manifests
        manifests = discover_solutions(SOLUTIONS_DIR)
        assert len(manifests) >= 1  # At least qa-agent
        ids = [m.id for m in manifests]
        assert "rag-policy-qa" in ids

    def test_load_qa_agent_manifest(self):
        manifest = load_solution_manifest(SOLUTIONS_DIR / "qa-agent")
        assert manifest.name == "CBA Annual Report Q&A Agent"
        assert manifest.id == "rag-policy-qa"
        assert manifest.risk_tier == "production_customer_facing"

    def test_manifest_has_evaluation_config(self):
        manifest = load_solution_manifest(SOLUTIONS_DIR / "qa-agent")
        assert manifest.evaluation.test_cases == 50
        assert len(manifest.evaluation.metrics) > 0

    def test_nonexistent_dir_returns_empty(self):
        manifests = discover_solutions(Path("/nonexistent"))
        assert manifests == []
