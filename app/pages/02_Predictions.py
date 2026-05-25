"""Prediction engine for provider-level dissertation models."""

from pathlib import Path
import sys

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"
MODELS_DIR = OUTPUT_DIR / "models_final"
PREDICTIONS_DIR = OUTPUT_DIR / "predictions_final"

if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

from utils.auth import require_login
from utils.theme import apply_theme, page_header, render_sidebar_brand, style_figure
from components.cards import metric_card
from components.status import ask_data_panel, risk_badge

MODEL_FILES = {
    "Default": "loan_default_model_final.pkl",
    "Churn": "churn_model_final.pkl",
    "Adoption": "adoption_model_final.pkl",
    "Income Growth": "income_growth_model_final.pkl",
}

IMPORTANCE_FILES = {
    "Default": "loan_default_prediction_feature_importance.csv",
    "Churn": "churn_prediction_feature_importance.csv",
    "Adoption": "embedded_finance_adoption_feature_importance.csv",
    "Income Growth": "income_growth_prediction_feature_importance.csv",
}


st.set_page_config(page_title="Prediction Engine", layout="wide")


@st.cache_data(show_spinner=False)
def load_provider_context() -> pd.DataFrame:
    merchants = pd.read_csv(DATA_DIR / "merchants.csv")
    kpis = pd.read_csv(DATA_DIR / "provider_kpis.csv")
    payouts = pd.read_csv(DATA_DIR / "payouts_loans.csv")

    latest_kpis = kpis.sort_values("month").groupby("merchant_id", as_index=False).tail(1)
    latest_payouts = payouts.sort_values("month").groupby("merchant_id", as_index=False).tail(1)

    context = merchants.merge(latest_kpis, on="merchant_id", how="left")
    context = context.merge(latest_payouts, on=["merchant_id", "month"], how="left")
    return context


@st.cache_data(show_spinner=False)
def load_prediction_exports() -> pd.DataFrame:
    default = pd.read_csv(PREDICTIONS_DIR / "default_predictions_final.csv").rename(
        columns={"prediction_probability": "default_probability"}
    )
    churn = pd.read_csv(PREDICTIONS_DIR / "churn_predictions_final.csv").rename(
        columns={"prediction_probability": "churn_probability"}
    )
    adoption = pd.read_csv(PREDICTIONS_DIR / "adoption_predictions_final.csv").rename(
        columns={"prediction_probability": "adoption_probability"}
    )
    income = pd.read_csv(PREDICTIONS_DIR / "income_growth_predictions_final.csv").rename(
        columns={"prediction_value": "income_growth_forecast"}
    )

    base_cols = ["provider_id", "month", "target_month", "split"]
    predictions = default[base_cols + ["default_probability", "predicted_class"]].rename(
        columns={"predicted_class": "default_class"}
    )
    predictions = predictions.merge(
        churn[base_cols + ["churn_probability", "predicted_class"]].rename(
            columns={"predicted_class": "churn_class"}
        ),
        on=base_cols,
        how="left",
    )
    predictions = predictions.merge(
        adoption[base_cols + ["adoption_probability", "predicted_class"]].rename(
            columns={"predicted_class": "adoption_class"}
        ),
        on=base_cols,
        how="left",
    )
    predictions = predictions.merge(
        income[base_cols + ["income_growth_forecast"]],
        on=base_cols,
        how="left",
    )
    return predictions.sort_values(["provider_id", "month"])


@st.cache_resource(show_spinner=False)
def load_models() -> dict[str, dict]:
    return {name: joblib.load(MODELS_DIR / file_name) for name, file_name in MODEL_FILES.items()}


@st.cache_data(show_spinner=False)
def load_feature_importance() -> dict[str, pd.DataFrame]:
    importance = {}
    for name, file_name in IMPORTANCE_FILES.items():
        path = MODELS_DIR / file_name
        if path.exists():
            importance[name] = pd.read_csv(path).sort_values("importance", ascending=False)
    return importance


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -30, 30)))


