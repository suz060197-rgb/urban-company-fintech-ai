"""
Create provider-month lagged features for leakage-safe modeling.

The output is designed for next-period modeling: lagged features for month t are
computed only from provider information available before or through prior months.
"""

from __future__ import annotations

import argparse
import os
import sys
import warnings
from typing import List

import numpy as np
import pandas as pd

warnings.filterwarnings(
    "ignore",
    message=".*ChainedAssignmentError: behaviour will change in pandas 3.0.*",
    category=FutureWarning,
)
warnings.filterwarnings(
    "ignore",
    message=".*Series.fillna with 'method' is deprecated.*",
    category=FutureWarning,
)


LAG_FEATURES = [
    "payout_delay_days",
    "working_capital_gap",
    "income_growth_pct",
    "forecast_usage",
    "technology_adoption_score",
    "agentic_intelligence_score",
    "loan_amount",
    "loan_offer_flag",
    "active_provider_month_flag",
    "lock_in_score",
]

REQUIRED_OUTPUT_COLUMNS = [
    "payout_delay_days_lag1",
    "working_capital_gap_lag1",
    "income_growth_pct_lag1",
    "forecast_usage_lag1",
    "technology_adoption_score_lag1",
    "agentic_intelligence_score_lag1",
    "loan_amount_lag1",
    "loan_offer_flag_lag1",
    "active_provider_month_flag_lag1",
    "lock_in_score_lag1",
    "payout_delay_days_lag1_imputed",
    "payout_delay_days_rolling3",
    "working_capital_gap_rolling3",
    "payout_volatility_rolling3",
    "rating_rolling3",
    "cancellation_rate_rolling3",
    "months_since_intervention",
    "pre_treatment_flag",
    "post_treatment_flag",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create provider-month lagged feature table.")
    parser.add_argument("--data_dir", default="data", help="Directory containing generated CSVs.")
    parser.add_argument(
        "--out_path",
        default=os.path.join("data", "model_ready", "provider_month_lagged.csv"),
        help="Output CSV path.",
    )
    return parser.parse_args()


def require_columns(df: pd.DataFrame, name: str, columns: List[str]) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"{name} missing required columns: {missing}")


