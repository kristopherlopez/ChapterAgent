"""Ablation study runner for the Australian Credit Approval Scorer.

Incrementally adds feature groups, trains a model at each step, and logs
results to MLflow. With only 14 features and 690 records, this runs in
milliseconds — but the governance story is the same as a production model.

Usage:
    cd solutions/credit-approval-scorer
    python src/ablation.py                          # uses default dataset path
    python src/ablation.py path/to/australian.dat   # custom dataset path

    # Browse results:
    mlflow ui                                       # http://localhost:5000
"""

from __future__ import annotations

import sys
import time
from itertools import chain
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

# Handle imports whether run as module or standalone script
try:
    from solutions.credit_approval_scorer.src.data import (
        CATEGORICAL_BINARY_FEATURES,
        CATEGORICAL_MULTI_FEATURES,
        CONTINUOUS_PRIMARY_FEATURES,
        CONTINUOUS_SECONDARY_FEATURES,
        PROXY_CANDIDATES,
        load_dataset,
        prepare_splits,
    )
    from solutions.credit_approval_scorer.src.evaluate import run_evaluation
    from solutions.credit_approval_scorer.src.explain import compute_shap_values, shap_coverage
    from solutions.credit_approval_scorer.src import tracking
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from data import (  # type: ignore[no-redef]
        CATEGORICAL_BINARY_FEATURES,
        CATEGORICAL_MULTI_FEATURES,
        CONTINUOUS_PRIMARY_FEATURES,
        CONTINUOUS_SECONDARY_FEATURES,
        PROXY_CANDIDATES,
        load_dataset,
        prepare_splits,
    )
    from evaluate import run_evaluation  # type: ignore[no-redef]
    from explain import compute_shap_values, shap_coverage  # type: ignore[no-redef]
    import tracking  # type: ignore[no-redef]


# ---------------------------------------------------------------------------
# Ablation step definitions
# ---------------------------------------------------------------------------

ABLATION_STEPS: list[tuple[str, list[str], list[list[str]], str]] = [
    (
        "step1_binary_categoricals",
        ["categorical_binary"],
        [CATEGORICAL_BINARY_FEATURES],
        "Binary flags (A1, A8, A9, A11) — includes proxy discrimination candidates. Do these alone predict approval?",
    ),
    (
        "step2_plus_continuous_primary",
        ["categorical_binary", "continuous_primary"],
        [CATEGORICAL_BINARY_FEATURES, CONTINUOUS_PRIMARY_FEATURES],
        "Primary continuous features (A2, A3, A7) add numeric signal — expect significant AUC lift",
    ),
    (
        "step3_plus_multi_categoricals",
        ["categorical_binary", "continuous_primary", "categorical_multi"],
        [CATEGORICAL_BINARY_FEATURES, CONTINUOUS_PRIMARY_FEATURES, CATEGORICAL_MULTI_FEATURES],
        "Multi-value categoricals (A4, A5, A6, A12) add segment granularity — proxy risk increases",
    ),
    (
        "step4_all_features",
        ["categorical_binary", "continuous_primary", "categorical_multi", "continuous_secondary"],
        [CATEGORICAL_BINARY_FEATURES, CONTINUOUS_PRIMARY_FEATURES, CATEGORICAL_MULTI_FEATURES, CONTINUOUS_SECONDARY_FEATURES],
        "All 14 features — full model. With 690 records, overfitting risk is the governance question.",
    ),
]

# Fixed hyperparameters — same across all steps to isolate feature effects
HYPERPARAMS = {
    "max_iter": 1000,
    "C": 1.0,
    "solver": "lbfgs",
    "random_state": 42,
}


# ---------------------------------------------------------------------------
# Training and evaluation helpers
# ---------------------------------------------------------------------------


def train_with_features(
    splits: dict[str, Any],
    features: list[str],
) -> LogisticRegression:
    """Train a logistic regression on a feature subset using pre-computed splits."""
    X_train = splits["X_train"][features]
    y_train = splits["y_train"]

    model = LogisticRegression(**HYPERPARAMS)
    model.fit(X_train, y_train)
    return model


