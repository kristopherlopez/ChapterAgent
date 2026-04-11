"""MLflow experiment tracking for the credit default scorer."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import mlflow
import numpy as np
import pandas as pd
import shap
from sklearn.base import BaseEstimator


def get_or_create_experiment(
    name: str = "credit-default-ablation",
    *,
    tracking_dir: str | Path = "./mlruns",
) -> str:
    """Set up MLflow experiment with local file-based tracking.

    No MLflow server required — results stored in ./mlruns/.
    Browse with: mlflow ui
    """
    mlflow.set_tracking_uri(f"file:{Path(tracking_dir).resolve().as_posix()}")
    mlflow.set_experiment(name)
    return name


def log_training_run(
    *,
    run_name: str,
    features_used: list[str],
    feature_groups: list[str],
    hyperparams: dict[str, Any],
    metrics: dict[str, Any],
    model: BaseEstimator,
    X_test: pd.DataFrame,
    step_number: int = 0,
) -> str:
    """Log a single training run to MLflow.

    Logs parameters, metrics, and artifacts (feature importance plot,
    SHAP summary plot, evaluation results JSON).

    Returns the MLflow run ID.
    """
    with mlflow.start_run(run_name=run_name) as run:
        # --- Tags ---
        mlflow.set_tag("step_number", step_number)
        mlflow.set_tag("feature_groups", ", ".join(feature_groups))

        # --- Params ---
        mlflow.log_param("feature_groups", ", ".join(feature_groups))
        mlflow.log_param("n_features", len(features_used))
        mlflow.log_param("features", ", ".join(features_used))
        for k, v in hyperparams.items():
            mlflow.log_param(k, v)

        # --- Metrics ---
        for key, result in metrics.items():
            if key == "_summary":
                continue
            if isinstance(result, dict) and "value" in result:
                mlflow.log_metric(key, result["value"])
                if "pass" in result:
                    mlflow.log_metric(f"{key}_pass", 1.0 if result["pass"] else 0.0)

        # Summary
        if "_summary" in metrics:
            mlflow.log_metric("metrics_passed", metrics["_summary"]["passed"])
            mlflow.log_metric("metrics_failed", metrics["_summary"]["failed"])

        # --- Artifacts ---
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Feature importance plot
            _save_feature_importance_plot(
                model, features_used, Path(tmpdir) / "feature_importance.png"
            )
            mlflow.log_artifact(str(Path(tmpdir) / "feature_importance.png"))

            # 2. SHAP summary plot
            _save_shap_summary_plot(
                model, X_test, Path(tmpdir) / "shap_summary.png"
            )
            mlflow.log_artifact(str(Path(tmpdir) / "shap_summary.png"))

            # 3. Evaluation results JSON
            results_path = Path(tmpdir) / "evaluation_results.json"
            with open(results_path, "w") as f:
                json.dump(metrics, f, indent=2, default=str)
            mlflow.log_artifact(str(results_path))

        # 4. Save the trained model
        mlflow.sklearn.log_model(
            model,
            artifact_path="model",
            input_example=X_test.head(1),
        )

        return run.info.run_id


def build_summary_table(experiment_name: str) -> pd.DataFrame:
    """Query all runs from an experiment and build a comparison table.

    Returns a DataFrame sorted by step number with delta columns
    showing the lift from each incremental feature group.
    """
    runs = mlflow.search_runs(
        experiment_names=[experiment_name],
        order_by=["tags.step_number ASC"],
    )

    if runs.empty:
        return pd.DataFrame()

    metric_cols = {
        "metrics.auc_roc": "AUC",
        "metrics.gini": "Gini",
        "metrics.brier_score": "Brier",
        "metrics.ece": "ECE",
        "metrics.demographic_parity_diff": "DemParity",
        "metrics.equalised_odds_diff": "EqOdds",
        "metrics.disparate_impact_ratio": "DI_Ratio",
        "metrics.shap_coverage": "SHAP_Cov",
    }

    summary = pd.DataFrame()
    summary["Step"] = runs["tags.mlflow.runName"]
    summary["Features"] = runs["params.feature_groups"]
    summary["N"] = runs["params.n_features"].astype(int)

    for col, label in metric_cols.items():
        if col in runs.columns:
            summary[label] = runs[col].round(4)

    # Compute deltas
    for label in metric_cols.values():
        if label in summary.columns:
            summary[f"{label}_delta"] = summary[label].diff()
            summary[f"{label}_delta"] = summary[f"{label}_delta"].apply(
                lambda x: f"{x:+.4f}" if pd.notna(x) else "--"
            )

    summary = summary.reset_index(drop=True)
    return summary


# ---------------------------------------------------------------------------
# Artifact helpers
# ---------------------------------------------------------------------------


def _save_feature_importance_plot(
    model: BaseEstimator,
    feature_names: list[str],
    path: Path,
) -> None:
    """Save a horizontal bar chart of feature importances."""
    importances = model.feature_importances_
    indices = np.argsort(importances)

    fig, ax = plt.subplots(figsize=(10, max(4, len(feature_names) * 0.3)))
    ax.barh(range(len(indices)), importances[indices], align="center")
    ax.set_yticks(range(len(indices)))
    ax.set_yticklabels([feature_names[i] for i in indices])
    ax.set_xlabel("Feature Importance")
    ax.set_title("Feature Importance (Gradient Boosting)")
    plt.tight_layout()
    fig.savefig(path, dpi=100)
    plt.close(fig)


def _save_shap_summary_plot(
    model: BaseEstimator,
    X: pd.DataFrame,
    path: Path,
    *,
    max_samples: int = 500,
) -> None:
    """Save a SHAP summary beeswarm plot."""
    if len(X) > max_samples:
        X = X.sample(n=max_samples, random_state=42)

    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer(X)
        vals = shap_values.values
        if vals.ndim == 3:
            vals = vals[:, :, 1]

        fig, ax = plt.subplots(figsize=(10, max(4, X.shape[1] * 0.3)))
        shap.summary_plot(vals, X, show=False)
        plt.tight_layout()
        plt.savefig(path, dpi=100, bbox_inches="tight")
        plt.close("all")
    except Exception:
        # Fallback: save a placeholder if SHAP plotting fails
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, "SHAP plot unavailable", ha="center", va="center")
        ax.set_axis_off()
        fig.savefig(path, dpi=100)
        plt.close(fig)
