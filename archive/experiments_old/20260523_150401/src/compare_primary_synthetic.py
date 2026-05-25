"""
Compare cleaned primary survey distributions with synthetic dataset variables.
"""

from __future__ import annotations

import argparse
import os
from datetime import date
from pathlib import Path
from typing import Callable, Dict, List

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare primary and synthetic distributions.")
    parser.add_argument("--primary", default=os.path.join("data", "primary_responses_clean.csv"))
    parser.add_argument("--mapping", default=os.path.join("docs", "primary_secondary_mapping.csv"))
    parser.add_argument("--merchants", default=os.path.join("data", "merchants.csv"))
    parser.add_argument("--kpis", default=os.path.join("data", "provider_kpis.csv"))
    parser.add_argument("--payouts", default=os.path.join("data", "payouts_loans.csv"))
    parser.add_argument("--out_report", default=os.path.join("output", "primary_vs_synthetic_report.md"))
    parser.add_argument("--out_scores", default=os.path.join("output", "agreement_scores.csv"))
    return parser.parse_args()


def clamp01(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").clip(0, 1)


def minmax(series: pd.Series, lower: float | None = None, upper: float | None = None) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    lo = values.min() if lower is None else lower
    hi = values.max() if upper is None else upper
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        return values * np.nan
    return ((values - lo) / (hi - lo)).clip(0, 1)


def quantile_scale(series: pd.Series, q_low: float = 0.05, q_high: float = 0.95) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    lo = values.quantile(q_low)
    hi = values.quantile(q_high)
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        return values * np.nan
    return ((values - lo) / (hi - lo)).clip(0, 1)


def bool_float(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.astype(float)
    return series.astype(str).str.lower().isin(["true", "1", "yes"]).astype(float)


def summarize(name: str, values: pd.Series) -> Dict[str, float | str]:
    values = pd.to_numeric(values, errors="coerce").dropna()
    if values.empty:
        return {"variable": name, "n": 0, "mean": np.nan, "median": np.nan, "q25": np.nan, "q75": np.nan}
    return {
        "variable": name,
        "n": int(values.shape[0]),
        "mean": float(values.mean()),
        "median": float(values.median()),
        "q25": float(values.quantile(0.25)),
        "q75": float(values.quantile(0.75)),
    }


def agreement_score(primary_values: pd.Series, synthetic_values: pd.Series) -> Dict[str, float]:
    p = pd.to_numeric(primary_values, errors="coerce").dropna()
    s = pd.to_numeric(synthetic_values, errors="coerce").dropna()
    if p.empty or s.empty:
        return {"primary_mean": np.nan, "synthetic_mean": np.nan, "mean_gap": np.nan, "agreement_score": np.nan}
    primary_mean = float(p.mean())
    synthetic_mean = float(s.mean())
    gap = abs(primary_mean - synthetic_mean)
    return {
        "primary_mean": primary_mean,
        "synthetic_mean": synthetic_mean,
        "mean_gap": gap,
        "agreement_score": max(0.0, 1.0 - gap),
    }


def score_band(score: float) -> str:
    if pd.isna(score):
        return "Unavailable"
    if score >= 0.8:
        return "High"
    if score >= 0.6:
        return "Moderate"
    if score >= 0.4:
        return "Weak"
    return "Low"


def md_table(frame: pd.DataFrame, float_digits: int = 3) -> str:
    if frame.empty:
        return "_No rows._"
    view = pd.DataFrame(index=frame.index)
    for column in frame.columns:
        if pd.api.types.is_float_dtype(frame[column]):
            view[column] = frame[column].map(lambda x: "" if pd.isna(x) else f"{x:.{float_digits}f}").astype(str)
        else:
            view[column] = frame[column].map(lambda x: "" if pd.isna(x) else str(x)).astype(str)
    lines = [
        "| " + " | ".join(view.columns) + " |",
        "| " + " | ".join("---" for _ in view.columns) + " |",
    ]
    for _, row in view.iterrows():
        values = [str(row[column]).replace("|", "\\|") for column in view.columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    primary = pd.read_csv(args.primary)
    mapping = pd.read_csv(args.mapping)
    merchants = pd.read_csv(args.merchants)
    kpis = pd.read_csv(args.kpis)
    payouts = pd.read_csv(args.payouts)

    comparisons: List[Dict] = []
    distribution_rows: List[Dict] = []

    configs = [
        {
            "construct": "Digital adoption",
            "primary_variable": "digital_adoption_score_scaled",
            "primary_values": clamp01(primary["digital_adoption_score_scaled"]),
            "synthetic_dataset": "merchants.csv",
            "synthetic_variable": "digital_tool_usage",
            "synthetic_values": clamp01(merchants["digital_tool_usage"]),
            "quality": "Direct scaled proxy",
            "commentary": "Survey digital adoption is directly comparable to synthetic digital tool usage.",
        },
        {
            "construct": "Digital adoption",
            "primary_variable": "digital_adoption_score_scaled",
            "primary_values": clamp01(primary["digital_adoption_score_scaled"]),
            "synthetic_dataset": "provider_kpis.csv",
            "synthetic_variable": "technology_adoption_score",
            "synthetic_values": clamp01(kpis["technology_adoption_score"]),
            "quality": "Composite proxy",
            "commentary": "Synthetic technology score includes digital tools and payment reliability, so exact agreement is not expected.",
        },
        {
            "construct": "Settlement pain",
            "primary_variable": "settlement_delay_impact_scaled",
            "primary_values": clamp01(primary["settlement_delay_impact_scaled"]),
            "synthetic_dataset": "payouts_loans.csv",
            "synthetic_variable": "payout_delay_days_scaled",
            "synthetic_values": minmax(payouts["payout_delay_days"], lower=0, upper=7),
            "quality": "Impact-to-delay proxy",
            "commentary": "Survey measures perceived pain; synthetic variable measures payout delay days.",
        },
        {
            "construct": "Settlement pain",
            "primary_variable": "cashflow_issues_scaled",
            "primary_values": clamp01(primary["cashflow_issues_scaled"]),
            "synthetic_dataset": "payouts_loans.csv",
            "synthetic_variable": "working_capital_gap_scaled",
            "synthetic_values": quantile_scale(payouts["working_capital_gap"]),
            "quality": "Liquidity-pressure proxy",
            "commentary": "Cashflow pain is compared with synthetic working-capital pressure.",
        },
        {
            "construct": "Credit need",
            "primary_variable": "needed_business_credit_binary",
            "primary_values": clamp01(primary["needed_business_credit_binary"]),
            "synthetic_dataset": "payouts_loans.csv",
            "synthetic_variable": "loan_offer_flag",
            "synthetic_values": bool_float(payouts["loan_offer_flag"]),
            "quality": "Demand-to-offer proxy",
            "commentary": "Primary credit need is not the same as synthetic loan offer; compare directionally.",
        },
        {
            "construct": "Credit need",
            "primary_variable": "approx_credit_amount_numeric_scaled",
            "primary_values": quantile_scale(primary["approx_credit_amount_numeric"]),
            "synthetic_dataset": "payouts_loans.csv",
            "synthetic_variable": "loan_amount_scaled",
            "synthetic_values": quantile_scale(payouts.loc[payouts["loan_amount"] > 0, "loan_amount"]),
            "quality": "Amount distribution proxy",
            "commentary": "Compares requested/needed credit size with positive synthetic loan amounts.",
        },
        {
            "construct": "Business growth",
            "primary_variable": "business_growth_after_digital_scaled",
            "primary_values": clamp01(primary["business_growth_after_digital_scaled"]),
            "synthetic_dataset": "provider_kpis.csv",
            "synthetic_variable": "advancement_score",
            "synthetic_values": clamp01(kpis["advancement_score"]),
            "quality": "Direct mechanism proxy",
            "commentary": "Primary perceived growth is aligned with synthetic advancement score.",
        },
        {
            "construct": "Business growth",
            "primary_variable": "business_growth_after_digital_scaled",
            "primary_values": clamp01(primary["business_growth_after_digital_scaled"]),
            "synthetic_dataset": "provider_kpis.csv",
            "synthetic_variable": "income_growth_pct_scaled",
            "synthetic_values": quantile_scale(kpis["income_growth_pct"]),
            "quality": "Perception-to-outcome proxy",
            "commentary": "Perceived growth is compared with synthetic income growth after percentile scaling.",
        },
        {
            "construct": "Retention",
            "primary_variable": "repeat_customer_change_scaled",
            "primary_values": clamp01(primary["repeat_customer_change_scaled"]),
            "synthetic_dataset": "provider_kpis.csv",
            "synthetic_variable": "lock_in_score",
            "synthetic_values": clamp01(kpis["lock_in_score"]),
            "quality": "Indirect retention proxy",
            "commentary": "The uploaded survey does not contain explicit retention intent; repeat-customer change is used as a lock-in proxy.",
        },
        {
            "construct": "Retention",
            "primary_variable": "repeat_customer_change_scaled",
            "primary_values": clamp01(primary["repeat_customer_change_scaled"]),
            "synthetic_dataset": "provider_kpis.csv",
            "synthetic_variable": "retention_flag",
            "synthetic_values": bool_float(kpis["retention_flag"]),
            "quality": "Weak indirect proxy",
            "commentary": "Repeat-customer improvement is only a weak proxy for actual provider retention.",
        },
        {
            "construct": "AI usage",
            "primary_variable": "ai_tool_usage_binary",
            "primary_values": clamp01(primary["ai_tool_usage_binary"]),
            "synthetic_dataset": "merchants.csv",
            "synthetic_variable": "agent_usage_flag",
            "synthetic_values": bool_float(merchants["agent_usage_flag"]),
            "quality": "Direct binary proxy",
            "commentary": "Primary AI usage maps directly to synthetic agent usage flag.",
        },
        {
            "construct": "AI usage",
            "primary_variable": "ai_tool_usage_binary",
            "primary_values": clamp01(primary["ai_tool_usage_binary"]),
            "synthetic_dataset": "provider_kpis.csv",
            "synthetic_variable": "forecast_usage",
            "synthetic_values": bool_float(kpis["forecast_usage"]),
            "quality": "Partial binary proxy",
            "commentary": "Forecast usage is narrower than general AI-tool use.",
        },
        {
            "construct": "AI usage",
            "primary_variable": "ai_tool_usage_binary",
            "primary_values": clamp01(primary["ai_tool_usage_binary"]),
            "synthetic_dataset": "provider_kpis.csv",
            "synthetic_variable": "agentic_intelligence_score",
            "synthetic_values": clamp01(kpis["agentic_intelligence_score"]),
            "quality": "Composite proxy",
            "commentary": "Primary AI use is compared with the broader agentic-intelligence score.",
        },
    ]

    for config in configs:
        stats = agreement_score(config["primary_values"], config["synthetic_values"])
        row = {
            "construct": config["construct"],
            "primary_variable": config["primary_variable"],
            "synthetic_dataset": config["synthetic_dataset"],
            "synthetic_variable": config["synthetic_variable"],
            **stats,
            "agreement_band": score_band(stats["agreement_score"]),
            "mapping_quality": config["quality"],
            "commentary": config["commentary"],
        }
        comparisons.append(row)
        distribution_rows.append(
            {
                "construct": config["construct"],
                "source": "Primary",
                **summarize(config["primary_variable"], config["primary_values"]),
            }
        )
        distribution_rows.append(
            {
                "construct": config["construct"],
                "source": "Synthetic",
                **summarize(f"{config['synthetic_dataset']}::{config['synthetic_variable']}", config["synthetic_values"]),
            }
        )

    scores = pd.DataFrame(comparisons)
    distributions = pd.DataFrame(distribution_rows).drop_duplicates()

    construct_scores = (
        scores.groupby("construct", as_index=False)["agreement_score"]
        .mean()
        .sort_values("construct")
    )
    construct_scores = construct_scores.assign(agreement_band=construct_scores["agreement_score"].map(score_band))
    mapping_summary = mapping.groupby("compatibility_band").size().reset_index(name="mapping_rows")

    Path(args.out_scores).parent.mkdir(parents=True, exist_ok=True)
    scores.to_csv(args.out_scores, index=False)

    lines = [
        "# Primary Vs Synthetic Validation Report",
        "",
        f"Generated on {date.today().isoformat()}.",
        "",
        "## Inputs",
        "",
        f"- Primary responses: `{args.primary}` ({len(primary)} rows)",
        f"- Mapping: `{args.mapping}` ({len(mapping)} rows)",
        f"- Synthetic merchants: `{args.merchants}` ({len(merchants)} rows)",
        f"- Synthetic provider KPIs: `{args.kpis}` ({len(kpis)} rows)",
        f"- Synthetic payouts/loans: `{args.payouts}` ({len(payouts)} rows)",
        "",
        "## Agreement Score Method",
        "",
        "Variables are converted to comparable 0-1 scales where needed. Agreement score is `1 - absolute(mean gap)`.",
        "Scores are distribution-level checks for pilot validation, not row-level matching and not causal evidence.",
        "",
        "## Construct-Level Scores",
        "",
        md_table(construct_scores),
        "",
        "## Agreement Scores",
        "",
        md_table(scores[["construct", "primary_variable", "synthetic_dataset", "synthetic_variable", "primary_mean", "synthetic_mean", "mean_gap", "agreement_score", "agreement_band", "mapping_quality"]]),
        "",
        "## Distribution Comparison Tables",
        "",
        md_table(distributions[["construct", "source", "variable", "n", "mean", "median", "q25", "q75"]]),
        "",
        "## Mapping Compatibility Context",
        "",
        md_table(mapping_summary),
        "",
        "## Validation Commentary",
        "",
    ]

    for construct in sorted(scores["construct"].unique()):
        subset = scores[scores["construct"] == construct]
        mean_score = subset["agreement_score"].mean()
        band = score_band(mean_score)
        lines.append(f"### {construct}")
        lines.append("")
        lines.append(f"Mean agreement score: `{mean_score:.3f}` ({band}).")
        for _, row in subset.iterrows():
            lines.append(
                f"- `{row['primary_variable']}` vs `{row['synthetic_dataset']}::{row['synthetic_variable']}`: "
                f"{row['agreement_score']:.3f}. {row['commentary']}"
            )
        if construct == "Retention":
            lines.append("- Limitation: the uploaded primary survey does not include an explicit retention-intent question, so retention uses repeat-customer change as an indirect proxy.")
        lines.append("")

    lines.extend(
        [
            "## Overall Interpretation",
            "",
            f"Average agreement across all comparisons is `{scores['agreement_score'].mean():.3f}`.",
            "The primary survey aligns best where respondent-observable constructs map directly to synthetic variables, especially digital adoption, business growth, and broad lock-in signals.",
            "Agreement is weaker where the survey measures perceived pain or need while the synthetic variable is an administrative or modeled construct, such as payout delay days, loan offers, or forecast usage.",
            "Use these results as calibration and face-validity evidence for the synthetic dissertation dataset.",
        ]
    )

    Path(args.out_report).write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved agreement scores to {args.out_scores}")
    print(f"Saved report to {args.out_report}")
    print(f"Overall agreement score: {scores['agreement_score'].mean():.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
