"""Evaluation metrics for the Australian Credit Approval Scorer.

Statistical metrics (AUC, Gini, Brier, Hosmer-Lemeshow, bootstrap CI, proxy
fairness) adapted for small-sample governance. Same harness interface as the
credit default scorer — the platform doesn't care about dataset size.
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
    """Kolmogorov-Smirnov statistic — separation between approved/denied."""
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


def hosmer_lemeshow_test(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    *,
    n_groups: int = 10,
) -> tuple[float, float]:
    """Hosmer-Lemeshow goodness-of-fit test — better for small samples than ECE.

    Returns (statistic, p_value). p > 0.05 means good calibration.
    """
    # Sort by predicted probability
    order = np.argsort(y_prob)
    y_true_sorted = y_true[order]
    y_prob_sorted = y_prob[order]

    # Split into roughly equal groups
    groups = np.array_split(np.arange(len(y_true)), n_groups)

    hl_stat = 0.0
    for group_idx in groups:
        if len(group_idx) == 0:
            continue
        observed = y_true_sorted[group_idx].sum()
        expected = y_prob_sorted[group_idx].sum()
        n = len(group_idx)
        expected_neg = n - expected

        if expected > 0:
            hl_stat += (observed - expected) ** 2 / expected
        if expected_neg > 0:
            hl_stat += ((n - observed) - expected_neg) ** 2 / expected_neg

    # Chi-squared with (n_groups - 2) degrees of freedom
    df = max(n_groups - 2, 1)
    p_value = 1.0 - stats.chi2.cdf(hl_stat, df)
    return float(round(hl_stat, 4)), float(round(p_value, 4))


# ---------------------------------------------------------------------------
# Bootstrap confidence intervals (small sample governance)
# ---------------------------------------------------------------------------


def bootstrap_metric_ci(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    metric_fn,
    *,
    n_iterations: int = 1000,
    ci_level: float = 0.95,
    random_state: int = 42,
) -> dict[str, float]:
    """Compute bootstrap confidence interval for a metric.

    Returns dict with point_estimate, ci_lower, ci_upper, ci_width.
    """
    rng = np.random.RandomState(random_state)
    n = len(y_true)
    boot_values = []

    for _ in range(n_iterations):
        idx = rng.choice(n, size=n, replace=True)
        # Ensure both classes present in bootstrap sample
        if len(np.unique(y_true[idx])) < 2:
            continue
        try:
            boot_values.append(metric_fn(y_true[idx], y_prob[idx]))
        except Exception:
            continue

    if not boot_values:
        point = metric_fn(y_true, y_prob)
        return {"point_estimate": point, "ci_lower": point, "ci_upper": point, "ci_width": 0.0}

    alpha = (1.0 - ci_level) / 2.0
    ci_lower = float(np.percentile(boot_values, 100 * alpha))
    ci_upper = float(np.percentile(boot_values, 100 * (1 - alpha)))

    return {
        "point_estimate": float(np.mean(boot_values)),
        "ci_lower": round(ci_lower, 4),
        "ci_upper": round(ci_upper, 4),
        "ci_width": round(ci_upper - ci_lower, 4),
    }


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
# Proxy discrimination metrics (anonymised features)
# ---------------------------------------------------------------------------


def subgroup_approval_rate_variance(
    y_prob: np.ndarray,
    proxy_feature: np.ndarray,
    *,
    threshold: float = 0.5,
) -> dict[str, Any]:
    """Compute approval rate difference across subgroups of a proxy candidate.

    Returns the max approval rate difference and per-group rates.
    """
    y_pred = (y_prob >= threshold).astype(int)
    groups = np.unique(proxy_feature[~np.isnan(proxy_feature)]) if proxy_feature.dtype in (float, np.float64) else np.unique(proxy_feature)

    group_rates = {}
    for g in groups:
        mask = proxy_feature == g
        if mask.sum() > 0:
            group_rates[str(g)] = float(round(y_pred[mask].mean(), 4))

    rates = list(group_rates.values())
    max_diff = max(rates) - min(rates) if len(rates) >= 2 else 0.0

    return {
        "max_difference": round(max_diff, 4),
        "group_rates": group_rates,
    }


def demographic_parity_difference(
    y_prob: np.ndarray,
    protected: np.ndarray,
) -> float:
    """Max absolute difference in mean predicted probability across groups."""
    groups = np.unique(protected)
    means = [y_prob[protected == g].mean() for g in groups]
    return float(round(max(means) - min(means), 6))


def disparate_impact_ratio(
    y_prob: np.ndarray,
    protected: np.ndarray,
    *,
    threshold: float = 0.5,
) -> float:
    """Four-fifths rule: min(group_positive_rate) / max(group_positive_rate)."""
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
    proxy_df: pd.DataFrame,
    *,
    baseline_scores: np.ndarray | None = None,
    shap_coverage_value: float = 1.0,
    thresholds: dict[str, float] | None = None,
    bootstrap_iterations: int = 1000,
) -> dict[str, Any]:
    """Run the full evaluation harness and return metric results with pass/fail.

    Adapted for small-sample governance: includes Hosmer-Lemeshow test and
    bootstrap confidence intervals on key metrics.
    """
    defaults = {
        "auc_roc": 0.70,
        "gini": 0.40,
        "brier_score": 0.25,
        "hosmer_lemeshow_p": 0.05,
        "subgroup_approval_variance": 0.15,
        "shap_coverage": 1.0,
        "ci_width_auc": 0.20,
    }
    t = {**defaults, **(thresholds or {})}

    results: dict[str, Any] = {}

    # Performance
    auc = auc_roc(y_true, y_prob)
    results["auc_roc"] = {"value": round(auc, 4), "threshold": t["auc_roc"], "pass": auc >= t["auc_roc"]}

    gini = gini_coefficient(y_true, y_prob)
    results["gini"] = {"value": round(gini, 4), "threshold": t["gini"], "pass": gini >= t["gini"]}

    bs = brier_score(y_true, y_prob)
    results["brier_score"] = {"value": round(bs, 4), "threshold": t["brier_score"], "pass": bs <= t["brier_score"]}

    ks = ks_statistic(y_true, y_prob)
    results["ks_statistic"] = {"value": round(ks, 4), "threshold": None, "pass": True}

    # Calibration — Hosmer-Lemeshow (better for small samples)
    hl_stat, hl_p = hosmer_lemeshow_test(y_true, y_prob)
    results["hosmer_lemeshow"] = {
        "value": hl_p,
        "statistic": hl_stat,
        "threshold": t["hosmer_lemeshow_p"],
        "pass": hl_p >= t["hosmer_lemeshow_p"],
    }

    ece = expected_calibration_error(y_true, y_prob)
    results["ece"] = {"value": round(ece, 4), "threshold": None, "pass": True}

    # Bootstrap confidence intervals (small sample governance)
    auc_ci = bootstrap_metric_ci(y_true, y_prob, auc_roc, n_iterations=bootstrap_iterations)
    results["auc_roc_ci"] = {
        "ci_lower": auc_ci["ci_lower"],
        "ci_upper": auc_ci["ci_upper"],
        "ci_width": auc_ci["ci_width"],
        "threshold": t["ci_width_auc"],
        "pass": True,
        "warning": auc_ci["ci_width"] > t["ci_width_auc"],
    }

    # Proxy discrimination — check each binary candidate
    max_variance = 0.0
    proxy_details: dict[str, Any] = {}
    for col in proxy_df.columns:
        result = subgroup_approval_rate_variance(y_prob, proxy_df[col].values)
        proxy_details[col] = result
        max_variance = max(max_variance, result["max_difference"])

    results["subgroup_approval_variance"] = {
        "value": round(max_variance, 4),
        "threshold": t["subgroup_approval_variance"],
        "pass": max_variance <= t["subgroup_approval_variance"],
        "details": proxy_details,
    }

    # Stability
    if baseline_scores is not None:
        psi = population_stability_index(baseline_scores, y_prob)
        results["psi"] = {"value": round(psi, 4), "threshold": 0.25, "pass": psi <= 0.25}

    # Explainability
    results["shap_coverage"] = {
        "value": shap_coverage_value,
        "threshold": t["shap_coverage"],
        "pass": shap_coverage_value >= t["shap_coverage"],
    }

    # Summary
    all_pass = all(r["pass"] for r in results.values() if isinstance(r, dict) and "pass" in r)
    has_warnings = any(r.get("warning", False) for r in results.values() if isinstance(r, dict))
    results["_summary"] = {
        "total_metrics": sum(1 for k in results if k != "_summary"),
        "passed": sum(1 for k, r in results.items() if k != "_summary" and isinstance(r, dict) and r.get("pass", False)),
        "failed": sum(1 for k, r in results.items() if k != "_summary" and isinstance(r, dict) and not r.get("pass", True)),
        "warnings": has_warnings,
        "overall": "pass" if all_pass else "FAIL",
        "note": "Small dataset (690 records) — metrics include uncertainty. Confidence intervals may be wide."
        if has_warnings else None,
    }

    return results
