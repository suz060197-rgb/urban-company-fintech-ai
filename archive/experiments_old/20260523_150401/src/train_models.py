"""
Train lightweight research models for the Urban Company DELTA synthetic dataset.

Only project-approved third-party libraries are used: pandas, numpy, scipy, and
tqdm. Models are implemented directly with NumPy to avoid adding dependencies.
"""

from __future__ import annotations

import argparse
import os
import pickle
import warnings
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.special import expit
from tqdm import tqdm

warnings.filterwarnings(
    "ignore",
    message=".*ChainedAssignmentError: behaviour will change in pandas 3.0.*",
    category=FutureWarning,
)


NUMERIC_FEATURES = [
    "tenure_days",
    "avg_ticket",
    "monthly_income",
    "repeat_customer_rate",
    "platform_commission_pct",
    "payment_success_rate",
    "transaction_velocity",
    "multi_product_adoption",
    "digital_tool_usage",
    "ai_adoption_score",
    "payout_amount",
    "payout_delay_days",
    "active_provider_month_flag",
    "loan_offer_flag",
    "loan_amount",
    "repayment_amount",
    "working_capital_gap",
    "loan_disbursal_time",
    "treatment_flag",
    "post_treatment_flag",
    "lock_in_score",
    "technology_adoption_score",
    "advancement_score",
    "agentic_intelligence_score",
    "forecast_usage",
]

CATEGORICAL_FEATURES = ["region", "city", "category", "loan_status"]


@dataclass
class PreparedMatrix:
    x: np.ndarray
    y: np.ndarray
    feature_names: List[str]
    means: np.ndarray
    stds: np.ndarray


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train DELTA synthetic-data models.")
    parser.add_argument("--data_dir", default="data", help="Directory containing generated CSVs.")
    parser.add_argument("--out_dir", default="output/models", help="Directory for model artifacts.")
    parser.add_argument("--seed", type=int, default=42, help="Train/test split seed.")
    parser.add_argument("--test_frac", type=float, default=0.25, help="Held-out test fraction.")
    parser.add_argument("--epochs", type=int, default=900, help="Optimization epochs.")
    parser.add_argument("--lr", type=float, default=0.04, help="Learning rate.")
    return parser.parse_args()


