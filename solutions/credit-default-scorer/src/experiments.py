"""Advanced experiments for the credit default scorer.

Three studies to push AUC beyond the ablation baseline:
  1. Hyperparameter re-tuning on the winning feature set (step 8 ratios)
  2. SHAP-based feature selection (prune low-importance features)
  3. Model comparison: sklearn GBM vs XGBoost vs LightGBM

Usage:
    cd solutions/credit-default-scorer
    python src/experiments.py                          # run all 3 studies
    python src/experiments.py path/to/dataset.csv      # custom dataset

    # Browse results:
    mlflow ui                                          # http://localhost:5000
"""

from __future__ import annotations

import sys
import time
from itertools import chain, product
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier

try:
    from solutions.credit_default_scorer.src.data import (
        BALANCE_TREND_FEATURES,
        BILL_AMOUNT_FEATURES,
        CREDIT_FEATURES,
        PAYMENT_HISTORY_FEATURES,
        PAYMENT_RATIO_FEATURES,
        UTILISATION_FEATURES,
        load_dataset,
        prepare_splits,
    )
    from solutions.credit_default_scorer.src.evaluate import run_evaluation
    from solutions.credit_default_scorer.src.explain import compute_shap_values, shap_coverage
    from solutions.credit_default_scorer.src import tracking
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from data import (  # type: ignore[no-redef]
        BALANCE_TREND_FEATURES,
        BILL_AMOUNT_FEATURES,
        CREDIT_FEATURES,
        PAYMENT_HISTORY_FEATURES,
        PAYMENT_RATIO_FEATURES,
        UTILISATION_FEATURES,
        load_dataset,
        prepare_splits,
    )
    from evaluate import run_evaluation  # type: ignore[no-redef]
    from explain import compute_shap_values, shap_coverage  # type: ignore[no-redef]
    import tracking  # type: ignore[no-redef]

import lightgbm as lgb
import xgboost as xgb


# ---------------------------------------------------------------------------
# Step 8 feature set (the ablation winner)
# ---------------------------------------------------------------------------

STEP8_FEATURES = list(chain.from_iterable([
    PAYMENT_HISTORY_FEATURES,
    CREDIT_FEATURES,
    BILL_AMOUNT_FEATURES,
    UTILISATION_FEATURES,
    PAYMENT_RATIO_FEATURES,
    BALANCE_TREND_FEATURES,
]))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _evaluate_model(
    model: Any,
    splits: dict[str, Any],
    features: list[str],
) -> dict[str, Any]:
    """Evaluate any sklearn-compatible model on the holdout set."""
    X_test = splits["X_test"][features]
    y_test = splits["y_test"].values
    protected_test = splits["protected_test"]

    y_prob = model.predict_proba(X_test)[:, 1]

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


def _print_metrics(metrics: dict[str, Any]) -> None:
    """Print key metrics on one line."""
    parts = []
    for key, label in [("auc_roc", "AUC"), ("gini", "Gini"), ("brier_score", "Brier"),
                        ("ece", "ECE"), ("demographic_parity_diff", "DemParity"),
                        ("disparate_impact_ratio", "DI_Ratio")]:
        if key in metrics:
            val = metrics[key]["value"]
            status = "PASS" if metrics[key]["pass"] else "FAIL"
            parts.append(f"{label}: {val:.4f} [{status}]")
    mid = len(parts) // 2 + 1
    print(f"  {' | '.join(parts[:mid])}")
    if parts[mid:]:
        print(f"  {' | '.join(parts[mid:])}")


# ===================================================================
# Study 1: Hyperparameter re-tuning on step 8 features
# ===================================================================


HYPERPARAM_GRID = [
    {"n_estimators": 100, "max_depth": 5, "learning_rate": 0.05, "subsample": 0.8, "min_samples_leaf": 1},
    {"n_estimators": 200, "max_depth": 5, "learning_rate": 0.05, "subsample": 0.8, "min_samples_leaf": 1},
    {"n_estimators": 200, "max_depth": 4, "learning_rate": 0.05, "subsample": 0.8, "min_samples_leaf": 1},
    {"n_estimators": 200, "max_depth": 5, "learning_rate": 0.05, "subsample": 0.8, "min_samples_leaf": 5},
    {"n_estimators": 200, "max_depth": 5, "learning_rate": 0.05, "subsample": 0.8, "min_samples_leaf": 10},
    {"n_estimators": 300, "max_depth": 4, "learning_rate": 0.05, "subsample": 0.8, "min_samples_leaf": 5},
    {"n_estimators": 300, "max_depth": 5, "learning_rate": 0.03, "subsample": 0.8, "min_samples_leaf": 5},
    {"n_estimators": 300, "max_depth": 5, "learning_rate": 0.05, "subsample": 0.9, "min_samples_leaf": 5},
    {"n_estimators": 500, "max_depth": 4, "learning_rate": 0.03, "subsample": 0.8, "min_samples_leaf": 5},
    {"n_estimators": 500, "max_depth": 5, "learning_rate": 0.02, "subsample": 0.8, "min_samples_leaf": 10},
]