def prepare_features(input_data: pd.DataFrame, model: dict) -> pd.DataFrame:
    frame = input_data.copy()
    feature_names = model["feature_names"]
    prepared = pd.DataFrame(index=frame.index)

    for feature in feature_names:
        if feature in frame.columns:
            prepared[feature] = frame[feature]
        elif feature.startswith("region_") and "region" in frame.columns:
            prepared[feature] = (frame["region"].astype(str) == feature.replace("region_", "")).astype(int)
        elif feature.startswith("city_") and "city" in frame.columns:
            prepared[feature] = (frame["city"].astype(str) == feature.replace("city_", "")).astype(int)
        elif feature.startswith("category_") and "category" in frame.columns:
            prepared[feature] = (frame["category"].astype(str) == feature.replace("category_", "")).astype(int)
        else:
            prepared[feature] = np.nan

    prepared = prepared.replace({True: 1, False: 0, "True": 1, "False": 0})
    prepared = prepared.apply(pd.to_numeric, errors="coerce")
    means = pd.Series(model["means"], index=feature_names)
    return prepared.fillna(means)


def score_uploaded_rows(input_data: pd.DataFrame, models: dict[str, dict]) -> pd.DataFrame:
    scored = pd.DataFrame(index=input_data.index)
    provider_col = "provider_id" if "provider_id" in input_data.columns else "merchant_id"

    if provider_col in input_data.columns:
        scored["provider_id"] = input_data[provider_col]
    else:
        scored["provider_id"] = [f"uploaded_{idx + 1}" for idx in range(len(input_data))]

    if "month" in input_data.columns:
        scored["month"] = input_data["month"].astype(str)
    else:
        scored["month"] = "uploaded"

    for name, model in models.items():
        features = prepare_features(input_data, model)
        x_scaled = (features.values - model["means"]) / model["stds"]
        raw_score = x_scaled @ model["weights"] + model["bias"]

        if name == "Income Growth":
            scored["income_growth_forecast"] = raw_score
        else:
            probability = sigmoid(raw_score)
            threshold = model.get("threshold", 0.5)
            column_name = f"{name.lower()}_probability"
            if name == "Default":
                column_name = "default_probability"
            elif name == "Churn":
                column_name = "churn_probability"
            elif name == "Adoption":
                column_name = "adoption_probability"
            scored[column_name] = probability
            scored[f"{name.lower()}_class"] = (probability >= threshold).astype(int)

    return scored


def latest_prediction_for_provider(predictions: pd.DataFrame, provider_id: str) -> pd.Series:
    provider_rows = predictions[predictions["provider_id"] == provider_id].sort_values("month")
    return provider_rows.iloc[-1]


def risk_band(default_probability: float) -> str:
    if default_probability >= 0.70:
        return "High"
    if default_probability >= 0.30:
        return "Medium"
    return "Low"


def confidence_score(probability: float, threshold: float = 0.5) -> float:
    if pd.isna(probability):
        return np.nan
    return min(1.0, abs(probability - threshold) * 2.0)


def format_percent(value: float) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{value:.1%}"


def show_probability_cards(row: pd.Series) -> None:
    default_prob = row.get("default_probability", np.nan)
    churn_prob = row.get("churn_probability", np.nan)
    adoption_prob = row.get("adoption_probability", np.nan)
    growth = row.get("income_growth_forecast", np.nan)

    cards = st.columns(4)
    with cards[0]:
        metric_card("Default Probability", format_percent(default_prob), "Credit risk output", "▲", "risk")
    with cards[1]:
        metric_card("Churn Probability", format_percent(churn_prob), "Retention risk output", "◌", "warn")
    with cards[2]:
        metric_card("Adoption Probability", format_percent(adoption_prob), "Embedded finance propensity", "◆", "accent")
    with cards[3]:
        metric_card("Income Growth Forecast", format_percent(growth), "Next-period growth signal", "↑", "good")

    detail_cols = st.columns(3)
    with detail_cols[0]:
        metric_card("Risk Band", risk_band(default_prob), "Operational segment", "●", "accent")
    with detail_cols[1]:
        metric_card("Default Confidence", format_percent(confidence_score(default_prob)), "Probability distance", "◉", "good")
    with detail_cols[2]:
        metric_card("Churn Confidence", format_percent(confidence_score(churn_prob)), "Probability distance", "◉", "good")


