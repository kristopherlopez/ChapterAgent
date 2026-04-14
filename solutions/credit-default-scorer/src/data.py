"""Data loading and preparation for the Taiwan Credit Card Default dataset."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


# Feature groups as defined in the dataset specification
DEMOGRAPHIC_FEATURES = ["SEX", "EDUCATION", "MARRIAGE", "AGE"]
CREDIT_FEATURES = ["LIMIT_BAL"]
PAYMENT_HISTORY_FEATURES = [f"PAY_{i}" for i in [0, 2, 3, 4, 5, 6]]
BILL_AMOUNT_FEATURES = [f"BILL_AMT{i}" for i in range(1, 7)]
PAYMENT_AMOUNT_FEATURES = [f"PAY_AMT{i}" for i in range(1, 7)]

PROTECTED_ATTRIBUTES = ["SEX", "EDUCATION", "MARRIAGE", "AGE"]

# Engineered feature groups — derived from raw bill/payment data
UNPAID_BALANCE_FEATURES = [f"UNPAID_BAL{i}" for i in range(1, 7)]
UTILISATION_FEATURES = [f"UTIL_RATIO{i}" for i in range(1, 7)]
PAYMENT_RATIO_FEATURES = [f"PAY_RATIO{i}" for i in range(1, 7)]
BALANCE_TREND_FEATURES = ["BAL_TREND", "AVG_UTIL"]

ENGINEERED_FEATURES = (
    UNPAID_BALANCE_FEATURES
    + UTILISATION_FEATURES
    + PAYMENT_RATIO_FEATURES
    + BALANCE_TREND_FEATURES
)

ALL_FEATURES = (
    CREDIT_FEATURES
    + DEMOGRAPHIC_FEATURES
    + PAYMENT_HISTORY_FEATURES
    + BILL_AMOUNT_FEATURES
    + PAYMENT_AMOUNT_FEATURES
)

TARGET = "default_payment_next_month"


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create derived features from raw bill and payment data.

    Adds:
        UNPAID_BAL{1-6}: bill minus payment — outstanding debt each month
        UTIL_RATIO{1-6}: bill / credit limit — credit utilisation per month
        PAY_RATIO{1-6}: payment / bill — fraction of bill paid (capped at 1.0)
        BAL_TREND: slope of unpaid balance over 6 months (positive = growing debt)
        AVG_UTIL: mean utilisation across 6 months
    """
    df = df.copy()

    for i in range(1, 7):
        bill_col = f"BILL_AMT{i}"
        pay_col = f"PAY_AMT{i}"

        if bill_col not in df.columns or pay_col not in df.columns:
            continue

        # Unpaid balance: how much is left after payment
        df[f"UNPAID_BAL{i}"] = df[bill_col] - df[pay_col]

        # Utilisation ratio: bill / credit limit (0 if no limit)
        if "LIMIT_BAL" in df.columns:
            df[f"UTIL_RATIO{i}"] = np.where(
                df["LIMIT_BAL"] > 0,
                df[bill_col] / df["LIMIT_BAL"],
                0.0,
            )

        # Payment ratio: payment / bill, capped at 1.0 (0 if no bill)
        df[f"PAY_RATIO{i}"] = np.where(
            df[bill_col] > 0,
            np.minimum(df[pay_col] / df[bill_col], 1.0),
            0.0,
        )

    # Balance trend: slope of unpaid balances (positive = debt growing)
    unpaid_cols = [f"UNPAID_BAL{i}" for i in range(1, 7) if f"UNPAID_BAL{i}" in df.columns]
    if len(unpaid_cols) == 6:
        # Linear slope across 6 months (month 1 = most recent)
        x = np.arange(6, dtype=float)
        x_centered = x - x.mean()
        unpaid_matrix = df[unpaid_cols].values
        df["BAL_TREND"] = (unpaid_matrix * x_centered).sum(axis=1) / (x_centered ** 2).sum()

    # Average utilisation across 6 months
    util_cols = [f"UTIL_RATIO{i}" for i in range(1, 7) if f"UTIL_RATIO{i}" in df.columns]
    if util_cols:
        df["AVG_UTIL"] = df[util_cols].mean(axis=1)

    return df


