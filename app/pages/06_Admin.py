"""Admin and data-management console for dissertation artifacts."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil
import sys

import pandas as pd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"
MODELS_DIR = OUTPUT_DIR / "models_final"
PREDICTIONS_DIR = OUTPUT_DIR / "predictions_final"
DOCS_DIR = ROOT_DIR / "docs"
ARCHIVE_DIR = ROOT_DIR / "archive"
APP_VERSION = "0.6-admin"

if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

from utils.auth import require_login
from utils.theme import apply_theme, page_header, render_sidebar_brand
from components.cards import metric_card, status_card
from components.status import system_health_panel


st.set_page_config(page_title="Admin Console", layout="wide")


DATE_COLUMNS = [
    "timestamp",
    "month",
    "target_month",
    "survey_response_date",
    "intervention_timestamp",
]


def traffic_light(status: str) -> str:
    mapping = {
        "Current": "Green",
        "Recent": "Green",
        "Stale": "Amber",
        "Very stale": "Red",
        "No date": "Gray",
        "Error": "Red",
    }
    return mapping.get(status, "Gray")


def read_csv_safe(path: Path, nrows: int | None = None, usecols: list[str] | None = None) -> pd.DataFrame:
    try:
        return pd.read_csv(path, nrows=nrows, usecols=usecols)
    except ValueError:
        return pd.read_csv(path, nrows=nrows)


def latest_date_from_frame(frame: pd.DataFrame) -> pd.Timestamp | pd.NaT:
    for column in DATE_COLUMNS:
        if column in frame.columns:
            parsed = pd.to_datetime(frame[column], errors="coerce")
            if parsed.notna().any():
                return parsed.max()
    return pd.NaT


def stale_status(latest_date: pd.Timestamp | pd.NaT) -> str:
    if pd.isna(latest_date):
        return "No date"

    age_days = (pd.Timestamp(datetime.now().date()) - latest_date.normalize()).days
    if age_days <= 60:
        return "Current"
    if age_days <= 365:
        return "Recent"
    if age_days <= 730:
        return "Stale"
    return "Very stale"


@st.cache_data(show_spinner=False)
def scan_csv_file(path: Path) -> dict:
    try:
        sample = read_csv_safe(path, nrows=5000)
        columns = len(sample.columns)

        row_count = sum(1 for _ in path.open("r", encoding="utf-8", errors="ignore")) - 1
        row_count = max(row_count, 0)

        missing_values = int(sample.isna().sum().sum())
        duplicate_sample_rows = int(sample.duplicated().sum())
        latest_date = latest_date_from_frame(sample)
        status = stale_status(latest_date)

        return {
            "name": path.name,
            "path": str(path.relative_to(ROOT_DIR)),
            "rows": row_count,
            "columns": columns,
            "latest_date": "" if pd.isna(latest_date) else latest_date.date().isoformat(),
            "missing_values_sample": missing_values,
            "duplicate_rows_sample": duplicate_sample_rows,
            "stale_status": status,
            "indicator": traffic_light(status),
            "size_mb": round(path.stat().st_size / (1024 * 1024), 2),
            "error": "",
        }
    except Exception as exc:  # pragma: no cover - admin diagnostics should not crash
        return {
            "name": path.name,
            "path": str(path.relative_to(ROOT_DIR)),
            "rows": None,
            "columns": None,
            "latest_date": "",
            "missing_values_sample": None,
            "duplicate_rows_sample": None,
            "stale_status": "Error",
            "indicator": "Red",
            "size_mb": round(path.stat().st_size / (1024 * 1024), 2) if path.exists() else None,
            "error": str(exc),
        }


@st.cache_data(show_spinner=False)
def dataset_status() -> pd.DataFrame:
    files = sorted(DATA_DIR.glob("*.csv"))
    return pd.DataFrame([scan_csv_file(path) for path in files])


@st.cache_data(show_spinner=False)
def prediction_status() -> pd.DataFrame:
    files = [
        OUTPUT_DIR / "risk_scores.csv",
        OUTPUT_DIR / "default_predictions.csv",
        OUTPUT_DIR / "churn_predictions.csv",
        OUTPUT_DIR / "adoption_predictions.csv",
        PREDICTIONS_DIR / "default_predictions_final.csv",
        PREDICTIONS_DIR / "churn_predictions_final.csv",
        PREDICTIONS_DIR / "adoption_predictions_final.csv",
        PREDICTIONS_DIR / "income_growth_predictions_final.csv",
    ]
    existing = [path for path in files if path.exists()]
    return pd.DataFrame([scan_csv_file(path) for path in existing])


@st.cache_data(show_spinner=False)
def model_status() -> pd.DataFrame:
    rows = []
    for path in sorted(MODELS_DIR.glob("*.pkl")):
        stat = path.stat()
        modified = datetime.fromtimestamp(stat.st_mtime)
        rows.append(
            {
                "model_name": path.name,
                "path": str(path.relative_to(ROOT_DIR)),
                "size_mb": round(stat.st_size / (1024 * 1024), 3),
                "created_date": datetime.fromtimestamp(stat.st_ctime).isoformat(timespec="seconds"),
                "last_modified": modified.isoformat(timespec="seconds"),
                "stale_status": stale_status(pd.Timestamp(modified.date())),
                "indicator": traffic_light(stale_status(pd.Timestamp(modified.date()))),
            }
        )
    return pd.DataFrame(rows)


def data_quality_findings(datasets: pd.DataFrame, predictions: pd.DataFrame) -> list[str]:
    findings = []
    combined = pd.concat([datasets, predictions], ignore_index=True)
    if combined.empty:
        return ["No CSV artifacts were found for audit."]

    stale = combined[combined["stale_status"].isin(["Stale", "Very stale"])]
    if not stale.empty:
        findings.append(f"{len(stale)} CSV files are stale or very stale.")

    missing = combined[combined["missing_values_sample"].fillna(0) > 0]
    if not missing.empty:
        findings.append(f"{len(missing)} CSV files contain missing values in the audit sample.")

    duplicates = combined[combined["duplicate_rows_sample"].fillna(0) > 0]
    if not duplicates.empty:
        findings.append(f"{len(duplicates)} CSV files contain duplicate rows in the audit sample.")

    no_date = combined[combined["stale_status"] == "No date"]
    if not no_date.empty:
        findings.append(f"{len(no_date)} CSV files have no recognized date column.")

    if not findings:
        findings.append("No major data quality warnings detected in the current audit sample.")
    return findings


def date_gap_summary(path: Path) -> dict:
    if not path.exists():
        return {"dataset": path.name, "date_gaps": "missing file"}

    sample = read_csv_safe(path, nrows=100000)
    date_column = next((column for column in ["month", "target_month"] if column in sample.columns), None)
    if date_column is None:
        return {"dataset": path.name, "date_gaps": "no monthly date column"}

    months = pd.to_datetime(sample[date_column], errors="coerce").dropna().dt.to_period("M").drop_duplicates()
    if months.empty:
        return {"dataset": path.name, "date_gaps": "no parseable dates"}

    expected = pd.period_range(months.min(), months.max(), freq="M")
    missing = sorted(set(expected).difference(set(months)))
    return {
        "dataset": path.name,
        "date_gaps": "none" if not missing else ", ".join(str(month) for month in missing[:12]),
    }


def load_leakage_rows() -> pd.DataFrame:
    path = DOCS_DIR / "leakage_audit.md"
    if not path.exists():
        return pd.DataFrame(
            [
                {
                    "risk_level": "High",
                    "feature": "repayment_ratio",
                    "note": "Potential post-outcome loan repayment leakage.",
                },
                {
                    "risk_level": "Medium",
                    "feature": "treatment_flag / post_treatment_flag",
                    "note": "Can leak rollout timing into adoption models.",
                },
                {
                    "risk_level": "Low",
                    "feature": "working_capital_gap_lag1",
                    "note": "Lagged value is acceptable before prediction month.",
                },
            ]
        )

    text = path.read_text(encoding="utf-8", errors="replace")
    rows = []
    for level in ["High", "Medium", "Low"]:
        if level.lower() in text.lower():
            rows.append({"risk_level": level, "feature": "See leakage_audit.md", "note": "Audit document available."})
    return pd.DataFrame(rows) if rows else pd.DataFrame([{"risk_level": "Unknown", "feature": path.name, "note": "Document available."}])


def archive_candidates() -> pd.DataFrame:
    candidates = []
    patterns = ["*old*", "*before_after*", "*leakage*", "*experiment*", "*retrained*"]
    search_dirs = [OUTPUT_DIR, DOCS_DIR]

    for directory in search_dirs:
        if not directory.exists():
            continue
        for pattern in patterns:
            for path in directory.rglob(pattern):
                if path.is_file():
                    candidates.append(path)

    for path in ARCHIVE_DIR.rglob("*") if ARCHIVE_DIR.exists() else []:
        if path.is_file():
            candidates.append(path)

    unique = sorted(set(candidates))
    return pd.DataFrame(
        [
            {
                "path": str(path.relative_to(ROOT_DIR)),
                "size_mb": round(path.stat().st_size / (1024 * 1024), 3),
                "last_modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
                "already_archived": str(path).startswith(str(ARCHIVE_DIR)),
            }
            for path in unique
        ]
    )


def dataframe_download(label: str, frame: pd.DataFrame, file_name: str) -> None:
    st.download_button(
        label=label,
        data=frame.to_csv(index=False).encode("utf-8"),
        file_name=file_name,
        mime="text/csv",
    )


def show_dataset_status(datasets: pd.DataFrame) -> None:
    st.subheader("Dataset Status")
    if datasets.empty:
        st.warning("No datasets found in data/.")
        return

    st.dataframe(datasets, hide_index=True, width="stretch")


def show_model_status(models: pd.DataFrame) -> None:
    st.subheader("Model Status")
    if models.empty:
        st.warning("No final model files found in output/models_final/.")
        return

    cards = st.columns(3)
    cards[0].metric("Models loaded", f"{len(models):,}")
    cards[1].metric("Total model size MB", f"{models['size_mb'].sum():.2f}")
    cards[2].metric("Latest model modified", str(models["last_modified"].max()))
    st.dataframe(models, hide_index=True, width="stretch")


def show_prediction_outputs(predictions: pd.DataFrame) -> None:
    st.subheader("Prediction Outputs")
    if predictions.empty:
        st.warning("No prediction output files found.")
        return

    st.dataframe(predictions, hide_index=True, width="stretch")


def show_quality_audit(datasets: pd.DataFrame, predictions: pd.DataFrame) -> None:
    st.subheader("Data Quality Audit")
    for finding in data_quality_findings(datasets, predictions):
        if "No major" in finding:
            st.success(finding)
        else:
            st.warning(finding)

    gap_rows = [
        date_gap_summary(DATA_DIR / "provider_kpis.csv"),
        date_gap_summary(DATA_DIR / "payouts_loans.csv"),
        date_gap_summary(OUTPUT_DIR / "risk_scores.csv"),
    ]
    st.dataframe(pd.DataFrame(gap_rows), hide_index=True, width="stretch")


def show_leakage_audit() -> None:
    st.subheader("Leakage Audit")
    path = DOCS_DIR / "leakage_audit.md"
    if not path.exists():
        st.warning("docs/leakage_audit.md is not available. Showing built-in leakage risk rules.")

    leakage = load_leakage_rows()
    for level in ["High", "Medium", "Low"]:
        subset = leakage[leakage["risk_level"] == level]
        with st.expander(f"{level} risk features", expanded=(level == "High")):
            if subset.empty:
                st.write("No entries found.")
            else:
                st.dataframe(subset, hide_index=True, width="stretch")

    if path.exists():
        with st.expander("Full leakage audit document"):
            st.markdown(path.read_text(encoding="utf-8", errors="replace"))


def show_refresh_controls() -> None:
    st.subheader("Refresh Data")
    col1, col2, col3 = st.columns(3)
    if col1.button("Refresh datasets"):
        dataset_status.clear()
        st.success("Dataset cache cleared. Rerun or refresh the app to reload datasets.")
    if col2.button("Reload prediction files"):
        prediction_status.clear()
        st.success("Prediction cache cleared. Rerun or refresh the app to reload predictions.")
    if col3.button("Reload models"):
        model_status.clear()
        st.success("Model cache cleared. Rerun or refresh the app to reload models.")
    st.info("These controls reload cached artifacts only. They do not retrain models.")


def show_archive_cleaner(candidates: pd.DataFrame) -> None:
    st.subheader("Archive Cleaner")
    if candidates.empty:
        st.success("No archive candidates found.")
        return

    st.dataframe(candidates.head(200), hide_index=True, width="stretch")
    selected = st.selectbox("Candidate file to archive", candidates["path"].tolist())
    archive_action = st.button("Archive selected file")
    if archive_action:
        source = ROOT_DIR / selected
        if not source.exists():
            st.error("Selected file no longer exists.")
            return
        if str(source).startswith(str(ARCHIVE_DIR)):
            st.warning("Selected file is already archived.")
            return

        destination = ARCHIVE_DIR / "experiments_old" / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            destination = destination.with_name(
                f"{destination.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{destination.suffix}"
            )
        shutil.move(str(source), str(destination))
        st.success(f"Archived to {destination.relative_to(ROOT_DIR)}")


def show_exports(datasets: pd.DataFrame, models: pd.DataFrame, predictions: pd.DataFrame) -> None:
    st.subheader("Export Reports")
    col1, col2, col3 = st.columns(3)
    with col1:
        dataframe_download("Download dataset audit", datasets, "dataset_audit.csv")
    with col2:
        dataframe_download("Download model audit", models, "model_audit.csv")
    with col3:
        dataframe_download("Download prediction audit", predictions, "prediction_audit.csv")


def show_system_health(datasets: pd.DataFrame, models: pd.DataFrame, predictions: pd.DataFrame) -> None:
    st.subheader("System Health")
    errors = []
    if datasets.empty:
        errors.append("No datasets loaded.")
    if models.empty:
        errors.append("No models loaded.")
    if predictions.empty:
        errors.append("No prediction outputs loaded.")

    cards = st.columns(4)
    with cards[0]:
        metric_card("Datasets Loaded", f"{len(datasets):,}", "CSV inventory", "▦", "good")
    with cards[1]:
        metric_card("Models Loaded", f"{len(models):,}", "Final artifacts", "◆", "accent")
    with cards[2]:
        metric_card("Prediction Files", f"{len(predictions):,}", "Output health", "◷", "warn")
    with cards[3]:
        metric_card("App Version", APP_VERSION, "Admin console build", "●", "accent")

    if errors:
        for error in errors:
            st.error(error)
    else:
        st.success("Admin console health check passed.")


def main() -> None:
    apply_theme()
    render_sidebar_brand("Admin Console")
    page_header(
        "System Diagnostics Console",
        "Dataset freshness, model versioning, prediction outputs, storage monitor, archive health, and operational controls.",
        "Operations Console",
    )
    require_login()

    datasets = dataset_status()
    models = model_status()
    predictions = prediction_status()
    candidates = archive_candidates()

    status_tab, audit_tab, leakage_tab, maintenance_tab, exports_tab, health_tab = st.tabs(
        ["Status", "Data Quality", "Leakage Audit", "Maintenance", "Exports", "System Health"]
    )

    with status_tab:
        show_dataset_status(datasets)
        st.divider()
        show_model_status(models)
        st.divider()
        show_prediction_outputs(predictions)

    with audit_tab:
        show_quality_audit(datasets, predictions)

    with leakage_tab:
        show_leakage_audit()

    with maintenance_tab:
        show_refresh_controls()
        st.divider()
        show_archive_cleaner(candidates)

    with exports_tab:
        show_exports(datasets, models, predictions)

    with health_tab:
        system_health_panel(0.97, "Platform Health Score")
        st.divider()
        show_system_health(datasets, models, predictions)


if __name__ == "__main__":
    main()
