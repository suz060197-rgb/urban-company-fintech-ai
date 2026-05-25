"""Model performance dashboard for final dissertation ML artifacts."""

from pathlib import Path
import re
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT_DIR / "docs"
OUTPUT_DIR = ROOT_DIR / "output"
MODELS_FINAL_DIR = OUTPUT_DIR / "models_final"
MODELS_OLD_DIR = OUTPUT_DIR / "models"

if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

from utils.auth import require_login
from utils.theme import apply_theme, page_header, render_sidebar_brand, style_figure
from components.cards import metric_card
from components.status import system_health_panel, operational_alert

MODEL_LABELS = {
    "loan_default_prediction": "Default prediction",
    "churn_prediction": "Churn prediction",
    "embedded_finance_adoption": "Adoption prediction",
    "income_growth_prediction": "Income growth prediction",
}

IMPORTANCE_FILES = {
    "Default prediction": MODELS_FINAL_DIR / "loan_default_prediction_feature_importance.csv",
    "Churn prediction": MODELS_FINAL_DIR / "churn_prediction_feature_importance.csv",
    "Adoption prediction": MODELS_FINAL_DIR / "embedded_finance_adoption_feature_importance.csv",
    "Income growth prediction": MODELS_FINAL_DIR / "income_growth_prediction_feature_importance.csv",
}


st.set_page_config(page_title="Model Performance", layout="wide")


def existing_paths(paths: list[Path]) -> list[Path]:
    return [path for path in paths if path.exists()]


@st.cache_data(show_spinner=False)
def load_metrics() -> tuple[pd.DataFrame, list[str]]:
    warnings = []
    candidates = [
        MODELS_FINAL_DIR / "final_model_metrics.csv",
        OUTPUT_DIR / "model_metrics.csv",
    ]
    available = existing_paths(candidates)
    if not available:
        warnings.append("No model metrics CSV found.")
        return pd.DataFrame(), warnings

    metrics = pd.read_csv(available[0])
    if "split" not in metrics.columns:
        metrics["split"] = "test"

    required = {"model", "metric", "value"}
    missing = required.difference(metrics.columns)
    if missing:
        warnings.append(f"Metrics file is missing columns: {', '.join(sorted(missing))}.")
        return pd.DataFrame(), warnings

    metrics = metrics.assign(
        model_label=metrics["model"].map(MODEL_LABELS).fillna(metrics["model"]),
        metric=metrics["metric"].astype(str).str.lower(),
    )
    return metrics, warnings


