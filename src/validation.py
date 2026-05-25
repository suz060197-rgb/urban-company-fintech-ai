"""
Validation utilities for the Urban Company embedded-finance synthetic dataset.

The report focuses on research readiness: schema integrity, plausible ranges,
treatment/control balance, placebo evidence, and Difference-in-Differences setup.
"""

from __future__ import annotations

import argparse
import os
import sys
import warnings
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings(
    "ignore",
    message=".*ChainedAssignmentError: behaviour will change in pandas 3.0.*",
    category=FutureWarning,
)

try:
    from provenance import DELTA_COLUMN_MAP, SCHEMAS, schema_columns
except ImportError:
    from src.provenance import DELTA_COLUMN_MAP, SCHEMAS, schema_columns


REQUIRED_FILES = ["merchants.csv", "transactions.csv", "payouts_loans.csv", "provider_kpis.csv", "provenance.csv"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate generated embedded-finance synthetic datasets.")
    parser.add_argument("--data_dir", default="data", help="Directory containing generated CSV files.")
    parser.add_argument(
        "--report_path",
        default="validation_report.txt",
        help="Path where the validation report should be written.",
    )
    return parser.parse_args()


def read_datasets(data_dir: str) -> Dict[str, pd.DataFrame]:
    missing = [file_name for file_name in REQUIRED_FILES if not os.path.exists(os.path.join(data_dir, file_name))]
    if missing:
        raise FileNotFoundError(f"Missing required files in {data_dir}: {', '.join(missing)}")

    return {
        "merchants": pd.read_csv(os.path.join(data_dir, "merchants.csv")),
        "transactions": pd.read_csv(os.path.join(data_dir, "transactions.csv"), parse_dates=["timestamp"]),
        "payouts_loans": pd.read_csv(os.path.join(data_dir, "payouts_loans.csv")),
        "provider_kpis": pd.read_csv(os.path.join(data_dir, "provider_kpis.csv")),
        "provenance": pd.read_csv(os.path.join(data_dir, "provenance.csv")),
    }


def boolify(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


def p_value_for_groups(left: pd.Series, right: pd.Series) -> float:
    left = pd.to_numeric(left, errors="coerce").dropna()
    right = pd.to_numeric(right, errors="coerce").dropna()
    if len(left) < 2 or len(right) < 2:
        return np.nan
    if left.nunique() <= 1 and right.nunique() <= 1:
        return np.nan
    return float(stats.ttest_ind(left, right, equal_var=False).pvalue)


def standardized_mean_difference(left: pd.Series, right: pd.Series) -> float:
    left = pd.to_numeric(left, errors="coerce").dropna()
    right = pd.to_numeric(right, errors="coerce").dropna()
    if len(left) == 0 or len(right) == 0:
        return np.nan
    pooled_sd = np.sqrt((left.var(ddof=1) + right.var(ddof=1)) / 2)
    if pooled_sd == 0 or np.isnan(pooled_sd):
        return 0.0
    return float((left.mean() - right.mean()) / pooled_sd)


def format_table(df: pd.DataFrame, max_rows=None) -> str:
    if df.empty:
        return "(no rows)"
    table = df if max_rows is None else df.head(max_rows)
    with pd.option_context("display.max_rows", None, "display.width", 180, "display.max_columns", None):
        return table.to_string(index=False)


def schema_checks(datasets: Dict[str, pd.DataFrame]) -> List[str]:
    lines = ["SCHEMA CHECKS"]
    status = []
    for file_name in REQUIRED_FILES:
        key = file_name.replace(".csv", "")
        df = datasets[key]
        expected = schema_columns(file_name)
        missing = [column for column in expected if column not in df.columns]
        extra = [column for column in df.columns if column not in expected]
        duplicate_ids = ""
        if file_name == "merchants.csv":
            duplicate_ids = f", duplicate merchant_id rows={df['merchant_id'].duplicated().sum()}"
        if file_name == "transactions.csv":
            duplicate_ids = f", duplicate transaction_id rows={df['transaction_id'].duplicated().sum()}"
        result = "PASS" if not missing else "FAIL"
        status.append(result == "PASS")
        lines.append(
            f"- {file_name}: {result}; rows={len(df):,}; missing={missing if missing else 'none'}; "
            f"extra={extra if extra else 'none'}{duplicate_ids}"
        )
    lines.append(f"Overall schema status: {'PASS' if all(status) else 'FAIL'}")
    return lines


def distribution_checks(datasets: Dict[str, pd.DataFrame]) -> List[str]:
    merchants = datasets["merchants"]
    transactions = datasets["transactions"]
    payouts = datasets["payouts_loans"]
    kpis = datasets["provider_kpis"]

    checks = [
        ("avg_ticket_positive", (merchants["avg_ticket"] > 0).mean()),
        ("monthly_income_positive", (merchants["monthly_income"] > 0).mean()),
        ("repeat_rate_in_0_1", merchants["repeat_customer_rate"].between(0, 1).mean()),
        ("commission_in_0_1", merchants["platform_commission_pct"].between(0, 1).mean()),
        ("payment_success_rate_in_0_1", merchants["payment_success_rate"].between(0, 1).mean()),
        ("digital_tool_usage_in_0_1", merchants["digital_tool_usage"].between(0, 1).mean()),
        ("ai_adoption_score_in_0_1", merchants["ai_adoption_score"].between(0, 1).mean()),
        ("transaction_velocity_positive", (merchants["transaction_velocity"] > 0).mean()),
        ("transaction_amount_positive", (transactions["amount"] > 0).mean()),
        ("rating_in_1_5", transactions["customer_rating"].between(1, 5).mean()),
        ("tip_nonnegative", (transactions["tip_amount"] >= 0).mean()),
        ("settlement_delay_nonnegative", (transactions["settlement_delay"] >= 0).mean()),
        ("service_completion_rate_in_0_1", transactions["service_completion_rate"].between(0, 1).mean()),
        ("payout_nonnegative", (payouts["payout_amount"] >= 0).mean()),
        ("active_provider_month_flag_present", payouts["active_provider_month_flag"].notna().mean()),
        (
            "payout_delay_present_when_active",
            payouts.loc[boolify(payouts["active_provider_month_flag"]), "payout_delay_days"].notna().mean(),
        ),
        (
            "payout_delay_nan_when_inactive",
            payouts.loc[~boolify(payouts["active_provider_month_flag"]), "payout_delay_days"].isna().mean(),
        ),
        (
            "active_payout_delay_nonnegative",
            (payouts.loc[boolify(payouts["active_provider_month_flag"]), "payout_delay_days"] >= 0).mean(),
        ),
        ("loan_nonnegative", (payouts["loan_amount"] >= 0).mean()),
        ("working_capital_gap_nonnegative", (payouts["working_capital_gap"] >= 0).mean()),
        ("loan_disbursal_time_nonnegative", (payouts["loan_disbursal_time"] >= 0).mean()),
        ("churn_probability_in_0_1", kpis["churn_probability"].between(0, 1).mean()),
        ("lock_in_score_in_0_1", kpis["lock_in_score"].between(0, 1).mean()),
        ("technology_adoption_score_in_0_1", kpis["technology_adoption_score"].between(0, 1).mean()),
        ("advancement_score_in_0_1", kpis["advancement_score"].between(0, 1).mean()),
        ("agentic_intelligence_score_in_0_1", kpis["agentic_intelligence_score"].between(0, 1).mean()),
    ]
    check_df = pd.DataFrame(checks, columns=["check", "share_valid"]).assign(
        status=lambda frame: np.where(frame["share_valid"] >= 0.99, "PASS", "REVIEW")
    )

    summary = pd.DataFrame(
        {
            "metric": [
                "avg_ticket",
                "monthly_income",
                "transaction_amount",
                "customer_rating",
                "payout_amount",
                "monthly_profit",
                "income_growth_pct",
                "payment_success_rate",
                "digital_tool_usage",
                "ai_adoption_score",
                "settlement_delay",
                "service_completion_rate",
                "working_capital_gap",
                "loan_disbursal_time",
                "lock_in_score",
                "technology_adoption_score",
                "advancement_score",
                "agentic_intelligence_score",
            ],
            "mean": [
                merchants["avg_ticket"].mean(),
                merchants["monthly_income"].mean(),
                transactions["amount"].mean(),
                transactions["customer_rating"].mean(),
                payouts["payout_amount"].mean(),
                kpis["monthly_profit"].mean(),
                kpis["income_growth_pct"].mean(),
                merchants["payment_success_rate"].mean(),
                merchants["digital_tool_usage"].mean(),
                merchants["ai_adoption_score"].mean(),
                transactions["settlement_delay"].mean(),
                transactions["service_completion_rate"].mean(),
                payouts["working_capital_gap"].mean(),
                payouts["loan_disbursal_time"].mean(),
                kpis["lock_in_score"].mean(),
                kpis["technology_adoption_score"].mean(),
                kpis["advancement_score"].mean(),
                kpis["agentic_intelligence_score"].mean(),
            ],
            "p05": [
                merchants["avg_ticket"].quantile(0.05),
                merchants["monthly_income"].quantile(0.05),
                transactions["amount"].quantile(0.05),
                transactions["customer_rating"].quantile(0.05),
                payouts["payout_amount"].quantile(0.05),
                kpis["monthly_profit"].quantile(0.05),
                kpis["income_growth_pct"].quantile(0.05),
                merchants["payment_success_rate"].quantile(0.05),
                merchants["digital_tool_usage"].quantile(0.05),
                merchants["ai_adoption_score"].quantile(0.05),
                transactions["settlement_delay"].quantile(0.05),
                transactions["service_completion_rate"].quantile(0.05),
                payouts["working_capital_gap"].quantile(0.05),
                payouts["loan_disbursal_time"].quantile(0.05),
                kpis["lock_in_score"].quantile(0.05),
                kpis["technology_adoption_score"].quantile(0.05),
                kpis["advancement_score"].quantile(0.05),
                kpis["agentic_intelligence_score"].quantile(0.05),
            ],
            "p95": [
                merchants["avg_ticket"].quantile(0.95),
                merchants["monthly_income"].quantile(0.95),
                transactions["amount"].quantile(0.95),
                transactions["customer_rating"].quantile(0.95),
                payouts["payout_amount"].quantile(0.95),
                kpis["monthly_profit"].quantile(0.95),
                kpis["income_growth_pct"].quantile(0.95),
                merchants["payment_success_rate"].quantile(0.95),
                merchants["digital_tool_usage"].quantile(0.95),
                merchants["ai_adoption_score"].quantile(0.95),
                transactions["settlement_delay"].quantile(0.95),
                transactions["service_completion_rate"].quantile(0.95),
                payouts["working_capital_gap"].quantile(0.95),
                payouts["loan_disbursal_time"].quantile(0.95),
                kpis["lock_in_score"].quantile(0.95),
                kpis["technology_adoption_score"].quantile(0.95),
                kpis["advancement_score"].quantile(0.95),
                kpis["agentic_intelligence_score"].quantile(0.95),
            ],
        }
    ).round(3)

    lines = ["", "DISTRIBUTION CHECKS", format_table(check_df), "", "KEY DISTRIBUTION SUMMARY", format_table(summary)]
    return lines


def balance_table(datasets: Dict[str, pd.DataFrame]) -> List[str]:
    merchants = datasets["merchants"].copy()
    merchants = merchants.assign(treatment_flag=boolify(merchants["treatment_flag"]))
    treated = merchants[merchants["treatment_flag"]]
    control = merchants[~merchants["treatment_flag"]]
    covariates = [
        "tenure_days",
        "avg_ticket",
        "monthly_income",
        "repeat_customer_rate",
        "platform_commission_pct",
        "payment_success_rate",
        "digital_tool_usage",
        "ai_adoption_score",
    ]

    rows = []
    for covariate in covariates:
        rows.append(
            {
                "covariate": covariate,
                "treated_mean": treated[covariate].mean(),
                "control_mean": control[covariate].mean(),
                "std_mean_diff": standardized_mean_difference(treated[covariate], control[covariate]),
                "p_value": p_value_for_groups(treated[covariate], control[covariate]),
            }
        )
    table = pd.DataFrame(rows).round(4)
    max_abs_smd = table["std_mean_diff"].abs().max()
    status = "PASS" if pd.notna(max_abs_smd) and max_abs_smd < 0.25 else "REVIEW"

    lines = [
        "",
        "BALANCE TABLE",
        f"Treatment providers={len(treated):,}; control providers={len(control):,}; status={status}",
        format_table(table),
    ]
    return lines


def treatment_vs_control(datasets: Dict[str, pd.DataFrame]) -> List[str]:
    kpis = datasets["provider_kpis"].copy()
    payouts = datasets["payouts_loans"].copy()
    kpis = kpis.assign(
        treatment_flag=boolify(kpis["treatment_flag"]),
        post_treatment_flag=boolify(kpis["post_treatment_flag"]),
    )

    merged = kpis.merge(
        payouts[
            [
                "merchant_id",
                "month",
                "payout_delay_days",
                "active_provider_month_flag",
                "loan_offer_flag",
                "working_capital_gap",
                "loan_disbursal_time",
                "default_flag",
            ]
        ],
        on=["merchant_id", "month"],
    )
    merged = merged.assign(loan_offer_flag=boolify(merged["loan_offer_flag"]))
    merged = merged.assign(default_flag=boolify(merged["default_flag"]))
    merged = merged.assign(active_provider_month_flag=boolify(merged["active_provider_month_flag"]))
    grouped = (
        merged.groupby(["treatment_flag", "post_treatment_flag"])
        .agg(
            rows=("merchant_id", "size"),
            income_growth_pct=("income_growth_pct", "mean"),
            monthly_profit=("monthly_profit", "mean"),
            retention_rate=("retention_flag", "mean"),
            churn_probability=("churn_probability", "mean"),
            payout_delay_days=("payout_delay_days", "mean"),
            active_provider_month_rate=("active_provider_month_flag", "mean"),
            loan_offer_rate=("loan_offer_flag", "mean"),
            working_capital_gap=("working_capital_gap", "mean"),
            default_rate=("default_flag", "mean"),
            lock_in_score=("lock_in_score", "mean"),
            technology_adoption_score=("technology_adoption_score", "mean"),
            advancement_score=("advancement_score", "mean"),
            agentic_intelligence_score=("agentic_intelligence_score", "mean"),
        )
        .reset_index()
        .round(4)
    )

    post = merged[merged["post_treatment_flag"]]
    treated_post = post[post["treatment_flag"]]
    control_all = merged[~merged["treatment_flag"]]
    rows = []
    for outcome in [
        "income_growth_pct",
        "monthly_profit",
        "churn_probability",
        "payout_delay_days",
        "working_capital_gap",
        "lock_in_score",
        "technology_adoption_score",
        "advancement_score",
        "agentic_intelligence_score",
    ]:
        rows.append(
            {
                "outcome": outcome,
                "treated_post_mean": treated_post[outcome].mean(),
                "control_mean": control_all[outcome].mean(),
                "difference": treated_post[outcome].mean() - control_all[outcome].mean(),
                "p_value": p_value_for_groups(treated_post[outcome], control_all[outcome]),
            }
        )
    effect_table = pd.DataFrame(rows).round(4)

    return [
        "",
        "TREATMENT VS CONTROL COMPARISON",
        format_table(grouped),
        "",
        "POST-TREATMENT OUTCOME CONTRASTS",
        format_table(effect_table),
    ]


def delta_framework_summary(datasets: Dict[str, pd.DataFrame]) -> List[str]:
    merchants = datasets["merchants"]
    transactions = datasets["transactions"]
    payouts = datasets["payouts_loans"]
    kpis = datasets["provider_kpis"]
    provenance = datasets["provenance"]

    rows = [
        {
            "dimension": "Data",
            "primary_metric": "payment_success_rate",
            "mean": merchants["payment_success_rate"].mean(),
            "coverage": merchants["payment_success_rate"].notna().mean(),
        },
        {
            "dimension": "Embedded Finance",
            "primary_metric": "settlement_delay",
            "mean": transactions["settlement_delay"].mean(),
            "coverage": transactions["settlement_delay"].notna().mean(),
        },
        {
            "dimension": "Lock-in",
            "primary_metric": "lock_in_score",
            "mean": kpis["lock_in_score"].mean(),
            "coverage": kpis["lock_in_score"].notna().mean(),
        },
        {
            "dimension": "Technology",
            "primary_metric": "technology_adoption_score",
            "mean": kpis["technology_adoption_score"].mean(),
            "coverage": kpis["technology_adoption_score"].notna().mean(),
        },
        {
            "dimension": "Advancement",
            "primary_metric": "advancement_score",
            "mean": kpis["advancement_score"].mean(),
            "coverage": kpis["advancement_score"].notna().mean(),
        },
        {
            "dimension": "Agentic Intelligence",
            "primary_metric": "agentic_intelligence_score",
            "mean": kpis["agentic_intelligence_score"].mean(),
            "coverage": kpis["agentic_intelligence_score"].notna().mean(),
        },
    ]
    table = pd.DataFrame(rows).round(4)

    provenance_dimensions = sorted(provenance["delta_dimension"].dropna().unique())
    missing_dimensions = sorted(set(["Data", "Embedded Finance", "Lock-in", "Technology", "Advancement", "Agentic Intelligence"]) - set(provenance_dimensions))
    mapped_columns = sum(1 for column in DELTA_COLUMN_MAP if column in set(provenance["column_name"]))

    return [
        "",
        "DELTA FRAMEWORK SUMMARY",
        format_table(table),
        f"Provenance dimensions present: {', '.join(provenance_dimensions)}",
        f"Missing DELTA dimensions in provenance: {missing_dimensions if missing_dimensions else 'none'}",
        f"Mapped provenance columns found: {mapped_columns}",
    ]


def delta_variable_detail(datasets: Dict[str, pd.DataFrame]) -> List[str]:
    provenance = datasets["provenance"]
    dataset_key = {
        "merchants.csv": "merchants",
        "transactions.csv": "transactions",
        "payouts_loans.csv": "payouts_loans",
        "provider_kpis.csv": "provider_kpis",
    }
    rows = []
    for item in provenance[provenance["dataset"].isin(dataset_key)].to_dict("records"):
        df = datasets[dataset_key[item["dataset"]]]
        column = item["column_name"]
        series = df[column]
        coverage = float(series.notna().mean())
        value_mean = np.nan
        value_min = np.nan
        value_max = np.nan
        distinct = int(series.nunique(dropna=True))
        if series.dtype == bool:
            value_mean = float(series.mean())
            value_min = float(series.min())
            value_max = float(series.max())
        else:
            numeric = pd.to_numeric(series, errors="coerce")
            if numeric.notna().any():
                value_mean = float(numeric.mean())
                value_min = float(numeric.min())
                value_max = float(numeric.max())
        rows.append(
            {
                "dataset": item["dataset"],
                "column_name": column,
                "delta_dimension": item["delta_dimension"],
                "source_type": item["source_type"],
                "coverage": coverage,
                "mean_or_rate": value_mean,
                "min": value_min,
                "max": value_max,
                "distinct": distinct,
            }
        )
    table = pd.DataFrame(rows).round(4)
    return ["", "DELTA VARIABLE DETAIL", format_table(table)]


def placebo_test(datasets: Dict[str, pd.DataFrame]) -> List[str]:
    kpis = datasets["provider_kpis"].copy()
    kpis = kpis.assign(
        treatment_flag=boolify(kpis["treatment_flag"]),
        post_treatment_flag=boolify(kpis["post_treatment_flag"]),
    )
    pre = kpis[(kpis["treatment_flag"]) & (~kpis["post_treatment_flag"])].copy()
    control = kpis[~kpis["treatment_flag"]].copy()

    if pre.empty or control.empty:
        return ["", "PLACEBO TEST", "Not enough pre-treatment treated rows for a placebo test."]

    pre_months = sorted(pre["month"].unique())
    control_pre = control[control["month"].isin(pre_months)]
    rows = []
    for outcome in ["income_growth_pct", "monthly_profit", "churn_probability"]:
        smd = standardized_mean_difference(pre[outcome], control_pre[outcome])
        rows.append(
            {
                "outcome": outcome,
                "treated_pre_mean": pre[outcome].mean(),
                "control_same_months_mean": control_pre[outcome].mean(),
                "placebo_difference": pre[outcome].mean() - control_pre[outcome].mean(),
                "std_mean_diff": smd,
                "p_value": p_value_for_groups(pre[outcome], control_pre[outcome]),
            }
        )
    table = pd.DataFrame(rows).round(4)
    max_abs_smd = table["std_mean_diff"].abs().max()
    status = "PASS" if pd.notna(max_abs_smd) and max_abs_smd < 0.10 else "REVIEW"
    note = (
        "Status uses practical pre-period balance: PASS when all absolute standardized mean differences are below 0.10. "
        "P-values are still shown, but large synthetic panels can flag tiny differences as statistically significant."
    )
    return ["", "PLACEBO TEST", f"Status={status}; compared treated pre-period rows with control rows in the same calendar months.", note, format_table(table)]


def did_readiness(datasets: Dict[str, pd.DataFrame]) -> List[str]:
    merchants = datasets["merchants"].copy()
    kpis = datasets["provider_kpis"].copy()
    kpis = kpis.assign(
        treatment_flag=boolify(kpis["treatment_flag"]),
        post_treatment_flag=boolify(kpis["post_treatment_flag"]),
    )

    n_months = kpis["month"].nunique()
    treated_count = int(merchants["treatment_flag"].astype(str).str.lower().isin(["true", "1"]).sum())
    control_count = int(len(merchants) - treated_count)
    has_pre = bool(((kpis["treatment_flag"]) & (~kpis["post_treatment_flag"])).any())
    has_post = bool(((kpis["treatment_flag"]) & (kpis["post_treatment_flag"])).any())
    balanced_panel_rows = len(merchants) * n_months
    completeness = len(kpis) / balanced_panel_rows if balanced_panel_rows else np.nan
    untreated_post_proxy = bool((~kpis["treatment_flag"]).any())

    readiness = {
        "multiple_months": n_months >= 2,
        "treated_group_present": treated_count > 0,
        "control_group_present": control_count > 0,
        "treated_pre_period_present": has_pre,
        "treated_post_period_present": has_post,
        "control_counterfactual_present": untreated_post_proxy,
        "panel_completeness_at_least_95pct": completeness >= 0.95,
    }
    status = "PASS" if all(readiness.values()) else "REVIEW"
    table = pd.DataFrame(
        [{"criterion": key, "pass": value} for key, value in readiness.items()]
        + [{"criterion": "panel_completeness", "pass": round(completeness, 4)}]
    )

    note = (
        "For strongest DiD diagnostics, prefer --phased_rollout so treated providers have explicit "
        "pre-treatment months. A non-phased rollout can still support treatment/control contrasts, "
        "but it weakens pre-trend checks."
    )
    return ["", "DIFFERENCE-IN-DIFFERENCES READINESS", f"Status={status}", format_table(table), note]


def build_report(datasets: Dict[str, pd.DataFrame], data_dir: str) -> str:
    lines = [
        "Urban Company Embedded Finance Synthetic Dataset Validation Report",
        f"Data directory: {os.path.abspath(data_dir)}",
        "",
        "ROW COUNTS",
    ]
    for key, df in datasets.items():
        lines.append(f"- {key}: {len(df):,}")
    for section in [
        schema_checks,
        distribution_checks,
        balance_table,
        treatment_vs_control,
        delta_framework_summary,
        delta_variable_detail,
        placebo_test,
        did_readiness,
    ]:
        lines.extend(section(datasets))
    lines.append("")
    lines.append("END OF REPORT")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        datasets = read_datasets(args.data_dir)
        report = build_report(datasets, args.data_dir)
        with open(args.report_path, "w", encoding="utf-8") as handle:
            handle.write(report)
        print(f"Validation report written to {os.path.abspath(args.report_path)}")
        return 0
    except Exception as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