def boolify(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.astype(float)
    return series.astype(str).str.lower().isin(["true", "1", "yes"]).astype(float)


def load_training_frame(data_dir: str) -> pd.DataFrame:
    merchants = pd.read_csv(os.path.join(data_dir, "merchants.csv"))
    payouts = pd.read_csv(os.path.join(data_dir, "payouts_loans.csv"))
    kpis = pd.read_csv(os.path.join(data_dir, "provider_kpis.csv"))
    frame = kpis.merge(merchants, on="merchant_id", suffixes=("", "_merchant"))
    frame = frame.merge(payouts, on=["merchant_id", "month"], how="left")
    return frame


def encode_features(frame: pd.DataFrame, target: str, feature_columns: List[str]) -> PreparedMatrix:
    data = pd.DataFrame(index=frame.index)
    for column in feature_columns:
        if column in CATEGORICAL_FEATURES:
            continue
        if column not in frame:
            raise KeyError(f"Missing feature column: {column}")
        if frame[column].dtype == bool:
            data[column] = frame[column].astype(float)
        elif frame[column].dtype == object and set(frame[column].dropna().astype(str).str.lower().unique()).issubset(
            {"true", "false"}
        ):
            data[column] = boolify(frame[column])
        else:
            data[column] = pd.to_numeric(frame[column], errors="coerce")

    for column in CATEGORICAL_FEATURES:
        if column in feature_columns:
            dummies = pd.get_dummies(frame[column].fillna("missing"), prefix=column, dtype=float)
            data = pd.concat([data, dummies], axis=1)

    data = data.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    y = pd.to_numeric(frame[target], errors="coerce").fillna(0.0).to_numpy(dtype=float)
    x = data.to_numpy(dtype=float)
    means = x.mean(axis=0)
    stds = x.std(axis=0)
    stds[stds == 0] = 1.0
    x_scaled = (x - means) / stds
    return PreparedMatrix(x=x_scaled, y=y, feature_names=list(data.columns), means=means, stds=stds)


def train_test_indices(n_rows: int, test_frac: float, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    order = rng.permutation(n_rows)
    test_n = max(1, int(round(n_rows * test_frac)))
    return order[test_n:], order[:test_n]


def train_logistic(x: np.ndarray, y: np.ndarray, epochs: int, lr: float, l2: float = 0.001) -> Tuple[np.ndarray, float]:
    weights = np.zeros(x.shape[1])
    bias = 0.0
    n_rows = max(len(y), 1)
    iterator = tqdm(range(epochs), desc="logistic", leave=False, disable=True)
    for _ in iterator:
        pred = expit(x @ weights + bias)
        error = pred - y
        grad_w = (x.T @ error) / n_rows + l2 * weights
        grad_b = float(error.mean())
        weights -= lr * grad_w
        bias -= lr * grad_b
    return weights, bias


def train_linear(x: np.ndarray, y: np.ndarray, epochs: int, lr: float, l2: float = 0.001) -> Tuple[np.ndarray, float]:
    weights = np.zeros(x.shape[1])
    bias = float(y.mean())
    n_rows = max(len(y), 1)
    iterator = tqdm(range(epochs), desc="linear", leave=False, disable=True)
    for _ in iterator:
        pred = x @ weights + bias
        error = pred - y
        grad_w = (x.T @ error) / n_rows + l2 * weights
        grad_b = float(error.mean())
        weights -= lr * grad_w
        bias -= lr * grad_b
    return weights, bias


def best_threshold(y_true: np.ndarray, scores: np.ndarray) -> float:
    candidates = np.linspace(0.05, 0.95, 91)
    best_f1 = -1.0
    best = 0.5
    y_int = y_true.astype(int)
    for threshold in candidates:
        pred = (scores >= threshold).astype(int)
        tp = ((pred == 1) & (y_int == 1)).sum()
        fp = ((pred == 1) & (y_int == 0)).sum()
        fn = ((pred == 0) & (y_int == 1)).sum()
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        f1 = 2 * precision * recall / max(precision + recall, 1e-12)
        if f1 > best_f1:
            best_f1 = f1
            best = float(threshold)
    return best


def classification_metrics(y_true: np.ndarray, scores: np.ndarray, threshold: float = 0.5) -> Dict[str, float]:
    pred = (scores >= threshold).astype(int)
    y_int = y_true.astype(int)
    tp = int(((pred == 1) & (y_int == 1)).sum())
    tn = int(((pred == 0) & (y_int == 0)).sum())
    fp = int(((pred == 1) & (y_int == 0)).sum())
    fn = int(((pred == 0) & (y_int == 1)).sum())
    accuracy = (tp + tn) / max(len(y_int), 1)
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "roc_auc": roc_auc(y_int, scores),
        "threshold": threshold,
        "positive_rate": float(y_int.mean()),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
    }


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


def regression_metrics(y_true: np.ndarray, pred: np.ndarray) -> Dict[str, float]:
    error = pred - y_true
    mse = float(np.mean(error**2))
    mae = float(np.mean(np.abs(error)))
    rmse = float(np.sqrt(mse))
    denom = float(np.sum((y_true - y_true.mean()) ** 2))
    r2 = 1 - float(np.sum(error**2)) / denom if denom > 0 else np.nan
    directional_accuracy = float((np.sign(pred) == np.sign(y_true)).mean())
    return {"rmse": rmse, "mae": mae, "r2": r2, "directional_accuracy": directional_accuracy}


def top_importance(feature_names: List[str], weights: np.ndarray, top_n: int = 12) -> pd.DataFrame:
    table = pd.DataFrame({"feature": feature_names, "coefficient": weights}).assign(
        importance=lambda frame: frame["coefficient"].abs()
    )
    return table.sort_values("importance", ascending=False).head(top_n)


def run_classification_model(
    name: str,
    frame: pd.DataFrame,
    target: str,
    feature_columns: List[str],
    args: argparse.Namespace,
    seed_offset: int = 0,
) -> Tuple[Dict[str, object], pd.DataFrame]:
    prepared = encode_features(frame, target, feature_columns)
    train_idx, test_idx = train_test_indices(len(prepared.y), args.test_frac, args.seed + seed_offset)
    weights, bias = train_logistic(prepared.x[train_idx], prepared.y[train_idx], args.epochs, args.lr)
    train_scores = expit(prepared.x[train_idx] @ weights + bias)
    threshold = best_threshold(prepared.y[train_idx], train_scores)
    scores = expit(prepared.x[test_idx] @ weights + bias)
    metrics = classification_metrics(prepared.y[test_idx], scores, threshold)
    artifact = {
        "model_type": "numpy_logistic_regression",
        "model_name": name,
        "target": target,
        "feature_names": prepared.feature_names,
        "means": prepared.means,
        "stds": prepared.stds,
        "weights": weights,
        "bias": bias,
        "threshold": threshold,
        "metrics": metrics,
    }
    return artifact, top_importance(prepared.feature_names, weights)


def run_regression_model(
    name: str,
    frame: pd.DataFrame,
    target: str,
    feature_columns: List[str],
    args: argparse.Namespace,
) -> Tuple[Dict[str, object], pd.DataFrame]:
    prepared = encode_features(frame, target, feature_columns)
    train_idx, test_idx = train_test_indices(len(prepared.y), args.test_frac, args.seed + 100)
    weights, bias = train_linear(prepared.x[train_idx], prepared.y[train_idx], args.epochs, args.lr)
    pred = prepared.x[test_idx] @ weights + bias
    metrics = regression_metrics(prepared.y[test_idx], pred)
    artifact = {
        "model_type": "numpy_linear_regression",
        "model_name": name,
        "target": target,
        "feature_names": prepared.feature_names,
        "means": prepared.means,
        "stds": prepared.stds,
        "weights": weights,
        "bias": bias,
        "metrics": metrics,
    }
    return artifact, top_importance(prepared.feature_names, weights)


def save_artifacts(out_dir: str, artifacts: Dict[str, Dict[str, object]], importances: Dict[str, pd.DataFrame]) -> None:
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    for name, artifact in artifacts.items():
        with open(os.path.join(out_dir, f"{name}.pkl"), "wb") as handle:
            pickle.dump(artifact, handle)
        for metric, value in artifact["metrics"].items():
            rows.append({"model": name, "metric": metric, "value": value})
        imp = importances[name].copy()
        imp.insert(0, "model", name)
        imp.to_csv(os.path.join(out_dir, f"{name}_feature_importance.csv"), index=False)
    pd.DataFrame(rows).to_csv(os.path.join(out_dir, "model_metrics.csv"), index=False)

    report_lines = ["Model Training Summary", ""]
    for name, artifact in artifacts.items():
        report_lines.append(name)
        for metric, value in artifact["metrics"].items():
            report_lines.append(f"- {metric}: {value}")
        report_lines.append("- top_features: " + ", ".join(importances[name]["feature"].head(5).tolist()))
        report_lines.append("")
    with open(os.path.join(out_dir, "model_report.txt"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(report_lines))


def main() -> int:
    args = parse_args()
    frame = load_training_frame(args.data_dir)

    base_features = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    no_target_leakage = [
        column
        for column in base_features
        if column
        not in {
            "churn_probability",
            "retention_flag",
            "income_growth_pct",
            "monthly_profit",
            "default_flag",
        }
    ]

    modeling_frame = frame.copy().assign(
        churn_target=lambda data: (~data["retention_flag"].astype(bool)).astype(int),
        default_target=lambda data: data["default_flag"].astype(int),
        adoption_target=lambda data: data["treatment_flag"].astype(int),
    )

    artifacts: Dict[str, Dict[str, object]] = {}
    importances: Dict[str, pd.DataFrame] = {}

    artifacts["churn_prediction"], importances["churn_prediction"] = run_classification_model(
        "churn_prediction",
        modeling_frame,
        "churn_target",
        [
            c
            for c in no_target_leakage
            if c
            not in {
                "lock_in_score",
                "advancement_score",
                "active_provider_month_flag",
                "payout_amount",
            }
        ],
        args,
        seed_offset=1,
    )

    default_frame = modeling_frame[modeling_frame["loan_status"].isin(["active", "repaid", "defaulted"])].copy()
    artifacts["loan_default_prediction"], importances["loan_default_prediction"] = run_classification_model(
        "loan_default_prediction",
        default_frame,
        "default_target",
        [c for c in no_target_leakage if c not in {"loan_status"}],
        args,
        seed_offset=2,
    )

    artifacts["income_growth_prediction"], importances["income_growth_prediction"] = run_regression_model(
        "income_growth_prediction",
        modeling_frame,
        "income_growth_pct",
        [c for c in no_target_leakage if c not in {"advancement_score"}],
        args,
    )

    merchant_month_first = modeling_frame.sort_values(["merchant_id", "month"]).groupby("merchant_id").head(1).copy()
    adoption_features = [
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
        "region",
        "city",
        "category",
    ]
    artifacts["embedded_finance_adoption"], importances["embedded_finance_adoption"] = run_classification_model(
        "embedded_finance_adoption",
        merchant_month_first,
        "adoption_target",
        adoption_features,
        args,
        seed_offset=3,
    )

    save_artifacts(args.out_dir, artifacts, importances)
    print(f"Saved trained models and reports to {os.path.abspath(args.out_dir)}")
    for name, artifact in artifacts.items():
        print(f"\n{name}")
        for metric, value in artifact["metrics"].items():
            print(f"  {metric}: {value}")
        print("  top features:", ", ".join(importances[name]["feature"].head(5).tolist()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