def show_gauge(default_probability: float, chart_key: str) -> None:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=float(default_probability * 100),
            title={"text": "Default Risk %"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#334155"},
                "steps": [
                    {"range": [0, 30], "color": "#dcfce7"},
                    {"range": [30, 70], "color": "#fef9c3"},
                    {"range": [70, 100], "color": "#fee2e2"},
                ],
            },
        )
    )
    st.plotly_chart(style_figure(fig), width="stretch", key=chart_key)


def show_recommendations(row: pd.Series) -> None:
    default_prob = row.get("default_probability", 0.0)
    churn_prob = row.get("churn_probability", 0.0)
    adoption_prob = row.get("adoption_probability", 1.0)

    st.subheader("Recommendation Engine")
    recommendations = []

    if default_prob >= 0.70:
        recommendations.extend(
            [
                "High default risk: reduce payout delay.",
                "Lower loan dependency before increasing credit exposure.",
                "Improve repayment behavior through smaller repayment cycles.",
            ]
        )
    elif default_prob >= 0.30:
        recommendations.append("Medium default risk: monitor working-capital gap and settlement speed.")
    else:
        recommendations.append("Low default risk: maintain current engagement and payment reliability.")

    if churn_prob >= 0.50:
        recommendations.extend(
            [
                "High churn risk: improve settlement speed.",
                "Increase working capital access for providers with repeated cash-flow pressure.",
            ]
        )

    if adoption_prob < 0.40:
        recommendations.append("Low adoption propensity: improve digital readiness and product education.")

    for item in recommendations:
        st.write(f"- {item}")


def show_explainability(importance: dict[str, pd.DataFrame], selected_model: str, chart_key: str) -> None:
    st.subheader("Explainability")
    model_importance = importance.get(selected_model)
    if model_importance is None or model_importance.empty:
        st.warning("Feature importance is unavailable for this model.")
        return

    top_features = model_importance.head(10).copy()
    st.plotly_chart(
        style_figure(px.bar(
            top_features.sort_values("importance"),
            x="importance",
            y="feature",
            orientation="h",
            title=f"Top Drivers: {selected_model}",
        )),
        width="stretch",
        key=chart_key,
    )

    with st.expander("Business interpretation"):
        st.write(
            "The chart ranks model drivers by absolute coefficient importance. Positive coefficients "
            "increase the model score; negative coefficients reduce it. Use this as directional evidence, "
            "not as a causal claim."
        )
        st.dataframe(
            top_features[["feature", "coefficient", "importance"]],
            hide_index=True,
            width="stretch",
        )


def show_existing_provider(predictions: pd.DataFrame, context: pd.DataFrame, importance: dict[str, pd.DataFrame]) -> None:
    provider_ids = sorted(predictions["provider_id"].dropna().unique())
    provider_id = st.selectbox("Select existing provider_id", provider_ids)
    provider_months = predictions.loc[predictions["provider_id"] == provider_id, "month"].sort_values().unique()
    selected_month = st.selectbox("Prediction month", provider_months, index=len(provider_months) - 1)

    row = predictions[
        (predictions["provider_id"] == provider_id) & (predictions["month"] == selected_month)
    ].iloc[0]

    provider_context = context[context["merchant_id"] == provider_id]
    if not provider_context.empty:
        profile = provider_context.iloc[0]
        st.caption(
            f"{profile.get('city', 'Unknown city')} | {profile.get('region', 'Unknown region')} | "
            f"{profile.get('category', 'Unknown category')}"
        )

    show_probability_cards(row)

    left, right = st.columns([1, 1])
    with left:
        show_gauge(row.get("default_probability", 0.0), "predictions_existing_default_gauge")
    with right:
        show_recommendations(row)

    selected_model = st.selectbox("Explain model", list(IMPORTANCE_FILES.keys()))
    show_explainability(
        importance,
        selected_model,
        f"predictions_existing_importance_{selected_model.lower().replace(' ', '_')}",
    )


