"""Evaluation metrics for the credit default scorer.

Statistical metrics (AUC, Gini, Brier, ECE, PSI, fairness) that plug into
the platform's evaluation harness — same interface, different implementations
than the GenAI LLM-as-judge metrics.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import brier_score_loss, roc_auc_score


# ---------------------------------------------------------------------------
# Performance metrics
# ---------------------------------------------------------------------------


def auc_roc(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Area Under the ROC Curve."""
    return float(roc_auc_score(y_true, y_prob))


def gini_coefficient(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Gini = 2 * AUC - 1. Industry-standard discrimination measure."""
    return 2.0 * auc_roc(y_true, y_prob) - 1.0


def brier_score(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Brier score — lower is better. Measures calibration quality."""
    return float(brier_score_loss(y_true, y_prob))


def ks_statistic(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Kolmogorov-Smirnov statistic — separation between default/non-default."""
    pos = y_prob[y_true == 1]
    neg = y_prob[y_true == 0]
    return float(stats.ks_2samp(pos, neg).statistic)


# ---------------------------------------------------------------------------
# Calibration metrics
# ---------------------------------------------------------------------------


def expected_calibration_error(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    *,
    n_bins: int = 10,
) -> float:
    """Expected Calibration Error — weighted average of per-bin |accuracy - confidence|."""
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    total = len(y_true)

    for lo, hi in zip(bin_edges[:-1], bin_edges[1:]):
        mask = (y_prob >= lo) & (y_prob < hi)
        count = mask.sum()
        if count == 0:
            continue
        avg_confidence = y_prob[mask].mean()
        avg_accuracy = y_true[mask].mean()
        ece += (count / total) * abs(avg_accuracy - avg_confidence)

    return float(round(ece, 6))


# ---------------------------------------------------------------------------
# Stability / drift metrics
# ---------------------------------------------------------------------------


def population_stability_index(
    baseline: np.ndarray,
    current: np.ndarray,
    *,
    n_bins: int = 10,
) -> float:
    """Population Stability Index between two score distributions.

    PSI < 0.10: no significant shift
    PSI 0.10-0.25: moderate shift — investigate
    PSI > 0.25: significant shift — model may need re-evaluation
    """
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    eps = 1e-6

    baseline_counts, _ = np.histogram(baseline, bins=bin_edges)
    current_counts, _ = np.histogram(current, bins=bin_edges)

    baseline_pct = baseline_counts / max(baseline_counts.sum(), 1) + eps
    current_pct = current_counts / max(current_counts.sum(), 1) + eps

    psi = float(np.sum((current_pct - baseline_pct) * np.log(current_pct / baseline_pct)))
    return round(psi, 6)


# ---------------------------------------------------------------------------
# Fairness / discrimination metrics
# ---------------------------------------------------------------------------


def demographic_parity_difference(
    y_prob: np.ndarray,
    protected: np.ndarray,
) -> float:
    """Max absolute difference in mean predicted probability across groups."""
    groups = np.unique(protected)
    means = [y_prob[protected == g].mean() for g in groups]
    return float(round(max(means) - min(means), 6))


def equalised_odds_difference(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    protected: np.ndarray,
) -> float:
    """Max difference in TPR or FPR across protected groups."""
    groups = np.unique(protected)
    tprs, fprs = [], []
    for g in groups:
        mask = protected == g
        positives = y_true[mask] == 1
        negatives = y_true[mask] == 0
        if positives.sum() > 0:
            tprs.append(y_pred[mask][positives].mean())
        if negatives.sum() > 0:
            fprs.append(y_pred[mask][negatives].mean())

    max_tpr_diff = max(tprs) - min(tprs) if len(tprs) >= 2 else 0.0
    max_fpr_diff = max(fprs) - min(fprs) if len(fprs) >= 2 else 0.0
    return float(round(max(max_tpr_diff, max_fpr_diff), 6))


def disparate_impact_ratio(
    y_prob: np.ndarray,
    protected: np.ndarray,
    *,
    threshold: float = 0.5,
) -> float:
    """Four-fifths rule: min(group_positive_rate) / max(group_positive_rate).

    Must be >= 0.80 to pass.
    """
    y_pred = (y_prob >= threshold).astype(int)
    groups = np.unique(protected)
    rates = []
    for g in groups:
        mask = protected == g
        if mask.sum() > 0:
            rates.append(y_pred[mask].mean())

    if not rates or max(rates) == 0:
        return 0.0
    return float(round(min(rates) / max(rates), 6))


# ---------------------------------------------------------------------------
# Full evaluation run
# ---------------------------------------------------------------------------


def run_evaluation(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    protected_df: pd.DataFrame,
    *,
    baseline_scores: np.ndarray | None = None,
    shap_coverage_value: float = 1.0,
    thresholds: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Run the full evaluation harness and return metric results with pass/fail.

    This is the same harness interface used by GenAI solutions — the platform
    doesn't care whether the metric is an LLM call or a numpy computation.
    """
    defaults = {
        "auc_roc": 0.70,
        "gini": 0.40,
        "brier_score": 0.20,
        "ece": 0.05,
        "demographic_parity_diff": 0.05,
        "equalised_odds_diff": 0.05,
        "disparate_impact_ratio": 0.80,
        "psi": 0.25,
        "shap_coverage": 1.0,
    }
    t = {**defaults, **(thresholds or {})}

    y_pred_binary = (y_prob >= 0.5).astype(int)

    results: dict[str, Any] = {}

    # Performance
    auc = auc_roc(y_true, y_prob)
    results["auc_roc"] = {"value": round(auc, 4), "threshold": t["auc_roc"], "pass": auc >= t["auc_roc"]}

    gini = gini_coefficient(y_true, y_prob)
    results["gini"] = {"value": round(gini, 4), "threshold": t["gini"], "pass": gini >= t["gini"]}

    bs = brier_score(y_true, y_prob)
    results["brier_score"] = {"value": round(bs, 4), "threshold": t["brier_score"], "pass": bs <= t["brier_score"]}

    ece = expected_calibration_error(y_true, y_prob)
    results["ece"] = {"value": round(ece, 4), "threshold": t["ece"], "pass": ece <= t["ece"]}

    ks = ks_statistic(y_true, y_prob)
    results["ks_statistic"] = {"value": round(ks, 4), "threshold": None, "pass": True}

    # Fairness — across gender (SEX)
    if "SEX" in protected_df.columns:
        sex = protected_df["SEX"].values
        dp = demographic_parity_difference(y_prob, sex)
        results["demographic_parity_diff"] = {"value": round(dp, 4), "threshold": t["demographic_parity_diff"], "pass": dp <= t["demographic_parity_diff"]}

        eo = equalised_odds_difference(y_true, y_pred_binary, sex)
        results["equalised_odds_diff"] = {"value": round(eo, 4), "threshold": t["equalised_odds_diff"], "pass": eo <= t["equalised_odds_diff"]}

        di = disparate_impact_ratio(y_prob, sex)
        results["disparate_impact_ratio"] = {"value": round(di, 4), "threshold": t["disparate_impact_ratio"], "pass": di >= t["disparate_impact_ratio"]}

    # Stability
    if baseline_scores is not None:
        psi = population_stability_index(baseline_scores, y_prob)
        results["psi"] = {"value": round(psi, 4), "threshold": t["psi"], "pass": psi <= t["psi"]}

    # Explainability
    results["shap_coverage"] = {"value": shap_coverage_value, "threshold": t["shap_coverage"], "pass": shap_coverage_value >= t["shap_coverage"]}

    # Summary
    all_pass = all(r["pass"] for r in results.values())
    results["_summary"] = {
        "total_metrics": len(results) - 1,
        "passed": sum(1 for k, r in results.items() if k != "_summary" and r["pass"]),
        "failed": sum(1 for k, r in results.items() if k != "_summary" and not r["pass"]),
        "overall": "pass" if all_pass else "FAIL",
    }

    return results
