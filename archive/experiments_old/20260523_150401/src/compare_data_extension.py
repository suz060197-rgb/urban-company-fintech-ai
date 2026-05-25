"""
Compare original data/ coverage with extended data_v2/ outputs.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List

import pandas as pd


DATASETS = ["merchants.csv", "transactions.csv", "payouts_loans.csv", "provider_kpis.csv"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare old and extended synthetic datasets.")
    parser.add_argument("--old_dir", default="data")
    parser.add_argument("--new_dir", default="data_v2")
    parser.add_argument("--report", default="docs/data_extension_report.md")
    return parser.parse_args()


def load_csv(base: str, dataset: str) -> pd.DataFrame:
    return pd.read_csv(Path(base) / dataset, low_memory=False)


def date_series(frame: pd.DataFrame, dataset: str) -> pd.Series | None:
    if dataset == "transactions.csv" and "timestamp" in frame.columns:
        return pd.to_datetime(frame["timestamp"], errors="coerce")
    if "month" in frame.columns:
        return pd.to_datetime(frame["month"], errors="coerce")
    if "intervention_timestamp" in frame.columns:
        return pd.to_datetime(frame["intervention_timestamp"], errors="coerce")
    return None


def coverage_row(dataset: str, old: pd.DataFrame, new: pd.DataFrame) -> Dict[str, object]:
    old_dates = date_series(old, dataset)
    new_dates = date_series(new, dataset)
    old_latest = "" if old_dates is None or old_dates.dropna().empty else old_dates.max().date().isoformat()
    new_latest = "" if new_dates is None or new_dates.dropna().empty else new_dates.max().date().isoformat()
    old_earliest = "" if old_dates is None or old_dates.dropna().empty else old_dates.min().date().isoformat()
    new_earliest = "" if new_dates is None or new_dates.dropna().empty else new_dates.min().date().isoformat()
    old_months = "" if old_dates is None or old_dates.dropna().empty else old_dates.dt.to_period("M").nunique()
    new_months = "" if new_dates is None or new_dates.dropna().empty else new_dates.dt.to_period("M").nunique()
    return {
        "dataset": dataset,
        "old_rows": len(old),
        "new_rows": len(new),
        "row_delta": len(new) - len(old),
        "old_earliest": old_earliest,
        "old_latest": old_latest,
        "new_earliest": new_earliest,
        "new_latest": new_latest,
        "old_observed_months": old_months,
        "new_observed_months": new_months,
    }


def bool_mean(series: pd.Series) -> float:
    if series.dtype == bool:
        return float(series.mean())
    return float(series.astype(str).str.lower().isin(["true", "1", "yes"]).mean())


def metric_value(frame: pd.DataFrame, metric: str):
    if metric == "upi_share":
        return float(frame["payment_method"].astype(str).eq("UPI").mean())
    if metric == "cash_share":
        return float(frame["payment_method"].astype(str).eq("cash").mean())
    if metric.endswith("_rate"):
        candidates = [metric.removesuffix("_rate"), metric.replace("_rate", "_flag")]
        for candidate in candidates:
            if candidate in frame.columns:
                return bool_mean(frame[candidate])
    if metric in frame.columns:
        if frame[metric].dtype == bool or set(frame[metric].dropna().astype(str).str.lower().unique()).issubset({"true", "false"}):
            return bool_mean(frame[metric])
        return float(pd.to_numeric(frame[metric], errors="coerce").mean())
    return None


def distribution_rows(dataset: str, old: pd.DataFrame, new: pd.DataFrame) -> List[Dict[str, object]]:
    metric_map = {
        "merchants.csv": [
            "monthly_income",
            "avg_ticket",
            "payment_success_rate",
            "transaction_velocity",
            "multi_product_adoption",
            "digital_tool_usage",
            "ai_adoption_score",
            "treatment_flag_rate",
        ],
        "transactions.csv": [
            "amount",
            "customer_rating",
            "upi_share",
            "cash_share",
            "settlement_delay",
            "service_completion_rate",
            "cancellation_rate",
        ],
        "payouts_loans.csv": [
            "payout_amount",
            "payout_delay_days",
            "loan_offer_rate",
            "loan_amount",
            "working_capital_gap",
            "loan_disbursal_time",
            "default_rate",
            "active_provider_month_rate",
        ],
        "provider_kpis.csv": [
            "income_growth_pct",
            "monthly_profit",
            "retention_rate",
            "churn_probability",
            "post_treatment_rate",
            "lock_in_score",
            "technology_adoption_score",
            "advancement_score",
            "agentic_intelligence_score",
            "forecast_usage_rate",
        ],
    }
    rows = []
    for metric in metric_map[dataset]:
        old_value = metric_value(old, metric)
        new_value = metric_value(new, metric)
        rows.append(
            {
                "dataset": dataset,
                "metric": metric,
                "old_mean_or_share": "" if old_value is None else round(old_value, 4),
                "new_mean_or_share": "" if new_value is None else round(new_value, 4),
                "delta": "" if old_value is None or new_value is None else round(new_value - old_value, 4),
            }
        )
    return rows


def monthly_gap_summary(frame: pd.DataFrame, dataset: str) -> str:
    dates = date_series(frame, dataset)
    if dates is None or dates.dropna().empty:
        return "No date column"
    observed = pd.PeriodIndex(dates.dropna().dt.to_period("M").unique()).sort_values()
    expected = pd.period_range(observed.min(), observed.max(), freq="M")
    missing = expected.difference(observed)
    return "None" if len(missing) == 0 else ", ".join(str(period) for period in missing)


def md_table(rows: List[Dict[str, object]], columns: List[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = [str(row.get(column, "")).replace("|", "\\|") for column in columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(coverage: List[Dict[str, object]], distributions: List[Dict[str, object]], gaps: List[Dict[str, str]], path: Path) -> None:
    lines = [
        "# Data Extension Report",
        "",
        "Extended synthetic provider-month observations from `2024-01` through `2026-05` into `data_v2/`.",
        "",
        "The original `data/` directory was left intact as the historical backup. No existing production CSVs were overwritten.",
        "",
        "## Pipeline Changes",
        "",
        "- `generate_uc_dataset.py` now accepts `--start_month` and `--end_month`.",
        "- Monthly generation now includes UPI growth, recurring seasonality, inflation, increasing digital/AI maturity, credit uptake growth, settlement-delay improvements, treatment-driven liquidity effects, and provider churn.",
        "- `create_lagged_features.py` no longer hardcodes 2024 when computing `months_since_intervention`; it derives month numbering from the panel start.",
        "",
        "## Coverage And Row Counts",
        "",
        md_table(
            coverage,
            [
                "dataset",
                "old_rows",
                "new_rows",
                "row_delta",
                "old_earliest",
                "old_latest",
                "new_earliest",
                "new_latest",
                "old_observed_months",
                "new_observed_months",
            ],
        ),
        "",
        "## Missing Monthly Periods In New Data",
        "",
        md_table(gaps, ["dataset", "missing_months"]),
        "",
        "## Distribution Changes",
        "",
        md_table(distributions, ["dataset", "metric", "old_mean_or_share", "new_mean_or_share", "delta"]),
        "",
        "## Interpretation",
        "",
        "- The new panel reaches May 2026 while preserving the old directory as a backup.",
        "- Transaction volume rises because the panel expands from 12 months to 29 months.",
        "- UPI share, technology adoption, agentic intelligence, and settlement speed should move in dissertation-consistent directions over time.",
        "- `data_v2/` should be used for refreshed Power BI work and any post-extension modeling.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    coverage = []
    distributions = []
    gaps = []
    for dataset in DATASETS:
        old = load_csv(args.old_dir, dataset)
        new = load_csv(args.new_dir, dataset)
        coverage.append(coverage_row(dataset, old, new))
        distributions.extend(distribution_rows(dataset, old, new))
        gaps.append({"dataset": dataset, "missing_months": monthly_gap_summary(new, dataset)})

    write_report(coverage, distributions, gaps, Path(args.report))
    print(f"Saved data extension report to {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
