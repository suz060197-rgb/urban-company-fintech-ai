"""Executive primary research insights dashboard."""

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"

if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

from utils.auth import render_auth_controls
from utils.theme import apply_theme, page_header, render_sidebar_brand, style_figure
from components.cards import metric_card
from components.status import ask_data_panel


st.set_page_config(page_title="Survey Insights", layout="wide")


@st.cache_data(show_spinner=False)
def load_primary_data() -> pd.DataFrame:
    path = DATA_DIR / "primary_responses_clean.csv"
    if not path.exists():
        return pd.DataFrame()

    data = pd.read_csv(path)
    object_columns = data.select_dtypes(include=["object"]).columns
    if len(object_columns) > 0:
        data[object_columns] = data[object_columns].fillna("Unknown")
    return data


@st.cache_data(show_spinner=False)
def load_operational_summary() -> dict[str, float]:
    summary = {}

    payouts_path = DATA_DIR / "payouts_loans.csv"
    if payouts_path.exists():
        payouts = pd.read_csv(
            payouts_path,
            usecols=["payout_delay_days", "working_capital_gap", "loan_offer_flag"],
        )
        summary["operational_settlement_delay_share"] = (
            payouts["payout_delay_days"].fillna(0) >= 2
        ).mean()
        summary["operational_working_capital_gap"] = payouts["working_capital_gap"].mean()
        summary["operational_credit_offer_share"] = payouts["loan_offer_flag"].astype(bool).mean()

    kpis_path = DATA_DIR / "provider_kpis.csv"
    if kpis_path.exists():
        kpis = pd.read_csv(
            kpis_path,
            usecols=["income_growth_pct", "technology_adoption_score", "advancement_score"],
        )
        summary["operational_income_growth"] = kpis["income_growth_pct"].mean()
        summary["operational_digital_score"] = kpis["technology_adoption_score"].mean()
        summary["operational_advancement_score"] = kpis["advancement_score"].mean()

    merchants_path = DATA_DIR / "merchants.csv"
    if merchants_path.exists():
        merchants = pd.read_csv(
            merchants_path,
            usecols=["digital_tool_usage", "transaction_velocity", "monthly_income"],
        )
        summary["operational_digital_tool_usage"] = merchants["digital_tool_usage"].mean()
        summary["operational_transaction_velocity"] = merchants["transaction_velocity"].mean()
        summary["operational_monthly_income"] = merchants["monthly_income"].mean()

    return summary


def pct(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:.1%}"