def load_dataset(path: str | Path) -> pd.DataFrame:
    """Load the Taiwan Credit Card Default dataset from CSV or Excel.

    Accepts the UCI dataset in CSV or XLS format. Normalises column names
    and drops the ID column if present.
    """
    path = Path(path)
    if path.suffix in (".xls", ".xlsx"):
        df = pd.read_excel(path, header=1)
    else:
        df = pd.read_csv(path)

    # Normalise: the UCI dataset sometimes ships with 'ID' or 'id'
    if "ID" in df.columns:
        df = df.drop(columns=["ID"])
    if "id" in df.columns:
        df = df.drop(columns=["id"])

    # Rename PAY_0 alias — older versions of the dataset use 'PAY_0', some use 'PAY_1'
    if "PAY_1" in df.columns and "PAY_0" not in df.columns:
        df = df.rename(columns={"PAY_1": "PAY_0"})

    # Rename target — the dataset ships with various column name formats
    target_aliases = [
        "default.payment.next.month",
        "default.payment",
        "default payment next month",
    ]
    for alias in target_aliases:
        if alias in df.columns and alias != TARGET:
            df = df.rename(columns={alias: TARGET})

    # Create engineered features from raw data
    df = engineer_features(df)

    return df


def prepare_splits(
    df: pd.DataFrame,
    *,
    test_size: float = 0.3,
    random_state: int = 42,
) -> dict[str, Any]:
    """Split into train/test and separate features, target, and protected attributes.

    Returns a dict with keys:
        X_train, X_test, y_train, y_test,
        protected_train, protected_test,
        feature_names
    """
    feature_cols = [c for c in ALL_FEATURES + ENGINEERED_FEATURES if c in df.columns]
    X = df[feature_cols]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y,
    )

    protected_train = X_train[PROTECTED_ATTRIBUTES].copy()
    protected_test = X_test[PROTECTED_ATTRIBUTES].copy()

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "protected_train": protected_train,
        "protected_test": protected_test,
        "feature_names": feature_cols,
    }


def generate_discrimination_probes(
    df: pd.DataFrame,
    *,
    n_pairs: int = 200,
    random_state: int = 42,
) -> list[dict[str, Any]]:
    """Generate paired profiles for discrimination testing.

    For each protected attribute, creates profile pairs that are identical
    in all credit-behaviour features but differ in the protected attribute.
    """
    rng = np.random.RandomState(random_state)
    probes: list[dict[str, Any]] = []
    probe_id = 0

    behaviour_features = (
        CREDIT_FEATURES + PAYMENT_HISTORY_FEATURES
        + BILL_AMOUNT_FEATURES + PAYMENT_AMOUNT_FEATURES
    )

    sample = df.sample(n=min(n_pairs, len(df)), random_state=random_state)

    # Gender probes
    for _, row in sample.iterrows():
        probe_id += 1
        base = {f: row[f] for f in behaviour_features if f in row.index}
        base.update({"EDUCATION": row.get("EDUCATION", 2), "MARRIAGE": row.get("MARRIAGE", 1), "AGE": row.get("AGE", 35)})
        probes.append({
            "probe_id": f"DISC-{probe_id:04d}",
            "probe_type": "gender",
            "base_profile": base,
            "variants": [
                {"SEX": 1, "label": "male"},
                {"SEX": 2, "label": "female"},
            ],
            "tolerance": 0.02,
            "metric": "absolute_score_difference",
        })

    # Age band probes
    age_bands = [(21, 30), (31, 40), (41, 50), (51, 79)]
    for _, row in sample.head(50).iterrows():
        probe_id += 1
        base = {f: row[f] for f in behaviour_features if f in row.index}
        base.update({"SEX": row.get("SEX", 1), "EDUCATION": row.get("EDUCATION", 2), "MARRIAGE": row.get("MARRIAGE", 1)})
        probes.append({
            "probe_id": f"DISC-{probe_id:04d}",
            "probe_type": "age",
            "base_profile": base,
            "variants": [
                {"AGE": rng.randint(lo, hi + 1), "label": f"age_{lo}_{hi}"}
                for lo, hi in age_bands
            ],
            "tolerance": 0.02,
            "metric": "absolute_score_difference",
        })

    return probes


def risk_band(probability: float) -> tuple[str, str]:
    """Map a default probability to a risk band and recommendation."""
    if probability < 0.10:
        return "LOW", "No action"
    elif probability < 0.30:
        return "MEDIUM", "MONITOR"
    elif probability < 0.60:
        return "HIGH", "Proactive outreach"
    else:
        return "VERY_HIGH", "Immediate intervention"
