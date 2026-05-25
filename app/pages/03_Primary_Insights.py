"""Primary research insights dashboard for cleaned survey responses."""

from components.status import ask_data_panel
from components.cards import metric_card
from utils.theme import apply_theme, page_header, render_sidebar_brand, style_figure
from utils.auth import render_auth_controls
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DOCS_DIR = ROOT_DIR / "docs"

if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))


st.set_page_config(page_title="Primary Research Insights", layout="wide")


@st.cache_data(show_spinner=False)
def load_primary_responses() -> pd.DataFrame:
    primary_path = DATA_DIR / "primary_responses_clean.csv"
    fallback_path = DOCS_DIR / "primary_secondary_mapping.csv"

    if primary_path.exists():
        data = pd.read_csv(primary_path)
    elif fallback_path.exists():
        data = pd.read_csv(fallback_path)
    else:
        raise FileNotFoundError(str(primary_path))

    object_columns = data.select_dtypes(include=["object"]).columns
    if len(object_columns) > 0:
        data = data.copy()
        data[object_columns] = data[object_columns].fillna("Unknown")

    return data


def format_percent(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:.1%}"


def format_currency(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    return f"Rs {value:,.0f}"


def scaled_mean(data: pd.DataFrame, column: str) -> float:
    if column not in data.columns:
        return np.nan
    return data[column].mean()


def pain_point_counts(data: pd.DataFrame) -> pd.DataFrame:
    if "key_pain_points" not in data.columns:
        return pd.DataFrame(columns=["pain_point", "respondents"])

    points = (
        data["key_pain_points"]
        .dropna()
        .astype(str)
        .str.split(",")
        .explode()
        .str.strip()
    )
    points = points[points.ne("") & points.ne("Unknown")]
    return points.value_counts().rename_axis("pain_point").reset_index(name="respondents")


def show_respondent_overview(data: pd.DataFrame) -> None:
    st.subheader("Respondent Overview")

    cards = st.columns(4)
    with cards[0]:
        metric_card("Total Respondents",
                    f"{len(data):,}", "Primary sample", "▦", "accent")
    with cards[1]:
        metric_card(
            "Avg Experience", f"{scaled_mean(data, 'experience_years'):.1f} yrs", "Provider tenure proxy", "◷", "good")
    with cards[2]:
        metric_card("Avg Monthly Income", format_currency(scaled_mean(
            data, "monthly_income_midpoint")), "Survey midpoint", "₹", "accent")
    with cards[3]:
        metric_card("Digital Adoption", format_percent(scaled_mean(
            data, "digital_adoption_score_scaled")), "Readiness score", "◆", "good")

    left, right = st.columns(2)
    if "business_type" in data.columns:
        business_counts = data["business_type"].value_counts().reset_index()
        business_counts.columns = ["business_type", "respondents"]
        left.plotly_chart(
            style_figure(px.bar(
                business_counts,
                x="business_type",
                y="respondents",
                title="Respondents by Business Type",
            )),
            width="stretch",
            key="primary_overview_business_type",
        )

    if "region" in data.columns:
        region_counts = data["region"].value_counts().reset_index()
        region_counts.columns = ["region", "respondents"]
        right.plotly_chart(
            style_figure(px.bar(region_counts, x="region",
                         y="respondents", title="Respondents by Region")),
            width="stretch",
            key="primary_overview_region",
        )


def show_cashflow_issues(data: pd.DataFrame) -> None:
    st.subheader("Cashflow Issues")

    left, right = st.columns([2, 1])
    if "cashflow_issues_likert" in data.columns:
        cashflow = (
            data["cashflow_issues_likert"]
            .dropna()
            .round()
            .astype(int)
            .value_counts()
            .sort_index()
            .rename_axis("cashflow_issues")
            .reset_index(name="respondents")
        )
        left.plotly_chart(
            px.bar(
                cashflow,
                x="cashflow_issues",
                y="respondents",
                title="Cashflow Issues Likert Distribution",
            ),
            width="stretch",
            key="primary_cashflow_likert",
        )

    issue_share = (data.get("cashflow_issues_scaled",
                   pd.Series(dtype=float)) >= 0.75).mean()
    right.metric("Strong Cashflow Pain", format_percent(issue_share))
    right.write(
        "Financial pain points are concentrated among providers reporting high cashflow stress.")

    with st.expander("Pain point detail"):
        pain_points = pain_point_counts(data)
        if pain_points.empty:
            st.info("No pain point text field available.")
        else:
            st.dataframe(pain_points, hide_index=True, width="stretch")


def show_settlement_delay(data: pd.DataFrame) -> None:
    st.subheader("Settlement Delay Impact")

    delayed = data.get("settlement_delay_impact_scaled",
                       pd.Series(dtype=float)) >= 0.75
    delayed_pct = delayed.mean()

    left, right = st.columns([2, 1])
    if "settlement_delay_impact_likert" in data.columns:
        settlement = (
            data["settlement_delay_impact_likert"]
            .dropna()
            .round()
            .astype(int)
            .value_counts()
            .sort_index()
            .rename_axis("settlement_delay_impact")
            .reset_index(name="respondents")
        )
        left.plotly_chart(
            px.histogram(
                data,
                x="settlement_delay_impact_likert",
                nbins=5,
                title="Settlement Delay Impact Distribution",
            ),
            width="stretch",
            key="primary_settlement_delay_distribution",
        )

    right.metric("Report Meaningful Delays", format_percent(delayed_pct))
    right.write(
        "Delay pressure is treated as meaningful when response score is 4 or 5 on the 5-point scale.")


def show_credit_need(data: pd.DataFrame) -> None:
    st.subheader("Credit Need")

    left, right = st.columns(2)
    if "approx_credit_amount_numeric" in data.columns:
        credit_data = data[data["approx_credit_amount_numeric"].notna()].copy()
        left.plotly_chart(
            px.histogram(
                credit_data,
                x="approx_credit_amount_numeric",
                nbins=10,
                title="Approximate Credit Amount Needed",
            ),
            width="stretch",
            key="primary_credit_amount",
        )

    if "credit_purpose" in data.columns:
        purposes = data["credit_purpose"].value_counts().head(10).reset_index()
        purposes.columns = ["credit_purpose", "respondents"]
        right.plotly_chart(
            px.bar(
                purposes,
                x="respondents",
                y="credit_purpose",
                orientation="h",
                title="Credit Purpose",
            ),
            width="stretch",
            key="primary_credit_purpose",
        )

    credit_need = scaled_mean(data, "needed_business_credit_binary")
    growth_with_credit = data.loc[
        data.get("needed_business_credit_binary", pd.Series(dtype=float)) == 1,
        "business_growth_after_digital_scaled",
    ].mean()
    st.info(
        f"Credit need share: {format_percent(credit_need)}. "
        f"Average digital-payment growth score among credit-seeking respondents: {format_percent(growth_with_credit)}."
    )


def show_digital_adoption(data: pd.DataFrame) -> None:
    st.subheader("Digital Adoption")

    col1, col2, col3 = st.columns(3)
    col1.metric("UPI Users", format_percent(
        scaled_mean(data, "uses_upi_flag")))
    col2.metric("AI Tool Adoption", format_percent(
        scaled_mean(data, "ai_tool_usage_binary")))
    col3.metric("Digital Readiness", format_percent(
        scaled_mean(data, "digital_adoption_score_scaled")))

    left, right = st.columns(2)
    if "upi_usage_frequency_raw" in data.columns:
        upi = data["upi_usage_frequency_raw"].value_counts().reset_index()
        upi.columns = ["upi_frequency", "respondents"]
        left.plotly_chart(
            px.bar(upi, x="upi_frequency", y="respondents",
                   title="UPI Usage Frequency"),
            width="stretch",
            key="primary_upi_usage",
        )

    readiness = data[["digital_adoption_score_scaled",
                      "ai_tool_usage_binary"]].copy()
    readiness = readiness.rename(
        columns={
            "digital_adoption_score_scaled": "Digital readiness",
            "ai_tool_usage_binary": "AI tool adoption",
        }
    )
    right.plotly_chart(
        px.box(
            readiness.melt(var_name="measure", value_name="score"),
            x="measure",
            y="score",
            title="Digital Readiness and AI Adoption",
        ),
        width="stretch",
        key="primary_digital_readiness_box",
    )


def show_business_growth(data: pd.DataFrame) -> None:
    st.subheader("Business Growth")

    col1, col2 = st.columns(2)
    col1.metric(
        "Growth After Digital Payments",
        format_percent(scaled_mean(
            data, "business_growth_after_digital_scaled")),
    )
    col2.metric(
        "Repeat Customer Change",
        format_percent(scaled_mean(data, "repeat_customer_change_scaled")),
    )

    growth_cols = [
        "faster_payout_impact_scaled",
        "business_growth_after_digital_scaled",
        "repeat_customer_change_scaled",
    ]
    available = [column for column in growth_cols if column in data.columns]
    if available:
        summary = data[available].mean().reset_index()
        summary.columns = ["measure", "average_score"]
        st.plotly_chart(
            px.bar(summary, x="measure", y="average_score",
                   title="Business Growth Indicators"),
            width="stretch",
            key="primary_business_growth_indicators",
        )


def show_cross_analysis(data: pd.DataFrame) -> None:
    st.subheader("Cross-Analysis")

    col1, col2, col3 = st.columns(3)

    col1.plotly_chart(
        px.scatter(
            data,
            x="digital_adoption_score_scaled",
            y="monthly_income_midpoint",
            color="business_type" if "business_type" in data.columns else None,
            title="Income vs Digital Adoption",
        ),
        width="stretch",
        key="primary_cross_income_digital",
    )

    col2.plotly_chart(
        px.box(
            data,
            x="needed_business_credit_binary",
            y="business_growth_after_digital_scaled",
            title="Growth vs Credit Access Need",
        ),
        width="stretch",
        key="primary_cross_growth_credit",
    )

    col3.plotly_chart(
        px.scatter(
            data,
            x="settlement_delay_impact_scaled",
            y="business_growth_after_digital_scaled",
            color="needed_business_credit_binary" if "needed_business_credit_binary" in data.columns else None,
            title="Settlement Delay vs Business Growth",
        ),
        width="stretch",
        key="primary_cross_settlement_growth",
    )


def build_ai_insights(data: pd.DataFrame) -> dict[str, list[str]]:
    high_cashflow = scaled_mean(data, "cashflow_issues_scaled")
    high_settlement = scaled_mean(data, "settlement_delay_impact_scaled")
    digital = scaled_mean(data, "digital_adoption_score_scaled")
    credit = scaled_mean(data, "needed_business_credit_binary")
    ai_usage = scaled_mean(data, "ai_tool_usage_binary")
    growth = scaled_mean(data, "business_growth_after_digital_scaled")

    findings = [
        f"Digital adoption is strong at {format_percent(digital)}, with UPI usage at {format_percent(scaled_mean(data, 'uses_upi_flag'))}.",
        f"Settlement delay pressure averages {format_percent(high_settlement)}, indicating payout speed is a material provider concern.",
        f"Credit need is reported by {format_percent(credit)} of respondents, linking embedded finance to working-capital resilience.",
    ]

    risks = [
        f"Cashflow stress score is {format_percent(high_cashflow)}, so delayed settlement can amplify short-term default and churn risk.",
        f"AI tool usage is {format_percent(ai_usage)}, creating an adoption gap for agentic intelligence features.",
        "Small primary sample size means findings should validate directionality, not replace the synthetic panel.",
    ]

    opportunities = [
        f"Business growth after digital payments averages {format_percent(growth)}, supporting a payments-led growth narrative.",
        "Bundle faster payout messaging with credit education for providers reporting high cashflow stress.",
        "Use high digital-readiness respondents as early adopters for forecasting, reminders, and AI scheduling tools.",
    ]

    return {
        "Top 3 Findings": findings,
        "Operational Risks": risks,
        "Growth Opportunities": opportunities,
    }


def show_ai_insight_panel(data: pd.DataFrame) -> None:
    st.subheader("AI-Generated Insight Panel")
    insight_groups = build_ai_insights(data)

    columns = st.columns(3)
    for column, (title, items) in zip(columns, insight_groups.items()):
        with column:
            st.markdown(f"**{title}**")
            for item in items:
                st.write(f"- {item}")

    with st.expander("How this panel is generated"):
        st.write(
            "The insight panel uses deterministic rules over survey summary statistics. "
            "It does not call an external LLM, which keeps the dissertation app reproducible."
        )


def survey_summary(data: pd.DataFrame) -> pd.DataFrame:
    metrics = {
        "total_respondents": len(data),
        "average_experience_years": scaled_mean(data, "experience_years"),
        "average_monthly_income": scaled_mean(data, "monthly_income_midpoint"),
        "average_transaction_volume": scaled_mean(data, "monthly_transaction_estimate"),
        "digital_adoption_score": scaled_mean(data, "digital_adoption_score_scaled"),
        "cashflow_issues_score": scaled_mean(data, "cashflow_issues_scaled"),
        "settlement_delay_impact_score": scaled_mean(data, "settlement_delay_impact_scaled"),
        "credit_need_share": scaled_mean(data, "needed_business_credit_binary"),
        "ai_tool_adoption_share": scaled_mean(data, "ai_tool_usage_binary"),
        "business_growth_after_digital_score": scaled_mean(
            data, "business_growth_after_digital_scaled"
        ),
    }
    return pd.DataFrame([metrics])


def show_survey_download(data: pd.DataFrame) -> None:
    st.download_button(
        label="Download Survey Summary CSV",
        data=survey_summary(data).to_csv(index=False).encode("utf-8"),
        file_name="survey_summary.csv",
        mime="text/csv",
        key="download_survey_summary_csv",
    )


def main() -> None:
    apply_theme()
    render_sidebar_brand("Primary Research")
    render_auth_controls()

    page_header(
        "Primary Research Intelligence Layer",
        "Survey insight cards for cashflow stress, settlement pain, credit need, digital maturity, and growth opportunity.",
        "Survey Analytics",
    )

    try:
        data = load_primary_responses()
    except FileNotFoundError as exc:
        st.error(f"Missing primary research file: {exc}")
        st.stop()

    overview_tab, finance_tab, digital_tab, growth_tab, analysis_tab = st.tabs(
        ["Overview", "Cashflow and Credit", "Digital Adoption",
            "Business Growth", "Cross-Analysis"]
    )

    with overview_tab:
        show_respondent_overview(data)
        st.divider()
        ask_data_panel(
            "Which survey theme most strongly validates embedded-finance adoption?")
        st.divider()
        show_ai_insight_panel(data)
        st.divider()
        show_survey_download(data)

    with finance_tab:
        show_cashflow_issues(data)
        st.divider()
        show_settlement_delay(data)
        st.divider()
        show_credit_need(data)

    with digital_tab:
        show_digital_adoption(data)

    with growth_tab:
        show_business_growth(data)

    with analysis_tab:
        show_cross_analysis(data)


if __name__ == "__main__":
    main()
