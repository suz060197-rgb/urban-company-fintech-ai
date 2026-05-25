"""
Integrate primary survey priors into provider-level synthetic features.

The output is a provider-level enrichment table for dissertation analysis and
Power BI use. It does not train or retrain any model.
"""

from __future__ import annotations

import argparse
import warnings
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

warnings.filterwarnings(
    "ignore",
    message=".*ChainedAssignmentError: behaviour will change in pandas 3.0.*",
    category=FutureWarning,
)


SURVEY_FEATURES = [
    "digital_adoption_score_scaled",
    "cashflow_issues_scaled",
    "settlement_delay_impact_scaled",
    "needed_business_credit_binary",
    "business_growth_after_digital_scaled",
    "repeat_customer_change_scaled",
    "ai_tool_usage_binary",
    "faster_payout_impact_scaled",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create primary-informed provider features.")
    parser.add_argument("--survey", default="data/primary_responses_clean.csv")
    parser.add_argument("--synthetic_dir", default="data_v2")
    parser.add_argument("--output", default="data/provider_features_enriched.csv")
    parser.add_argument("--report", default="docs/primary_integration_report.md")
    return parser.parse_args()


def bool_mean(series: pd.Series) -> float:
    if series.dtype == bool:
        return float(series.mean())
    return float(series.astype(str).str.lower().isin(["true", "1", "yes"]).mean())


def scale_01(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    low = values.quantile(0.05)
    high = values.quantile(0.95)
    if pd.isna(low) or pd.isna(high) or high == low:
        return pd.Series(np.zeros(len(values)), index=values.index, dtype=float)
    return ((values - low) / (high - low)).clip(0, 1)


def load_inputs(args: argparse.Namespace):
    survey = pd.read_csv(args.survey)
    base = Path(args.synthetic_dir)
    merchants = pd.read_csv(base / "merchants.csv")
    kpis = pd.read_csv(base / "provider_kpis.csv")
    payouts = pd.read_csv(base / "payouts_loans.csv")
    tx = pd.read_csv(base / "transactions.csv", usecols=["merchant_id", "timestamp", "payment_method", "settlement_delay", "service_completion_rate", "cancellation_flag"])
    return survey, merchants, kpis, payouts, tx


def survey_priors(survey: pd.DataFrame) -> pd.DataFrame:
    required = ["business_type", "region"] + SURVEY_FEATURES
    missing = [column for column in required if column not in survey.columns]
    if missing:
        raise ValueError(f"Survey file missing required columns: {missing}")

    survey_numeric = survey.copy()
    for column in SURVEY_FEATURES:
        survey_numeric.loc[:, column] = pd.to_numeric(survey_numeric[column], errors="coerce")

    grouped = (
        survey_numeric.groupby(["business_type", "region"], dropna=False)
        .agg(
            survey_response_count=("respondent_id", "size"),
            survey_digital_adoption_prior=("digital_adoption_score_scaled", "mean"),
            survey_cashflow_stress_prior=("cashflow_issues_scaled", "mean"),
            survey_settlement_pain_prior=("settlement_delay_impact_scaled", "mean"),
            survey_credit_need_prior=("needed_business_credit_binary", "mean"),
            survey_business_growth_prior=("business_growth_after_digital_scaled", "mean"),
            survey_repeat_customer_prior=("repeat_customer_change_scaled", "mean"),
            survey_ai_usage_prior=("ai_tool_usage_binary", "mean"),
            survey_faster_payout_value_prior=("faster_payout_impact_scaled", "mean"),
            survey_income_midpoint=("monthly_income_midpoint", "mean"),
            survey_transaction_estimate=("monthly_transaction_estimate", "mean"),
        )
        .reset_index()
    )

    overall = pd.DataFrame(
        [
            {
                "business_type": "__overall__",
                "region": "__overall__",
                "survey_response_count": len(survey_numeric),
                "survey_digital_adoption_prior": survey_numeric["digital_adoption_score_scaled"].mean(),
                "survey_cashflow_stress_prior": survey_numeric["cashflow_issues_scaled"].mean(),
                "survey_settlement_pain_prior": survey_numeric["settlement_delay_impact_scaled"].mean(),
                "survey_credit_need_prior": survey_numeric["needed_business_credit_binary"].mean(),
                "survey_business_growth_prior": survey_numeric["business_growth_after_digital_scaled"].mean(),
                "survey_repeat_customer_prior": survey_numeric["repeat_customer_change_scaled"].mean(),
                "survey_ai_usage_prior": survey_numeric["ai_tool_usage_binary"].mean(),
                "survey_faster_payout_value_prior": survey_numeric["faster_payout_impact_scaled"].mean(),
                "survey_income_midpoint": survey_numeric["monthly_income_midpoint"].mean(),
                "survey_transaction_estimate": survey_numeric["monthly_transaction_estimate"].mean(),
            }
        ]
    )
    return pd.concat([grouped, overall], ignore_index=True)


def provider_summaries(merchants: pd.DataFrame, kpis: pd.DataFrame, payouts: pd.DataFrame, tx: pd.DataFrame) -> pd.DataFrame:
    kpi_summary = (
        kpis.groupby("merchant_id", as_index=False)
        .agg(
            avg_income_growth_pct=("income_growth_pct", "mean"),
            latest_income_growth_pct=("income_growth_pct", "last"),
            avg_monthly_profit=("monthly_profit", "mean"),
            avg_churn_probability=("churn_probability", "mean"),
            avg_retention_rate=("retention_flag", bool_mean),
            avg_post_treatment_rate=("post_treatment_flag", bool_mean),
            avg_lock_in_score=("lock_in_score", "mean"),
            latest_lock_in_score=("lock_in_score", "last"),
            avg_technology_adoption_score=("technology_adoption_score", "mean"),
            latest_technology_adoption_score=("technology_adoption_score", "last"),
            avg_advancement_score=("advancement_score", "mean"),
            latest_advancement_score=("advancement_score", "last"),
            avg_agentic_intelligence_score=("agentic_intelligence_score", "mean"),
            latest_agentic_intelligence_score=("agentic_intelligence_score", "last"),
            forecast_usage_rate=("forecast_usage", bool_mean),
        )
    )

    payout_summary = (
        payouts.groupby("merchant_id", as_index=False)
        .agg(
            avg_payout_amount=("payout_amount", "mean"),
            latest_payout_amount=("payout_amount", "last"),
            avg_payout_delay_days=("payout_delay_days", "mean"),
            latest_payout_delay_days=("payout_delay_days", "last"),
            active_provider_month_rate=("active_provider_month_flag", bool_mean),
            loan_offer_rate=("loan_offer_flag", bool_mean),
            avg_loan_amount=("loan_amount", "mean"),
            max_loan_amount=("loan_amount", "max"),
            avg_working_capital_gap=("working_capital_gap", "mean"),
            latest_working_capital_gap=("working_capital_gap", "last"),
            avg_loan_disbursal_time=("loan_disbursal_time", "mean"),
            default_rate=("default_flag", bool_mean),
        )
    )

    tx = tx.copy()
    tx.loc[:, "cancellation_numeric"] = tx["cancellation_flag"].astype(str).str.lower().isin(["true", "1", "yes"]).astype(float)
    tx_summary = (
        tx.groupby("merchant_id", as_index=False)
        .agg(
            transaction_count=("timestamp", "size"),
            upi_share=("payment_method", lambda s: float(s.astype(str).eq("UPI").mean())),
            cash_share=("payment_method", lambda s: float(s.astype(str).eq("cash").mean())),
            avg_settlement_delay=("settlement_delay", "mean"),
            avg_service_completion_rate=("service_completion_rate", "mean"),
            avg_cancellation_rate=("cancellation_numeric", "mean"),
        )
    )

    return (
        merchants.rename(columns={"category": "business_type"})
        .merge(kpi_summary, on="merchant_id", how="left")
        .merge(payout_summary, on="merchant_id", how="left")
        .merge(tx_summary, on="merchant_id", how="left")
    )


def attach_priors(provider: pd.DataFrame, priors: pd.DataFrame) -> pd.DataFrame:
    exact = priors[priors["business_type"].ne("__overall__")].copy()
    overall = priors[priors["business_type"].eq("__overall__")].iloc[0].to_dict()
    merged = provider.merge(exact, on=["business_type", "region"], how="left")

    prior_columns = [column for column in priors.columns if column.startswith("survey_")]
    for column in prior_columns:
        merged.loc[:, column] = pd.to_numeric(merged[column], errors="coerce").fillna(overall[column])

    matched_keys = set(zip(exact["business_type"], exact["region"]))
    provider_keys = list(zip(provider["business_type"], provider["region"]))
    merged.loc[:, "primary_match_level"] = [
        "business_type_region" if key in matched_keys else "overall_prior" for key in provider_keys
    ]
    return merged


def create_blended_features(provider: pd.DataFrame) -> pd.DataFrame:
    frame = provider.copy()
    payout_gap_scaled = scale_01(frame["avg_working_capital_gap"])
    payout_delay_scaled = scale_01(frame["avg_payout_delay_days"])
    loan_amount_scaled = scale_01(frame["avg_loan_amount"])
    churn_scaled = scale_01(frame["avg_churn_probability"])
    settlement_scaled = scale_01(frame["avg_settlement_delay"])

    frame.loc[:, "technology_adoption_score_blended"] = (
        0.70 * frame["avg_technology_adoption_score"] + 0.30 * frame["survey_digital_adoption_prior"]
    ).clip(0, 1)
    frame.loc[:, "working_capital_gap_blended"] = (
        0.70 * payout_gap_scaled + 0.30 * frame["survey_cashflow_stress_prior"]
    ).clip(0, 1)
    frame.loc[:, "payout_delay_days_blended"] = (
        0.70 * payout_delay_scaled + 0.30 * frame["survey_settlement_pain_prior"]
    ).clip(0, 1)
    frame.loc[:, "loan_uptake_propensity_blended"] = (
        0.45 * frame["loan_offer_rate"]
        + 0.35 * frame["survey_credit_need_prior"]
        + 0.20 * loan_amount_scaled
    ).clip(0, 1)
    frame.loc[:, "advancement_score_blended"] = (
        0.70 * frame["avg_advancement_score"] + 0.30 * frame["survey_business_growth_prior"]
    ).clip(0, 1)
    frame.loc[:, "lock_in_score_blended"] = (
        0.65 * frame["avg_lock_in_score"]
        + 0.25 * frame["survey_repeat_customer_prior"]
        + 0.10 * (1 - churn_scaled)
    ).clip(0, 1)
    frame.loc[:, "agentic_intelligence_score_blended"] = (
        0.70 * frame["avg_agentic_intelligence_score"] + 0.30 * frame["survey_ai_usage_prior"]
    ).clip(0, 1)
    frame.loc[:, "settlement_credit_stress"] = (
        0.40 * frame["working_capital_gap_blended"]
        + 0.35 * frame["payout_delay_days_blended"]
        + 0.25 * frame["survey_faster_payout_value_prior"]
    ).clip(0, 1)
    frame.loc[:, "digital_growth_index"] = (
        0.40 * frame["technology_adoption_score_blended"]
        + 0.30 * frame["advancement_score_blended"]
        + 0.20 * frame["upi_share"]
        + 0.10 * frame["agentic_intelligence_score_blended"]
    ).clip(0, 1)
    frame.loc[:, "credit_dependency_score_primary_informed"] = (
        0.35 * frame["loan_uptake_propensity_blended"]
        + 0.30 * frame["working_capital_gap_blended"]
        + 0.20 * frame["survey_credit_need_prior"]
        + 0.15 * frame["default_rate"]
    ).clip(0, 1)
    frame.loc[:, "settlement_experience_index"] = (
        1 - (0.55 * settlement_scaled + 0.45 * frame["survey_settlement_pain_prior"])
    ).clip(0, 1)
    return frame


def md_table(frame: pd.DataFrame, columns: List[str], n: int | None = None) -> str:
    table = frame[columns].head(n).copy() if n else frame[columns].copy()
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in table.iterrows():
        values = []
        for column in columns:
            value = row[column]
            if isinstance(value, float):
                values.append("" if pd.isna(value) else f"{value:.4f}")
            else:
                values.append(str(value).replace("|", "\\|"))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(output: pd.DataFrame, priors: pd.DataFrame, path: Path, output_path: str) -> None:
    match_counts = output["primary_match_level"].value_counts().reset_index()
    match_counts.columns = ["primary_match_level", "providers"]
    feature_summary = output[
        [
            "technology_adoption_score_blended",
            "working_capital_gap_blended",
            "payout_delay_days_blended",
            "loan_uptake_propensity_blended",
            "settlement_credit_stress",
            "digital_growth_index",
            "credit_dependency_score_primary_informed",
        ]
    ].describe().round(4).reset_index().rename(columns={"index": "statistic"})
    prior_display = priors[priors["business_type"].ne("__overall__")].copy()

    lines = [
        "# Primary Integration Report",
        "",
        "Primary survey responses were mapped into provider-level synthetic features using segment-level priors.",
        "",
        "No models were retrained.",
        "",
        "## Output",
        "",
        f"- File: `{output_path}`",
        f"- Provider rows: `{len(output):,}`",
        "",
        "## Variable Mapping",
        "",
        "| Survey variable | Synthetic/provider feature target | Blended output |",
        "|---|---|---|",
        "| `digital_adoption_score_scaled` | `technology_adoption_score` | `technology_adoption_score_blended` |",
        "| `cashflow_issues_scaled` | `working_capital_gap` | `working_capital_gap_blended`, `settlement_credit_stress` |",
        "| `settlement_delay_impact_scaled` | `payout_delay_days`, `settlement_delay` | `payout_delay_days_blended`, `settlement_experience_index` |",
        "| `needed_business_credit_binary` | loan offer and uptake behavior | `loan_uptake_propensity_blended`, `credit_dependency_score_primary_informed` |",
        "| `business_growth_after_digital_scaled` | `advancement_score`, income growth | `advancement_score_blended`, `digital_growth_index` |",
        "| `repeat_customer_change_scaled` | `lock_in_score`, repeat customers | `lock_in_score_blended` |",
        "| `ai_tool_usage_binary` | `agentic_intelligence_score`, forecast usage | `agentic_intelligence_score_blended` |",
        "",
        "## Match Quality",
        "",
        md_table(match_counts, ["primary_match_level", "providers"]),
        "",
        "## Survey Priors By Segment",
        "",
        md_table(
            prior_display,
            [
                "business_type",
                "region",
                "survey_response_count",
                "survey_digital_adoption_prior",
                "survey_cashflow_stress_prior",
                "survey_settlement_pain_prior",
                "survey_credit_need_prior",
                "survey_ai_usage_prior",
            ],
        ),
        "",
        "## Enriched Feature Summary",
        "",
        md_table(feature_summary, list(feature_summary.columns)),
        "",
        "## Method",
        "",
        "- Provider-level synthetic summaries were computed from `data_v2/merchants.csv`, `provider_kpis.csv`, `payouts_loans.csv`, and `transactions.csv`.",
        "- Primary priors were estimated by `business_type + region` where survey coverage existed.",
        "- Providers without a matching primary segment received overall survey priors.",
        "- Blended features use synthetic behavior as the main signal and survey responses as calibration priors.",
        "- The enrichment is intended for analysis, dashboards, and dissertation triangulation, not as new primary-observed provider records.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    survey, merchants, kpis, payouts, tx = load_inputs(args)
    priors = survey_priors(survey)
    provider = provider_summaries(merchants, kpis, payouts, tx)
    provider = attach_priors(provider, priors)
    enriched = create_blended_features(provider)

    output_columns = [
        "merchant_id",
        "region",
        "city",
        "business_type",
        "tenure_days",
        "avg_ticket",
        "monthly_income",
        "repeat_customer_rate",
        "kyc_flag",
        "treatment_flag",
        "treatment_start_month",
        "intervention_timestamp",
        "primary_match_level",
        "survey_response_count",
        "survey_digital_adoption_prior",
        "survey_cashflow_stress_prior",
        "survey_settlement_pain_prior",
        "survey_credit_need_prior",
        "survey_business_growth_prior",
        "survey_repeat_customer_prior",
        "survey_ai_usage_prior",
        "survey_faster_payout_value_prior",
        "avg_technology_adoption_score",
        "avg_working_capital_gap",
        "avg_payout_delay_days",
        "loan_offer_rate",
        "avg_loan_amount",
        "default_rate",
        "avg_lock_in_score",
        "avg_advancement_score",
        "avg_agentic_intelligence_score",
        "upi_share",
        "avg_settlement_delay",
        "avg_service_completion_rate",
        "active_provider_month_rate",
        "technology_adoption_score_blended",
        "working_capital_gap_blended",
        "payout_delay_days_blended",
        "loan_uptake_propensity_blended",
        "advancement_score_blended",
        "lock_in_score_blended",
        "agentic_intelligence_score_blended",
        "settlement_credit_stress",
        "digital_growth_index",
        "credit_dependency_score_primary_informed",
        "settlement_experience_index",
    ]
    final = enriched[output_columns].copy()
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    final.to_csv(args.output, index=False)
    write_report(final, priors, Path(args.report), args.output)
    print(f"Saved enriched provider features to {args.output}")
    print(f"Rows: {len(final):,}")
    print(f"Columns: {len(final.columns):,}")
    print(f"Saved primary integration report to {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
