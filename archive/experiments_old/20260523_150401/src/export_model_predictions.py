"""
Export provider-month predictions from existing trained NumPy model artifacts.

This script does not train or modify models. It reconstructs the feature frame
used by src/train_models.py, aligns columns to each saved model's feature
contract, and writes prediction CSVs for dashboard/reporting use.
"""

from __future__ import annotations

import os
import pickle
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.special import expit


DATA_DIR = Path("data")
MODEL_DIR = Path("output/models")
OUTPUT_DIR = Path("output")
DOCS_DIR = Path("docs")

PREDICTION_SPECS = {
    "churn_prediction": {
        "artifact": MODEL_DIR / "churn_prediction.pkl",
        "output": OUTPUT_DIR / "churn_predictions.csv",
    },
    "embedded_finance_adoption": {
        "artifact": MODEL_DIR / "embedded_finance_adoption.pkl",
        "output": OUTPUT_DIR / "adoption_predictions.csv",
    },
    "loan_default_prediction": {
        "artifact": MODEL_DIR / "loan_default_prediction.pkl",
        "output": OUTPUT_DIR / "default_predictions.csv",
    },
}


def boolify(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.astype(float)
    return series.astype(str).str.lower().isin(["true", "1", "yes"]).astype(float)


def load_provider_month_frame(data_dir: Path) -> pd.DataFrame:
    merchants = pd.read_csv(data_dir / "merchants.csv")
    payouts = pd.read_csv(data_dir / "payouts_loans.csv")
    kpis = pd.read_csv(data_dir / "provider_kpis.csv")

    frame = kpis.merge(merchants, on="merchant_id", suffixes=("", "_merchant"))
    frame = frame.merge(payouts, on=["merchant_id", "month"], how="left").copy()

    # Preserve the monthly grain requested by the dashboard exports.
    frame.loc[:, "provider_id"] = frame["merchant_id"]
    frame.loc[:, "business_type"] = frame["category"]

    for column in ["kyc_flag", "agent_usage_flag", "active_provider_month_flag", "forecast_usage"]:
        if column in frame.columns:
            column_position = frame.columns.get_loc(column)
            values = boolify(frame[column]).to_numpy(dtype=float)
            frame = frame.drop(columns=[column])
            frame.insert(column_position, column, values)

    return frame


def load_model(path: Path) -> Dict[str, object]:
    with path.open("rb") as handle:
        return pickle.load(handle)


def feature_frame_for_model(frame: pd.DataFrame, feature_names: List[str]) -> Tuple[pd.DataFrame, List[str]]:
    data = pd.DataFrame(index=frame.index)
    missing_features: List[str] = []

    for feature in feature_names:
        if feature in frame.columns:
            if frame[feature].dtype == bool:
                data[feature] = frame[feature].astype(float)
            elif frame[feature].dtype == object and set(
                frame[feature].dropna().astype(str).str.lower().unique()
            ).issubset({"true", "false", "1", "0", "yes", "no"}):
                data[feature] = boolify(frame[feature])
            else:
                data[feature] = pd.to_numeric(frame[feature], errors="coerce")
        elif feature.startswith("region_") and "region" in frame.columns:
            value = feature.replace("region_", "", 1)
            data[feature] = (frame["region"].fillna("missing").astype(str) == value).astype(float)
        elif feature.startswith("city_") and "city" in frame.columns:
            value = feature.replace("city_", "", 1)
            data[feature] = (frame["city"].fillna("missing").astype(str) == value).astype(float)
        elif feature.startswith("category_") and "category" in frame.columns:
            value = feature.replace("category_", "", 1)
            data[feature] = (frame["category"].fillna("missing").astype(str) == value).astype(float)
        elif feature.startswith("loan_status_") and "loan_status" in frame.columns:
            value = feature.replace("loan_status_", "", 1)
            data[feature] = (frame["loan_status"].fillna("missing").astype(str) == value).astype(float)
        else:
            missing_features.append(feature)
            data[feature] = 0.0

    return data.replace([np.inf, -np.inf], np.nan).fillna(0.0), missing_features


def score_artifact(model: Dict[str, object], frame: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    feature_names = list(model["feature_names"])
    x_frame, missing_features = feature_frame_for_model(frame, feature_names)
    x = x_frame.to_numpy(dtype=float)

    means = np.asarray(model["means"], dtype=float)
    stds = np.asarray(model["stds"], dtype=float)
    stds = np.where(stds == 0, 1.0, stds)
    weights = np.asarray(model["weights"], dtype=float)
    bias = float(model["bias"])
    threshold = float(model.get("threshold", 0.5))

    if x.shape[1] != len(weights):
        raise ValueError(
            f"Feature width mismatch for {model.get('model_name')}: "
            f"matrix has {x.shape[1]} columns, model has {len(weights)} weights"
        )

    scores = expit(((x - means) / stds) @ weights + bias)
    result = pd.DataFrame(
        {
            "provider_id": frame["provider_id"],
            "month": frame["month"],
            "prediction_probability": scores,
            "predicted_class": (scores >= threshold).astype(int),
            "model_name": model.get("model_name", "unknown_model"),
        }
    )
    return result, missing_features


def risk_band(probability: float) -> str:
    if probability < 0.30:
        return "Low"
    if probability < 0.70:
        return "Medium"
    return "High"


def write_report(
    report_path: Path,
    row_count: int,
    model_summaries: List[Dict[str, object]],
    risk_counts: pd.DataFrame,
) -> None:
    lines = [
        "# Predictions Export Report",
        "",
        "Generated provider-month prediction exports from existing artifacts in `output/models/`.",
        "No models were retrained.",
        "",
        f"Provider-month scoring rows: {row_count}",
        "",
        "## Model Exports",
        "",
        "| Model | Artifact | Output | Target | Threshold | Rows | Missing feature fallbacks |",
        "|---|---|---|---|---:|---:|---:|",
    ]

    for summary in model_summaries:
        lines.append(
            "| {model} | `{artifact}` | `{output}` | {target} | {threshold:.2f} | {rows} | {missing_count} |".format(
                **summary
            )
        )

    missing = {
        summary["model"]: summary["missing_features"]
        for summary in model_summaries
        if summary["missing_features"]
    }
    lines.extend(["", "## Feature Alignment", ""])
    if missing:
        for model, features in missing.items():
            lines.append(f"- `{model}`: missing columns filled with 0.0: {', '.join(features)}")
    else:
        lines.append("All saved model features were reconstructed from the current datasets.")

    lines.extend(
        [
            "",
            "## Default Risk Bands",
            "",
            "| Risk band | Rows | Share | Mean default probability |",
            "|---|---:|---:|---:|",
        ]
    )
    for _, row in risk_counts.iterrows():
        lines.append(
            f"| {row['risk_band']} | {int(row['rows'])} | {row['share']:.3f} | {row['mean_default_probability']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- `risk_scores.csv` uses the requested bands: Low `<0.30`, Medium `0.30-0.70`, High `>=0.70`.",
            "- Predictions are provider-month records, keyed by `provider_id` and `month`.",
            "- The default risk file enriches default probabilities with `city` and `business_type` from `merchants.csv`.",
        ]
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(DOCS_DIR, exist_ok=True)

    frame = load_provider_month_frame(DATA_DIR)
    model_summaries: List[Dict[str, object]] = []
    default_predictions = None

    for model_name, spec in PREDICTION_SPECS.items():
        model = load_model(spec["artifact"])
        predictions, missing_features = score_artifact(model, frame)
        predictions.to_csv(spec["output"], index=False)

        if model_name == "loan_default_prediction":
            default_predictions = predictions

        model_summaries.append(
            {
                "model": model.get("model_name", model_name),
                "artifact": spec["artifact"].as_posix(),
                "output": spec["output"].as_posix(),
                "target": model.get("target", ""),
                "threshold": float(model.get("threshold", 0.5)),
                "rows": len(predictions),
                "missing_count": len(missing_features),
                "missing_features": missing_features,
            }
        )

    if default_predictions is None:
        raise RuntimeError("Default prediction export was not created.")

    risk_scores = default_predictions.rename(columns={"prediction_probability": "default_probability"})[
        ["provider_id", "month", "default_probability"]
    ].copy()
    risk_scores.loc[:, "risk_band"] = risk_scores["default_probability"].map(risk_band)
    risk_scores = risk_scores.merge(
        frame[["provider_id", "month", "city", "business_type"]],
        on=["provider_id", "month"],
        how="left",
    )
    risk_scores.to_csv(OUTPUT_DIR / "risk_scores.csv", index=False)

    risk_counts = (
        risk_scores.groupby("risk_band", dropna=False)
        .agg(rows=("provider_id", "size"), mean_default_probability=("default_probability", "mean"))
        .reset_index()
    )
    risk_counts.loc[:, "share"] = risk_counts["rows"] / max(len(risk_scores), 1)
    risk_counts.loc[:, "risk_band"] = pd.Categorical(
        risk_counts["risk_band"], ["Low", "Medium", "High"], ordered=True
    )
    risk_counts = risk_counts.sort_values("risk_band")

    write_report(
        DOCS_DIR / "predictions_export_report.md",
        len(frame),
        model_summaries,
        risk_counts,
    )

    print("Prediction exports created:")
    for summary in model_summaries:
        print(f"- {summary['output']} ({summary['rows']} rows)")
    print(f"- {(OUTPUT_DIR / 'risk_scores.csv').as_posix()} ({len(risk_scores)} rows)")
    print(f"- {(DOCS_DIR / 'predictions_export_report.md').as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
