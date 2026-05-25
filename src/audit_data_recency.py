"""
Audit date coverage and staleness across project CSV datasets.

The audit scans CSV files recursively, detects date-like columns, reports
earliest/latest dates, monthly coverage, missing monthly periods, and flags
datasets whose latest record is older than 12 months from the audit date.
"""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional
import warnings

import pandas as pd


DATE_COLUMN_NAMES = {"date", "month", "timestamp", "created_at", "updated_at"}


def is_date_like_column(column: str) -> bool:
    lower = column.lower().strip()
    return (
        lower in DATE_COLUMN_NAMES
        or lower.endswith("_date")
        or lower.endswith("_timestamp")
        or lower.endswith("_datetime")
        or lower.endswith("_month")
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate data recency audit.")
    parser.add_argument("--root", default=".", help="Project root.")
    parser.add_argument("--report", default="docs/data_recency_audit.md", help="Markdown report path.")
    parser.add_argument("--today", default="2026-05-23", help="Audit date in YYYY-MM-DD format.")
    return parser.parse_args()


def detect_date_columns(frame: pd.DataFrame) -> Dict[str, pd.Series]:
    detected: Dict[str, pd.Series] = {}
    for column in frame.columns:
        if not is_date_like_column(column):
            continue
        values = frame[column].dropna()
        if values.empty:
            continue
        numeric_values = pd.to_numeric(values, errors="coerce")
        numeric_rate = numeric_values.notna().mean()
        if numeric_rate >= 0.90 and numeric_values.max() < 10000:
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            parsed = pd.to_datetime(values, errors="coerce")
        valid_rate = parsed.notna().mean()
        if valid_rate >= 0.60:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                detected[column] = pd.to_datetime(frame[column], errors="coerce")
    return detected


def preferred_date_column(date_columns: Dict[str, pd.Series]) -> Optional[str]:
    if not date_columns:
        return None
    for exact in ("timestamp", "month", "survey_response_date", "date"):
        if exact in date_columns:
            return exact
    return sorted(date_columns.keys())[0]


def monthly_missing_periods(series: pd.Series) -> Dict[str, object]:
    valid = series.dropna()
    if valid.empty:
        return {
            "coverage_months": 0,
            "observed_months": 0,
            "missing_months": [],
            "coverage_pct": None,
        }

    observed = pd.PeriodIndex(valid.dt.to_period("M").unique()).sort_values()
    expected = pd.period_range(observed.min(), observed.max(), freq="M")
    missing = [str(period) for period in expected.difference(observed)]
    coverage_pct = len(observed) / max(len(expected), 1)
    return {
        "coverage_months": len(expected),
        "observed_months": len(observed),
        "missing_months": missing,
        "coverage_pct": coverage_pct,
    }


def audit_file(path: Path, project_root: Path, stale_cutoff: pd.Timestamp) -> Dict[str, object]:
    row = {
        "dataset": path.relative_to(project_root).as_posix(),
        "rows": None,
        "columns": None,
        "date_columns": "",
        "primary_date_column": "",
        "earliest_date": "",
        "latest_date": "",
        "observed_months": "",
        "coverage_months": "",
        "coverage_pct": "",
        "missing_periods": "",
        "stale_records": "",
        "stale_flag": "No date column",
        "read_status": "OK",
    }
    try:
        frame = pd.read_csv(path, low_memory=False)
    except Exception as exc:  # pragma: no cover - defensive report path
        row["read_status"] = f"FAILED: {type(exc).__name__}: {exc}"
        return row

    row["rows"] = len(frame)
    row["columns"] = len(frame.columns)
    date_columns = detect_date_columns(frame)
    row["date_columns"] = ", ".join(date_columns.keys())
    primary = preferred_date_column(date_columns)
    if primary is None:
        return row

    series = date_columns[primary]
    valid = series.dropna()
    row["primary_date_column"] = primary
    if valid.empty:
        row["stale_flag"] = "No valid dates"
        return row

    earliest = valid.min().normalize()
    latest = valid.max().normalize()
    row["earliest_date"] = earliest.date().isoformat()
    row["latest_date"] = latest.date().isoformat()
    coverage = monthly_missing_periods(series)
    row["observed_months"] = coverage["observed_months"]
    row["coverage_months"] = coverage["coverage_months"]
    row["coverage_pct"] = round(float(coverage["coverage_pct"]), 3)
    row["missing_periods"] = ", ".join(coverage["missing_months"]) if coverage["missing_months"] else "None"
    row["stale_records"] = int((series < stale_cutoff).sum())
    row["stale_flag"] = "STALE >12 months" if latest < stale_cutoff else "Current within 12 months"
    return row


def markdown_table(frame: pd.DataFrame, columns: List[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for _, record in frame[columns].iterrows():
        values = []
        for column in columns:
            value = "" if pd.isna(record[column]) else str(record[column])
            values.append(value.replace("|", "\\|"))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(audit: pd.DataFrame, report_path: Path, today: date, stale_cutoff: pd.Timestamp) -> None:
    date_scanned = audit[audit["primary_date_column"].astype(str).ne("")]
    stale = date_scanned[date_scanned["stale_flag"].eq("STALE >12 months")]
    no_dates = audit[audit["primary_date_column"].astype(str).eq("")]
    missing_periods = date_scanned[date_scanned["missing_periods"].ne("None")]

    lines = [
        "# Data Recency Audit",
        "",
        f"Audit date: {today.isoformat()}",
        f"Stale cutoff: records/datasets with latest date before {stale_cutoff.date().isoformat()} are flagged.",
        "",
        "## Summary",
        "",
        f"- CSV files scanned: {len(audit)}",
        f"- Files with detected date columns: {len(date_scanned)}",
        f"- Files without detected date columns: {len(no_dates)}",
        f"- Files flagged older than 12 months: {len(stale)}",
        f"- Files with missing monthly periods inside their own earliest/latest range: {len(missing_periods)}",
        "",
        "## Recency By Dataset",
        "",
        markdown_table(
            audit,
            [
                "dataset",
                "rows",
                "primary_date_column",
                "earliest_date",
                "latest_date",
                "observed_months",
                "coverage_months",
                "coverage_pct",
                "stale_flag",
            ],
        ),
        "",
        "## Missing Periods",
        "",
    ]
    if missing_periods.empty:
        lines.append("No monthly gaps were detected within each dated dataset's own coverage window.")
    else:
        lines.append(markdown_table(missing_periods, ["dataset", "primary_date_column", "missing_periods"]))

    lines.extend(["", "## Stale Dataset Flags", ""])
    if stale.empty:
        lines.append("No dated datasets are older than 12 months.")
    else:
        lines.append(markdown_table(stale, ["dataset", "latest_date", "stale_flag", "stale_records"]))

    lines.extend(["", "## Files Without Date Columns", ""])
    if no_dates.empty:
        lines.append("Every scanned CSV had at least one detected date-like column.")
    else:
        lines.append(markdown_table(no_dates, ["dataset", "rows", "columns", "read_status"]))

    lines.extend(
        [
            "",
            "## Method",
            "",
            "- Date-like columns were detected from column names containing `date`, `time`, `timestamp`, or `month`.",
            "- A column was treated as date-bearing when at least 60% of non-null values parsed as dates.",
            "- Monthly coverage compares observed months against a continuous month range from earliest to latest date.",
            "- Stale dataset flags are based on each dataset's latest parsed date, not file modification time.",
        ]
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    project_root = Path(args.root).resolve()
    report_path = Path(args.report)
    today = pd.Timestamp(args.today).date()
    stale_cutoff = pd.Timestamp(today) - pd.DateOffset(months=12)

    csv_paths = sorted(project_root.rglob("*.csv"))
    audit = pd.DataFrame([audit_file(path, project_root, stale_cutoff) for path in csv_paths])
    write_report(audit, report_path, today, stale_cutoff)

    print(f"Scanned {len(audit)} CSV files.")
    print(f"Saved data recency audit to {report_path}")
    print(f"Datasets older than 12 months: {(audit['stale_flag'] == 'STALE >12 months').sum()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
