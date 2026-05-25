"""
Retrain only weak models with lagged, engineered, and primary-informed features.

Models retrained:
- loan_default_prediction
- embedded_finance_adoption

Churn and income models are intentionally not retrained.
"""

from __future__ import annotations

import argparse
import os
import pickle
from typing import Dict, List

import numpy as np
import pandas as pd

from retrain_weak_models import (
    CATEGORICAL_FEATURES,
    LAGGED_NUMERIC_FEATURES,
    before_after,
    prepare_frame,
    train_model,
)


ENGINEERED_FEATURES = [
    "primary_digital_adoption_prior",
    "primary_cashflow_stress_prior",
    "primary_settlement_pain_prior",
    "primary_faster_payout_prior",
    "primary_credit_need_prior",
    "primary_credit_amount_prior",
    "primary_growth_prior",
    "primary_repeat_customer_prior",
    "primary_ai_usage_prior",
    "primary_upi_frequency_prior",
    "settlement_credit_stress",
    "digital_growth_index",
    "credit_dependency_score",
    "repayment_pressure_index",
    "digital_finance_readiness",
    "lockin_resilience_score",
    "agentic_productivity_signal",
    "cash_to_digital_transition_score",
    "credit_offer_mismatch",
    "payout_pain_gap",
]


PRIMARY_PRIOR_COLUMNS = {
    "digital_adoption_score_scaled": "primary_digital_adoption_prior",
    "cashflow_issues_scaled": "primary_cashflow_stress_prior",
    "settlement_delay_impact_scaled": "primary_settlement_pain_prior",
    "faster_payout_impact_scaled": "primary_faster_payout_prior",
    "needed_business_credit_binary": "primary_credit_need_prior",
    "approx_credit_amount_numeric_scaled": "primary_credit_amount_prior",
    "business_growth_after_digital_scaled": "primary_growth_prior",
    "repeat_customer_change_scaled": "primary_repeat_customer_prior",
    "ai_tool_usage_binary": "primary_ai_usage_prior",
    "upi_usage_frequency_scaled": "primary_upi_frequency_prior",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Retrain weak models with engineered features.")
    parser.add_argument("--data_path", default=os.path.join("data", "model_ready", "provider_month_future_targets.csv"))
    parser.add_argument("--primary_path", default=os.path.join("data", "primary_responses_clean.csv"))
    parser.add_argument("--old_metrics", default=os.path.join("output", "models", "model_metrics.csv"))
    parser.add_argument("--out_dir", default=os.path.join("output", "models_retrained_engineered"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--test_frac", type=float, default=0.25)
    parser.add_argument("--epochs", type=int, default=1200)
    parser.add_argument("--lr", type=float, default=0.035)
    return parser.parse_args()


def scale_01(series: pd.Series, q_low: float = 0.05, q_high: float = 0.95) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    lo = values.quantile(q_low)
    hi = values.quantile(q_high)
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        return pd.Series(np.zeros(len(values)), index=values.index, dtype=float)
    return ((values - lo) / (hi - lo)).clip(0, 1).fillna(0.0)


def bool_float(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.astype(float)
    return series.astype(str).str.lower().isin(["true", "1", "yes"]).astype(float)


def prepare_primary_priors(primary_path: str) -> tuple[pd.DataFrame, Dict[str, float]]:
    primary = pd.read_csv(primary_path)
    primary = primary.assign(
        approx_credit_amount_numeric_scaled=scale_01(primary["approx_credit_amount_numeric"])
    )

    global_priors = {
        output_col: float(pd.to_numeric(primary[input_col], errors="coerce").mean())
        for input_col, output_col in PRIMARY_PRIOR_COLUMNS.items()
    }

    group_cols = ["business_type", "region"]
    priors = (
        primary.groupby(group_cols, dropna=False)[list(PRIMARY_PRIOR_COLUMNS.keys())]
        .mean()
        .reset_index()
        .rename(columns=PRIMARY_PRIOR_COLUMNS)
    )
    return priors, global_priors


def add_primary_priors(frame: pd.DataFrame, primary_path: str) -> pd.DataFrame:
    priors, global_priors = prepare_primary_priors(primary_path)
    enhanced = frame.merge(
        priors,
        left_on=["category", "region"],
        right_on=["business_type", "region"],
        how="left",
    ).drop(columns=["business_type"], errors="ignore")

    filled = {
        column: pd.to_numeric(enhanced[column], errors="coerce").fillna(fill_value)
        for column, fill_value in global_priors.items()
    }
    enhanced = enhanced.assign(**filled)
    return enhanced


def add_engineered_features(frame: pd.DataFrame) -> pd.DataFrame:
    enhanced = frame.copy()
    payout_delay_scaled = scale_01(enhanced["payout_delay_days_lag1_imputed"])
    working_gap_scaled = scale_01(enhanced["working_capital_gap_lag1"])
    loan_amount_scaled = scale_01(enhanced["loan_amount_lag1"])
    income_growth_scaled = scale_01(enhanced["income_growth_pct_lag1"])
    cash_dependency = (bool_float(enhanced.get("agent_usage_flag", pd.Series(False, index=enhanced.index))) * 0) + 1

    settlement_credit_stress = (
        0.35 * payout_delay_scaled
        + 0.30 * working_gap_scaled
        + 0.20 * enhanced["primary_cashflow_stress_prior"]
        + 0.15 * enhanced["primary_credit_need_prior"]
    ).clip(0, 1)
    digital_growth_index = (
        0.30 * pd.to_numeric(enhanced["digital_tool_usage"], errors="coerce").fillna(0)
        + 0.25 * pd.to_numeric(enhanced["payment_success_rate"], errors="coerce").fillna(0)
        + 0.25 * pd.to_numeric(enhanced["technology_adoption_score_lag1"], errors="coerce").fillna(0)
        + 0.20 * enhanced["primary_growth_prior"]
    ).clip(0, 1)
    credit_dependency_score = (
        0.35 * enhanced["primary_credit_need_prior"]
        + 0.30 * enhanced["primary_credit_amount_prior"]
        + 0.25 * working_gap_scaled
        + 0.10 * loan_amount_scaled
    ).clip(0, 1)
    repayment_pressure_index = (
        0.40 * working_gap_scaled
        + 0.30 * loan_amount_scaled
        + 0.20 * payout_delay_scaled
        - 0.10 * income_growth_scaled
    ).clip(0, 1)
    digital_finance_readiness = (
        0.25 * pd.to_numeric(enhanced["payment_success_rate"], errors="coerce").fillna(0)
        + 0.20 * pd.to_numeric(enhanced["digital_tool_usage"], errors="coerce").fillna(0)
        + 0.20 * bool_float(enhanced["kyc_flag"])
        + 0.20 * enhanced["primary_upi_frequency_prior"]
        + 0.15 * enhanced["primary_ai_usage_prior"]
    ).clip(0, 1)
    lockin_resilience_score = (
        0.30 * pd.to_numeric(enhanced["lock_in_score_lag1"], errors="coerce").fillna(0)
        + 0.25 * enhanced["primary_repeat_customer_prior"]
        + 0.20 * pd.to_numeric(enhanced["active_provider_month_flag_lag1"], errors="coerce").fillna(0)
        + 0.15 * pd.to_numeric(enhanced["digital_tool_usage"], errors="coerce").fillna(0)
        + 0.10 * pd.to_numeric(enhanced["payment_success_rate"], errors="coerce").fillna(0)
    ).clip(0, 1)
    agentic_productivity_signal = (
        0.25 * enhanced["primary_ai_usage_prior"]
        + 0.25 * pd.to_numeric(enhanced["forecast_usage_lag1"], errors="coerce").fillna(0)
        + 0.25 * pd.to_numeric(enhanced["agentic_intelligence_score_lag1"], errors="coerce").fillna(0)
        + 0.25 * enhanced["primary_growth_prior"]
    ).clip(0, 1)
    cash_to_digital_transition_score = (
        0.35 * enhanced["primary_upi_frequency_prior"]
        + 0.35 * enhanced["primary_digital_adoption_prior"]
        + 0.20 * pd.to_numeric(enhanced["payment_success_rate"], errors="coerce").fillna(0)
        - 0.10 * cash_dependency
    ).clip(0, 1)
    credit_offer_mismatch = (
        enhanced["primary_credit_need_prior"] - pd.to_numeric(enhanced["loan_offer_flag_lag1"], errors="coerce").fillna(0)
    ).clip(0, 1)
    payout_pain_gap = (enhanced["primary_settlement_pain_prior"] - payout_delay_scaled).clip(0, 1)
    enhanced = enhanced.assign(
        settlement_credit_stress=settlement_credit_stress,
        digital_growth_index=digital_growth_index,
        credit_dependency_score=credit_dependency_score,
        repayment_pressure_index=repayment_pressure_index,
        digital_finance_readiness=digital_finance_readiness,
        lockin_resilience_score=lockin_resilience_score,
        agentic_productivity_signal=agentic_productivity_signal,
        cash_to_digital_transition_score=cash_to_digital_transition_score,
        credit_offer_mismatch=credit_offer_mismatch,
        payout_pain_gap=payout_pain_gap,
    )
    return enhanced


def write_feature_summary(frame: pd.DataFrame, out_dir: str) -> None:
    summary = frame[ENGINEERED_FEATURES].describe().T.round(4)
    summary.to_csv(os.path.join(out_dir, "engineered_feature_summary.csv"))


def run(args: argparse.Namespace) -> int:
    os.makedirs(args.out_dir, exist_ok=True)
    frame = prepare_frame(args.data_path)
    frame = add_primary_priors(frame, args.primary_path)
    frame = add_engineered_features(frame)
    write_feature_summary(frame, args.out_dir)

    features = LAGGED_NUMERIC_FEATURES + ENGINEERED_FEATURES + ["month_index"] + CATEGORICAL_FEATURES

    loan_frame = frame[frame["active_provider_month_flag_lag1"] == 1].copy()
    loan_artifact, loan_importance = train_model(
        "loan_default_prediction",
        loan_frame,
        "default_next_cycle",
        features,
        args,
        seed_offset=20,
    )
    adoption_artifact, adoption_importance = train_model(
        "embedded_finance_adoption",
        frame,
        "adoption_state_tplus1",
        features,
        args,
        seed_offset=30,
    )

    artifacts = {
        "loan_default_prediction": loan_artifact,
        "embedded_finance_adoption": adoption_artifact,
    }
    importances = {
        "loan_default_prediction": loan_importance,
        "embedded_finance_adoption": adoption_importance,
    }

    for model_name, artifact in artifacts.items():
        with open(os.path.join(args.out_dir, f"{model_name}.pkl"), "wb") as handle:
            pickle.dump(artifact, handle)
        importances[model_name].to_csv(os.path.join(args.out_dir, f"{model_name}_feature_importance.csv"), index=False)

    comparison = before_after(args.old_metrics, {name: artifact["metrics"] for name, artifact in artifacts.items()})
    comparison.to_csv(os.path.join(args.out_dir, "before_after_model_metrics.csv"), index=False)
    comparison.to_csv(os.path.join("output", "before_after_model_metrics.csv"), index=False)

    print(f"Saved engineered weak-model artifacts to {os.path.abspath(args.out_dir)}")
    print(f"Saved before/after metrics to {os.path.abspath(os.path.join(args.out_dir, 'before_after_model_metrics.csv'))}")
    for model_name, artifact in artifacts.items():
        print(f"\n{model_name}")
        for metric, value in artifact["metrics"].items():
            print(f"  {metric}: {value}")
        print("  top features:", ", ".join(importances[model_name]["feature"].head(8).tolist()))
    return 0


def main() -> int:
    return run(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
