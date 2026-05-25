"""
Train dissertation-final leakage-safe models on the extended data_v2 panel.

Models use month-t baseline, lagged, and rolling features to predict t+1
outcomes. Same-period outcome variables and rollout timing fields are excluded.
"""

from __future__ import annotations

import argparse
import os
import pickle
import shutil
import warnings
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.special import expit

warnings.filterwarnings(
    "ignore",
    message=".*ChainedAssignmentError: behaviour will change in pandas 3.0.*",
    category=FutureWarning,
)


BASELINE_FEATURES = [
    "tenure_days",
    "avg_ticket",
    "monthly_income",
    "repeat_customer_rate",
    "platform_commission_pct",
    "kyc_flag",
    "payment_success_rate",
    "transaction_velocity",
    "multi_product_adoption",
    "digital_tool_usage",
    "ai_adoption_score",
    "agent_usage_flag",
]

LAGGED_FEATURES = [
    "payout_delay_days_lag1_imputed",
    "working_capital_gap_lag1",
    "income_growth_pct_lag1",
    "forecast_usage_lag1",
    "technology_adoption_score_lag1",
    "agentic_intelligence_score_lag1",
    "loan_amount_lag1",
    "loan_offer_flag_lag1",
    "active_provider_month_flag_lag1",
    "lock_in_score_lag1",
    "payout_delay_days_rolling3",
    "working_capital_gap_rolling3",
    "payout_volatility_rolling3",
    "rating_rolling3",
    "cancellation_rate_rolling3",
]

