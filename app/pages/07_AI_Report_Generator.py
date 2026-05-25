"""AI executive report generator for dissertation artifacts."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "output"

if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

from utils.auth import require_login
from utils.report_generator import (
    build_executive_pdf,
    executive_findings,
    load_report_inputs,
    report_sections,
    summarize_inputs,
)
from utils.theme import apply_theme, page_header, render_sidebar_brand
from components.cards import metric_card
from components.status import ask_data_panel


st.set_page_config(page_title="AI Report Generator", layout="wide")


def fmt_percent(value: object) -> str:
    try:
        if pd.isna(value):
            return "N/A"
        return f"{float(value):.1%}"
    except Exception:
        return "N/A"


def fmt_number(value: object) -> str:
    try:
        if pd.isna(value):
            return "N/A"
        return f"{float(value):,.2f}"
    except Exception:
        return "N/A"


def show_kpis(summary: dict[str, object]) -> None:
    cols = st.columns(5)
    provider_value = "N/A" if pd.isna(summary["provider_count"]) else f"{summary['provider_count']:,.0f}"
    with cols[0]:
        metric_card("Providers", provider_value, "Report population", "▦", "accent")
    with cols[1]:
        metric_card("High Risk", fmt_percent(summary["high_risk_share"]), "Risk segment", "▲", "risk")
    with cols[2]:
        metric_card("Retention", fmt_percent(summary["retention_rate"]), "Provider health", "●", "good")
    with cols[3]:
        metric_card("Avg Growth", fmt_percent(summary["avg_growth"]), "Growth signal", "↑", "good")
    with cols[4]:
        metric_card("Survey N", f"{summary['survey_count']:,}", "Primary sample", "◆", "accent")


def show_summary(summary: dict[str, object]) -> None:
    st.subheader("Executive Summary")
    for finding in executive_findings(summary):
        st.write(f"- {finding}")


def show_sections(summary: dict[str, object]) -> None:
    sections = report_sections(summary)
    tabs = st.tabs(list(sections.keys()))
    for tab, section_name in zip(tabs, sections.keys()):
        with tab:
            for bullet in sections[section_name]:
                st.write(f"- {bullet}")


def show_source_status(inputs: dict[str, pd.DataFrame]) -> None:
    rows = []
    for name, frame in inputs.items():
        rows.append(
            {
                "artifact": name,
                "rows": len(frame),
                "columns": len(frame.columns),
                "status": "Loaded" if not frame.empty else "Missing or empty",
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def main() -> None:
    apply_theme()
    render_sidebar_brand("AI Report")
    require_login()

    page_header(
        "AI Executive Report Studio",
        "Generate board-ready PDF intelligence briefs covering risk, predictions, model metrics, survey findings, and recommendations.",
        "Board-Ready Reporting",
    )

    inputs = load_report_inputs()
    summary = summarize_inputs(inputs)

    show_kpis(summary)
    st.divider()

    left, right = st.columns([2, 1])
    with left:
        show_summary(summary)
        st.divider()
        ask_data_panel("Create a board summary explaining why risk and churn changed this month.")
    with right:
        st.subheader("Report Controls")
        report_name = st.text_input("PDF file name", value="Executive_Report.pdf")
        save_copy = st.checkbox("Also save a copy to output/", value=True)

        try:
            pdf_bytes = build_executive_pdf(summary)
        except RuntimeError as exc:
            st.error(str(exc))
            st.info("Install ReportLab with `pip install reportlab`, then refresh this page.")
            return

        st.download_button(
            label="Download Executive Report PDF",
            data=pdf_bytes,
            file_name=report_name.strip() or "Executive_Report.pdf",
            mime="application/pdf",
            key="download_ai_executive_report_pdf",
        )

        if save_copy and st.button("Save PDF to output", key="save_ai_report_pdf"):
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            output_path = OUTPUT_DIR / (report_name.strip() or "Executive_Report.pdf")
            output_path.write_bytes(pdf_bytes)
            st.success(f"Saved {output_path}")

    st.divider()
    show_sections(summary)

    with st.expander("Source Artifact Status"):
        show_source_status(inputs)


if __name__ == "__main__":
    main()
