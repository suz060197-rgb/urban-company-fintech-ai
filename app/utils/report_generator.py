"""Executive PDF report generation for the dissertation Streamlit app."""

from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"
DOCS_DIR = ROOT_DIR / "docs"
MODELS_FINAL_DIR = OUTPUT_DIR / "models_final"


def read_csv_optional(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def pct(value: float | int | np.floating) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{float(value):.1%}"


def money(value: float | int | np.floating) -> str:
    if pd.isna(value):
        return "N/A"
    return f"Rs {float(value):,.0f}"


def number(value: float | int | np.floating) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{float(value):,.2f}"


def metric_value(metrics: pd.DataFrame, model_keyword: str, metric_keyword: str) -> float:
    if metrics.empty or not {"model", "metric", "value"}.issubset(metrics.columns):
        return np.nan

    model_mask = metrics["model"].astype(str).str.lower().str.contains(model_keyword.lower(), na=False)
    metric_mask = metrics["metric"].astype(str).str.lower().str.contains(metric_keyword.lower(), na=False)
    values = pd.to_numeric(metrics.loc[model_mask & metric_mask, "value"], errors="coerce").dropna()
    if values.empty:
        return np.nan
    return float(values.iloc[0])


def latest_month(frame: pd.DataFrame, column: str = "month") -> str:
    if frame.empty or column not in frame.columns:
        return "N/A"
    dates = pd.to_datetime(frame[column], errors="coerce")
    if dates.notna().any():
        return dates.max().strftime("%Y-%m")
    return "N/A"


def load_report_inputs() -> dict[str, pd.DataFrame]:
    return {
        "merchants": read_csv_optional(DATA_DIR / "merchants.csv"),
        "provider_kpis": read_csv_optional(DATA_DIR / "provider_kpis.csv"),
        "payouts_loans": read_csv_optional(DATA_DIR / "payouts_loans.csv"),
        "primary": read_csv_optional(DATA_DIR / "primary_responses_clean.csv"),
        "risk_scores": read_csv_optional(OUTPUT_DIR / "risk_scores.csv"),
        "default_predictions": read_csv_optional(OUTPUT_DIR / "default_predictions.csv"),
        "churn_predictions": read_csv_optional(OUTPUT_DIR / "churn_predictions.csv"),
        "adoption_predictions": read_csv_optional(OUTPUT_DIR / "adoption_predictions.csv"),
        "metrics": read_csv_optional(MODELS_FINAL_DIR / "final_model_metrics.csv"),
    }


def summarize_inputs(inputs: dict[str, pd.DataFrame]) -> dict[str, object]:
    merchants = inputs["merchants"]
    kpis = inputs["provider_kpis"]
    payouts = inputs["payouts_loans"]
    primary = inputs["primary"]
    risk = inputs["risk_scores"]
    default_predictions = inputs["default_predictions"]
    churn_predictions = inputs["churn_predictions"]
    adoption_predictions = inputs["adoption_predictions"]
    metrics = inputs["metrics"]

    provider_count = merchants["merchant_id"].nunique() if "merchant_id" in merchants.columns else np.nan
    high_risk_share = (
        risk["risk_band"].astype(str).str.lower().eq("high").mean()
        if "risk_band" in risk.columns and not risk.empty
        else np.nan
    )
    medium_risk_share = (
        risk["risk_band"].astype(str).str.lower().eq("medium").mean()
        if "risk_band" in risk.columns and not risk.empty
        else np.nan
    )
    avg_default_probability = (
        pd.to_numeric(risk["default_probability"], errors="coerce").mean()
        if "default_probability" in risk.columns
        else np.nan
    )
    default_positive_rate = (
        pd.to_numeric(default_predictions["predicted_class"], errors="coerce").mean()
        if "predicted_class" in default_predictions.columns
        else np.nan
    )
    avg_churn_probability = (
        pd.to_numeric(churn_predictions["prediction_probability"], errors="coerce").mean()
        if "prediction_probability" in churn_predictions.columns
        else np.nan
    )
    churn_positive_rate = (
        pd.to_numeric(churn_predictions["predicted_class"], errors="coerce").mean()
        if "predicted_class" in churn_predictions.columns
        else np.nan
    )
    avg_adoption_probability = (
        pd.to_numeric(adoption_predictions["prediction_probability"], errors="coerce").mean()
        if "prediction_probability" in adoption_predictions.columns
        else np.nan
    )
    adoption_positive_rate = (
        pd.to_numeric(adoption_predictions["predicted_class"], errors="coerce").mean()
        if "predicted_class" in adoption_predictions.columns
        else np.nan
    )

    retention_rate = (
        pd.to_numeric(kpis["retention_flag"], errors="coerce").mean()
        if "retention_flag" in kpis.columns
        else np.nan
    )
    avg_growth = (
        pd.to_numeric(kpis["income_growth_pct"], errors="coerce").mean()
        if "income_growth_pct" in kpis.columns
        else np.nan
    )
    active_growth = np.nan
    retained_growth = np.nan
    median_growth = np.nan
    if {"income_growth_pct", "merchant_id", "month"}.issubset(kpis.columns):
        growth_values = pd.to_numeric(kpis["income_growth_pct"], errors="coerce")
        median_growth = float(growth_values.median())
        if "active_provider_month_flag" in payouts.columns:
            active = kpis[["merchant_id", "month", "income_growth_pct"]].merge(
                payouts[["merchant_id", "month", "active_provider_month_flag"]],
                on=["merchant_id", "month"],
                how="left",
            )
            active_mask = active["active_provider_month_flag"].astype(str).str.lower().isin(["true", "1", "yes"])
            active_growth = pd.to_numeric(active.loc[active_mask, "income_growth_pct"], errors="coerce").mean()
        if "retention_flag" in kpis.columns:
            retained_mask = kpis["retention_flag"].astype(str).str.lower().isin(["true", "1", "yes"])
            retained_growth = pd.to_numeric(kpis.loc[retained_mask, "income_growth_pct"], errors="coerce").mean()
    avg_profit = (
        pd.to_numeric(kpis["monthly_profit"], errors="coerce").mean()
        if "monthly_profit" in kpis.columns
        else np.nan
    )
    avg_tech = (
        pd.to_numeric(kpis["technology_adoption_score"], errors="coerce").mean()
        if "technology_adoption_score" in kpis.columns
        else np.nan
    )

    loan_offer_rate = (
        pd.to_numeric(payouts["loan_offer_flag"], errors="coerce").mean()
        if "loan_offer_flag" in payouts.columns
        else np.nan
    )
    default_rate = (
        pd.to_numeric(payouts["default_flag"], errors="coerce").mean()
        if "default_flag" in payouts.columns
        else np.nan
    )
    avg_working_capital_gap = (
        pd.to_numeric(payouts["working_capital_gap"], errors="coerce").mean()
        if "working_capital_gap" in payouts.columns
        else np.nan
    )

    survey_count = len(primary)
    survey_digital = (
        pd.to_numeric(primary["digital_adoption_score_scaled"], errors="coerce").mean()
        if "digital_adoption_score_scaled" in primary.columns
        else np.nan
    )
    settlement_pain = (
        pd.to_numeric(primary["settlement_delay_impact_scaled"], errors="coerce").ge(0.75).mean()
        if "settlement_delay_impact_scaled" in primary.columns
        else np.nan
    )
    credit_need = (
        pd.to_numeric(primary["needed_business_credit_binary"], errors="coerce").mean()
        if "needed_business_credit_binary" in primary.columns
        else np.nan
    )
    ai_usage = (
        pd.to_numeric(primary["ai_tool_usage_binary"], errors="coerce").mean()
        if "ai_tool_usage_binary" in primary.columns
        else np.nan
    )

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "coverage_month": latest_month(kpis),
        "provider_count": provider_count,
        "high_risk_share": high_risk_share,
        "medium_risk_share": medium_risk_share,
        "avg_default_probability": avg_default_probability,
        "default_positive_rate": default_positive_rate,
        "avg_churn_probability": avg_churn_probability,
        "churn_positive_rate": churn_positive_rate,
        "avg_adoption_probability": avg_adoption_probability,
        "adoption_positive_rate": adoption_positive_rate,
        "retention_rate": retention_rate,
        "avg_growth": avg_growth,
        "active_growth": active_growth,
        "retained_growth": retained_growth,
        "median_growth": median_growth,
        "avg_profit": avg_profit,
        "avg_tech": avg_tech,
        "loan_offer_rate": loan_offer_rate,
        "default_rate": default_rate,
        "avg_working_capital_gap": avg_working_capital_gap,
        "survey_count": survey_count,
        "survey_digital": survey_digital,
        "settlement_pain": settlement_pain,
        "credit_need": credit_need,
        "ai_usage": ai_usage,
        "default_auc": metric_value(metrics, "default", "roc"),
        "churn_auc": metric_value(metrics, "churn", "roc"),
        "adoption_auc": metric_value(metrics, "adoption", "roc"),
        "income_r2": metric_value(metrics, "income", "r2"),
    }