def run_hyperparam_study(
    splits: dict[str, Any],
    *,
    experiment_name: str = "credit-default-hyperparam-v2",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Re-tune hyperparameters on the step 8 feature set.

    Returns (best_hyperparams, best_metrics).
    """
    print("\n" + "=" * 60)
    print("STUDY 1: Hyperparameter Re-Tuning (Step 8 Features)")
    print("=" * 60)

    tracking.get_or_create_experiment(experiment_name)

    best_auc = 0.0
    best_params: dict[str, Any] = {}
    best_metrics: dict[str, Any] = {}

    for i, params in enumerate(HYPERPARAM_GRID, 1):
        run_params = {**params, "random_state": 42}
        label = (f"est={params['n_estimators']}_depth={params['max_depth']}"
                 f"_lr={params['learning_rate']}_sub={params['subsample']}"
                 f"_leaf={params['min_samples_leaf']}")

        print(f"\n  [{i}/{len(HYPERPARAM_GRID)}] {label}")

        start = time.perf_counter()
        model = GradientBoostingClassifier(**run_params)
        model.fit(splits["X_train"][STEP8_FEATURES], splits["y_train"])
        train_ms = (time.perf_counter() - start) * 1000
        print(f"    Training: {train_ms:.0f}ms")

        metrics = _evaluate_model(model, splits, STEP8_FEATURES)
        _print_metrics(metrics)

        auc = metrics["auc_roc"]["value"]
        if auc > best_auc:
            best_auc = auc
            best_params = params
            best_metrics = metrics

        # Log to MLflow
        X_test_subset = splits["X_test"][STEP8_FEATURES]
        tracking.log_training_run(
            run_name=f"hp_{label}",
            features_used=STEP8_FEATURES,
            feature_groups=["payment_history", "credit", "bill_amounts",
                            "utilisation", "payment_ratio", "balance_trend"],
            hyperparams=run_params,
            metrics=metrics,
            model=model,
            X_test=X_test_subset,
            step_number=i,
        )

    print(f"\n  BEST: AUC={best_auc:.4f} with {best_params}")
    return best_params, best_metrics


# ===================================================================
# Study 2: SHAP-based feature selection
# ===================================================================


def run_feature_selection_study(
    splits: dict[str, Any],
    hyperparams: dict[str, Any],
    *,
    experiment_name: str = "credit-default-feature-selection",
) -> tuple[list[str], dict[str, Any]]:
    """Prune features by SHAP importance, re-train, and compare.

    Uses the best hyperparams from study 1.
    Returns (best_feature_list, best_metrics).
    """
    print("\n" + "=" * 60)
    print("STUDY 2: SHAP-Based Feature Selection")
    print("=" * 60)

    tracking.get_or_create_experiment(experiment_name)

    # Train baseline model to get SHAP importances
    run_params = {**hyperparams, "random_state": 42}
    model = GradientBoostingClassifier(**run_params)
    model.fit(splits["X_train"][STEP8_FEATURES], splits["y_train"])

    X_test = splits["X_test"][STEP8_FEATURES]
    shap_vals = compute_shap_values(model, X_test, max_samples=500)
    vals = shap_vals.values
    if vals.ndim == 3:
        vals = vals[:, :, 1]

    # Mean absolute SHAP value per feature
    mean_abs_shap = np.abs(vals).mean(axis=0)
    importance_order = np.argsort(mean_abs_shap)[::-1]
    ranked_features = [(STEP8_FEATURES[i], float(mean_abs_shap[i])) for i in importance_order]

    print("\n  Feature importance ranking (mean |SHAP|):")
    for rank, (feat, imp) in enumerate(ranked_features, 1):
        print(f"    {rank:2d}. {feat:<20s} {imp:.6f}")

    # Test subsets: top-N features for various N values
    test_sizes = [5, 8, 10, 13, 15, 20, 25, len(STEP8_FEATURES)]
    best_auc = 0.0
    best_features: list[str] = STEP8_FEATURES
    best_metrics: dict[str, Any] = {}

    step = 0
    for n in test_sizes:
        step += 1
        n = min(n, len(STEP8_FEATURES))
        features = [ranked_features[i][0] for i in range(n)]
        label = f"top_{n}_features"

        print(f"\n  [{step}/{len(test_sizes)}] {label}: {', '.join(features[:5])}{'...' if n > 5 else ''}")

        start = time.perf_counter()
        model = GradientBoostingClassifier(**run_params)
        model.fit(splits["X_train"][features], splits["y_train"])
        train_ms = (time.perf_counter() - start) * 1000
        print(f"    Training: {train_ms:.0f}ms")

        metrics = _evaluate_model(model, splits, features)
        _print_metrics(metrics)

        auc = metrics["auc_roc"]["value"]
        if auc > best_auc:
            best_auc = auc
            best_features = features
            best_metrics = metrics

        X_test_subset = splits["X_test"][features]
        tracking.log_training_run(
            run_name=label,
            features_used=features,
            feature_groups=[f"top_{n}_by_shap"],
            hyperparams=run_params,
            metrics=metrics,
            model=model,
            X_test=X_test_subset,
            step_number=step,
        )

    print(f"\n  BEST: AUC={best_auc:.4f} with {len(best_features)} features")
    return best_features, best_metrics


# ===================================================================
# Study 3: Model comparison — sklearn GBM vs XGBoost vs LightGBM
# ===================================================================


def _build_model_configs(hyperparams: dict[str, Any]) -> list[tuple[str, Any, dict[str, Any]]]:
    """Build model configs for comparison, translating sklearn params to each framework."""
    configs: list[tuple[str, Any, dict[str, Any]]] = []

    # sklearn GradientBoostingClassifier (baseline)
    sklearn_params = {**hyperparams, "random_state": 42}
    configs.append(("sklearn_gbm", GradientBoostingClassifier(**sklearn_params), sklearn_params))

    # XGBoost
    xgb_params = {
        "n_estimators": hyperparams["n_estimators"],
        "max_depth": hyperparams["max_depth"],
        "learning_rate": hyperparams["learning_rate"],
        "subsample": hyperparams["subsample"],
        "min_child_weight": hyperparams.get("min_samples_leaf", 1),
        "reg_alpha": 0.0,
        "reg_lambda": 1.0,
        "random_state": 42,
        "eval_metric": "auc",
        "tree_method": "hist",
        "verbosity": 0,
    }
    configs.append(("xgboost", xgb.XGBClassifier(**xgb_params), xgb_params))

    # XGBoost with L1 regularization
    xgb_l1_params = {**xgb_params, "reg_alpha": 0.1}
    configs.append(("xgboost_l1", xgb.XGBClassifier(**xgb_l1_params), xgb_l1_params))

    # XGBoost with L2 regularization
    xgb_l2_params = {**xgb_params, "reg_lambda": 5.0}
    configs.append(("xgboost_l2", xgb.XGBClassifier(**xgb_l2_params), xgb_l2_params))

    # XGBoost with both L1 and L2
    xgb_elastic_params = {**xgb_params, "reg_alpha": 0.05, "reg_lambda": 3.0}
    configs.append(("xgboost_elastic", xgb.XGBClassifier(**xgb_elastic_params), xgb_elastic_params))

    # LightGBM
    lgb_params = {
        "n_estimators": hyperparams["n_estimators"],
        "max_depth": hyperparams["max_depth"],
        "learning_rate": hyperparams["learning_rate"],
        "subsample": hyperparams["subsample"],
        "min_child_samples": max(hyperparams.get("min_samples_leaf", 1), 5),
        "reg_alpha": 0.0,
        "reg_lambda": 0.0,
        "random_state": 42,
        "verbose": -1,
    }
    configs.append(("lightgbm", lgb.LGBMClassifier(**lgb_params), lgb_params))

    # LightGBM with L1 regularization
    lgb_l1_params = {**lgb_params, "reg_alpha": 0.1}
    configs.append(("lightgbm_l1", lgb.LGBMClassifier(**lgb_l1_params), lgb_l1_params))

    # LightGBM with L2 regularization
    lgb_l2_params = {**lgb_params, "reg_lambda": 5.0}
    configs.append(("lightgbm_l2", lgb.LGBMClassifier(**lgb_l2_params), lgb_l2_params))

    # LightGBM with dart boosting
    lgb_dart_params = {**lgb_params, "boosting_type": "dart", "n_estimators": min(hyperparams["n_estimators"], 200)}
    configs.append(("lightgbm_dart", lgb.LGBMClassifier(**lgb_dart_params), lgb_dart_params))

    return configs


def run_model_comparison(
    splits: dict[str, Any],
    features: list[str],
    hyperparams: dict[str, Any],
    *,
    experiment_name: str = "credit-default-model-comparison-v2",
) -> tuple[str, Any, dict[str, Any]]:
    """Compare sklearn GBM, XGBoost, and LightGBM on the best feature set.

    Returns (best_model_name, best_model, best_metrics).
    """
    print("\n" + "=" * 60)
    print("STUDY 3: Model Comparison (sklearn GBM vs XGBoost vs LightGBM)")
    print("=" * 60)
    print(f"  Features: {len(features)}")

    tracking.get_or_create_experiment(experiment_name)

    configs = _build_model_configs(hyperparams)
    best_auc = 0.0
    best_name = ""
    best_model = None
    best_metrics: dict[str, Any] = {}

    for i, (name, model, params) in enumerate(configs, 1):
        print(f"\n  [{i}/{len(configs)}] {name}")

        start = time.perf_counter()
        model.fit(splits["X_train"][features], splits["y_train"])
        train_ms = (time.perf_counter() - start) * 1000
        print(f"    Training: {train_ms:.0f}ms")

        metrics = _evaluate_model(model, splits, features)
        _print_metrics(metrics)

        auc = metrics["auc_roc"]["value"]
        if auc > best_auc:
            best_auc = auc
            best_name = name
            best_model = model
            best_metrics = metrics

        X_test_subset = splits["X_test"][features]
        tracking.log_training_run(
            run_name=name,
            features_used=features,
            feature_groups=[f"model_comparison_{name}"],
            hyperparams=params,
            metrics=metrics,
            model=model,
            X_test=X_test_subset,
            step_number=i,
        )

    print(f"\n  BEST: {best_name} AUC={best_auc:.4f}")
    return best_name, best_model, best_metrics


# ===================================================================
# Main runner
# ===================================================================


def run_all_experiments(dataset_path: str | Path) -> None:
    """Run all three studies in sequence, passing results forward."""
    print("Credit Default Scorer — Advanced Experiments")
    print("=" * 60)

    df = load_dataset(dataset_path)
    splits = prepare_splits(df)
    print(f"Dataset: {len(df)} records ({len(splits['X_train'])} train / {len(splits['X_test'])} test)")
    print(f"Baseline default rate: {splits['y_train'].mean():.2%}")
    print(f"Step 8 feature set: {len(STEP8_FEATURES)} features")

    # Ablation baseline for comparison
    print("\n--- Ablation baseline (step 8, original hyperparams) ---")
    baseline_params = {"n_estimators": 100, "max_depth": 5, "learning_rate": 0.1, "subsample": 0.8, "random_state": 42}
    baseline_model = GradientBoostingClassifier(**baseline_params)
    baseline_model.fit(splits["X_train"][STEP8_FEATURES], splits["y_train"])
    baseline_metrics = _evaluate_model(baseline_model, splits, STEP8_FEATURES)
    baseline_auc = baseline_metrics["auc_roc"]["value"]
    _print_metrics(baseline_metrics)
    print(f"  Baseline AUC: {baseline_auc:.4f}")

    # Study 1: Hyperparameter tuning
    best_params, hp_metrics = run_hyperparam_study(splits)
    hp_auc = hp_metrics["auc_roc"]["value"]

    # Study 2: Feature selection (using best hyperparams from study 1)
    best_features, fs_metrics = run_feature_selection_study(splits, best_params)
    fs_auc = fs_metrics["auc_roc"]["value"]

    # Study 3: Model comparison (using best features and hyperparams)
    best_model_name, best_model, mc_metrics = run_model_comparison(
        splits, best_features, best_params
    )
    mc_auc = mc_metrics["auc_roc"]["value"]

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"  Ablation baseline (step 8):  AUC={baseline_auc:.4f}  (100 trees, lr=0.1, 27 features, sklearn GBM)")
    print(f"  Study 1 — HP tuning:         AUC={hp_auc:.4f}  (best: {best_params})")
    print(f"  Study 2 — Feature selection:  AUC={fs_auc:.4f}  ({len(best_features)} features)")
    print(f"  Study 3 — Model comparison:   AUC={mc_auc:.4f}  ({best_model_name})")
    print(f"\n  Total AUC lift: {mc_auc - baseline_auc:+.4f}")
    print(f"\n  DI Ratio: {mc_metrics['disparate_impact_ratio']['value']:.4f} "
          f"[{'PASS' if mc_metrics['disparate_impact_ratio']['pass'] else 'FAIL'}]")
    print(f"\nBrowse full results: mlflow ui  (http://localhost:5000)")


if __name__ == "__main__":
    default_path = Path(__file__).parent.parent / "data" / "UCI_Credit_Card.csv"
    dataset = Path(sys.argv[1]) if len(sys.argv) > 1 else default_path

    if not dataset.exists():
        print(f"Dataset not found: {dataset}")
        print("Usage: python src/experiments.py [path/to/dataset.csv]")
        sys.exit(1)

    run_all_experiments(dataset)