def money(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    return f"Rs {value:,.0f}"


def average(data: pd.DataFrame, column: str) -> float:
    if column not in data.columns:
        return np.nan
    return pd.to_numeric(data[column], errors="coerce").mean()


def filtered_data(data: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Survey Segmentation")

    city_options = sorted(data["city"].dropna().unique()) if "city" in data.columns else []
    business_options = sorted(data["business_type"].dropna().unique()) if "business_type" in data.columns else []
    income_options = (
        sorted(data["monthly_income_range_raw"].dropna().unique())
        if "monthly_income_range_raw" in data.columns
        else []
    )

    selected_cities = st.sidebar.multiselect("City", city_options, default=city_options)
    selected_business = st.sidebar.multiselect(
        "Business type", business_options, default=business_options
    )
    selected_income = st.sidebar.multiselect("Income band", income_options, default=income_options)

    min_exp = int(data["experience_years"].min()) if "experience_years" in data.columns else 0
    max_exp = int(data["experience_years"].max()) if "experience_years" in data.columns else 0
    exp_range = st.sidebar.slider(
        "Experience years",
        min_value=min_exp,
        max_value=max_exp,
        value=(min_exp, max_exp),
    )

    result = data.copy()
    if selected_cities:
        result = result[result["city"].isin(selected_cities)]
    if selected_business:
        result = result[result["business_type"].isin(selected_business)]
    if selected_income:
        result = result[result["monthly_income_range_raw"].isin(selected_income)]
    if "experience_years" in result.columns:
        result = result[
            result["experience_years"].between(exp_range[0], exp_range[1], inclusive="both")
        ]
    return result


def likert_distribution(data: pd.DataFrame, column: str, label: str) -> pd.DataFrame:
    if column not in data.columns:
        return pd.DataFrame(columns=["measure", "score", "respondents", "percent"])

    counts = (
        data[column]
        .dropna()
        .round()
        .astype(int)
        .value_counts()
        .sort_index()
        .rename_axis("score")
        .reset_index(name="respondents")
    )
    counts = counts.assign(
        measure=label,
        percent=counts["respondents"] / max(counts["respondents"].sum(), 1),
    )
    return counts


def split_counts(data: pd.DataFrame, column: str, separator: str = ";") -> pd.DataFrame:
    if column not in data.columns:
        return pd.DataFrame(columns=["item", "respondents"])

    items = (
        data[column]
        .dropna()
        .astype(str)
        .str.split(separator)
        .explode()
        .str.strip()
    )
    items = items[items.ne("") & items.ne("Unknown")]
    return items.value_counts().rename_axis("item").reset_index(name="respondents")


def overview_section(data: pd.DataFrame) -> None:
    st.subheader("Respondent Overview")
    cards = st.columns(5)
    with cards[0]:
        metric_card("Respondents", f"{len(data):,}", "Survey records", "▦", "accent")
    with cards[1]:
        metric_card("Experience", f"{average(data, 'experience_years'):.1f} yrs", "Provider tenure", "◷", "good")
    with cards[2]:
        metric_card("Monthly Income", money(average(data, "monthly_income_midpoint")), "Income midpoint", "₹", "accent")
    with cards[3]:
        metric_card("Transactions", f"{average(data, 'monthly_transaction_estimate'):.1f}", "Monthly volume", "◆", "warn")
    with cards[4]:
        metric_card("Digital Adoption", pct(average(data, "digital_adoption_score_scaled")), "Readiness score", "●", "good")

    left, right = st.columns(2)
    if "business_type" in data.columns:
        business = data["business_type"].value_counts().reset_index()
        business.columns = ["business_type", "respondents"]
        left.plotly_chart(
            style_figure(px.bar(business, x="business_type", y="respondents", title="Respondents by Business Type")),
            width="stretch",
            key="primary05_overview_business",
        )
    if "city" in data.columns:
        city = data["city"].value_counts().reset_index()
        city.columns = ["city", "respondents"]
        right.plotly_chart(
            style_figure(px.bar(city, x="city", y="respondents", title="Respondents by City")),
            width="stretch",
            key="primary05_overview_city",
        )


def digital_adoption_section(data: pd.DataFrame) -> None:
    st.subheader("Digital Adoption")
    col1, col2, col3 = st.columns(3)
    col1.metric("UPI users", pct(average(data, "uses_upi_flag")))
    col2.metric("AI tool adoption", pct(average(data, "ai_tool_usage_binary")))
    col3.metric("Digital readiness", pct(average(data, "digital_adoption_score_scaled")))

    left, right = st.columns(2)
    if "upi_usage_frequency_raw" in data.columns:
        upi = data["upi_usage_frequency_raw"].value_counts().reset_index()
        upi.columns = ["upi_usage_frequency", "respondents"]
        left.plotly_chart(
            px.bar(upi, x="upi_usage_frequency", y="respondents", title="UPI Usage Frequency"),
            width="stretch",
            key="primary05_upi_frequency",
        )

    right.plotly_chart(
        px.histogram(
            data,
            x="digital_adoption_score_likert",
            nbins=5,
            title="Digital Adoption Score Distribution",
        ),
        width="stretch",
        key="primary05_digital_score_distribution",
    )

    left, right = st.columns(2)
    ai = pd.DataFrame(
        {
            "status": ["Uses AI tools", "Does not use AI tools"],
            "respondents": [
                int((data["ai_tool_usage_binary"] == 1).sum()),
                int((data["ai_tool_usage_binary"] != 1).sum()),
            ],
        }
    )
    left.plotly_chart(
        px.bar(ai, x="status", y="respondents", title="AI Tool Adoption"),
        width="stretch",
        key="primary05_ai_adoption",
    )

    methods = split_counts(data, "payment_methods_standardized")
    right.plotly_chart(
        px.bar(methods, x="item", y="respondents", title="Payment Methods"),
        width="stretch",
        key="primary05_payment_methods",
    )


def cashflow_section(data: pd.DataFrame) -> None:
    st.subheader("Cashflow Challenges")
    measures = [
        ("cashflow_issues_likert", "Cashflow issues"),
        ("settlement_delay_impact_likert", "Settlement delay impact"),
        ("faster_payout_impact_likert", "Faster payout impact"),
    ]
    distributions = pd.concat(
        [likert_distribution(data, column, label) for column, label in measures],
        ignore_index=True,
    )

    left, right = st.columns([2, 1])
    left.plotly_chart(
        px.bar(
            distributions,
            x="measure",
            y="percent",
            color="score",
            title="Cashflow Challenge Percent Distribution",
            barmode="stack",
        ),
        width="stretch",
        key="primary05_cashflow_stacked",
    )

    pain_points = split_counts(data, "key_pain_points", separator=",")
    right.plotly_chart(
        px.bar(
            pain_points.head(8),
            x="respondents",
            y="item",
            orientation="h",
            title="Main Merchant Pain Points",
        ),
        width="stretch",
        key="primary05_pain_points",
    )

    with st.expander("Interpretation panel"):
        high_settlement = (data["settlement_delay_impact_scaled"] >= 0.75).mean()
        high_cashflow = (data["cashflow_issues_scaled"] >= 0.75).mean()
        st.write(f"{pct(high_settlement)} report settlement delays as a strong business issue.")
        st.write(f"{pct(high_cashflow)} report strong cashflow pressure.")
        st.write("Main pain points connect delayed settlements, cancellations, and tool financing needs.")


def credit_section(data: pd.DataFrame) -> None:
    st.subheader("Credit Need Analysis")
    col1, col2, col3 = st.columns(3)
    col1.metric("Need business credit", pct(average(data, "needed_business_credit_binary")))
    col2.metric("Avg requested credit", money(average(data, "approx_credit_amount_numeric")))
    col3.metric(
        "Credit seekers",
        f"{int((data['needed_business_credit_binary'] == 1).sum()):,}",
    )

    left, right = st.columns(2)
    need = data["needed_business_credit_binary"].map({1.0: "Needs credit", 0.0: "No credit need"})
    need_counts = need.fillna("Unknown").value_counts().reset_index()
    need_counts.columns = ["loan_need", "respondents"]
    left.plotly_chart(
        px.bar(need_counts, x="loan_need", y="respondents", title="Loan Need Distribution"),
        width="stretch",
        key="primary05_credit_need_distribution",
    )

    purpose = data["credit_purpose"].value_counts().head(10).reset_index()
    purpose.columns = ["credit_purpose", "respondents"]
    right.plotly_chart(
        px.bar(
            purpose,
            x="respondents",
            y="credit_purpose",
            orientation="h",
            title="Credit Purpose",
        ),
        width="stretch",
        key="primary05_credit_purpose",
    )

    st.plotly_chart(
        px.histogram(
            data,
            x="approx_credit_amount_numeric",
            nbins=10,
            title="Approximate Credit Amount Requested",
        ),
        width="stretch",
        key="primary05_credit_amount_histogram",
    )


def growth_section(data: pd.DataFrame) -> None:
    st.subheader("Growth Outcomes")
    col1, col2 = st.columns(2)
    col1.metric(
        "Growth after digital payments",
        pct(average(data, "business_growth_after_digital_scaled")),
    )
    col2.metric("Repeat customer change", pct(average(data, "repeat_customer_change_scaled")))

    summary = pd.DataFrame(
        {
            "measure": ["Business growth after digital", "Repeat customer change"],
            "score": [
                average(data, "business_growth_after_digital_scaled"),
                average(data, "repeat_customer_change_scaled"),
            ],
        }
    )
    st.plotly_chart(
        px.bar(summary, x="measure", y="score", title="Growth and Customer Change Scores"),
        width="stretch",
        key="primary05_growth_scores",
    )

    trend_data = pd.concat(
        [
            likert_distribution(data, "business_growth_after_digital_likert", "Business growth"),
            likert_distribution(data, "repeat_customer_change_likert", "Repeat customers"),
        ],
        ignore_index=True,
    )
    st.plotly_chart(
        px.line(
            trend_data,
            x="score",
            y="respondents",
            color="measure",
            markers=True,
            title="Growth Outcome Response Trends",
        ),
        width="stretch",
        key="primary05_growth_trends",
    )


def cross_analysis_section(data: pd.DataFrame) -> None:
    st.subheader("Cross Analysis")
    col1, col2 = st.columns(2)
    col1.plotly_chart(
        px.scatter(
            data,
            x="digital_adoption_score_scaled",
            y="business_growth_after_digital_scaled",
            color="business_type",
            title="Digital Adoption vs Business Growth",
        ),
        width="stretch",
        key="primary05_cross_digital_growth",
    )
    col2.plotly_chart(
        px.box(
            data,
            x="needed_business_credit_binary",
            y="settlement_delay_impact_scaled",
            title="Settlement Delay vs Need for Credit",
        ),
        width="stretch",
        key="primary05_cross_settlement_credit",
    )

    col1, col2 = st.columns(2)
    col1.plotly_chart(
        px.box(
            data,
            x="ai_tool_usage_binary",
            y="experience_years",
            title="Experience Years vs AI Adoption",
        ),
        width="stretch",
        key="primary05_cross_experience_ai",
    )
    col2.plotly_chart(
        px.scatter(
            data,
            x="monthly_income_midpoint",
            y="monthly_transaction_estimate",
            color="business_type",
            title="Income vs Transaction Volume",
        ),
        width="stretch",
        key="primary05_cross_income_transactions",
    )


def insight_panel(data: pd.DataFrame) -> None:
    st.subheader("AI Insight Panel")
    high_settlement = (data["settlement_delay_impact_scaled"] >= 0.75).mean()
    high_cashflow = (data["cashflow_issues_scaled"] >= 0.75).mean()
    high_payout = (data["faster_payout_impact_scaled"] >= 0.75).mean()
    credit_need = average(data, "needed_business_credit_binary")
    digital = average(data, "digital_adoption_score_scaled")
    ai = average(data, "ai_tool_usage_binary")

    pain_points = split_counts(data, "key_pain_points", separator=",").head(3)
    top_issues = ", ".join(pain_points["item"].tolist()) if not pain_points.empty else "Not available"

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**Top respondent issues**")
        st.write(f"Top issues: {top_issues}.")
        st.write(f"{pct(high_settlement)} report settlement delays affecting growth.")
    with col2:
        st.markdown("**Growth opportunities**")
        st.write(f"{pct(high_payout)} say faster payouts improve business operations.")
        st.write("Target faster settlement, reminders, and platform reliability.")
    with col3:
        st.markdown("**Digital readiness summary**")
        st.write(f"Digital adoption score is {pct(digital)}.")
        st.write(f"AI tool adoption is {pct(ai)}, leaving room for guided automation.")
    with col4:
        st.markdown("**Credit dependence risks**")
        st.write(f"{pct(credit_need)} need business credit.")
        st.write(f"{pct(high_cashflow)} show high cashflow stress.")


def primary_secondary_section(data: pd.DataFrame, operational: dict[str, float]) -> None:
    st.subheader("Primary vs Secondary Comparison")

    survey_settlement = (data["settlement_delay_impact_scaled"] >= 0.75).mean()
    survey_credit = average(data, "needed_business_credit_binary")
    survey_digital = average(data, "digital_adoption_score_scaled")
    survey_growth = average(data, "business_growth_after_digital_scaled")

    comparisons = [
        {
            "theme": "Settlement pain",
            "survey": pct(survey_settlement),
            "operational": pct(operational.get("operational_settlement_delay_share", np.nan)),
            "interpretation": "Survey pain aligns with operational payout-delay exposure.",
        },
        {
            "theme": "Need credit",
            "survey": pct(survey_credit),
            "operational": money(operational.get("operational_working_capital_gap", np.nan)),
            "interpretation": "Credit demand maps to synthetic working-capital gaps.",
        },
        {
            "theme": "Digital readiness",
            "survey": pct(survey_digital),
            "operational": pct(operational.get("operational_digital_tool_usage", np.nan)),
            "interpretation": "Survey digital readiness validates operational digital-tool usage.",
        },
        {
            "theme": "Business growth",
            "survey": pct(survey_growth),
            "operational": pct(operational.get("operational_income_growth", np.nan)),
            "interpretation": "Survey growth sentiment is compared with panel income-growth trend.",
        },
    ]

    columns = st.columns(4)
    for column, item in zip(columns, comparisons):
        with column:
            st.metric(item["theme"], item["survey"])
            st.caption(f"Operational: {item['operational']}")
            st.write(item["interpretation"])

    with st.expander("Comparison table"):
        st.dataframe(pd.DataFrame(comparisons), hide_index=True, width="stretch")


def survey_summary(data: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "total_respondents": len(data),
                "average_experience_years": average(data, "experience_years"),
                "average_monthly_income": average(data, "monthly_income_midpoint"),
                "average_transaction_volume": average(data, "monthly_transaction_estimate"),
                "digital_adoption_score": average(data, "digital_adoption_score_scaled"),
                "cashflow_issues_score": average(data, "cashflow_issues_scaled"),
                "settlement_delay_impact_score": average(data, "settlement_delay_impact_scaled"),
                "credit_need_share": average(data, "needed_business_credit_binary"),
                "ai_tool_adoption_share": average(data, "ai_tool_usage_binary"),
                "business_growth_after_digital_score": average(
                    data, "business_growth_after_digital_scaled"
                ),
            }
        ]
    )