def show_uploaded_provider(predictions: pd.DataFrame, models: dict[str, dict], importance: dict[str, pd.DataFrame]) -> None:
    uploaded_file = st.file_uploader("Upload provider CSV", type=["csv"])
    if uploaded_file is None:
        st.info("Upload a CSV with provider_id/month columns or model feature columns.")
        return

    uploaded = pd.read_csv(uploaded_file)
    if uploaded.empty:
        st.warning("Uploaded CSV has no rows.")
        return

    id_col = "provider_id" if "provider_id" in uploaded.columns else "merchant_id"
    if id_col in uploaded.columns and "month" in uploaded.columns:
        joined = uploaded.rename(columns={id_col: "provider_id"}).merge(
            predictions,
            on=["provider_id", "month"],
            how="left",
        )
        if joined["default_probability"].notna().any():
            scored = joined
        else:
            scored = score_uploaded_rows(uploaded, models)
    else:
        scored = score_uploaded_rows(uploaded, models)

    st.dataframe(scored.head(100), hide_index=True, width="stretch")

    row = scored.iloc[0]
    st.caption("Showing prediction detail for the first uploaded row.")
    show_probability_cards(row)

    left, right = st.columns([1, 1])
    with left:
        show_gauge(row.get("default_probability", 0.0), "predictions_upload_default_gauge")
    with right:
        show_recommendations(row)

    selected_model = st.selectbox("Explain model", list(IMPORTANCE_FILES.keys()), key="upload_explain_model")
    show_explainability(
        importance,
        selected_model,
        f"predictions_upload_importance_{selected_model.lower().replace(' ', '_')}",
    )


def show_prediction_download(predictions: pd.DataFrame) -> None:
    st.download_button(
        label="Download Prediction Results CSV",
        data=predictions.to_csv(index=False).encode("utf-8"),
        file_name="prediction_results.csv",
        mime="text/csv",
        key="download_prediction_results_csv",
    )


def main() -> None:
    apply_theme()
    render_sidebar_brand("Prediction Engine")
    page_header(
        "AI Prediction Copilot",
        "Upload, predict, explain, and recommend provider interventions across default, churn, adoption, and income growth.",
        "Prediction Intelligence",
    )
    require_login()

    try:
        predictions = load_prediction_exports()
        context = load_provider_context()
        models = load_models()
        importance = load_feature_importance()
    except FileNotFoundError as exc:
        st.error(f"Missing required artifact: {exc.filename}")
        st.stop()

    input_tab, explain_tab, data_tab = st.tabs(
        ["Predict", "Model Explainability", "Data Coverage"]
    )

    with input_tab:
        ask_data_panel("Why is this provider high risk? What intervention should be recommended?")
        mode = st.radio(
            "Prediction input",
            ["Select existing provider", "Upload provider CSV"],
            horizontal=True,
        )
        if mode == "Select existing provider":
            show_existing_provider(predictions, context, importance)
        else:
            show_uploaded_provider(predictions, models, importance)

    with explain_tab:
        selected_model = st.selectbox("Feature importance model", list(IMPORTANCE_FILES.keys()), key="global_explain_model")
        show_explainability(
            importance,
            selected_model,
            f"predictions_global_importance_{selected_model.lower().replace(' ', '_')}",
        )

    with data_tab:
        provider_count = predictions["provider_id"].nunique()
        month_count = predictions["month"].nunique()
        cols = st.columns(2)
        with cols[0]:
            metric_card("Prediction Providers", f"{provider_count:,}", "Scored provider base", "▦", "accent")
        with cols[1]:
            metric_card("Prediction Months", f"{month_count:,}", "Temporal prediction coverage", "◷", "good")
        show_prediction_download(predictions)
        st.dataframe(predictions.head(50), hide_index=True, width="stretch")


if __name__ == "__main__":
    main()
