"""
Create future-state prediction targets from provider-month model-ready data.

No models are trained here. This script only aligns month t features with month
t+1 outcomes while preserving explicit treatment timing fields.
"""

from __future__ import annotations

import argparse
import os
import sys

import pandas as pd


TARGET_COLUMNS = ["churn_target_tplus1", "income_growth_tplus1", "default_next_cycle"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create future-state model targets.")
    parser.add_argument(
        "--in_path",
        default=os.path.join("data", "model_ready", "provider_month_lagged.csv"),
        help="Input provider-month lagged feature CSV.",
    )
    parser.add_argument(
        "--out_path",
        default=os.path.join("data", "model_ready", "provider_month_future_targets.csv"),
        help="Output provider-month table with t+1 targets.",
    )
    parser.add_argument(
        "--doc_path",
        default=os.path.join("docs", "target_mapping.md"),
        help="Target mapping documentation path.",
    )
    return parser.parse_args()


def require_columns(frame: pd.DataFrame, columns):
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Input table missing required columns: {missing}")


def create_targets(frame: pd.DataFrame) -> pd.DataFrame:
    require_columns(
        frame,
        [
            "merchant_id",
            "month",
            "retention_flag",
            "income_growth_pct",
            "default_flag",
            "treatment_flag",
            "treatment_start_month",
            "intervention_timestamp",
            "months_since_intervention",
            "pre_treatment_flag",
            "post_treatment_flag",
        ],
    )
    panel = frame.sort_values(["merchant_id", "month"]).copy()
    grouped = panel.groupby("merchant_id", sort=False)
    panel["retention_flag_tplus1"] = grouped["retention_flag"].shift(-1)
    panel["churn_target_tplus1"] = (~panel["retention_flag_tplus1"].astype("boolean")).astype("Float64")
    panel["income_growth_tplus1"] = grouped["income_growth_pct"].shift(-1)
    panel["default_next_cycle"] = grouped["default_flag"].shift(-1).astype("boolean").astype("Float64")
    panel["target_month"] = grouped["month"].shift(-1)
    panel["has_tplus1_target"] = panel["target_month"].notna()
    return panel


def validate_targets(frame: pd.DataFrame) -> None:
    missing = [column for column in TARGET_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Future target columns missing: {missing}")

    duplicate_rows = int(frame.duplicated(["merchant_id", "month"]).sum())
    if duplicate_rows:
        raise ValueError(f"Duplicate merchant-month rows found: {duplicate_rows}")

    targetable = frame["has_tplus1_target"]
    missing_counts = frame.loc[targetable, TARGET_COLUMNS].isna().sum()
    bad = missing_counts[missing_counts > 0].to_dict()
    if bad:
        raise ValueError(f"Missing future targets on rows with t+1 month: {bad}")

    treatment_timing = ["treatment_flag", "treatment_start_month", "intervention_timestamp", "months_since_intervention", "pre_treatment_flag", "post_treatment_flag"]
    missing_timing = [column for column in treatment_timing if column not in frame.columns]
    if missing_timing:
        raise ValueError(f"Treatment timing columns missing after target creation: {missing_timing}")


def write_target_mapping(frame: pd.DataFrame, doc_path: str) -> None:
    targetable = frame[frame["has_tplus1_target"]]
    lines = [
        "# Target Mapping",
        "",
        "This document maps leakage-safe provider-month features at month `t` to future-state outcomes at month `t+1`.",
        "",
        "No models are trained in this step.",
        "",
        "## Output",
        "",
        "- Dataset: `data/model_ready/provider_month_future_targets.csv`",
        f"- Rows: {len(frame):,}",
        f"- Rows with t+1 targets: {len(targetable):,}",
        f"- Rows without t+1 targets: {len(frame) - len(targetable):,}",
        "",
        "## Targets",
        "",
        "| Target | Definition | Source month | Notes |",
        "|---|---|---|---|",
        "| `churn_target_tplus1` | `1` if provider is not retained in month `t+1`, else `0` | Future month `t+1` | Derived from next-month `retention_flag`; final panel month is not targetable. |",
        "| `income_growth_tplus1` | Next-month income growth percentage | Future month `t+1` | Derived from next-month `income_growth_pct`. |",
        "| `default_next_cycle` | `1` if next provider-month loan state defaults, else `0` | Future month `t+1` | Derived from next-month `default_flag`; can be filtered to loan-active cases for credit-risk analysis. |",
        "",
        "## Treatment Timing Fields Preserved",
        "",
        "- `treatment_flag`",
        "- `treatment_start_month`",
        "- `intervention_timestamp`",
        "- `months_since_intervention`",
        "- `pre_treatment_flag`",
        "- `post_treatment_flag`",
        "",
        "## Recommended Modeling Use",
        "",
        "- Use rows where `has_tplus1_target == True`.",
        "- Use lagged and rolling predictors from month `t`.",
        "- Exclude same-month outcome variables when training forecasting models.",
        "- Keep treatment timing explicit for DiD, event-study, and post-treatment forecasting designs.",
    ]
    os.makedirs(os.path.dirname(doc_path), exist_ok=True)
    with open(doc_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def main() -> int:
    args = parse_args()
    try:
        frame = pd.read_csv(args.in_path)
        output = create_targets(frame)
        validate_targets(output)
        os.makedirs(os.path.dirname(args.out_path), exist_ok=True)
        output.to_csv(args.out_path, index=False)
        write_target_mapping(output, args.doc_path)
        print(f"Saved future target table to {os.path.abspath(args.out_path)}")
        print(f"Saved target mapping documentation to {os.path.abspath(args.doc_path)}")
        print(f"Rows: {len(output):,}")
        print(f"Rows with t+1 targets: {int(output['has_tplus1_target'].sum()):,}")
        print("Future target validation: PASS")
        return 0
    except Exception as exc:
        print(f"Future target creation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