def executive_findings(summary: dict[str, object]) -> list[str]:
    findings: list[str] = []

    if pd.notna(summary["high_risk_share"]):
        findings.append(
            f"High-risk providers represent {pct(summary['high_risk_share'])} of scored provider-month records, "
            f"with average default probability at {pct(summary['avg_default_probability'])}."
        )
    if pd.notna(summary["avg_growth"]):
        findings.append(
            f"Churn-adjusted provider growth is {pct(summary['avg_growth'])}, while active-provider growth is "
            f"{pct(summary['active_growth'])} and retention is {pct(summary['retention_rate'])}."
        )
    if pd.notna(summary["settlement_pain"]):
        findings.append(
            f"Primary research shows {pct(summary['settlement_pain'])} of respondents report strong settlement-delay pain, "
            f"while {pct(summary['credit_need'])} report a need for business credit."
        )
    if pd.notna(summary["default_auc"]):
        findings.append(
            f"The default model is the strongest production risk signal with ROC AUC {number(summary['default_auc'])}; "
            f"other models should be interpreted as decision support, not automated decisions."
        )
    if pd.notna(summary["avg_churn_probability"]):
        findings.append(
            f"Prediction outputs show average churn probability at {pct(summary['avg_churn_probability'])} "
            f"and average adoption propensity at {pct(summary['avg_adoption_probability'])}."
        )

    return findings or ["Insufficient project artifacts were available to generate a full executive summary."]


