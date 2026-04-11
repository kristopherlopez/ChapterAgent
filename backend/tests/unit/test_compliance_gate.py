"""Unit tests for the compliance deployment gate."""

from src.platform.compliance.gate import DeploymentGate
from src.platform.evaluation.harness import EvaluationHarness
from src.platform.guardrails.base import GuardrailResult


class TestDeploymentGate:
    def _make_guardrail_results(self, all_pass: bool = True) -> list[GuardrailResult]:
        results = [
            GuardrailResult(name="PII Detection", result="pass", detail="clean"),
            GuardrailResult(name="Scope Containment", result="pass", detail="in-scope"),
            GuardrailResult(name="Faithfulness Check", result="pass", detail="Score: 0.94"),
        ]
        if not all_pass:
            results.append(
                GuardrailResult(name="PII Detection", result="fail", detail="PII found")
            )
        return results

    def _make_eval_report(self, passing: bool = True):
        harness = EvaluationHarness(risk_tier="production_customer_facing")
        scores = {
            "faithfulness": 0.94 if passing else 0.50,
            "answer_relevancy": 0.91,
            "contextual_precision": 0.85,
            "contextual_recall": 0.79,
            "hallucination": 0.06,
            "citation_coverage": 0.98,
            "boundary_adherence": 0.98,
            "temporal_accuracy": 0.92,
            "bias": 0.02,
            "toxicity": 0.01,
        }
        return harness.run_prerecorded(scores, solution_id="test")

    def test_all_pass_gate_passes(self):
        gate = DeploymentGate()
        decision = gate.evaluate(
            self._make_guardrail_results(all_pass=True),
            self._make_eval_report(passing=True),
        )
        assert decision.result == "pass"

    def test_guardrail_failure_blocks(self):
        gate = DeploymentGate()
        decision = gate.evaluate(
            self._make_guardrail_results(all_pass=False),
            self._make_eval_report(passing=True),
        )
        assert decision.result == "fail"
        assert "PII Detection" in decision.reason

    def test_eval_failure_blocks(self):
        gate = DeploymentGate()
        decision = gate.evaluate(
            self._make_guardrail_results(all_pass=True),
            self._make_eval_report(passing=False),
        )
        assert decision.result == "fail"
        assert "Faithfulness" in decision.reason
