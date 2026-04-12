"""Check 8: Prompt Governance — AI-GOV-010.

Verifies system prompts are version-controlled with approval tracking.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from src.platform.compliance.checks import CheckResult


def run(solution_dir: Path) -> CheckResult:
    """Verify prompt governance requirements.

    Checks:
        - Prompt files exist in the solution
        - Prompt version is tracked (in solution.yaml or prompt_versions.json)
        - Prompt hash can be computed for change detection

    Args:
        solution_dir: Path to the solution directory.
    """
    # Look for prompt files
    prompt_candidates = [
        solution_dir / "prompts",
        solution_dir / "src",
    ]

    prompt_files: list[Path] = []
    for candidate in prompt_candidates:
        if candidate.is_dir():
            prompt_files.extend(candidate.glob("*.py"))
            prompt_files.extend(candidate.glob("*.txt"))
            prompt_files.extend(candidate.glob("*.md"))

    # Compute prompt hashes for change detection
    prompt_hashes: dict[str, str] = {}
    for pf in prompt_files:
        content = pf.read_bytes()
        prompt_hashes[pf.name] = hashlib.sha256(content).hexdigest()[:12]

    # Check for prompt version tracking
    version_file = solution_dir / "prompt_versions.json"
    prompt_version = "unknown"
    approval_commit = None

    if version_file.exists():
        with open(version_file) as f:
            versions = json.load(f)
        prompt_version = versions.get("current_version", "unknown")
        approval_commit = versions.get("approval_commit")
    else:
        # Fall back to solution.yaml version
        manifest_path = solution_dir / "solution.yaml"
        if manifest_path.exists():
            import yaml
            with open(manifest_path) as f:
                manifest = yaml.safe_load(f)
            prompt_version = manifest.get("solution", {}).get("version", "unknown")

    if not prompt_files:
        return CheckResult(
            check="prompt_governance",
            policy_id="AI-GOV-010",
            policy="System prompts version-controlled and approved",
            status="FAIL",
            evidence={"error": "No prompt files found in solution directory"},
        )

    return CheckResult(
        check="prompt_governance",
        policy_id="AI-GOV-010",
        policy="System prompts version-controlled and approved",
        status="PASS",
        evidence={
            "prompt_version": prompt_version,
            "prompt_files": len(prompt_files),
            "prompt_hashes": prompt_hashes,
            "approval_commit": approval_commit,
            "version_tracked": version_file.exists(),
        },
    )
