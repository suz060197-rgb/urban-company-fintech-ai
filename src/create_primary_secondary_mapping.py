"""
Create primary-to-synthetic variable mapping and compatibility score.
"""

from __future__ import annotations

import argparse
import os
from datetime import date
from pathlib import Path

import pandas as pd


MAPPING_ROWS = [
    ("business_type", "business_type_raw", "merchants.csv", "category", "Direct categorical proxy", 1.0, "Service category normalized from survey business type."),
    ("city", "city", "merchants.csv", "city", "Direct categorical match", 1.0, "Cleaned city labels can be compared with synthetic city distribution."),
    ("region", "city", "merchants.csv", "region", "Derived categorical match", 1.0, "Survey region is derived from city and maps to synthetic region."),
    ("tenure_days_estimate", "experience_years", "merchants.csv", "tenure_days", "Numeric midpoint proxy", 0.9, "Experience years converted to days; close proxy for platform tenure."),
    ("monthly_income_midpoint", "monthly_income_range_raw", "merchants.csv", "monthly_income", "Numeric midpoint proxy", 0.9, "Income range converted to midpoint rupee estimate."),
    ("monthly_income_midpoint", "monthly_income_range_raw", "provider_kpis.csv", "monthly_profit", "Loose numeric proxy", 0.45, "Survey income is gross-like; synthetic monthly_profit is modeled net profit."),
    ("monthly_transaction_estimate", "monthly_transaction_volume_raw", "merchants.csv", "transaction_velocity", "Numeric midpoint proxy", 0.9, "Booking range converted to midpoint monthly transaction estimate."),
    ("uses_upi_flag", "payment_methods_standardized", "merchants.csv", "payment_success_rate", "Directional component proxy", 0.55, "UPI use supports digital payment reliability but is not itself success rate."),
    ("uses_cash_flag", "payment_methods_standardized", "merchants.csv", "payment_success_rate", "Inverse directional proxy", 0.4, "Cash use can be compared directionally with digital payment adoption."),
    ("upi_usage_frequency_scaled", "upi_usage_frequency_raw", "merchants.csv", "payment_success_rate", "Frequency-to-score proxy", 0.65, "Daily UPI use provides a soft validation of payment reliability assumptions."),
    ("digital_adoption_score_scaled", "Digital_Adoption_Score", "merchants.csv", "digital_tool_usage", "Scaled Likert proxy", 0.85, "Direct survey score for digital adoption."),
    ("digital_adoption_score_scaled", "Digital_Adoption_Score", "provider_kpis.csv", "technology_adoption_score", "Composite component proxy", 0.8, "Maps well to technology adoption score, though synthetic score includes payment success."),
    ("cashflow_issues_scaled", "Cashflow_Issues", "payouts_loans.csv", "working_capital_gap", "Scaled Likert proxy", 0.75, "Cashflow issue severity validates working-capital pressure."),
    ("settlement_delay_impact_scaled", "Settlement_Delay_Impact", "payouts_loans.csv", "payout_delay_days", "Impact proxy", 0.65, "Survey measures impact of delay rather than exact delay days."),
    ("settlement_delay_impact_scaled", "Settlement_Delay_Impact", "payouts_loans.csv", "working_capital_gap", "Impact proxy", 0.65, "Higher delay impact should align with higher liquidity pressure."),
    ("faster_payout_impact_scaled", "Faster_Payout_Impact", "payouts_loans.csv", "payout_delay_days", "Inverse impact proxy", 0.6, "Measures benefit from faster payouts rather than actual delay."),
    ("faster_payout_impact_scaled", "Faster_Payout_Impact", "provider_kpis.csv", "advancement_score", "Mechanism proxy", 0.65, "Validates payout-to-advancement causal mechanism."),
    ("needed_business_credit_binary", "Needed_Business_Credit", "payouts_loans.csv", "loan_offer_flag", "Binary demand/offer proxy", 0.6, "Survey records credit need, not necessarily observed offer."),
    ("needed_business_credit_binary", "Needed_Business_Credit", "payouts_loans.csv", "working_capital_gap", "Binary liquidity proxy", 0.7, "Credit need is a strong directional proxy for working-capital gap."),
    ("approx_credit_amount_numeric", "approx_credit_amount_raw", "payouts_loans.csv", "loan_amount", "Numeric proxy", 0.8, "Credit amount can be compared with synthetic loan amount when credit was needed."),
    ("credit_purpose", "Credit_Purpose", "payouts_loans.csv", "loan_status", "Context-only proxy", 0.25, "Credit purpose helps interpret loan usage but does not map to lifecycle status."),
    ("business_growth_after_digital_scaled", "Business_Growth_After_Digital", "provider_kpis.csv", "income_growth_pct", "Scaled Likert proxy", 0.65, "Perceived growth validates direction of income growth."),
    ("business_growth_after_digital_scaled", "Business_Growth_After_Digital", "provider_kpis.csv", "advancement_score", "Composite proxy", 0.75, "Good directional match to advancement score."),
    ("repeat_customer_change_scaled", "Repeat_Customer_Change", "merchants.csv", "repeat_customer_rate", "Scaled Likert proxy", 0.8, "Repeat-customer change validates repeat-customer assumptions."),
    ("repeat_customer_change_scaled", "Repeat_Customer_Change", "provider_kpis.csv", "lock_in_score", "Composite component proxy", 0.75, "Repeat-customer improvement is a lock-in component."),
    ("ai_tool_usage_binary", "AI_Tool_Usage", "merchants.csv", "agent_usage_flag", "Direct binary proxy", 0.9, "Yes/No AI usage maps directly to agent usage flag."),
    ("ai_tool_usage_binary", "AI_Tool_Usage", "merchants.csv", "ai_adoption_score", "Binary component proxy", 0.75, "Binary use validates direction of synthetic AI adoption score."),
    ("ai_tool_usage_binary", "AI_Tool_Usage", "provider_kpis.csv", "forecast_usage", "Binary proxy", 0.7, "AI use partially validates forecast usage."),
    ("ai_tool_usage_binary", "AI_Tool_Usage", "provider_kpis.csv", "agentic_intelligence_score", "Composite component proxy", 0.75, "AI use is a key component of agentic intelligence."),
    ("automation_usage", "Automation_Usage", "merchants.csv", "digital_tool_usage", "Categorical component proxy", 0.65, "Automation use indicates digital tool adoption."),
    ("automation_usage", "Automation_Usage", "provider_kpis.csv", "technology_adoption_score", "Categorical component proxy", 0.6, "Automation use supports technology dimension validation."),
    ("platform_used_raw", "Platform_Used", "merchants.csv", "multi_product_adoption", "Product-count proxy", 0.55, "Platform/payment app mentions can approximate multi-product adoption."),
    ("key_pain_points", "Key_Pain_Points", "payouts_loans.csv", "working_capital_gap", "Qualitative support proxy", 0.45, "Pain points support interpretation but are not direct numeric measures."),
    ("has_interview_quote", "Interview_Quote", "provider_kpis.csv", "advancement_score", "Qualitative evidence flag", 0.25, "Quote availability supports interpretation, not measurement."),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create primary-secondary mapping.")
    parser.add_argument("--primary", default=os.path.join("data", "primary_responses_clean.csv"))
    parser.add_argument("--mapping", default=os.path.join("docs", "primary_secondary_mapping.csv"))
    parser.add_argument("--report", default=os.path.join("docs", "primary_secondary_compatibility_report.md"))
    return parser.parse_args()


def compatibility_band(score: float) -> str:
    if score >= 0.8:
        return "High"
    if score >= 0.6:
        return "Medium"
    if score >= 0.4:
        return "Low"
    return "Context only"


def validate_columns(primary_path: str, rows: list[tuple]) -> tuple[pd.DataFrame, list[str]]:
    primary = pd.read_csv(primary_path, nrows=5)
    primary_columns = set(primary.columns)
    output = pd.DataFrame(
        rows,
        columns=[
            "primary_response_variable",
            "source_primary_field",
            "synthetic_dataset",
            "synthetic_variable",
            "mapping_type",
            "compatibility_score",
            "notes",
        ],
    )
    output = output.assign(
        compatibility_band=output["compatibility_score"].map(compatibility_band),
        primary_column_present=output["primary_response_variable"].isin(primary_columns),
    )
    missing = sorted(output.loc[~output["primary_column_present"], "primary_response_variable"].unique().tolist())
    return output, missing


def write_report(mapping: pd.DataFrame, missing: list[str], report_path: str) -> None:
    score = float(mapping.loc[mapping["primary_column_present"], "compatibility_score"].mean())
    coverage = float(mapping["primary_column_present"].mean())
    by_dataset = (
        mapping.groupby("synthetic_dataset")["compatibility_score"]
        .mean()
        .round(3)
        .reset_index()
        .sort_values("synthetic_dataset")
    )
    by_band = mapping["compatibility_band"].value_counts().reindex(["High", "Medium", "Low", "Context only"]).fillna(0).astype(int)

    lines = [
        "# Primary-Secondary Compatibility Report",
        "",
        f"Generated on {date.today().isoformat()}.",
        "",
        "## Compatibility Score",
        "",
        f"- Overall compatibility score: `{score:.3f}` out of `1.000`",
        f"- Primary column coverage: `{coverage:.1%}`",
        f"- Compatibility interpretation: `{compatibility_band(score)}`",
        "",
        "The score is the mean of row-level mapping scores where the cleaned primary column is present.",
        "",
        "## Dataset-Level Scores",
        "",
        "| Synthetic dataset | Mean score |",
        "|---|---:|",
    ]
    for _, row in by_dataset.iterrows():
        lines.append(f"| {row['synthetic_dataset']} | {row['compatibility_score']:.3f} |")

    lines.extend(["", "## Mapping Bands", "", "| Band | Count |", "|---|---:|"])
    for band, count in by_band.items():
        lines.append(f"| {band} | {count} |")

    lines.extend(
        [
            "",
            "## Validation",
            "",
            "- PASS `data/primary_responses_clean.csv` was read successfully.",
            f"- PASS generated `{len(mapping)}` primary-secondary mapping rows.",
        ]
    )
    if missing:
        lines.append(f"- WARN missing mapped primary columns: {', '.join(missing)}")
    else:
        lines.append("- PASS all mapped primary columns are present in the cleaned primary dataset.")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The cleaned primary survey is compatible with the synthetic datasets for pilot validation and calibration.",
            "The strongest matches are city, region, business category, tenure, income midpoint, transaction volume, digital adoption, repeat-customer change, and AI usage.",
            "Lower-scoring mappings are mostly qualitative or perception-based fields that support interpretation but should not be treated as exact administrative measurements.",
        ]
    )
    Path(report_path).write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    mapping, missing = validate_columns(args.primary, MAPPING_ROWS)
    Path(args.mapping).parent.mkdir(parents=True, exist_ok=True)
    mapping.to_csv(args.mapping, index=False)
    write_report(mapping, missing, args.report)
    print(f"Saved mapping to {args.mapping}")
    print(f"Saved compatibility report to {args.report}")
    print(f"Overall compatibility score: {mapping.loc[mapping['primary_column_present'], 'compatibility_score'].mean():.3f}")
    if missing:
        print(f"WARN missing columns: {missing}")
    else:
        print("PASS all mapped primary columns are present.")
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
