"""Streamlit home page for the dissertation AI application."""

from pathlib import Path
import sys

import pandas as pd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]
APP_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"

if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

from utils.auth import render_auth_controls
from utils.theme import apply_theme, page_header, render_sidebar_brand
from components.cards import ai_panel, metric_card, status_card
from components.status import system_health_panel


st.set_page_config(
    page_title="Razorpay Embedded Finance Dissertation App",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def load_home_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    merchants = pd.read_csv(DATA_DIR / "merchants.csv")
    provider_kpis = pd.read_csv(DATA_DIR / "provider_kpis.csv")
    risk_scores = pd.read_csv(OUTPUT_DIR / "risk_scores.csv")
    return merchants, provider_kpis, risk_scores


def format_percent(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:.1%}"


def main() -> None:
    apply_theme()
    render_sidebar_brand("Home")
    render_auth_controls()

    page_header(
        "Urban Company Future Intelligence Platform",
        "AI-powered risk, growth, and embedded finance insights for service professionals.",
        "Service Provider AI Operating System",
    )

    try:
        merchants, provider_kpis, risk_scores = load_home_data()
    except FileNotFoundError as exc:
        st.error(f"Missing required project artifact: {exc.filename}")
        st.stop()

    provider_count = merchants["merchant_id"].nunique()
    high_risk_pct = (risk_scores["risk_band"].str.lower() == "high").mean()
    retention_pct = provider_kpis["retention_flag"].astype(bool).mean()

    metric_cols = st.columns(4)
    with metric_cols[0]:
        metric_card("Provider Count", f"{provider_count:,}", "↑ Active synthetic provider base", "▦", "accent")
    with metric_cols[1]:
        metric_card("High Risk %", format_percent(high_risk_pct), "↓ Monitor credit stress", "▲", "risk")
    with metric_cols[2]:
        metric_card("Retention %", format_percent(retention_pct), "↑ Retention health indicator", "●", "good")
    with metric_cols[3]:
        system_health_panel(0.96)

    st.divider()
    left, right = st.columns([1.3, 1])
    with left:
        ai_panel(
            "AI Operating System Brief",
            "Provider risk, retention, adoption, model health, and survey signals are unified into one executive intelligence surface.",
            "Ask the data: Which providers need payout or working-capital intervention this month?",
        )
    with right:
        status_card("Live Risk Alerts", "High-risk segments are available in the Risk Intelligence workspace.", "risk", "!")

    st.divider()
    st.subheader("Command Center")

    nav_cols = st.columns(6)
    nav_cols[0].page_link("pages/01_Risk_Dashboard.py", label="Risk Dashboard")
    nav_cols[1].page_link("pages/02_Predictions.py", label="Predictions")
    nav_cols[2].page_link("pages/03_Primary_Insights.py", label="Primary Insights")
    nav_cols[3].page_link("pages/04_Model_Performance.py", label="Model Performance")
    nav_cols[4].page_link("pages/07_AI_Report_Generator.py", label="AI Report")
    nav_cols[5].page_link("pages/06_Admin.py", label="Admin")

    st.divider()
    st.subheader("System Health")
    health_cols = st.columns(3)
    with health_cols[0]:
        status_card("Datasets", "Final CSV artifacts loaded from data/.", "good", "●")
    with health_cols[1]:
        status_card("Models", "Four final ML models available in output/models_final/.", "accent", "◆")
    with health_cols[2]:
        status_card("Reports", "PDF report and dashboard exports are ready.", "warn", "■")


if __name__ == "__main__":
    main()
