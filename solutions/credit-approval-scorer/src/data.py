"""Data loading and preparation for the Australian Credit Approval dataset."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


# Feature groups — all anonymised (A1-A14)
# 8 categorical, 6 continuous
CATEGORICAL_BINARY_FEATURES = ["A1", "A8", "A9", "A11"]
CATEGORICAL_MULTI_FEATURES = ["A4", "A5", "A6", "A12"]
CONTINUOUS_PRIMARY_FEATURES = ["A2", "A3", "A7"]
CONTINUOUS_SECONDARY_FEATURES = ["A10", "A13", "A14"]

# No known protected attributes — features are anonymised.
# Binary categoricals (A1, A8, A9, A11) are proxy discrimination candidates.
PROXY_CANDIDATES = ["A1", "A8", "A9", "A11"]

ALL_FEATURES = (
    CATEGORICAL_BINARY_FEATURES
    + CATEGORICAL_MULTI_FEATURES
    + CONTINUOUS_PRIMARY_FEATURES
    + CONTINUOUS_SECONDARY_FEATURES
)

TARGET = "A15"

# Mapping for categorical features that arrive as strings
CATEGORICAL_ENCODINGS: dict[str, dict[str, int]] = {
    "A1": {"b": 0, "a": 1},
    "A4": {"u": 0, "y": 1, "l": 2, "t": 3},
    "A5": {"g": 0, "p": 1, "gg": 2},
    "A6": {"c": 0, "d": 1, "cc": 2, "i": 3, "j": 4, "k": 5, "m": 6,
           "r": 7, "q": 8, "w": 9, "x": 10, "e": 11, "aa": 12, "ff": 13},
    "A8": {"t": 1, "f": 0},
    "A9": {"t": 1, "f": 0},
    "A11": {"t": 1, "f": 0},
    "A12": {"s": 0, "g": 1, "p": 2},
}


def load_dataset(path: str | Path) -> pd.DataFrame:
    """Load the Australian Credit Approval dataset.

    The UCI Statlog dataset ships as a space-separated file with no header.
    Columns are A1-A14 (features) and A15 (target: 0=denied, 1=approved).
    """
    path = Path(path)

    # Try CSV first (header present), then space-separated (no header)
    col_names = [f"A{i}" for i in range(1, 16)]

    if path.suffix == ".csv":
        # Check if it has a header
        first_line = path.read_text().split("\n")[0]
        if "A1" in first_line or "," in first_line:
            df = pd.read_csv(path)
            # Normalise column names
            if df.columns[0] != "A1":
                df.columns = col_names
        else:
            df = pd.read_csv(path, header=None, names=col_names)
    else:
        # Space-separated (original UCI format)
        df = pd.read_csv(path, sep=r"\s+", header=None, names=col_names)

    # Encode string categoricals to numeric
    for col, mapping in CATEGORICAL_ENCODINGS.items():
        if col in df.columns and df[col].dtype == object:
            df[col] = df[col].map(mapping)

    # Handle the target — may be '+'/'-' or 1/0
    if df[TARGET].dtype == object:
        df[TARGET] = df[TARGET].map({"+": 1, "-": 0})

    # Drop rows with any remaining NaN from encoding failures
    df = df.dropna().reset_index(drop=True)

    # Ensure all feature columns are numeric
    for col in ALL_FEATURES:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna().reset_index(drop=True)

    return df


def prepare_splits(
    df: pd.DataFrame,
    *,
    test_size: float = 0.3,
    random_state: int = 42,
) -> dict[str, Any]:
    """Split into train/test and separate features, target, and proxy candidates.

    Returns a dict with keys:
        X_train, X_test, y_train, y_test,
        proxy_train, proxy_test,
        feature_names
    """
    feature_cols = [c for c in ALL_FEATURES if c in df.columns]
    X = df[feature_cols]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y,
    )

    proxy_cols = [c for c in PROXY_CANDIDATES if c in X_train.columns]
    proxy_train = X_train[proxy_cols].copy()
    proxy_test = X_test[proxy_cols].copy()

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "proxy_train": proxy_train,
        "proxy_test": proxy_test,
        "feature_names": feature_cols,
    }


def generate_proxy_probes(
    df: pd.DataFrame,
    *,
    n_pairs: int = 100,
    random_state: int = 42,
) -> list[dict[str, Any]]:
    """Generate paired profiles for proxy discrimination testing.

    Since features are anonymised, we probe binary categoricals (A1, A8, A9, A11)
    to detect features that behave like demographic proxies.
    """
    rng = np.random.RandomState(random_state)
    probes: list[dict[str, Any]] = []
    probe_id = 0

    non_proxy_features = [f for f in ALL_FEATURES if f not in PROXY_CANDIDATES]
    sample = df.sample(n=min(n_pairs, len(df)), random_state=random_state)

    for proxy_feature in PROXY_CANDIDATES:
        unique_vals = sorted(df[proxy_feature].dropna().unique())
        if len(unique_vals) < 2:
            continue

        for _, row in sample.head(25).iterrows():
            probe_id += 1
            base = {f: row[f] for f in non_proxy_features if f in row.index}
            # Hold other proxy candidates constant
            for other in PROXY_CANDIDATES:
                if other != proxy_feature:
                    base[other] = row.get(other, 0)

            probes.append({
                "probe_id": f"PROXY-{probe_id:04d}",
                "probe_type": f"proxy_{proxy_feature}",
                "base_profile": base,
                "variants": [
                    {proxy_feature: v, "label": f"{proxy_feature}={v}"}
                    for v in unique_vals[:2]
                ],
                "tolerance": 0.05,
                "metric": "absolute_score_difference",
            })

    return probes


def risk_band(probability: float) -> tuple[str, str]:
    """Map an approval probability to a risk band and recommendation.

    Note: higher probability = more likely to be approved = lower risk.
    """
    if probability >= 0.70:
        return "LOW", "APPROVE"
    elif probability >= 0.45:
        return "MEDIUM", "REFER"
    elif probability >= 0.25:
        return "HIGH", "REVIEW"
    else:
        return "VERY_HIGH", "DENY"