def bool_to_float(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.astype(float)
    return series.astype(str).str.lower().isin(["true", "1", "yes"]).astype(float)


def load_inputs(data_dir: str):
    merchants = pd.read_csv(os.path.join(data_dir, "merchants.csv"))
    payouts = pd.read_csv(os.path.join(data_dir, "payouts_loans.csv"))
    kpis = pd.read_csv(os.path.join(data_dir, "provider_kpis.csv"))
    transactions = pd.read_csv(os.path.join(data_dir, "transactions.csv"), parse_dates=["timestamp"])

    require_columns(
        merchants,
        "merchants.csv",
        ["merchant_id", "treatment_flag", "treatment_start_month", "intervention_timestamp"],
    )
    require_columns(
        payouts,
        "payouts_loans.csv",
        [
            "merchant_id",
            "month",
            "payout_amount",
            "payout_delay_days",
            "working_capital_gap",
            "loan_amount",
            "loan_offer_flag",
            "active_provider_month_flag",
        ],
    )
    require_columns(
        kpis,
        "provider_kpis.csv",
        [
            "merchant_id",
            "month",
            "income_growth_pct",
            "forecast_usage",
            "technology_adoption_score",
            "agentic_intelligence_score",
            "lock_in_score",
            "post_treatment_flag",
        ],
    )
    require_columns(
        transactions,
        "transactions.csv",
        ["merchant_id", "timestamp", "customer_rating", "cancellation_flag"],
    )
    return merchants, payouts, kpis, transactions


def monthly_transaction_features(transactions: pd.DataFrame) -> pd.DataFrame:
    tx = transactions.copy().assign(
        month=lambda data: data["timestamp"].dt.to_period("M").astype(str),
        cancellation_numeric=lambda data: bool_to_float(data["cancellation_flag"]),
    )
    return (
        tx.groupby(["merchant_id", "month"], as_index=False)
        .agg(
            monthly_rating=("customer_rating", "mean"),
            monthly_cancellation_rate=("cancellation_numeric", "mean"),
        )
        .round({"monthly_rating": 4, "monthly_cancellation_rate": 4})
    )


def add_lagged_features(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.sort_values(["merchant_id", "month"]).copy()
    bool_columns = {}
    for column in [
        "forecast_usage",
        "loan_offer_flag",
        "active_provider_month_flag",
        "post_treatment_flag",
        "treatment_flag",
    ]:
        if column in panel.columns:
            bool_columns[column] = bool_to_float(panel[column])
    if bool_columns:
        panel = panel.assign(**bool_columns)

    lag_columns = {
        f"{column}_lag1": panel.groupby("merchant_id")[column].shift(1)
        for column in LAG_FEATURES
    }
    panel = panel.assign(**lag_columns)

    shifted = panel.groupby("merchant_id")[
        [
            "payout_delay_days",
            "working_capital_gap",
            "payout_amount",
            "monthly_rating",
            "monthly_cancellation_rate",
        ]
    ].shift(1)

    rolling_columns = {
        "payout_delay_days_rolling3": shifted["payout_delay_days"].groupby(panel["merchant_id"]).rolling(3, min_periods=1).mean().reset_index(level=0, drop=True),
        "working_capital_gap_rolling3": shifted["working_capital_gap"].groupby(panel["merchant_id"]).rolling(3, min_periods=1).mean().reset_index(level=0, drop=True),
        "payout_volatility_rolling3": shifted["payout_amount"].groupby(panel["merchant_id"]).rolling(3, min_periods=2).std().reset_index(level=0, drop=True),
        "rating_rolling3": shifted["monthly_rating"].groupby(panel["merchant_id"]).rolling(3, min_periods=1).mean().reset_index(level=0, drop=True),
        "cancellation_rate_rolling3": shifted["monthly_cancellation_rate"].groupby(panel["merchant_id"]).rolling(3, min_periods=1).mean().reset_index(level=0, drop=True),
    }
    panel = panel.assign(**rolling_columns)
    panel = panel.assign(
        payout_volatility_rolling3=panel["payout_volatility_rolling3"].fillna(0.0),
        payout_delay_days_lag1_imputed=panel["payout_delay_days_lag1"].fillna(panel["payout_delay_days_rolling3"]).fillna(0.0),
    )
    return panel


def add_intervention_features(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.copy()
    panel = panel.copy()
    month_period = pd.PeriodIndex(panel["month"], freq="M")
    first_period = month_period.min()
    start_month = panel["treatment_start_month"].fillna(0).astype(int)
    month_number = (month_period.year - first_period.year) * 12 + month_period.month - first_period.month + 1
    months_since = np.where(
        start_month > 0,
        month_number - start_month + 1,
        np.nan,
    )
    panel = panel.assign(
        months_since_intervention=months_since,
        pre_treatment_flag=((panel["treatment_flag"] == 1.0) & (months_since < 0)).astype(bool),
        post_treatment_flag=((panel["treatment_flag"] == 1.0) & (months_since >= 0)).astype(bool),
    )
    return panel


def validate_output(panel: pd.DataFrame) -> None:
    missing = [column for column in REQUIRED_OUTPUT_COLUMNS if column not in panel.columns]
    if missing:
        raise ValueError(f"Output missing required lagged columns: {missing}")

    duplicate_rows = int(panel.duplicated(["merchant_id", "month"]).sum())
    if duplicate_rows:
        raise ValueError(f"Output has duplicate merchant-month rows: {duplicate_rows}")

    first_month = panel["month"].min()
    non_first = panel[panel["month"] != first_month]
    critical = [
        "payout_delay_days_lag1_imputed",
        "working_capital_gap_lag1",
        "income_growth_pct_lag1",
        "forecast_usage_lag1",
        "technology_adoption_score_lag1",
        "agentic_intelligence_score_lag1",
        "loan_amount_lag1",
        "loan_offer_flag_lag1",
        "active_provider_month_flag_lag1",
        "lock_in_score_lag1",
    ]
    bad = {
        column: int(non_first[column].isna().sum())
        for column in critical
        if int(non_first[column].isna().sum()) > 0
    }
    if bad:
        raise ValueError(f"Lag1 features have missing values after first panel month: {bad}")

    active_lag_missing = non_first[
        (non_first["active_provider_month_flag_lag1"] == 1.0) & (non_first["payout_delay_days_lag1"].isna())
    ]
    if len(active_lag_missing):
        raise ValueError("payout_delay_days_lag1 is missing after active prior provider-months.")


def main() -> int:
    args = parse_args()
    try:
        merchants, payouts, kpis, transactions = load_inputs(args.data_dir)
        tx_monthly = monthly_transaction_features(transactions)
        panel = kpis.merge(payouts, on=["merchant_id", "month"], how="left")
        panel = panel.merge(merchants, on="merchant_id", how="left", suffixes=("", "_merchant"))
        panel = panel.merge(tx_monthly, on=["merchant_id", "month"], how="left")
        panel = panel.sort_values(["merchant_id", "month"]).copy()
        panel = panel.assign(
            monthly_rating=panel.groupby("merchant_id")["monthly_rating"].ffill().fillna(0.0),
            monthly_cancellation_rate=panel["monthly_cancellation_rate"].fillna(0.0),
        )
        panel = add_lagged_features(panel)
        panel = add_intervention_features(panel)
        validate_output(panel)

        os.makedirs(os.path.dirname(args.out_path), exist_ok=True)
        panel.to_csv(args.out_path, index=False)
        print(f"Saved lagged provider-month features to {os.path.abspath(args.out_path)}")
        print(f"Rows: {len(panel):,}")
        print(f"Columns: {len(panel.columns):,}")
        print("Required lagged/intervention columns: PASS")
        return 0
    except Exception as exc:
        print(f"Lagged feature generation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
