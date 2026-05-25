"""Executive risk dashboard for provider default and churn monitoring."""

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"
BA_DIR = OUTPUT_DIR / "business_analysis"

if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

from utils.auth import require_login
from utils.theme import RISK_COLORS, apply_theme, page_header, render_sidebar_brand, style_figure
from components.cards import alert_banner, metric_card, status_card
from components.status import operational_alert


st.set_page_config(page_title="Risk Dashboard", layout="wide")


@st.cache_data(show_spinner=False)
def load_risk_data() -> pd.DataFrame:
    risk = pd.read_csv(OUTPUT_DIR / "risk_scores.csv")
    risk = risk.rename(columns={"provider_id": "merchant_id"})

    merchants = pd.read_csv(
        DATA_DIR / "merchants.csv",
        usecols=["merchant_id", "region", "category"],
    )
    risk = risk.merge(merchants, on="merchant_id", how="left")

    prediction_files = {
        "default_probability_model": OUTPUT_DIR / "default_predictions.csv",
        "churn_probability": OUTPUT_DIR / "churn_predictions.csv",
        "adoption_probability": OUTPUT_DIR / "adoption_predictions.csv",
    }

    for probability_column, path in prediction_files.items():
        if not path.exists():
            continue

        prediction = pd.read_csv(
            path,
            usecols=["provider_id", "month", "prediction_probability"],
        ).rename(
            columns={
                "provider_id": "merchant_id",
                "prediction_probability": probability_column,
            }
        )
        risk = risk.merge(prediction, on=["merchant_id", "month"], how="left")

    if "default_probability_model" in risk.columns:
        risk = risk.assign(
            default_probability=risk["default_probability"].fillna(
                risk["default_probability_model"]
            )
        )

    risk = risk.assign(
        month=risk["month"].astype(str),
        risk_band=risk["risk_band"].fillna("Unknown"),
        region=risk["region"].fillna("Unknown"),
        category=risk["category"].fillna(risk["business_type"]).fillna("Unknown"),
    )
    return risk


@st.cache_data(show_spinner=False)
def load_business_analysis_outputs() -> dict[str, pd.DataFrame]:
    files = {
        "churn_retention": BA_DIR / "churn_retention_impact.csv",
        "adoption_growth": BA_DIR / "adoption_growth_impact.csv",
        "default_exposure": BA_DIR / "default_loan_exposure.csv",
        "opportunity": BA_DIR / "merchant_opportunity_matrix.csv",
        "high_growth": BA_DIR / "segment_high_growth_merchants.csv",
        "high_adoption": BA_DIR / "segment_high_adoption_merchants.csv",
        "low_retention": BA_DIR / "segment_low_retention_merchants.csv",
        "high_risk": BA_DIR / "segment_high_risk_merchants.csv",
    }
    outputs: dict[str, pd.DataFrame] = {}
    for name, path in files.items():
        if path.exists():
            outputs[name] = pd.read_csv(path, low_memory=False)
    return outputs


def format_percent(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:.1%}"


