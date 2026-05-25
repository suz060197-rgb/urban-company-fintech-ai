"""
Retrain only the weak models using leakage-safer lagged and rolling features.

Models retrained:
- loan_default_prediction -> target: default_next_cycle
- embedded_finance_adoption -> target: adoption_state_tplus1

Churn and income models are intentionally not retrained here.
"""

from __future__ import annotations

import argparse
import os
import pickle
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.special import expit


LAGGED_NUMERIC_FEATURES = [
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
    "treatment_flag",
    "treatment_start_month",
    "months_since_intervention",
    "pre_treatment_flag",
    "post_treatment_flag",
]

CATEGORICAL_FEATURES = ["region", "city", "category"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Retrain weak models with lagged features.")
    parser.add_argument(
        "--data_path",
        default=os.path.join("data", "model_ready", "provider_month_future_targets.csv"),
        help="Future-target provider-month table.",
    )
    parser.add_argument("--old_metrics", default=os.path.join("output", "models", "model_metrics.csv"))
    parser.add_argument("--out_dir", default=os.path.join("output", "models_retrained"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--test_frac", type=float, default=0.25)
    parser.add_argument("--epochs", type=int, default=900)
    parser.add_argument("--lr", type=float, default=0.035)
    return parser.parse_args()


def boolify(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.astype(float)
    return series.astype(str).str.lower().isin(["true", "1", "yes"]).astype(float)


def prepare_frame(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path)
    frame = frame[frame["has_tplus1_target"].astype(bool)].copy()
    month_values = pd.to_datetime(frame["month"], errors="coerce")
    frame = frame.assign(month_index=month_values.dt.year * 12 + month_values.dt.month)
    frame["adoption_state_tplus1"] = (
        frame.sort_values(["merchant_id", "month"])
        .groupby("merchant_id")["post_treatment_flag"]
        .shift(-1)
        .astype("boolean")
        .astype("Float64")
    )
    frame = frame[frame["adoption_state_tplus1"].notna()].copy()
    return frame


def encode(frame: pd.DataFrame, features: List[str], target: str):
    data = pd.DataFrame(index=frame.index)
    for feature in features:
        if feature in CATEGORICAL_FEATURES:
            continue
        if feature not in frame.columns:
            raise ValueError(f"Missing feature: {feature}")
        if frame[feature].dtype == bool:
            data[feature] = frame[feature].astype(float)
        elif frame[feature].dtype == object and set(frame[feature].dropna().astype(str).str.lower().unique()).issubset(
            {"true", "false"}
        ):
            data[feature] = boolify(frame[feature])
        else:
            data[feature] = pd.to_numeric(frame[feature], errors="coerce")

    for feature in CATEGORICAL_FEATURES:
        if feature in features:
            data = pd.concat([data, pd.get_dummies(frame[feature].fillna("missing"), prefix=feature, dtype=float)], axis=1)

    data = data.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    y = pd.to_numeric(frame[target], errors="coerce").fillna(0.0).to_numpy(dtype=float)
    x = data.to_numpy(dtype=float)
    means = x.mean(axis=0)
    stds = x.std(axis=0)
    stds[stds == 0] = 1.0
    return (x - means) / stds, y, list(data.columns), means, stds


def split_indices(n_rows: int, test_frac: float, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    order = rng.permutation(n_rows)
    n_test = max(1, int(round(n_rows * test_frac)))
    return order[n_test:], order[:n_test]


def class_weights(y: np.ndarray) -> np.ndarray:
    pos = max(float(y.sum()), 1.0)
    neg = max(float(len(y) - y.sum()), 1.0)
    pos_weight = len(y) / (2 * pos)
    neg_weight = len(y) / (2 * neg)
    return np.where(y == 1, pos_weight, neg_weight)


def train_weighted_logistic(x: np.ndarray, y: np.ndarray, epochs: int, lr: float, l2: float = 0.001):
    weights = np.zeros(x.shape[1])
    bias = 0.0
    sample_weights = class_weights(y)
    norm = sample_weights.sum()
    for _ in range(epochs):
        pred = expit(x @ weights + bias)
        error = (pred - y) * sample_weights
        grad_w = (x.T @ error) / norm + l2 * weights
        grad_b = float(error.sum() / norm)
        weights -= lr * grad_w
        bias -= lr * grad_b
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


def tune_threshold(y_true: np.ndarray, scores: np.ndarray) -> float:
    best_threshold = 0.5
    best_f1 = -1.0
    for threshold in np.linspace(0.03, 0.97, 95):
        pred = (scores >= threshold).astype(int)
        tp = ((pred == 1) & (y_true == 1)).sum()
        fp = ((pred == 1) & (y_true == 0)).sum()
        fn = ((pred == 0) & (y_true == 1)).sum()
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        f1 = 2 * precision * recall / max(precision + recall, 1e-12)
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = float(threshold)
    return best_threshold


def metrics(y_true: np.ndarray, scores: np.ndarray, threshold: float) -> Dict[str, float]:
    pred = (scores >= threshold).astype(int)
    y = y_true.astype(int)
    tp = int(((pred == 1) & (y == 1)).sum())
    tn = int(((pred == 0) & (y == 0)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    return {
        "accuracy": (tp + tn) / max(len(y), 1),
        "precision": precision,
        "recall": recall,
        "roc_auc": roc_auc(y, scores),
        "threshold": threshold,
        "positive_rate": float(y.mean()),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


def feature_importance(model_name: str, feature_names: List[str], weights: np.ndarray) -> pd.DataFrame:
    table = pd.DataFrame({"model": model_name, "feature": feature_names, "coefficient": weights})
    table = table.assign(importance=table["coefficient"].abs())
    return table.sort_values("importance", ascending=False)


def train_model(model_name: str, frame: pd.DataFrame, target: str, features: List[str], args: argparse.Namespace, seed_offset: int):
    x, y, names, means, stds = encode(frame, features, target)
    train_idx, test_idx = split_indices(len(y), args.test_frac, args.seed + seed_offset)
    weights, bias = train_weighted_logistic(x[train_idx], y[train_idx], args.epochs, args.lr)
    train_scores = expit(x[train_idx] @ weights + bias)
    threshold = tune_threshold(y[train_idx], train_scores)
    test_scores = expit(x[test_idx] @ weights + bias)
    result_metrics = metrics(y[test_idx], test_scores, threshold)
    artifact = {
        "model_type": "weighted_numpy_logistic_regression",
        "model_name": model_name,
        "target": target,
        "feature_names": names,
        "means": means,
        "stds": stds,
        "weights": weights,
        "bias": bias,
        "threshold": threshold,
        "metrics": result_metrics,
    }
    return artifact, feature_importance(model_name, names, weights)


def before_after(old_metrics_path: str, new_metrics: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    old = pd.read_csv(old_metrics_path)
    rows = []
    for model, metric_values in new_metrics.items():
        old_model = old[old["model"] == model].set_index("metric")["value"].to_dict()
        for metric, after_value in metric_values.items():
            before_value = old_model.get(metric, np.nan)
            rows.append(
                {
                    "model": model,
                    "metric": metric,
                    "before": before_value,
                    "after": after_value,
                    "delta": after_value - before_value if pd.notna(before_value) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def main() -> int:
    args = parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    frame = prepare_frame(args.data_path)
    base_features = LAGGED_NUMERIC_FEATURES + ["month_index"] + CATEGORICAL_FEATURES

    loan_frame = frame[frame["active_provider_month_flag_lag1"] == 1].copy()
    loan_artifact, loan_importance = train_model(
        "loan_default_prediction",
        loan_frame,
        "default_next_cycle",
        base_features,
        args,
        seed_offset=20,
    )

    adoption_artifact, adoption_importance = train_model(
        "embedded_finance_adoption",
        frame,
        "adoption_state_tplus1",
        base_features,
        args,
        seed_offset=30,
    )

    artifacts = {
        "loan_default_prediction": loan_artifact,
        "embedded_finance_adoption": adoption_artifact,
    }
    importances = {
        "loan_default_prediction": loan_importance,
        "embedded_finance_adoption": adoption_importance,
    }

    for model_name, artifact in artifacts.items():
        with open(os.path.join(args.out_dir, f"{model_name}.pkl"), "wb") as handle:
            pickle.dump(artifact, handle)
        importances[model_name].to_csv(os.path.join(args.out_dir, f"{model_name}_feature_importance.csv"), index=False)

    comparison = before_after(args.old_metrics, {name: artifact["metrics"] for name, artifact in artifacts.items()})
    comparison.to_csv(os.path.join(args.out_dir, "before_vs_after_metrics.csv"), index=False)

    print(f"Saved retrained weak-model artifacts to {os.path.abspath(args.out_dir)}")
    print(f"Saved before/after metrics to {os.path.abspath(os.path.join(args.out_dir, 'before_vs_after_metrics.csv'))}")
    for model_name, artifact in artifacts.items():
        print(f"\n{model_name}")
        for metric, value in artifact["metrics"].items():
            print(f"  {metric}: {value}")
        print("  top features:", ", ".join(importances[model_name]["feature"].head(5).tolist()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