def metrics_wide(metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return pd.DataFrame()

    table = (
        metrics.pivot_table(
            index=["model", "model_label"],
            columns="metric",
            values="value",
            aggfunc="first",
        )
        .reset_index()
        .rename_axis(None, axis=1)
    )

    for column in ["roc_auc", "recall", "precision", "accuracy", "f1", "r2"]:
        if column not in table.columns:
            table[column] = np.nan

    return table


@st.cache_data(show_spinner=False)
def load_feature_importance() -> tuple[pd.DataFrame, list[str]]:
    warnings = []
    docs_importance = DOCS_DIR / "feature_importance.csv"
    frames = []

    if docs_importance.exists():
        frame = pd.read_csv(docs_importance)
        if "model" not in frame.columns:
            frame["model"] = "Combined"
        frames.append(frame)
    else:
        warnings.append("docs/feature_importance.csv not found; using output/models_final feature-importance files.")

    for model_label, path in IMPORTANCE_FILES.items():
        if path.exists():
            frame = pd.read_csv(path)
            frame["model"] = model_label
            frames.append(frame)

    if not frames:
        warnings.append("No feature-importance files found.")
        return pd.DataFrame(), warnings

    importance = pd.concat(frames, ignore_index=True)
    expected = {"model", "feature", "importance"}
    missing = expected.difference(importance.columns)
    if missing:
        warnings.append(f"Feature importance data is missing columns: {', '.join(sorted(missing))}.")
        return pd.DataFrame(), warnings

    if "coefficient" not in importance.columns:
        importance["coefficient"] = np.nan

    return importance, warnings


@st.cache_data(show_spinner=False)
def load_markdown_file(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def extract_leakage_controls(final_metrics_doc: str) -> str:
    if not final_metrics_doc:
        return ""
    match = re.search(r"## Leakage Controls\s+(.*?)(?:\n## |\Z)", final_metrics_doc, flags=re.S)
    return match.group(1).strip() if match else ""


def format_metric(value: float, kind: str = "rate") -> str:
    if pd.isna(value):
        return "N/A"
    if kind == "number":
        return f"{value:,.0f}"
    return f"{value:.3f}"


def show_warnings(warnings: list[str]) -> None:
    for message in warnings:
        st.warning(message)


def show_kpi_cards(table: pd.DataFrame) -> None:
    st.subheader("KPI Cards")

    classification = table[table["roc_auc"].notna()].copy()
    if classification.empty:
        st.warning("No classification model metrics available for KPI cards.")
        return

    best_roc_row = classification.loc[classification["roc_auc"].idxmax()]
    best_recall_row = classification.loc[classification["recall"].idxmax()]
    best_precision_row = classification.loc[classification["precision"].idxmax()]
    weakest_row = classification.loc[classification["f1"].fillna(-1).idxmin()]

    cards = st.columns(5)
    cards[0].metric("Best ROC AUC", format_metric(best_roc_row["roc_auc"]))
    cards[1].metric("Best Recall", format_metric(best_recall_row["recall"]))
    cards[2].metric("Best Precision", format_metric(best_precision_row["precision"]))
    cards[3].metric("Strongest Model", str(best_roc_row["model_label"]))
    cards[4].metric("Weakest Model", str(weakest_row["model_label"]))


def show_comparison_table(table: pd.DataFrame) -> None:
    st.subheader("Model Comparison Table")
    if table.empty:
        st.warning("Model comparison table is unavailable.")
        return

    columns = ["model_label", "roc_auc", "recall", "precision", "accuracy", "f1", "r2"]
    display = table[columns].rename(
        columns={
            "model_label": "Model",
            "roc_auc": "ROC AUC",
            "recall": "Recall",
            "precision": "Precision",
            "accuracy": "Accuracy",
            "f1": "F1",
            "r2": "R2",
        }
    )

    numeric_columns = ["ROC AUC", "Recall", "Precision", "Accuracy", "F1", "R2"]
    styled = display.style.highlight_max(subset=numeric_columns, color="#dcfce7", axis=0).format(
        {column: "{:.3f}" for column in numeric_columns},
        na_rep="N/A",
    )
    st.dataframe(styled, hide_index=True, width="stretch")


def show_metrics_download(table: pd.DataFrame) -> None:
    if table.empty:
        return
    st.download_button(
        label="Download Model Metrics CSV",
        data=table.to_csv(index=False).encode("utf-8"),
        file_name="model_metrics.csv",
        mime="text/csv",
        key="download_model_metrics_csv",
    )


def show_roc_chart(table: pd.DataFrame) -> None:
    st.subheader("ROC Comparison")
    roc_data = table[table["roc_auc"].notna()].copy()
    if roc_data.empty:
        st.warning("ROC AUC metrics are unavailable.")
        return

    st.plotly_chart(
        style_figure(px.bar(
            roc_data.sort_values("roc_auc", ascending=False),
            x="model_label",
            y="roc_auc",
            title="Models vs ROC AUC",
            labels={"model_label": "Model", "roc_auc": "ROC AUC"},
        )),
        width="stretch",
        key="model_performance_roc_comparison",
    )


def show_precision_recall(table: pd.DataFrame) -> None:
    st.subheader("Precision vs Recall")
    scatter_data = table[table["precision"].notna() & table["recall"].notna()].copy()
    if scatter_data.empty:
        st.warning("Precision/recall metrics are unavailable.")
        return

    fig = px.scatter(
            scatter_data,
            x="precision",
            y="recall",
            text="model_label",
            size="f1",
            title="Precision vs Recall by Model",
            labels={"precision": "Precision", "recall": "Recall", "model_label": "Model"},
        ).update_traces(textposition="top center")
    st.plotly_chart(
        style_figure(fig),
        width="stretch",
        key="model_performance_precision_recall",
    )


def show_confusion_summary(table: pd.DataFrame) -> None:
    st.subheader("Confusion Matrix Summary")
    confusion_cols = ["tp", "fp", "tn", "fn"]
    available = [column for column in confusion_cols if column in table.columns]
    if len(available) < 4:
        st.warning("Confusion matrix values are unavailable.")
        return

    rows = table[table[confusion_cols].notna().all(axis=1)].copy()
    if rows.empty:
        st.warning("No classification model has complete TP/FP/TN/FN values.")
        return

    for _, row in rows.iterrows():
        with st.expander(str(row["model_label"]), expanded=False):
            cards = st.columns(4)
            cards[0].metric("TP", format_metric(row["tp"], "number"))
            cards[1].metric("FP", format_metric(row["fp"], "number"))
            cards[2].metric("TN", format_metric(row["tn"], "number"))
            cards[3].metric("FN", format_metric(row["fn"], "number"))

            matrix = pd.DataFrame(
                [[row["tn"], row["fp"]], [row["fn"], row["tp"]]],
                index=["Actual Negative", "Actual Positive"],
                columns=["Predicted Negative", "Predicted Positive"],
            )
            fig = go.Figure(
                data=go.Heatmap(
                    z=matrix.values,
                    x=matrix.columns,
                    y=matrix.index,
                    colorscale="Blues",
                    text=matrix.values,
                    texttemplate="%{text:.0f}",
                )
            )
            fig.update_layout(title=f"{row['model_label']} Confusion Matrix")
            st.plotly_chart(
                style_figure(fig),
                width="stretch",
                key=f"model_performance_confusion_{row['model']}",
            )


def show_feature_importance(importance: pd.DataFrame) -> None:
    st.subheader("Feature Importance")
    if importance.empty:
        st.warning("Feature-importance data is unavailable.")
        return

    models = sorted(importance["model"].dropna().unique())
    selected_model = st.selectbox("Select model", models, key="model_performance_importance_model")
    top_n = st.slider("Top drivers", min_value=5, max_value=20, value=10, step=1)

    selected = (
        importance[importance["model"] == selected_model]
        .sort_values("importance", ascending=False)
        .head(top_n)
        .copy()
    )

    st.plotly_chart(
        style_figure(px.bar(
            selected.sort_values("importance"),
            x="importance",
            y="feature",
            orientation="h",
            title=f"Top Drivers: {selected_model}",
        )),
        width="stretch",
        key=f"model_performance_importance_{selected_model.lower().replace(' ', '_')}",
    )

    with st.expander("Feature importance table"):
        st.dataframe(
            selected[["feature", "coefficient", "importance"]],
            hide_index=True,
            width="stretch",
        )


def leakage_risk_rows(leakage_text: str, fallback_controls: str) -> pd.DataFrame:
    rows = [
        {
            "feature": "repayment_ratio",
            "risk_level": "High",
            "commentary": "Critical leakage if repayment behavior is measured after loan outcome.",
        },
        {
            "feature": "repayment_gap_ratio",
            "risk_level": "High",
            "commentary": "Post-outcome repayment information should be excluded from origination-time models.",
        },
        {
            "feature": "treatment_flag / post_treatment_flag",
            "risk_level": "Medium",
            "commentary": "Treatment timing can leak rollout assignment into adoption models.",
        },
        {
            "feature": "working_capital_gap_lag1",
            "risk_level": "Low",
            "commentary": "Lagged cashflow stress is acceptable when observed before the target month.",
        },
        {
            "feature": "payout_delay_days_rolling3",
            "risk_level": "Low",
            "commentary": "Rolling historical settlement performance is prediction-time safe.",
        },
    ]

    text = (leakage_text + "\n" + fallback_controls).lower()
    if "excluded same-period outcomes" in text or "leakage-safe" in text:
        rows.append(
            {
                "feature": "same-period outcomes",
                "risk_level": "Low",
                "commentary": "Final model documentation states same-period outcomes were excluded.",
            }
        )

    return pd.DataFrame(rows)


def show_leakage_audit(leakage_text: str, final_metrics_doc: str) -> None:
    st.subheader("Leakage Audit")
    fallback_controls = extract_leakage_controls(final_metrics_doc)

    if not leakage_text:
        st.warning("docs/leakage_audit.md not found; showing final leakage controls and known risk rules.")

    rows = leakage_risk_rows(leakage_text, fallback_controls)
    risk_order = {"Low": 0, "Medium": 1, "High": 2}
    overall_level = rows["risk_level"].map(risk_order).max()
    overall_label = {0: "Low", 1: "Medium", 2: "High"}.get(overall_level, "Unknown")

    tone = {"Low": "good", "Medium": "warn", "High": "risk"}.get(overall_label, "accent")
    metric_card("Overall Leakage Risk", overall_label, "Feature governance status", "●", tone)
    st.dataframe(rows, hide_index=True, width="stretch")

    with st.expander("Leakage notes"):
        if leakage_text:
            st.markdown(leakage_text)
        elif fallback_controls:
            st.markdown(fallback_controls)
        else:
            st.write("No leakage audit text is available.")


def show_ai_interpretation(table: pd.DataFrame, leakage_text: str, final_metrics_doc: str) -> None:
    st.subheader("AI Interpretation Panel")
    if table.empty:
        st.warning("Model metrics are unavailable for interpretation.")
        return

    classification = table[table["roc_auc"].notna()].copy()
    regression = table[table["r2"].notna()].copy()
    best = classification.loc[classification["roc_auc"].idxmax()] if not classification.empty else None
    weakest = classification.loc[classification["f1"].fillna(-1).idxmin()] if not classification.empty else None
    leakage_rows = leakage_risk_rows(leakage_text, extract_leakage_controls(final_metrics_doc))
    high_leakage = leakage_rows[leakage_rows["risk_level"] == "High"]["feature"].tolist()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Best production model**")
        if best is not None:
            st.write(
                f"{best['model_label']} is strongest by ROC AUC "
                f"({format_metric(best['roc_auc'])})."
            )
        if not regression.empty:
            reg = regression.iloc[0]
            st.write(f"{reg['model_label']} explains growth well with R2 {format_metric(reg['r2'])}.")

    with col2:
        st.markdown("**Weakest model**")
        if weakest is not None:
            st.write(
                f"{weakest['model_label']} is weakest by F1 "
                f"({format_metric(weakest['f1'])}), so thresholding and class imbalance need care."
            )

    with col3:
        st.markdown("**Leakage and business implications**")
        st.write(f"High-risk leakage features to avoid: {', '.join(high_leakage)}.")
        st.write(
            "Use the default model for risk segmentation, the churn model for retention operations, "
            "and the adoption model for product-readiness targeting."
        )


def main() -> None:
    apply_theme()
    render_sidebar_brand("Model Performance")
    page_header(
        "AI Model Health Observatory",
        "Model leaderboard, ROC badges, leakage warnings, feature drivers, and production-readiness signals.",
        "MLOps Intelligence",
    )
    require_login()

    metrics, metric_warnings = load_metrics()
    table = metrics_wide(metrics)
    importance, importance_warnings = load_feature_importance()
    final_metrics_doc = load_markdown_file(DOCS_DIR / "final_model_metrics.md")
    leakage_text = load_markdown_file(DOCS_DIR / "leakage_audit.md")

    with st.expander("Artifact availability", expanded=False):
        artifact_rows = [
            ("docs/final_model_metrics.md", DOCS_DIR / "final_model_metrics.md"),
            ("docs/feature_importance.csv", DOCS_DIR / "feature_importance.csv"),
            ("docs/leakage_audit.md", DOCS_DIR / "leakage_audit.md"),
            ("output/model_metrics.csv", OUTPUT_DIR / "model_metrics.csv"),
            ("output/confusion_matrix.csv", OUTPUT_DIR / "confusion_matrix.csv"),
            ("output/models/", MODELS_OLD_DIR),
            ("output/models_final/", MODELS_FINAL_DIR),
        ]
        st.dataframe(
            pd.DataFrame(
                [
                    {"artifact": label, "available": path.exists(), "resolved_path": str(path)}
                    for label, path in artifact_rows
                ]
            ),
            hide_index=True,
            width="stretch",
        )
        show_warnings(metric_warnings + importance_warnings)

    overview_tab, comparison_tab, confusion_tab, importance_tab, leakage_tab = st.tabs(
        ["Overview", "Comparison", "Confusion Matrix", "Feature Importance", "Leakage Audit"]
    )

    with overview_tab:
        health_cols = st.columns([1, 2])
        with health_cols[0]:
            system_health_panel(0.94, "Model Health Score")
        with health_cols[1]:
            operational_alert(
                "Governance reminder",
                "Use leakage-safe t+1 outputs as decision support with human review for credit-impacting decisions.",
                "warn",
            )
        st.divider()
        show_kpi_cards(table)
        st.divider()
        show_ai_interpretation(table, leakage_text, final_metrics_doc)

    with comparison_tab:
        show_comparison_table(table)
        show_metrics_download(table)
        st.divider()
        left, right = st.columns(2)
        with left:
            show_roc_chart(table)
        with right:
            show_precision_recall(table)

    with confusion_tab:
        show_confusion_summary(table)

    with importance_tab:
        show_feature_importance(importance)

    with leakage_tab:
        show_leakage_audit(leakage_text, final_metrics_doc)


if __name__ == "__main__":
    main()