def filter_data(data: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    months = sorted(data["month"].dropna().unique())
    regions = sorted(data["region"].dropna().unique())
    categories = sorted(data["category"].dropna().unique())
    risk_bands = ["Low", "Medium", "High"]

    selected_months = st.sidebar.multiselect("Month", months, default=months[-6:])
    selected_regions = st.sidebar.multiselect("Region", regions, default=regions)
    selected_categories = st.sidebar.multiselect("Category", categories, default=categories)
    selected_risk_bands = st.sidebar.multiselect("Risk band", risk_bands, default=risk_bands)

    filtered = data[
        data["month"].isin(selected_months)
        & data["region"].isin(selected_regions)
        & data["category"].isin(selected_categories)
        & data["risk_band"].isin(selected_risk_bands)
    ].copy()
    return filtered


def show_kpis(data: pd.DataFrame) -> None:
    total_providers = data["merchant_id"].nunique()
    risk_share = data["risk_band"].value_counts(normalize=True)
    average_default = data["default_probability"].mean()
    average_churn = data.get("churn_probability", pd.Series(dtype=float)).mean()

    cards = st.columns(6)
    with cards[0]:
        metric_card("Total Providers", f"{total_providers:,}", "Filtered cohort", "▦", "accent")
    with cards[1]:
        metric_card("High Risk", format_percent(risk_share.get("High", 0.0)), "▲ Intervention queue", "▲", "risk")
    with cards[2]:
        metric_card("Medium Risk", format_percent(risk_share.get("Medium", 0.0)), "◆ Watchlist", "◆", "warn")
    with cards[3]:
        metric_card("Low Risk", format_percent(risk_share.get("Low", 0.0)), "● Stable base", "●", "good")
    with cards[4]:
        metric_card("Avg Default", format_percent(average_default), "Credit risk score", "◉", "risk")
    with cards[5]:
        metric_card("Avg Churn", format_percent(average_churn), "Retention risk score", "◌", "warn")


def show_charts(data: pd.DataFrame) -> None:
    left, right = st.columns(2)

    risk_counts = data["risk_band"].value_counts().rename_axis("risk_band").reset_index(name="providers")
    left.plotly_chart(
        style_figure(px.bar(
            risk_counts,
            x="risk_band",
            y="providers",
            color="risk_band",
            title="Risk Distribution",
            category_orders={"risk_band": ["Low", "Medium", "High"]},
            color_discrete_map=RISK_COLORS,
        )),
        width="stretch",
        key="risk_dashboard_risk_distribution",
    )

    trend = (
        data.groupby(["month", "risk_band"])["merchant_id"]
        .nunique()
        .reset_index(name="providers")
        .sort_values("month")
    )
    right.plotly_chart(
        style_figure(px.line(
            trend,
            x="month",
            y="providers",
            color="risk_band",
            markers=True,
            title="Risk Trend Over Time",
            color_discrete_map=RISK_COLORS,
        )),
        width="stretch",
        key="risk_dashboard_risk_trend",
    )

    left, right = st.columns(2)
    left.plotly_chart(
        style_figure(px.histogram(
            data,
            x="default_probability",
            nbins=30,
            title="Default Probability Distribution",
        )),
        width="stretch",
        key="risk_dashboard_default_probability_histogram",
    )

    if "churn_probability" in data.columns:
        right.plotly_chart(
            style_figure(px.histogram(
                data,
                x="churn_probability",
                nbins=30,
                title="Churn Probability Distribution",
            )),
            width="stretch",
            key="risk_dashboard_churn_probability_histogram",
        )
    else:
        right.warning("Churn prediction file is unavailable.")

    left, right = st.columns(2)
    region_risk = (
        data.groupby(["region", "risk_band"])["merchant_id"]
        .nunique()
        .reset_index(name="providers")
    )
    left.plotly_chart(
        style_figure(px.bar(
            region_risk,
            x="region",
            y="providers",
            color="risk_band",
            title="Risk by Region",
            barmode="stack",
            color_discrete_map=RISK_COLORS,
        )),
        width="stretch",
        key="risk_dashboard_region_risk",
    )

    category_risk = (
        data.groupby(["category", "risk_band"])["merchant_id"]
        .nunique()
        .reset_index(name="providers")
    )
    right.plotly_chart(
        style_figure(px.bar(
            category_risk,
            x="category",
            y="providers",
            color="risk_band",
            title="Risk by Category",
            barmode="stack",
            color_discrete_map=RISK_COLORS,
        )),
        width="stretch",
        key="risk_dashboard_category_risk",
    )


def show_business_impact() -> None:
    outputs = load_business_analysis_outputs()
    if not outputs:
        st.info("Business-impact audit outputs are not available yet. Run `python src/mba_ba_ml_improvements.py`.")
        return

    st.subheader("Business Impact Analysis")
    impact_tab, segment_tab = st.tabs(["Impact Visuals", "Merchant Segments"])

    with impact_tab:
        left, right = st.columns(2)
        churn_retention = outputs.get("churn_retention")
        if churn_retention is not None and not churn_retention.empty:
            left.plotly_chart(
                style_figure(px.line(
                    churn_retention,
                    x="churn_bin",
                    y="retention_rate",
                    markers=True,
                    title="Churn -> Retention Impact",
                    hover_data=["providers"],
                )),
                width="stretch",
                key="risk_dashboard_churn_retention_impact",
            )
        else:
            left.warning("Churn-retention impact output is unavailable.")

        adoption_growth = outputs.get("adoption_growth")
        if adoption_growth is not None and not adoption_growth.empty:
            sample = adoption_growth.sample(min(len(adoption_growth), 3000), random_state=42)
            right.plotly_chart(
                style_figure(px.scatter(
                    sample,
                    x="adoption_probability",
                    y="income_growth_pct",
                    color="adoption_bin",
                    title="Adoption -> Growth Impact",
                    opacity=0.65,
                )),
                width="stretch",
                key="risk_dashboard_adoption_growth_impact",
            )
        else:
            right.warning("Adoption-growth impact output is unavailable.")

        left, right = st.columns(2)
        default_exposure = outputs.get("default_exposure")
        if default_exposure is not None and not default_exposure.empty:
            sample = default_exposure.sample(min(len(default_exposure), 3000), random_state=42)
            left.plotly_chart(
                style_figure(px.scatter(
                    sample,
                    x="default_probability",
                    y="loan_amount",
                    color="risk_band",
                    size="working_capital_gap",
                    title="Default -> Loan Exposure",
                    color_discrete_map=RISK_COLORS,
                    opacity=0.7,
                )),
                width="stretch",
                key="risk_dashboard_default_loan_exposure",
            )
        else:
            left.warning("Default-loan exposure output is unavailable.")

        opportunity = outputs.get("opportunity")
        if opportunity is not None and not opportunity.empty:
            sample = opportunity.sample(min(len(opportunity), 3000), random_state=42)
            right.plotly_chart(
                style_figure(px.scatter(
                    sample,
                    x="default_probability",
                    y="predicted_income_growth",
                    color="opportunity_quadrant",
                    title="Merchant Opportunity Matrix",
                    opacity=0.7,
                )),
                width="stretch",
                key="risk_dashboard_merchant_opportunity_matrix",
            )
        else:
            right.warning("Merchant opportunity matrix output is unavailable.")

    with segment_tab:
        segment_files = [
            ("High-growth merchants", "high_growth"),
            ("High-adoption merchants", "high_adoption"),
            ("Low-retention merchants", "low_retention"),
            ("High-risk merchants", "high_risk"),
        ]
        for label, key in segment_files:
            with st.expander(label, expanded=False):
                frame = outputs.get(key)
                if frame is None or frame.empty:
                    st.warning(f"{label} output is unavailable.")
                    continue
                st.dataframe(frame.head(100), width="stretch", hide_index=True)


def show_recommendations(data: pd.DataFrame) -> None:
    st.subheader("Recommendation Engine")

    high_count = data.loc[data["risk_band"] == "High", "merchant_id"].nunique()
    medium_count = data.loc[data["risk_band"] == "Medium", "merchant_id"].nunique()
    low_count = data.loc[data["risk_band"] == "Low", "merchant_id"].nunique()

    high, medium, low = st.columns(3)
    with high:
        status_card("High Risk", f"{high_count:,} providers. Recommend working capital support.", "risk", "▲")
    with medium:
        status_card("Medium Risk", f"{medium_count:,} providers. Monitor settlement delay.", "warn", "◆")
    with low:
        status_card("Low Risk", f"{low_count:,} providers. Maintain engagement.", "good", "●")

    with st.expander("Rule logic"):
        st.write(
            "Providers are assigned actions from their risk band: High = working capital support, "
            "Medium = settlement-delay monitoring, Low = engagement maintenance."
        )


def show_downloads(data: pd.DataFrame) -> None:
    st.subheader("Exports")
    st.download_button(
        label="Download Risk Scores CSV",
        data=data.to_csv(index=False).encode("utf-8"),
        file_name="risk_scores_filtered.csv",
        mime="text/csv",
        key="download_risk_scores_csv",
    )


def main() -> None:
    apply_theme()
    render_sidebar_brand("Risk Intelligence")
    page_header(
        "Risk Intelligence Command Center",
        "AI risk radar for default probability, churn exposure, provider liquidity stress, and embedded-finance interventions.",
        "Risk Command Center",
    )
    require_login()

    try:
        data = load_risk_data()
    except FileNotFoundError as exc:
        st.error(f"Missing required file: {exc.filename}")
        st.stop()

    filtered = filter_data(data)
    if filtered.empty:
        st.warning("No records match the selected filters.")
        st.stop()

    high_share = (filtered["risk_band"] == "High").mean()
    if high_share >= 0.25:
        operational_alert(
            "High-risk concentration elevated",
            f"{format_percent(high_share)} of the selected cohort is high risk. Prioritize intervention review.",
            "risk",
        )

    show_kpis(filtered)
    st.divider()
    show_charts(filtered)
    st.divider()
    show_business_impact()
    st.divider()
    show_recommendations(filtered)
    st.divider()
    show_downloads(filtered)


if __name__ == "__main__":
    main()