def recommendation_bullets(summary: dict[str, object]) -> list[str]:
    recommendations = [
        "Prioritize high-risk providers for working-capital review, repayment nudges, and payout-delay monitoring.",
        "Use churn risk with retention outreach, faster settlement support, and repeat-customer enablement.",
        "Target low-adoption providers with digital-readiness training, UPI/payment workflow support, and simple embedded-finance education.",
        "Use model outputs as decision support with human review, especially where credit access or default classification affects providers.",
    ]
    if pd.notna(summary["settlement_pain"]) and float(summary["settlement_pain"]) >= 0.5:
        recommendations.append("Primary research indicates settlement delay is a major pain point; make settlement transparency a priority intervention.")
    if pd.notna(summary["credit_need"]) and float(summary["credit_need"]) >= 0.5:
        recommendations.append("Credit need is material in the survey sample; design responsible small-ticket credit with clear repayment terms.")
    return recommendations


def report_sections(summary: dict[str, object]) -> dict[str, list[str]]:
    return {
        "Risk Summary": [
            f"High risk share: {pct(summary['high_risk_share'])}",
            f"Medium risk share: {pct(summary['medium_risk_share'])}",
            f"Average default probability: {pct(summary['avg_default_probability'])}",
            f"Observed synthetic default rate: {pct(summary['default_rate'])}",
            "Recommended action: prioritize working-capital support and settlement monitoring for high-risk providers.",
        ],
        "Prediction Summary": [
            f"Predicted default class share: {pct(summary['default_positive_rate'])}",
            f"Average churn probability: {pct(summary['avg_churn_probability'])}",
            f"Predicted churn class share: {pct(summary['churn_positive_rate'])}",
            f"Average embedded-finance adoption probability: {pct(summary['avg_adoption_probability'])}",
            f"Predicted adoption class share: {pct(summary['adoption_positive_rate'])}",
            "Interpretation: predictions support provider segmentation across risk, retention, and adoption propensity.",
        ],
        "Growth And Retention": [
            f"Churn-adjusted growth: {pct(summary['avg_growth'])}",
            f"Growth among active providers: {pct(summary['active_growth'])}",
            f"Retained-provider growth: {pct(summary['retained_growth'])}",
            f"Median provider growth: {pct(summary['median_growth'])}",
            f"Average monthly profit: {money(summary['avg_profit'])}",
            f"Average technology adoption score: {number(summary['avg_tech'])}",
            f"Retention rate: {pct(summary['retention_rate'])}",
            "Interpretation: embedded finance and digital adoption appear more strongly associated with operational resilience, retention, liquidity stability, and profit continuity than direct income expansion.",
            "Growth appears constrained by churn and provider inactivity rather than technology failure.",
        ],
        "Model Metrics": [
            f"Default model ROC AUC: {number(summary['default_auc'])}",
            f"Churn model ROC AUC: {number(summary['churn_auc'])}",
            f"Adoption model ROC AUC: {number(summary['adoption_auc'])}",
            f"Income growth model R2: {number(summary['income_r2'])}",
            "Governance note: use leakage-safe t+1 features and monitor class imbalance before operational deployment.",
        ],
        "Primary Findings": [
            f"Survey respondents: {int(summary['survey_count']) if pd.notna(summary['survey_count']) else 'N/A'}",
            f"Digital adoption score: {number(summary['survey_digital'])}",
            f"Strong settlement-delay pain: {pct(summary['settlement_pain'])}",
            f"Need business credit: {pct(summary['credit_need'])}",
            f"AI tool usage: {pct(summary['ai_usage'])}",
            "Dissertation use: primary responses validate the direction of settlement, credit, and digital-readiness assumptions.",
        ],
        "Recommendations": recommendation_bullets(summary),
    }