def evaluate_with_features(
    model: LogisticRegression,
    splits: dict[str, Any],
    features: list[str],
) -> dict[str, Any]:
    """Evaluate a model trained on a feature subset.

    Proxy discrimination metrics are always computed against proxy candidates
    from the original data, even when those features aren't model inputs.
    """
    X_test = splits["X_test"][features]
    y_test = splits["y_test"].values
    proxy_test = splits["proxy_test"]

    y_prob = model.predict_proba(X_test)[:, 1]

    # SHAP coverage
    try:
        shap_vals = compute_shap_values(model, X_test)
        cov = shap_coverage(shap_vals, len(X_test))
    except Exception:
        cov = 0.0

    return run_evaluation(
        y_test,
        y_prob,
        proxy_test,
        shap_coverage_value=cov,
    )


# ---------------------------------------------------------------------------
# Main ablation runner
# ---------------------------------------------------------------------------


def run_ablation(
    dataset_path: str | Path,
    *,
    experiment_name: str = "credit-approval-ablation",
) -> pd.DataFrame:
    """Run the full ablation study — 4 incremental steps logged to MLflow.

    Returns a summary DataFrame comparing all steps.
    """
    print("Australian Credit Approval Scorer — Ablation Study")
    print("=" * 55)

    tracking.get_or_create_experiment(experiment_name)

    df = load_dataset(dataset_path)
    splits = prepare_splits(df)
    print(f"Dataset: {len(df)} records ({len(splits['X_train'])} train / {len(splits['X_test'])} test)")
    print(f"Baseline approval rate: {splits['y_train'].mean():.2%}\n")

    prev_metrics: dict[str, Any] = {}

    for step_num, (step_name, group_names, feature_lists, hypothesis) in enumerate(ABLATION_STEPS, 1):
        features = list(chain.from_iterable(feature_lists))

        print(f"Step {step_num}: {step_name} ({len(features)} features)")
        print(f"  Hypothesis: {hypothesis}")

        start = time.perf_counter()
        model = train_with_features(splits, features)
        train_ms = (time.perf_counter() - start) * 1000
        print(f"  Training: {train_ms:.0f}ms")

        metrics = evaluate_with_features(model, splits, features)

        _print_step_metrics(metrics, prev_metrics)

        X_test_subset = splits["X_test"][features]
        run_id = tracking.log_training_run(
            run_name=step_name,
            features_used=features,
            feature_groups=group_names,
            hyperparams=HYPERPARAMS,
            metrics=metrics,
            model=model,
            X_test=X_test_subset,
            step_number=step_num,
        )
        print(f"  MLflow run: {run_id}\n")

        prev_metrics = metrics

    print("\n" + "=" * 55)
    print("ABLATION SUMMARY")
    print("=" * 55)
    summary = tracking.build_summary_table(experiment_name)
    if not summary.empty:
        display_cols = [c for c in summary.columns if not c.endswith("_delta")]
        print(summary[display_cols].to_string(index=False))

    print(f"\nBrowse full results: mlflow ui  (http://localhost:5000)")
    return summary


def _print_step_metrics(
    metrics: dict[str, Any],
    prev: dict[str, Any],
) -> None:
    """Print key metrics for a step, with deltas from the previous step."""
    key_metrics = [
        ("auc_roc", "AUC", True),
        ("gini", "Gini", True),
        ("brier_score", "Brier", False),
        ("hosmer_lemeshow", "HL_p", True),
        ("subgroup_approval_variance", "ProxyVar", False),
        ("shap_coverage", "SHAP", True),
    ]

    parts = []
    for key, label, higher_is_better in key_metrics:
        if key not in metrics:
            continue
        val = metrics[key]["value"]
        passed = metrics[key]["pass"]

        delta_str = ""
        if key in prev:
            delta = val - prev[key]["value"]
            if delta != 0:
                concerning = (
                    (higher_is_better and delta < -0.01) or
                    (not higher_is_better and delta > 0.01)
                )
                flag = " [!]" if concerning else ""
                delta_str = f" ({delta:+.4f}{flag})"

        status = "PASS" if passed else "FAIL"
        parts.append(f"{label}: {val:.4f}{delta_str} [{status}]")

    mid = len(parts) // 2 + 1
    print(f"  {' | '.join(parts[:mid])}")
    if parts[mid:]:
        print(f"  {' | '.join(parts[mid:])}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    default_path = Path(__file__).parent.parent / "data" / "australian.dat"
    dataset = Path(sys.argv[1]) if len(sys.argv) > 1 else default_path

    if not dataset.exists():
        print(f"Dataset not found: {dataset}")
        print("Usage: python src/ablation.py [path/to/australian.dat]")
        sys.exit(1)

    run_ablation(dataset)
