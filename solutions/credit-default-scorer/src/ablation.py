"""Ablation study runner for the credit default scorer.

Incrementally adds feature groups, trains a model at each step, and logs
results to MLflow. Designed for methodical experimentation — isolate the
contribution of each feature group to model performance and fairness.

Usage:
    cd solutions/credit-default-scorer
    python src/ablation.py                          # uses default dataset path
    python src/ablation.py path/to/dataset.csv      # custom dataset path

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
from sklearn.ensemble import GradientBoostingClassifier

# Handle imports whether run as module or standalone script
try:
    from solutions.credit_default_scorer.src.data import (
        ALL_ENGINEERED_V2_FEATURES,
        BALANCE_TREND_FEATURES,
        BEHAVIORAL_FEATURES,
        BILL_AMOUNT_FEATURES,
        CAPACITY_FEATURES,
        CREDIT_FEATURES,
        DELINQUENCY_PATTERN_FEATURES,
        DEMOGRAPHIC_FEATURES,
        ENGINEERED_FEATURES,
        INTERACTION_FEATURES,
        PAYMENT_AMOUNT_FEATURES,
        PAYMENT_HISTORY_FEATURES,
        PAYMENT_RATIO_FEATURES,
        PROTECTED_ATTRIBUTES,
        UNPAID_BALANCE_FEATURES,
        UTILISATION_FEATURES,
        VOLATILITY_FEATURES,
        load_dataset,
        prepare_splits,
    )
    from solutions.credit_default_scorer.src.evaluate import run_evaluation
    from solutions.credit_default_scorer.src.explain import compute_shap_values, shap_coverage
    from solutions.credit_default_scorer.src import tracking
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from data import (  # type: ignore[no-redef]
        ALL_ENGINEERED_V2_FEATURES,
        BALANCE_TREND_FEATURES,
        BEHAVIORAL_FEATURES,
        BILL_AMOUNT_FEATURES,
        CAPACITY_FEATURES,
        CREDIT_FEATURES,
        DELINQUENCY_PATTERN_FEATURES,
        DEMOGRAPHIC_FEATURES,
        ENGINEERED_FEATURES,
        INTERACTION_FEATURES,
        PAYMENT_AMOUNT_FEATURES,
        PAYMENT_HISTORY_FEATURES,
        PAYMENT_RATIO_FEATURES,
        PROTECTED_ATTRIBUTES,
        UNPAID_BALANCE_FEATURES,
        UTILISATION_FEATURES,
        VOLATILITY_FEATURES,
        load_dataset,
        prepare_splits,
    )
    from evaluate import run_evaluation  # type: ignore[no-redef]
    from explain import compute_shap_values, shap_coverage  # type: ignore[no-redef]
    import tracking  # type: ignore[no-redef]


# ---------------------------------------------------------------------------
# Ablation step definitions
# ---------------------------------------------------------------------------

# Each step adds a feature group. The hypothesis for each is documented.
ABLATION_STEPS: list[tuple[str, list[str], list[list[str]], str]] = [
    (
        "step1_payment_history",
        ["payment_history"],
        [PAYMENT_HISTORY_FEATURES],
        "Strongest signal — delinquency history should be the primary default predictor",
    ),
    (
        "step2_plus_credit",
        ["payment_history", "credit"],
        [PAYMENT_HISTORY_FEATURES, CREDIT_FEATURES],
        "Credit limit adds capacity context — constrained borrowers default more",
    ),
    (
        "step3_plus_bills",
        ["payment_history", "credit", "bill_amounts"],
        [PAYMENT_HISTORY_FEATURES, CREDIT_FEATURES, BILL_AMOUNT_FEATURES],
        "Bill amounts reveal utilisation patterns — high utilisation increases risk",
    ),
    (
        "step4_plus_payments",
        ["payment_history", "credit", "bill_amounts", "payment_amounts"],
        [PAYMENT_HISTORY_FEATURES, CREDIT_FEATURES, BILL_AMOUNT_FEATURES, PAYMENT_AMOUNT_FEATURES],
        "Payment amounts show repayment behaviour — the full credit picture",
    ),
    (
        "step5_plus_demographics",
        ["payment_history", "credit", "bill_amounts", "payment_amounts", "demographics"],
        [PAYMENT_HISTORY_FEATURES, CREDIT_FEATURES, BILL_AMOUNT_FEATURES, PAYMENT_AMOUNT_FEATURES, DEMOGRAPHIC_FEATURES],
        "Demographics may improve AUC but at what fairness cost? This is the governance question.",
    ),
    (
        "step6_engineered_on_best_raw",
        ["payment_history", "credit", "bill_amounts", "engineered"],
        [PAYMENT_HISTORY_FEATURES, CREDIT_FEATURES, BILL_AMOUNT_FEATURES, ENGINEERED_FEATURES],
        "Engineered features (unpaid balance, utilisation, payment ratio, trend) on top of best raw config — do derived signals beat raw payment amounts?",
    ),
    (
        "step7_engineered_unpaid_only",
        ["payment_history", "credit", "bill_amounts", "unpaid_balance"],
        [PAYMENT_HISTORY_FEATURES, CREDIT_FEATURES, BILL_AMOUNT_FEATURES, UNPAID_BALANCE_FEATURES],
        "Unpaid balance alone (BILL - PAY) — simplest engineered feature, captures net debt without raw payment amounts.",
    ),
    (
        "step8_engineered_util_ratios",
        ["payment_history", "credit", "bill_amounts", "utilisation", "payment_ratio", "balance_trend"],
        [PAYMENT_HISTORY_FEATURES, CREDIT_FEATURES, BILL_AMOUNT_FEATURES, UTILISATION_FEATURES, PAYMENT_RATIO_FEATURES, BALANCE_TREND_FEATURES],
        "Ratio-based features only (utilisation, payment ratio, balance trend) — normalised signals without raw amounts.",
    ),
    (
        "step9_all_with_engineered",
        ["payment_history", "credit", "bill_amounts", "payment_amounts", "engineered"],
        [PAYMENT_HISTORY_FEATURES, CREDIT_FEATURES, BILL_AMOUNT_FEATURES, PAYMENT_AMOUNT_FEATURES, ENGINEERED_FEATURES],
        "All raw features plus all engineered features — does combining raw and derived signals improve over either alone?",
    ),
    # --- V2 engineered features: delinquency patterns, volatility, capacity, behavioral, interactions ---
    (
        "step10_delinquency_patterns",
        ["payment_history", "credit", "bill_amounts", "delinquency_patterns"],
        [PAYMENT_HISTORY_FEATURES, CREDIT_FEATURES, BILL_AMOUNT_FEATURES, DELINQUENCY_PATTERN_FEATURES],
        "Delinquency patterns (months late, max delay, streaks, revolving count) make the payment history signal explicit.",
    ),
    (
        "step11_plus_volatility",
        ["payment_history", "credit", "bill_amounts", "delinquency_patterns", "volatility"],
        [PAYMENT_HISTORY_FEATURES, CREDIT_FEATURES, BILL_AMOUNT_FEATURES, DELINQUENCY_PATTERN_FEATURES, VOLATILITY_FEATURES],
        "Spending and payment volatility — erratic behavior signals instability beyond levels.",
    ),
    (
        "step12_plus_capacity",
        ["payment_history", "credit", "bill_amounts", "delinquency_patterns", "volatility", "capacity"],
        [PAYMENT_HISTORY_FEATURES, CREDIT_FEATURES, BILL_AMOUNT_FEATURES, DELINQUENCY_PATTERN_FEATURES, VOLATILITY_FEATURES, CAPACITY_FEATURES],
        "Credit headroom and its trajectory — shrinking available credit compounds risk.",
    ),
    (
        "step13_plus_behavioral",
        ["payment_history", "credit", "bill_amounts", "delinquency_patterns", "volatility", "capacity", "behavioral"],
        [PAYMENT_HISTORY_FEATURES, CREDIT_FEATURES, BILL_AMOUNT_FEATURES, DELINQUENCY_PATTERN_FEATURES, VOLATILITY_FEATURES, CAPACITY_FEATURES, BEHAVIORAL_FEATURES],
        "Behavioral signals (minimum payment, overpayment patterns) — how customers pay matters as much as when.",
    ),
    (
        "step14_plus_interactions",
        ["payment_history", "credit", "bill_amounts", "delinquency_patterns", "volatility", "capacity", "behavioral", "interactions"],
        [PAYMENT_HISTORY_FEATURES, CREDIT_FEATURES, BILL_AMOUNT_FEATURES, DELINQUENCY_PATTERN_FEATURES, VOLATILITY_FEATURES, CAPACITY_FEATURES, BEHAVIORAL_FEATURES, INTERACTION_FEATURES],
        "Interaction features (util x delay, headroom x delinquent) — multiplicative risk signals.",
    ),
    (
        "step15_best_v1_plus_v2",
        ["payment_history", "credit", "bill_amounts", "utilisation", "payment_ratio", "balance_trend", "delinquency_patterns", "volatility", "capacity", "behavioral", "interactions"],
        [PAYMENT_HISTORY_FEATURES, CREDIT_FEATURES, BILL_AMOUNT_FEATURES, UTILISATION_FEATURES, PAYMENT_RATIO_FEATURES, BALANCE_TREND_FEATURES, DELINQUENCY_PATTERN_FEATURES, VOLATILITY_FEATURES, CAPACITY_FEATURES, BEHAVIORAL_FEATURES, INTERACTION_FEATURES],
        "Best V1 engineered (ratio features) combined with all V2 features — the full engineered feature set without raw payment amounts.",
    ),
    (
        "step16_kitchen_sink",
        ["payment_history", "credit", "bill_amounts", "payment_amounts", "engineered", "all_v2"],
        [PAYMENT_HISTORY_FEATURES, CREDIT_FEATURES, BILL_AMOUNT_FEATURES, PAYMENT_AMOUNT_FEATURES, ENGINEERED_FEATURES, ALL_ENGINEERED_V2_FEATURES],
        "Everything — all raw features plus all V1 and V2 engineered features. Maximum signal, maximum noise risk.",
    ),
]

# Fixed hyperparameters — same across all steps to isolate feature effects
HYPERPARAMS = {
    "n_estimators": 100,
    "max_depth": 5,
    "learning_rate": 0.1,
    "subsample": 0.8,
    "random_state": 42,
}


# ---------------------------------------------------------------------------
# Training and evaluation helpers
# ---------------------------------------------------------------------------


def train_with_features(
    splits: dict[str, Any],
    features: list[str],
) -> GradientBoostingClassifier:
    """Train a GBM on a feature subset using pre-computed splits."""
    X_train = splits["X_train"][features]
    y_train = splits["y_train"]

    model = GradientBoostingClassifier(**HYPERPARAMS)
    model.fit(X_train, y_train)
    return model


def evaluate_with_features(
    model: GradientBoostingClassifier,
    splits: dict[str, Any],
    features: list[str],
) -> dict[str, Any]:
    """Evaluate a model trained on a feature subset.

    Fairness metrics are always computed against protected attributes
    from the original data, even when demographics aren't model inputs.
    """
    X_test = splits["X_test"][features]
    y_test = splits["y_test"].values
    protected_test = splits["protected_test"]

    y_prob = model.predict_proba(X_test)[:, 1]

    # SHAP coverage
    try:
        shap_vals = compute_shap_values(model, X_test, max_samples=500)
        cov = shap_coverage(shap_vals, len(X_test))
    except Exception:
        cov = 0.0

    return run_evaluation(
        y_test,
        y_prob,
        protected_test,
        shap_coverage_value=cov,
    )


# ---------------------------------------------------------------------------
# Main ablation runner
# ---------------------------------------------------------------------------


def run_ablation(
    dataset_path: str | Path,
    *,
    experiment_name: str = "credit-default-ablation",
) -> pd.DataFrame:
    """Run the full ablation study — 16 steps logged to MLflow.

    Steps 1-5:   incremental raw feature groups.
    Steps 6-9:   V1 engineered features (unpaid balance, utilisation,
                 payment ratio, balance trend).
    Steps 10-14: V2 engineered features (delinquency patterns, volatility,
                 capacity, behavioral signals, interactions).
    Steps 15-16: combined V1+V2 and kitchen sink.

    Returns a summary DataFrame comparing all steps.
    """
    print("Credit Default Scorer — Ablation Study")
    print("=" * 55)

    # Set up MLflow
    tracking.get_or_create_experiment(experiment_name)

    # Load data once, split once — same split for all steps
    df = load_dataset(dataset_path)
    splits = prepare_splits(df)
    print(f"Dataset: {len(df)} records ({len(splits['X_train'])} train / {len(splits['X_test'])} test)")
    print(f"Baseline default rate: {splits['y_train'].mean():.2%}\n")

    prev_metrics: dict[str, Any] = {}

    for step_num, (step_name, group_names, feature_lists, hypothesis) in enumerate(ABLATION_STEPS, 1):
        features = list(chain.from_iterable(feature_lists))

        print(f"Step {step_num}: {step_name} ({len(features)} features)")
        print(f"  Hypothesis: {hypothesis}")

        # Train
        start = time.perf_counter()
        model = train_with_features(splits, features)
        train_ms = (time.perf_counter() - start) * 1000
        print(f"  Training: {train_ms:.0f}ms")

        # Evaluate
        metrics = evaluate_with_features(model, splits, features)

        # Print key metrics with deltas
        _print_step_metrics(metrics, prev_metrics)

        # Log to MLflow
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

    # Summary table
    print("\n" + "=" * 55)
    print("ABLATION SUMMARY")
    print("=" * 55)
    summary = tracking.build_summary_table(experiment_name)
    if not summary.empty:
        # Print a clean view with just the key columns
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
        ("ece", "ECE", False),
        ("demographic_parity_diff", "DemParity", False),
        ("equalised_odds_diff", "EqOdds", False),
        ("disparate_impact_ratio", "DI_Ratio", True),
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
                # Flag concerning changes
                concerning = (
                    (higher_is_better and delta < -0.01) or
                    (not higher_is_better and delta > 0.01)
                )
                flag = " [!]" if concerning else ""
                delta_str = f" ({delta:+.4f}{flag})"

        status = "PASS" if passed else "FAIL"
        parts.append(f"{label}: {val:.4f}{delta_str} [{status}]")

    # Print in two rows for readability
    mid = len(parts) // 2 + 1
    print(f"  {' | '.join(parts[:mid])}")
    if parts[mid:]:
        print(f"  {' | '.join(parts[mid:])}")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    default_path = Path(__file__).parent.parent / "data" / "UCI_Credit_Card.csv"
    dataset = Path(sys.argv[1]) if len(sys.argv) > 1 else default_path

    if not dataset.exists():
        print(f"Dataset not found: {dataset}")
        print("Usage: python src/ablation.py [path/to/dataset.csv]")
        sys.exit(1)

    run_ablation(dataset)
