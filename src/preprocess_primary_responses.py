"""
Clean the primary survey workbook into an analysis-ready CSV.

The script intentionally reads .xlsx files through the Python standard library
so the project does not need dependencies beyond the approved package set.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd


MISSING_VALUES = {"", "NULL", "NA", "N/A", "NONE", "NOT APPLICABLE", "NAN"}
TEXT_REPLACEMENTS = {
    "â‚¹": "Rs ",
    "₹": "Rs ",
    "â€“": "-",
    "–": "-",
    "—": "-",
    "\u00a0": " ",
}

LIKERT_COLUMNS = [
    "Digital_Adoption_Score",
    "Cashflow_Issues",
    "Settlement_Delay_Impact",
    "Faster_Payout_Impact",
    "Business_Growth_After_Digital",
    "Repeat_Customer_Change",
]

FREQUENCY_MAP = {
    "never": 0,
    "no": 0,
    "rarely": 1,
    "monthly": 2,
    "sometimes": 2,
    "weekly": 3,
    "often": 4,
    "daily": 5,
    "always": 5,
}

BUSINESS_TYPE_MAP = {
    "beauty & salon services": "beauty_wellness",
    "cleaning": "home_cleaning",
    "electrician": "plumbing_electrical",
    "plumber": "plumbing_electrical",
    "technician": "appliance_repair",
    "painter": "home_services_other",
    "masseuse": "beauty_wellness",
    "insta help": "home_cleaning",
}

CITY_REGION_MAP = {
    "mumbai": "West",
    "thane": "West",
    "navi mumbai": "West",
    "pune": "West",
    "surat": "West",
    "indore": "West",
    "bangalore": "South",
    "bengaluru": "South",
    "hyderabad": "South",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preprocess primary survey responses.")
    parser.add_argument("--input", default=os.path.join("data", "survey_data.csv.xlsx"))
    parser.add_argument("--output", default=os.path.join("data", "primary_responses_clean.csv"))
    parser.add_argument("--quotes", default=os.path.join("data", "primary_interview_quotes.csv"))
    parser.add_argument("--report", default=os.path.join("docs", "primary_cleaning_report.md"))
    return parser.parse_args()


def col_to_idx(cell_ref: str) -> int:
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    idx = 0
    for ch in letters:
        idx = idx * 26 + ord(ch.upper()) - 64
    return idx - 1


def read_xlsx_first_sheet(path: str) -> pd.DataFrame:
    ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with ZipFile(path) as zf:
        shared_strings: List[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            shared_root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            for si in shared_root.findall("main:si", ns):
                parts = []
                for text in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"):
                    parts.append(text.text or "")
                shared_strings.append("".join(parts))

        sheet_root = ET.fromstring(zf.read("xl/worksheets/sheet1.xml"))
        rows: List[List[str]] = []
        for row in sheet_root.findall("main:sheetData/main:row", ns):
            values: List[str] = []
            for cell in row.findall("main:c", ns):
                idx = col_to_idx(cell.attrib.get("r", "A1"))
                while len(values) <= idx:
                    values.append("")
                value_node = cell.find("main:v", ns)
                value = "" if value_node is None else value_node.text or ""
                if cell.attrib.get("t") == "s" and value != "":
                    value = shared_strings[int(value)]
                values[idx] = value
            rows.append(values)

    if not rows:
        return pd.DataFrame()
    headers = rows[0]
    normalized_rows = []
    for row in rows[1:]:
        padded = row + [""] * (len(headers) - len(row))
        normalized_rows.append(padded[: len(headers)])
    return pd.DataFrame(normalized_rows, columns=headers)


def standardize_column_name(value: str) -> str:
    text = clean_text(value).lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def clean_text(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    for old, new in TEXT_REPLACEMENTS.items():
        text = text.replace(old, new)
    if text.upper() in MISSING_VALUES:
        return ""
    return " ".join(text.split())


def prepare_raw_frame(raw: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    stats = {
        "raw_rows": len(raw),
        "raw_columns": len(raw.columns),
        "blank_rows_removed": 0,
        "blank_columns_removed": 0,
        "duplicate_rows_removed": 0,
        "duplicate_respondent_ids_removed": 0,
    }

    prepared = raw.copy()
    prepared.columns = [clean_text(column) for column in prepared.columns]
    prepared = prepared.map(clean_text)

    blank_columns = prepared.columns[(prepared == "").all(axis=0)].tolist()
    if blank_columns:
        prepared = prepared.drop(columns=blank_columns)
    stats["blank_columns_removed"] = len(blank_columns)

    blank_row_mask = (prepared == "").all(axis=1)
    stats["blank_rows_removed"] = int(blank_row_mask.sum())
    prepared = prepared.loc[~blank_row_mask].copy()

    before = len(prepared)
    prepared = prepared.drop_duplicates().copy()
    stats["duplicate_rows_removed"] = before - len(prepared)

    if "Respondent_ID" in prepared.columns:
        before = len(prepared)
        prepared = prepared.drop_duplicates(subset=["Respondent_ID"], keep="first").copy()
        stats["duplicate_respondent_ids_removed"] = before - len(prepared)

    stats["cleaned_raw_rows"] = len(prepared)
    stats["cleaned_raw_columns"] = len(prepared.columns)
    stats["standardized_output_columns"] = len({standardize_column_name(column) for column in prepared.columns})
    return prepared.reset_index(drop=True), stats


def normalize_category(value: str) -> str:
    text = clean_text(value).lower()
    return BUSINESS_TYPE_MAP.get(text, text.replace(" ", "_").replace("&", "and"))


def normalize_city(value: str) -> str:
    text = clean_text(value).lower()
    if not text:
        return ""
    return " ".join(part.capitalize() for part in text.split())


def derive_region(city: str) -> str:
    return CITY_REGION_MAP.get(clean_text(city).lower(), "Unknown")


def extract_numbers(value: str) -> List[float]:
    text = clean_text(value).replace(",", "")
    return [float(match) for match in re.findall(r"\d+(?:\.\d+)?", text)]


def midpoint_from_range(value: str, above_multiplier: float = 1.125) -> float:
    text = clean_text(value).lower()
    if not text:
        return np.nan
    nums = extract_numbers(text)
    if len(nums) >= 2:
        return float((nums[0] + nums[1]) / 2)
    if len(nums) == 1:
        if "above" in text or "+" in text or "& above" in text:
            return float(nums[0] * above_multiplier)
        if "below" in text or "less" in text:
            return float(nums[0] / 2)
        return float(nums[0])
    return np.nan


def yes_no_binary(value: str) -> float:
    text = clean_text(value).lower()
    if not text:
        return np.nan
    if text in {"yes", "y", "true", "1"}:
        return 1.0
    if text in {"no", "n", "false", "0"}:
        return 0.0
    return np.nan


def frequency_score(value: str) -> float:
    text = clean_text(value).lower()
    return float(FREQUENCY_MAP.get(text, np.nan))


def likert_score(value: str) -> float:
    nums = extract_numbers(value)
    if not nums:
        return np.nan
    score = nums[0]
    if 1 <= score <= 5:
        return float(score)
    return np.nan


def scale_0_1(value: float, min_value: float, max_value: float) -> float:
    if pd.isna(value):
        return np.nan
    return float((value - min_value) / (max_value - min_value))


def excel_serial_to_date(value: str) -> str:
    nums = extract_numbers(value)
    if not nums:
        return ""
    serial = int(nums[0])
    # Excel's Windows date system includes the 1900 leap-year bug; this offset
    # reproduces normal spreadsheet date conversion for modern serials.
    date_value = datetime(1899, 12, 30) + timedelta(days=serial)
    return date_value.date().isoformat()


def normalize_payment_methods(value: str) -> Tuple[str, int, int, int, int]:
    text = clean_text(value).lower()
    methods = []
    has_upi = int("upi" in text)
    has_cash = int("cash" in text)
    has_card = int("card" in text)
    has_wallet = int("wallet" in text or "paytm" in text or "phonepe" in text or "google pay" in text)
    if has_upi:
        methods.append("upi")
    if has_cash:
        methods.append("cash")
    if has_card:
        methods.append("card")
    if has_wallet:
        methods.append("wallet")
    return ";".join(methods), has_upi, has_cash, has_card, has_wallet


def build_clean_frame(raw: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    city = raw["City"].map(normalize_city)
    experience_years = pd.to_numeric(raw["Experience_Years"].map(clean_text), errors="coerce")
    payment_parts = raw["Payment_Methods"].map(normalize_payment_methods)
    upi_frequency_score = raw["UPI_Usage_Frequency"].map(frequency_score)

    clean_columns = {
        "respondent_id": raw["Respondent_ID"].map(clean_text),
        "data_type": raw["Data_Type"].map(lambda x: clean_text(x).lower()),
        "respondent_category": raw["Respondent_Category"].map(clean_text),
        "business_type_raw": raw["Business_Type"].map(clean_text),
        "business_type": raw["Business_Type"].map(normalize_category),
        "city": city,
        "region": city.map(derive_region),
        "experience_years": experience_years,
        "tenure_days_estimate": experience_years * 365,
        "monthly_income_range_raw": raw["Monthly_Income_Range"].map(clean_text),
        "monthly_income_midpoint": raw["Monthly_Income_Range"].map(midpoint_from_range),
        "monthly_transaction_volume_raw": raw["Monthly_Transaction_Volume"].map(clean_text),
        "monthly_transaction_estimate": raw["Monthly_Transaction_Volume"].map(
            lambda x: midpoint_from_range(x, above_multiplier=1.125)
        ),
        "payment_methods_standardized": payment_parts.map(lambda x: x[0]),
        "uses_upi_flag": payment_parts.map(lambda x: x[1]),
        "uses_cash_flag": payment_parts.map(lambda x: x[2]),
        "uses_card_flag": payment_parts.map(lambda x: x[3]),
        "uses_wallet_flag": payment_parts.map(lambda x: x[4]),
        "upi_usage_frequency_raw": raw["UPI_Usage_Frequency"].map(clean_text),
        "upi_usage_frequency_score": upi_frequency_score,
        "upi_usage_frequency_scaled": upi_frequency_score.map(lambda x: scale_0_1(x, 0, 5)),
        "needed_business_credit_binary": raw["Needed_Business_Credit"].map(yes_no_binary),
        "approx_credit_amount_raw": raw["Approx_Credit_Amount"].map(clean_text),
        "approx_credit_amount_numeric": raw["Approx_Credit_Amount"].map(midpoint_from_range),
        "credit_purpose": raw["Credit_Purpose"].map(lambda x: clean_text(x).lower()),
        "ai_tool_usage_binary": raw["AI_Tool_Usage"].map(yes_no_binary),
        "automation_usage": raw["Automation_Usage"].map(lambda x: clean_text(x).lower()),
        "platform_used_raw": raw["Platform_Used"].map(clean_text),
        "key_pain_points": raw["Key_Pain_Points"].map(lambda x: clean_text(x).lower()),
        "survey_response_date": raw["Survey_Response_Date"].map(excel_serial_to_date),
    }

    for column in LIKERT_COLUMNS:
        clean_name = column.lower()
        likert = raw[column].map(likert_score)
        clean_columns[f"{clean_name}_likert"] = likert
        clean_columns[f"{clean_name}_scaled"] = likert.map(lambda x: scale_0_1(x, 1, 5))

    clean = pd.DataFrame(clean_columns)

    quote_frame = pd.DataFrame(
        {
            "respondent_id": clean["respondent_id"],
            "data_type": clean["data_type"],
            "interview_quote": raw["Interview_Quote"].map(clean_text),
            "key_pain_points": clean["key_pain_points"],
        }
    )
    clean = clean.assign(has_interview_quote=quote_frame["interview_quote"].ne("").astype(int))
    return clean, quote_frame[quote_frame["interview_quote"].ne("")].copy()


def validate_clean_frame(clean: pd.DataFrame) -> List[str]:
    messages = []
    required = [
        "respondent_id",
        "monthly_income_midpoint",
        "monthly_transaction_estimate",
        "needed_business_credit_binary",
        "upi_usage_frequency_score",
        "digital_adoption_score_likert",
        "ai_tool_usage_binary",
    ]
    missing_columns = [column for column in required if column not in clean.columns]
    if missing_columns:
        messages.append(f"FAIL missing required cleaned columns: {missing_columns}")
    else:
        messages.append("PASS required cleaned columns are present.")

    if clean["respondent_id"].duplicated().any():
        messages.append("FAIL duplicate respondent_id values detected.")
    else:
        messages.append("PASS respondent_id values are unique.")

    for column in [col for col in clean.columns if col.endswith("_likert")]:
        valid = clean[column].dropna().between(1, 5).all()
        messages.append(("PASS" if valid else "FAIL") + f" {column} values are within 1-5.")

    for column in [col for col in clean.columns if col.endswith("_scaled")]:
        valid = clean[column].dropna().between(0, 1).all()
        messages.append(("PASS" if valid else "FAIL") + f" {column} values are within 0-1.")

    for column in ["needed_business_credit_binary", "ai_tool_usage_binary"]:
        valid_values = set(clean[column].dropna().unique()).issubset({0.0, 1.0})
        messages.append(("PASS" if valid_values else "FAIL") + f" {column} is binary.")
    return messages


def markdown_table(frame: pd.DataFrame, index_name: str = "") -> str:
    table = frame.copy()
    table.insert(0, index_name or "field", table.index.astype(str))
    headers = list(table.columns)
    lines = [
        "| " + " | ".join(str(header) for header in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for _, row in table.iterrows():
        values = [str(row[header]) for header in headers]
        values = [value.replace("|", "\\|") for value in values]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(
    raw: pd.DataFrame,
    clean: pd.DataFrame,
    quotes: pd.DataFrame,
    validation: List[str],
    report_path: str,
    cleaning_stats: Dict[str, int],
) -> None:
    numeric_summary = clean[
        [
            "experience_years",
            "monthly_income_midpoint",
            "monthly_transaction_estimate",
            "upi_usage_frequency_score",
            "needed_business_credit_binary",
            "approx_credit_amount_numeric",
            "ai_tool_usage_binary",
        ]
    ].describe().round(2)
    missing_summary = clean.isna().sum().sort_values(ascending=False)
    category_summary = {
        "business_type": clean["business_type"].value_counts().to_dict(),
        "city": clean["city"].value_counts().to_dict(),
        "region": clean["region"].value_counts().to_dict(),
        "data_type": clean["data_type"].value_counts().to_dict(),
    }

    lines = [
        "# Primary Response Cleaning Report",
        "",
        f"Generated on {datetime.now().date().isoformat()}.",
        "",
        "## Input And Output",
        "",
        f"- Raw input rows: {cleaning_stats['raw_rows']}",
        f"- Raw input columns: {cleaning_stats['raw_columns']}",
        f"- Blank rows removed: {cleaning_stats['blank_rows_removed']}",
        f"- Blank columns removed: {cleaning_stats['blank_columns_removed']}",
        f"- Duplicate full rows removed: {cleaning_stats['duplicate_rows_removed']}",
        f"- Duplicate respondent IDs removed: {cleaning_stats['duplicate_respondent_ids_removed']}",
        f"- Prepared raw rows after cleaning: {len(raw)}",
        f"- Clean output rows: {len(clean)}",
        f"- Clean output columns: {len(clean.columns)}",
        f"- Preserved interview quotes: {len(quotes)}",
        "",
        "Outputs:",
        "",
        "- `data/primary_responses_clean.csv`",
        "- `data/primary_interview_quotes.csv`",
        "",
        "## Cleaning Rules Applied",
        "",
        "- Income ranges were converted to numeric midpoint rupee estimates.",
        "- Monthly transaction ranges were converted to numeric midpoint estimates.",
        "- Yes/No variables were converted to binary values: Yes = 1, No = 0.",
        "- Daily/Weekly-style frequency variables were converted to ordinal scores.",
        "- Likert variables were preserved on a 1-5 scale and standardized to 0-1 scaled fields.",
        "- Missing values such as blank, `NULL`, `NA`, and `Not applicable` were treated as missing.",
        "- Blank rows and blank columns were removed before transformation.",
        "- Duplicate full rows and duplicate respondent IDs were removed, keeping the first observed response.",
        "- City and business category values were normalized to consistent labels.",
        "- Output column names were standardized to lower snake_case.",
        "- Interview quotes were excluded from the main analytical table and preserved separately.",
        "",
        "## Validation Results",
        "",
    ]
    lines.extend([f"- {message}" for message in validation])
    lines.extend(
        [
            "",
            "## Numeric Summary",
            "",
            markdown_table(numeric_summary, "statistic"),
            "",
            "## Missing Value Summary",
            "",
            markdown_table(missing_summary.to_frame("missing_count"), "column"),
            "",
            "## Category Summary",
            "",
        ]
    )
    for name, counts in category_summary.items():
        lines.append(f"### {name}")
        lines.append("")
        for key, value in counts.items():
            lines.append(f"- {key}: {value}")
        lines.append("")
    Path(report_path).write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    raw_source = read_xlsx_first_sheet(args.input)
    raw, cleaning_stats = prepare_raw_frame(raw_source)
    clean, quotes = build_clean_frame(raw)
    validation = validate_clean_frame(clean)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.quotes).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(args.output, index=False, quoting=csv.QUOTE_MINIMAL)
    quotes.to_csv(args.quotes, index=False, quoting=csv.QUOTE_MINIMAL)
    write_report(raw, clean, quotes, validation, args.report, cleaning_stats)

    print(f"Saved cleaned primary responses to {args.output}")
    print(f"Saved interview quotes to {args.quotes}")
    print(f"Saved cleaning report to {args.report}")
    for message in validation:
        print(message)
    if any(message.startswith("FAIL") for message in validation):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