def _wrap_lines(text: str, width: int = 92) -> list[str]:
    words = str(text).split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join(current + [word])
        if len(candidate) > width and current:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines


def _draw_bullets(canvas, bullets: Iterable[str], x: int, y: int, width: int, leading: int = 14) -> int:
    for bullet in bullets:
        lines = _wrap_lines(bullet, width=width)
        for i, line in enumerate(lines):
            prefix = "- " if i == 0 else "  "
            canvas.drawString(x, y, prefix + line)
            y -= leading
        y -= 4
    return y


def build_executive_pdf(summary: dict[str, object]) -> bytes:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError as exc:  # pragma: no cover - tested through page warning
        raise RuntimeError("ReportLab is required to generate PDF reports. Install `reportlab`.") from exc

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
        title="Razorpay Embedded Finance Executive Report",
    )
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Razorpay Embedded Finance x Urban Company Providers", styles["Title"]))
    story.append(Paragraph("Executive Report", styles["Heading2"]))
    story.append(Paragraph(f"Generated: {summary['generated_at']} | Data coverage: {summary['coverage_month']}", styles["Normal"]))
    story.append(Spacer(1, 12))

    kpi_rows = [
        ["Metric", "Value"],
        ["Providers", f"{summary['provider_count']:,.0f}" if pd.notna(summary["provider_count"]) else "N/A"],
        ["High Risk Share", pct(summary["high_risk_share"])],
        ["Retention Rate", pct(summary["retention_rate"])],
        ["Churn-Adjusted Growth", pct(summary["avg_growth"])],
        ["Active-Provider Growth", pct(summary["active_growth"])],
        ["Survey Respondents", str(summary["survey_count"])],
    ]
    table = Table(kpi_rows, colWidths=[210, 230])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F7F9FB")),
                ("PADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Executive Summary", styles["Heading2"]))
    for finding in executive_findings(summary):
        story.append(Paragraph(f"- {finding}", styles["BodyText"]))
    story.append(Spacer(1, 10))

    for section, bullets in report_sections(summary).items():
        story.append(Paragraph(section, styles["Heading2"]))
        for bullet in bullets:
            story.append(Paragraph(f"- {bullet}", styles["BodyText"]))
        story.append(Spacer(1, 8))

    story.append(Paragraph("Conclusion", styles["Heading2"]))
    story.append(
        Paragraph(
            "The combined synthetic operational data, leakage-safe ML outputs, and primary survey evidence support a dissertation narrative in which embedded finance appears to support liquidity and retention before measurable income expansion. Technology adoption improves operational resilience and retention; income expansion remains conditional on churn control, provider activity, settlement speed, and category economics.",
            styles["BodyText"],
        )
    )

    doc.build(story)
    return buffer.getvalue()