def show_survey_download(data: pd.DataFrame) -> None:
    st.download_button(
        label="Download Survey Summary CSV",
        data=survey_summary(data).to_csv(index=False).encode("utf-8"),
        file_name="survey_summary.csv",
        mime="text/csv",
        key="download_survey_summary_csv_survey_insights",
    )


def main() -> None:
    apply_theme()
    render_sidebar_brand("Survey Insights")
    render_auth_controls()

    page_header(
        "Survey Intelligence Command Center",
        "Primary insight cards, opportunity signals, digital maturity, credit dependence, and primary-vs-operational validation.",
        "Primary Intelligence",
    )

    data = load_primary_data()
    if data.empty:
        st.warning("data/primary_responses_clean.csv is missing or empty. Primary insights cannot be displayed.")
        st.stop()

    data = filtered_data(data)
    if data.empty:
        st.warning("No survey responses match the selected segmentation filters.")
        st.stop()

    operational = load_operational_summary()

    overview_tab, digital_tab, finance_tab, growth_tab, cross_tab, compare_tab = st.tabs(
        [
            "Overview",
            "Digital Adoption",
            "Cashflow and Credit",
            "Growth Outcomes",
            "Cross Analysis",
            "Primary vs Secondary",
        ]
    )

    with overview_tab:
        overview_section(data)
        st.divider()
        ask_data_panel("Which respondent segment shows the strongest settlement-delay pain?")
        st.divider()
        insight_panel(data)
        st.divider()
        show_survey_download(data)

    with digital_tab:
        digital_adoption_section(data)

    with finance_tab:
        cashflow_section(data)
        st.divider()
        credit_section(data)

    with growth_tab:
        growth_section(data)

    with cross_tab:
        cross_analysis_section(data)

    with compare_tab:
        primary_secondary_section(data, operational)


if __name__ == "__main__":
    main()
