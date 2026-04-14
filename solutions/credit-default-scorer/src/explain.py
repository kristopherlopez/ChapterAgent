"""SHAP-based explainability for the credit default scorer."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import shap
from sklearn.base import BaseEstimator


def compute_shap_values(
    model: BaseEstimator,
    X: pd.DataFrame,
    *,
    max_samples: int | None = None,
) -> shap.Explanation:
    """Compute SHAP values for predictions.

    Uses TreeExplainer for tree-based models (GradientBoosting, RandomForest),
    falls back to LinearExplainer for linear models (LogisticRegression).
    """
    model_type = type(model).__name__

    if max_samples and len(X) > max_samples:
        X = X.sample(n=max_samples, random_state=42)

    if model_type in ("GradientBoostingClassifier", "RandomForestClassifier",
                       "XGBClassifier", "LGBMClassifier"):
        explainer = shap.TreeExplainer(model)
    elif model_type in ("LogisticRegression",):
        explainer = shap.LinearExplainer(model, X)
    else:
        explainer = shap.Explainer(model, X)

    return explainer(X)


def top_contributors(
    shap_values: np.ndarray,
    feature_names: list[str],
    *,
    top_n: int = 4,
) -> list[dict[str, Any]]:
    """Extract the top contributing features for a single prediction.

    Args:
        shap_values: SHAP values for one prediction (1-D array).
        feature_names: Feature names aligned with the SHAP values.
        top_n: Number of top contributors to return.

    Returns:
        List of dicts with feature, direction, and shap_value.
    """
    indices = np.argsort(np.abs(shap_values))[::-1][:top_n]
    contributors = []
    for idx in indices:
        val = float(shap_values[idx])
        contributors.append({
            "feature": feature_names[idx],
            "direction": "increases_risk" if val > 0 else "decreases_risk",
            "shap_value": round(val, 4),
        })
    return contributors


def shap_coverage(
    shap_values: shap.Explanation | np.ndarray,
    n_predictions: int,
) -> float:
    """Compute SHAP coverage — fraction of predictions with SHAP values.

    Returns 1.0 if every prediction has SHAP values, <1.0 otherwise.
    """
    if isinstance(shap_values, shap.Explanation):
        n_explained = len(shap_values)
    else:
        n_explained = shap_values.shape[0] if shap_values.ndim >= 1 else 0

    if n_predictions == 0:
        return 0.0
    return round(n_explained / n_predictions, 4)
