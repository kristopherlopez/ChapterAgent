"""Controls register API routes."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["controls"])

CONTROLS = [
    {
        "id": "AI-GOV-001",
        "name": "Solution Registration",
        "description": "Every AI solution must be registered with complete metadata, risk tier, and named owner",
        "enforcementLayer": "deployment-gate",
        "controlType": "preventive",
        "risksMitigated": ["AIR-012"],
        "regulatoryAlignment": ["CPS 230", "DISR #1"],
        "sourceDoc": "07-compliance-as-code",
    },
    {
        "id": "AI-GOV-002",
        "name": "Risk Tier Assignment",
        "description": "Every solution must be assigned a risk tier that determines threshold strictness, guardrail scope, and re-evaluation frequency",
        "enforcementLayer": "deployment-gate",
        "controlType": "preventive",
        "risksMitigated": ["AIR-012"],
        "regulatoryAlignment": ["CPS 230", "CPS 234", "DISR #2"],
        "sourceDoc": "04-solution-lifecycle",
    },
    {
        "id": "AI-GOV-003",
        "name": "Quality Thresholds",
        "description": "Solutions must pass evaluation metrics at or above their risk tier's thresholds",
        "enforcementLayer": "deployment-gate+production",
        "controlType": "preventive+detective",
        "risksMitigated": ["AIR-001", "AIR-007"],
        "regulatoryAlignment": ["CPS 234", "DISR #4"],
        "sourceDoc": "08-evaluation-harness",
    },
    {
        "id": "AI-GOV-004",
        "name": "Content Safety",
        "description": "Solutions must not produce toxic, harmful, or dangerous content",
        "enforcementLayer": "deployment-gate+production",
        "controlType": "preventive+detective",
        "risksMitigated": ["AIR-005"],
        "regulatoryAlignment": ["DISR #3", "DISR #4"],
        "sourceDoc": "06-guardrails",
    },
    {
        "id": "AI-GOV-005",
        "name": "PII Protection",
        "description": "Zero PII in AI solution outputs; Presidio NER detection on every response",
        "enforcementLayer": "deployment-gate+production",
        "controlType": "preventive+detective",
        "risksMitigated": ["AIR-003"],
        "regulatoryAlignment": ["CPS 234", "DISR #3"],
        "sourceDoc": "06-guardrails",
    },
    {
        "id": "AI-GOV-006",
        "name": "Guardrail Validation",
        "description": "All guardrails (scope, injection, content safety) must pass their test suite before deployment",
        "enforcementLayer": "deployment-gate",
        "controlType": "preventive",
        "risksMitigated": ["AIR-004", "AIR-005", "AIR-006"],
        "regulatoryAlignment": ["CPS 234", "DISR #4"],
        "sourceDoc": "06-guardrails",
    },
    {
        "id": "AI-GOV-007",
        "name": "Bias & Fairness",
        "description": "Solutions must not exhibit systematic demographic bias",
        "enforcementLayer": "deployment-gate+production",
        "controlType": "preventive+detective",
        "risksMitigated": ["AIR-002"],
        "regulatoryAlignment": ["DISR #4", "PetSure Australia AI Policy"],
        "sourceDoc": "08-evaluation-harness",
    },
    {
        "id": "AI-GOV-008",
        "name": "Audit Trail Completeness",
        "description": "100% of interactions must have complete trace fields",
        "enforcementLayer": "deployment-gate+production",
        "controlType": "detective",
        "risksMitigated": ["AIR-008"],
        "regulatoryAlignment": ["CPS 230", "DISR #9"],
        "sourceDoc": "10-observability",
    },
    {
        "id": "AI-GOV-009",
        "name": "Golden Dataset Sign-Off",
        "description": "Human reviewer must approve the golden dataset with identity and date recorded",
        "enforcementLayer": "deployment-gate",
        "controlType": "preventive",
        "risksMitigated": ["AIR-011"],
        "regulatoryAlignment": ["DISR #5", "DISR #10"],
        "sourceDoc": "07-compliance-as-code",
    },
    {
        "id": "AI-GOV-010",
        "name": "Prompt Governance",
        "description": "System prompts must be version-controlled with linked approval commits",
        "enforcementLayer": "deployment-gate",
        "controlType": "preventive",
        "risksMitigated": ["AIR-009"],
        "regulatoryAlignment": ["CPS 230", "DISR #9"],
        "sourceDoc": "07-compliance-as-code",
    },
]

RISK_MAPPINGS = [
    {"riskId": "AIR-001", "risk": "Hallucination", "controls": ["AI-GOV-003"], "residualRisk": "low"},
    {"riskId": "AIR-002", "risk": "Bias & Discrimination", "controls": ["AI-GOV-007"], "residualRisk": "low"},
    {"riskId": "AIR-003", "risk": "PII Leakage", "controls": ["AI-GOV-005"], "residualRisk": "very-low"},
    {"riskId": "AIR-004", "risk": "Prompt Injection", "controls": ["AI-GOV-006"], "residualRisk": "low"},
    {"riskId": "AIR-005", "risk": "Toxic Content", "controls": ["AI-GOV-004", "AI-GOV-006"], "residualRisk": "very-low"},
    {"riskId": "AIR-006", "risk": "Scope Creep", "controls": ["AI-GOV-006"], "residualRisk": "very-low"},
    {"riskId": "AIR-007", "risk": "Model Drift", "controls": ["AI-GOV-003"], "residualRisk": "low"},
    {"riskId": "AIR-008", "risk": "Audit Trail Gaps", "controls": ["AI-GOV-008"], "residualRisk": "very-low"},
    {"riskId": "AIR-009", "risk": "Uncontrolled Prompt Changes", "controls": ["AI-GOV-010"], "residualRisk": "low"},
    {"riskId": "AIR-010", "risk": "Third-Party Model Changes", "controls": ["AI-GOV-003"], "residualRisk": "medium"},
    {"riskId": "AIR-011", "risk": "Insufficient Test Coverage", "controls": ["AI-GOV-009"], "residualRisk": "low"},
    {"riskId": "AIR-012", "risk": "Unauthorised Deployment", "controls": ["AI-GOV-001", "AI-GOV-002"], "residualRisk": "very-low"},
]


@router.get("/controls")
def list_controls() -> dict:
    """Return the full controls register."""
    return {
        "controls": CONTROLS,
        "riskMappings": RISK_MAPPINGS,
        "totalControls": len(CONTROLS),
        "totalRisks": len(RISK_MAPPINGS),
    }