CATEGORICAL_FEATURES = ["region", "city", "category"]
FORBIDDEN_FEATURES = {
    "income_growth_pct",
    "monthly_profit",
    "retention_flag",
    "churn_probability",
    "default_flag",
    "payout_amount",
    "payout_delay_days",
    "loan_amount",
    "loan_status",
    "repayment_amount",
    "working_capital_gap",
    "loan_disbursal_time",
    "treatment_flag",
    "post_treatment_flag",
    "treatment_start_month",
    "intervention_timestamp",
    "months_since_intervention",
    "pre_treatment_flag",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train dissertation-final models.")
    parser.add_argument("--data_path", default=os.path.join("data_v2", "model_ready", "provider_month_future_targets.csv"))
    parser.add_argument("--models_dir", default=os.path.join("output", "models_final"))
    parser.add_argument("--predictions_dir", default=os.path.join("output", "predictions_final"))
    parser.add_argument("--risk_scores", default=os.path.join("output", "risk_scores.csv"))
    parser.add_argument("--report", default=os.path.join("docs", "final_model_metrics.md"))
    parser.add_argument("--archive_root", default=os.path.join("archive", "old_models"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=1400)
    parser.add_argument("--lr", type=float, default=0.035)
    parser.add_argument("--test_months", type=int, default=6)
    return parser.parse_args()


def boolify(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.astype(float)
    return series.astype(str).str.lower().isin(["true", "1", "yes"]).astype(float)


def archive_path(source: Path, archive_root: Path, run_id: str) -> Path:
    return archive_root / f"pre_final_v2_{run_id}" / source


def archive_previous_outputs(args: argparse.Namespace) -> List[Dict[str, str]]:
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    candidates = [
        Path("output/models"),
        Path("output/adoption_propensity"),
        Path("output/default_model_safe"),
        Path(args.models_dir),
        Path(args.predictions_dir),
    ]
    files: List[Path] = []
    for candidate in candidates:
        if candidate.exists():
            files.extend(path for path in candidate.rglob("*") if path.is_file())
    if Path(args.risk_scores).exists():
        files.append(Path(args.risk_scores))

    moved = []
    for source in sorted(set(files)):
        destination = archive_path(source, Path(args.archive_root), run_id)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        moved.append({"source": source.as_posix(), "destination": destination.as_posix()})
    return moved


def add_adoption_target(frame: pd.DataFrame) -> pd.DataFrame:
    panel = frame.sort_values(["merchant_id", "month"]).copy()
    grouped = panel.groupby("merchant_id", sort=False)
    panel["embedded_finance_adoption_tplus1"] = grouped["post_treatment_flag"].shift(-1).astype("boolean").astype("Float64")
    return panel


def load_frame(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path, low_memory=False)
    frame = add_adoption_target(frame)
    frame = frame[frame["has_tplus1_target"].astype(str).str.lower().isin(["true", "1", "yes"])].copy()
    frame.loc[:, "month_period"] = pd.PeriodIndex(frame["month"], freq="M")
    frame.loc[:, "provider_id"] = frame["merchant_id"]
    return frame


def feature_list(include_lagged: bool = True) -> List[str]:
    features = BASELINE_FEATURES + (LAGGED_FEATURES if include_lagged else []) + CATEGORICAL_FEATURES
    overlap = sorted(set(features) & FORBIDDEN_FEATURES)
    if overlap:
        raise ValueError(f"Forbidden leakage features requested: {overlap}")
    return features


def encode(frame: pd.DataFrame, features: List[str]) -> Tuple[pd.DataFrame, List[str]]:
    data = pd.DataFrame(index=frame.index)
    for feature in features:
        if feature in CATEGORICAL_FEATURES:
            continue
        if feature not in frame.columns:
            raise ValueError(f"Missing required feature: {feature}")
        if frame[feature].dtype == bool:
            data[feature] = frame[feature].astype(float)
        elif frame[feature].dtype == object and set(frame[feature].dropna().astype(str).str.lower().unique()).issubset(
            {"true", "false", "1", "0", "yes", "no"}
        ):
            data[feature] = boolify(frame[feature])
        else:
            data[feature] = pd.to_numeric(frame[feature], errors="coerce")

    for feature in CATEGORICAL_FEATURES:
        data = pd.concat([data, pd.get_dummies(frame[feature].fillna("missing"), prefix=feature, dtype=float)], axis=1)

    data = data.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return data, list(data.columns)


def temporal_split(frame: pd.DataFrame, test_months: int) -> Tuple[np.ndarray, np.ndarray]:
    months = pd.PeriodIndex(sorted(frame["month_period"].unique()), freq="M")
    test_start = months[max(0, len(months) - test_months)]
    train_mask = frame["month_period"] < test_start
    test_mask = frame["month_period"] >= test_start
    return np.where(train_mask)[0], np.where(test_mask)[0]


def scale_train_test(x: np.ndarray, train_idx: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    means = x[train_idx].mean(axis=0)
    stds = x[train_idx].std(axis=0)
    stds[stds == 0] = 1.0
    return (x - means) / stds, means, stds


def class_weights(y: np.ndarray) -> np.ndarray:
    pos = max(float(y.sum()), 1.0)
    neg = max(float(len(y) - y.sum()), 1.0)
    return np.where(y == 1, len(y) / (2 * pos), len(y) / (2 * neg))


def train_logistic(x: np.ndarray, y: np.ndarray, epochs: int, lr: float, l2: float = 0.0015) -> Tuple[np.ndarray, float]:
    weights = np.zeros(x.shape[1])
    bias = 0.0
    sample_weights = class_weights(y)
    norm = sample_weights.sum()
    for _ in range(epochs):
        pred = expit(x @ weights + bias)
        error = (pred - y) * sample_weights
        weights -= lr * ((x.T @ error) / norm + l2 * weights)
        bias -= lr * float(error.sum() / norm)
    return weights, bias


def train_linear(x: np.ndarray, y: np.ndarray, epochs: int, lr: float, l2: float = 0.001) -> Tuple[np.ndarray, float]:
    weights = np.zeros(x.shape[1])
    bias = float(np.mean(y))
    n = max(len(y), 1)
    for _ in range(epochs):
        pred = x @ weights + bias
        error = pred - y
        weights -= lr * ((x.T @ error) / n + l2 * weights)
        bias -= lr * float(error.mean())
    return weights, bias


def roc_auc(y_true: np.ndarray, scores: np.ndarray) -> float:
    y_true = y_true.astype(int)
    positives = int(y_true.sum())
    negatives = int(len(y_true) - positives)
    if positives == 0 or negatives == 0:
        return np.nan
    order = np.argsort(scores)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(scores) + 1)
    pos_rank_sum = ranks[y_true == 1].sum()
    return float((pos_rank_sum - positives * (positives + 1) / 2) / (positives * negatives))


def tune_threshold(y_true: np.ndarray, scores: np.ndarray, beta: float = 1.0) -> float:
    best_threshold = 0.5
    best_score = -1.0
    beta_sq = beta * beta
    for threshold in np.linspace(0.02, 0.98, 97):
        pred = (scores >= threshold).astype(int)
        tp = ((pred == 1) & (y_true == 1)).sum()
        fp = ((pred == 1) & (y_true == 0)).sum()
        fn = ((pred == 0) & (y_true == 1)).sum()
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        score = (1 + beta_sq) * precision * recall / max(beta_sq * precision + recall, 1e-12)
        if score > best_score:
            best_score = score
            best_threshold = float(threshold)
    return best_threshold


def classification_metrics(y_true: np.ndarray, scores: np.ndarray, threshold: float) -> Dict[str, float]:
    pred = (scores >= threshold).astype(int)
    y = y_true.astype(int)
    tp = int(((pred == 1) & (y == 1)).sum())
    tn = int(((pred == 0) & (y == 0)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-12)
    return {
        "accuracy": (tp + tn) / max(len(y), 1),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc(y, scores),
        "threshold": threshold,
        "positive_rate": float(y.mean()),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


def regression_metrics(y_true: np.ndarray, pred: np.ndarray) -> Dict[str, float]:
    error = pred - y_true
    denom = float(np.sum((y_true - y_true.mean()) ** 2))
    return {
        "rmse": float(np.sqrt(np.mean(error**2))),
        "mae": float(np.mean(np.abs(error))),
        "r2": 1 - float(np.sum(error**2)) / denom if denom > 0 else np.nan,
        "directional_accuracy": float((np.sign(pred) == np.sign(y_true)).mean()),
    }


def feature_importance(names: List[str], weights: np.ndarray) -> pd.DataFrame:
    return (
        pd.DataFrame({"feature": names, "coefficient": weights})
        .assign(importance=lambda df: df["coefficient"].abs())
        .sort_values("importance", ascending=False)
    )


def fit_classifier(
    frame: pd.DataFrame,
    model_name: str,
    target: str,
    features: List[str],
    args: argparse.Namespace,
    beta: float = 1.0,
) -> Tuple[Dict[str, object], pd.DataFrame, pd.DataFrame]:
    model_frame = frame[pd.to_numeric(frame[target], errors="coerce").notna()].copy()
    encoded, names = encode(model_frame, features)
    train_idx, test_idx = temporal_split(model_frame, args.test_months)
    x_raw = encoded.to_numpy(dtype=float)
    x, means, stds = scale_train_test(x_raw, train_idx)
    y = pd.to_numeric(model_frame[target], errors="coerce").to_numpy(dtype=float)
    weights, bias = train_logistic(x[train_idx], y[train_idx], args.epochs, args.lr)
    train_scores = expit(x[train_idx] @ weights + bias)
    threshold = tune_threshold(y[train_idx], train_scores, beta=beta)
    scores = expit(x @ weights + bias)
    metrics = classification_metrics(y[test_idx], scores[test_idx], threshold)
    predictions = pd.DataFrame(
        {
            "provider_id": model_frame["provider_id"],
            "month": model_frame["month"],
            "target_month": model_frame["target_month"],
            "prediction_probability": scores,
            "predicted_class": (scores >= threshold).astype(int),
            "actual": y,
            "model_name": model_name,
            "split": np.where(np.isin(np.arange(len(model_frame)), test_idx), "test", "train"),
        }
    )
    artifact = {
        "model_type": "weighted_numpy_logistic_regression",
        "model_name": model_name,
        "target": target,
        "feature_names": names,
        "forbidden_features": sorted(FORBIDDEN_FEATURES),
        "means": means,
        "stds": stds,
        "weights": weights,
        "bias": bias,
        "threshold": threshold,
        "metrics": metrics,
        "split": "temporal_last_6_months",
    }
    return artifact, predictions, feature_importance(names, weights)


def fit_regressor(
    frame: pd.DataFrame,
    model_name: str,
    target: str,
    features: List[str],
    args: argparse.Namespace,
) -> Tuple[Dict[str, object], pd.DataFrame, pd.DataFrame]:
    model_frame = frame[pd.to_numeric(frame[target], errors="coerce").notna()].copy()
    encoded, names = encode(model_frame, features)
    train_idx, test_idx = temporal_split(model_frame, args.test_months)
    x_raw = encoded.to_numpy(dtype=float)
    x, means, stds = scale_train_test(x_raw, train_idx)
    y = pd.to_numeric(model_frame[target], errors="coerce").to_numpy(dtype=float)
    weights, bias = train_linear(x[train_idx], y[train_idx], args.epochs, args.lr)
    pred = x @ weights + bias
    metrics = regression_metrics(y[test_idx], pred[test_idx])
    predictions = pd.DataFrame(
        {
            "provider_id": model_frame["provider_id"],
            "month": model_frame["month"],
            "target_month": model_frame["target_month"],
            "prediction_value": pred,
            "actual": y,
            "model_name": model_name,
            "split": np.where(np.isin(np.arange(len(model_frame)), test_idx), "test", "train"),
        }
    )
    artifact = {
        "model_type": "numpy_linear_regression",
        "model_name": model_name,
        "target": target,
        "feature_names": names,
        "forbidden_features": sorted(FORBIDDEN_FEATURES),
        "means": means,
        "stds": stds,
        "weights": weights,
        "bias": bias,
        "metrics": metrics,
        "split": "temporal_last_6_months",
    }
    return artifact, predictions, feature_importance(names, weights)


def save_artifact(path: Path, artifact: Dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as handle:
        pickle.dump(artifact, handle)


def risk_band(prob: float) -> str:
    if prob < 0.30:
        return "Low"
    if prob < 0.70:
        return "Medium"
    return "High"


def write_report(
    args: argparse.Namespace,
    metrics_rows: List[Dict[str, object]],
    moved: List[Dict[str, str]],
    feature_sets: Dict[str, List[str]],
) -> None:
    metrics = pd.DataFrame(metrics_rows)
    lines = [
        "# Final Model Metrics",
        "",
        f"Generated on {datetime.now().date().isoformat()}.",
        "",
        "Models were retrained on the extended `data_v2` panel using leakage-safe month-t predictors and t+1 targets.",
        "",
        "## Outputs",
        "",
        "- Models: `output/models_final/`",
        "- Predictions: `output/predictions_final/`",
        "- Risk scores: `output/risk_scores.csv`",
        "",
        "## Leakage Controls",
        "",
        "- Used baseline provider fields plus lagged/rolling provider-month fields.",
        "- Excluded same-period outcomes such as `retention_flag`, `income_growth_pct`, `monthly_profit`, `default_flag`, current payout/loan amount fields, and repayment fields.",
        "- Excluded treatment rollout timing fields from predictors, including `treatment_flag`, `post_treatment_flag`, `treatment_start_month`, `intervention_timestamp`, and `months_since_intervention`.",
        "- Evaluation uses a temporal split: the latest six feature months are test rows.",
        "",
        "## Metrics",
        "",
        "| model | target | split | metric | value |",
        "|---|---|---|---|---:|",
    ]
    for _, row in metrics.iterrows():
        lines.append(f"| {row['model']} | {row['target']} | test | {row['metric']} | {row['value']:.4f} |")

    lines.extend(["", "## Feature Sets", ""])
    for model, features in feature_sets.items():
        lines.append(f"### {model}")
        lines.append("")
        for feature in features:
            lines.append(f"- `{feature}`")
        lines.append("")

    lines.extend(["## Archived Previous Models", ""])
    if moved:
        lines.extend(["| source | destination |", "|---|---|"])
        for row in moved:
            lines.append(f"| `{row['source']}` | `{row['destination']}` |")
    else:
        lines.append("No previous model files were found to archive.")

    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    moved = archive_previous_outputs(args)
    Path(args.models_dir).mkdir(parents=True, exist_ok=True)
    Path(args.predictions_dir).mkdir(parents=True, exist_ok=True)

    frame = load_frame(args.data_path)
    full_features = feature_list(include_lagged=True)
    adoption_features = feature_list(include_lagged=False)
    metrics_rows: List[Dict[str, object]] = []
    feature_sets = {
        "churn_prediction": full_features,
        "loan_default_prediction": full_features,
        "embedded_finance_adoption": adoption_features,
        "income_growth_prediction": full_features,
    }

    models = {}
    outputs = {}
    importances = {}
    models["churn_prediction"], outputs["churn_prediction"], importances["churn_prediction"] = fit_classifier(
        frame, "churn_prediction", "churn_target_tplus1", full_features, args, beta=1.0
    )
    models["loan_default_prediction"], outputs["loan_default_prediction"], importances["loan_default_prediction"] = fit_classifier(
        frame, "loan_default_prediction", "default_next_cycle", full_features, args, beta=2.0
    )
    models["embedded_finance_adoption"], outputs["embedded_finance_adoption"], importances["embedded_finance_adoption"] = fit_classifier(
        frame, "embedded_finance_adoption", "embedded_finance_adoption_tplus1", adoption_features, args, beta=1.0
    )
    models["income_growth_prediction"], outputs["income_growth_prediction"], importances["income_growth_prediction"] = fit_regressor(
        frame, "income_growth_prediction", "income_growth_tplus1", full_features, args
    )

    for model_name, artifact in models.items():
        save_artifact(Path(args.models_dir) / f"{model_name}.pkl", artifact)
        importances[model_name].to_csv(Path(args.models_dir) / f"{model_name}_feature_importance.csv", index=False)
        for metric, value in artifact["metrics"].items():
            metrics_rows.append({"model": model_name, "target": artifact["target"], "metric": metric, "value": float(value)})

    pd.DataFrame(metrics_rows).to_csv(Path(args.models_dir) / "final_model_metrics.csv", index=False)

    for model_name, prediction in outputs.items():
        prediction.to_csv(Path(args.predictions_dir) / f"{model_name}_predictions.csv", index=False)

    default_predictions = outputs["loan_default_prediction"].copy()
    merchants = pd.read_csv(Path("data_v2") / "merchants.csv", usecols=["merchant_id", "city", "category"])
    risk_scores = default_predictions.rename(columns={"prediction_probability": "default_probability"})[
        ["provider_id", "month", "target_month", "default_probability", "predicted_class", "split"]
    ].copy()
    risk_scores.loc[:, "risk_band"] = risk_scores["default_probability"].map(risk_band)
    risk_scores = risk_scores.merge(merchants.rename(columns={"merchant_id": "provider_id", "category": "business_type"}), on="provider_id", how="left")
    risk_scores.to_csv(args.risk_scores, index=False)

    write_report(args, metrics_rows, moved, feature_sets)
    print(f"Archived previous model artifacts: {len(moved)}")
    print(f"Saved final models to {Path(args.models_dir).resolve()}")
    print(f"Saved final predictions to {Path(args.predictions_dir).resolve()}")
    print(f"Saved final risk scores to {Path(args.risk_scores).resolve()}")
    print(f"Saved final metrics report to {Path(args.report).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
