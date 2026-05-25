"""
Train a pre-intervention embedded-finance adoption propensity model.

This model intentionally excludes rollout timing, post-treatment state, and
treatment-derived variables. It uses only baseline/provider characteristics.
"""

from __future__ import annotations

import argparse
import os
import pickle
from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.special import expit


NUMERIC_FEATURES = [
    "tenure_days",
    "kyc_flag",
    "digital_tool_usage",
    "monthly_income",
    "transaction_velocity",
    "ai_adoption_score",
    "agent_usage_flag",
    "repeat_customer_rate",
    "avg_ticket",
    "payment_success_rate",
    "multi_product_adoption",
]

CATEGORICAL_FEATURES = ["city", "category", "region"]

FORBIDDEN_FEATURES = {
    "post_treatment_flag",
    "treatment_flag",
    "treatment_flag_merchant",
    "months_since_intervention",
    "treatment_start_month",
    "pre_treatment_flag",
    "intervention_timestamp",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train safe adoption propensity model.")
    parser.add_argument("--merchants", default=os.path.join("data", "merchants.csv"))
    parser.add_argument("--old_metrics", default=os.path.join("output", "before_after_model_metrics.csv"))
    parser.add_argument("--out_dir", default=os.path.join("output", "adoption_propensity"))
    parser.add_argument("--report", default=os.path.join("output", "adoption_propensity_report.md"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--test_frac", type=float, default=0.25)
    parser.add_argument("--epochs", type=int, default=1200)
    parser.add_argument("--lr", type=float, default=0.04)
    return parser.parse_args()


def boolify(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.astype(float)
    return series.astype(str).str.lower().isin(["true", "1", "yes"]).astype(float)


def encode(frame: pd.DataFrame, features: List[str], target: str):
    data = pd.DataFrame(index=frame.index)
    for feature in features:
        if feature in FORBIDDEN_FEATURES:
            raise ValueError(f"Forbidden leakage feature requested: {feature}")
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
    y = boolify(frame[target]).to_numpy(dtype=float)
    x = data.to_numpy(dtype=float)
    means = x.mean(axis=0)
    stds = x.std(axis=0)
    stds[stds == 0] = 1.0
    return (x - means) / stds, y, list(data.columns), means, stds, data


def split_indices(y: np.ndarray, test_frac: float, seed: int) -> Tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    train_parts = []
    test_parts = []
    for cls in [0.0, 1.0]:
        indices = np.where(y == cls)[0]
        shuffled = rng.permutation(indices)
        n_test = max(1, int(round(len(shuffled) * test_frac)))
        test_parts.append(shuffled[:n_test])
        train_parts.append(shuffled[n_test:])
    return np.concatenate(train_parts), np.concatenate(test_parts)


def class_weights(y: np.ndarray) -> np.ndarray:
    pos = max(float(y.sum()), 1.0)
    neg = max(float(len(y) - y.sum()), 1.0)
    pos_weight = len(y) / (2 * pos)
    neg_weight = len(y) / (2 * neg)
    return np.where(y == 1, pos_weight, neg_weight)


def train_weighted_logistic(x: np.ndarray, y: np.ndarray, epochs: int, lr: float, l2: float = 0.002):
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
    for threshold in np.linspace(0.05, 0.95, 91):
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


def feature_importance(feature_names: List[str], weights: np.ndarray) -> pd.DataFrame:
    table = pd.DataFrame({"feature": feature_names, "coefficient": weights})
    return table.assign(importance=table["coefficient"].abs()).sort_values("importance", ascending=False)


def feature_correlations(data: pd.DataFrame, y: np.ndarray) -> pd.DataFrame:
    rows = []
    target = pd.Series(y, index=data.index)
    for column in data.columns:
        values = pd.to_numeric(data[column], errors="coerce")
        valid = values.notna() & target.notna()
        corr = np.nan
        if valid.sum() > 2 and values[valid].nunique() > 1:
            corr = float(np.corrcoef(values[valid], target[valid])[0, 1])
        rows.append({"feature": column, "correlation_with_target": corr, "abs_correlation": abs(corr) if pd.notna(corr) else np.nan})
    return pd.DataFrame(rows).sort_values("abs_correlation", ascending=False)


def read_old_roc(path: str) -> Dict[str, float]:
    metrics_frame = pd.read_csv(path)
    rows = metrics_frame[(metrics_frame["model"] == "embedded_finance_adoption") & (metrics_frame["metric"] == "roc_auc")]
    result = {}
    if {"before", "after"}.issubset(metrics_frame.columns) and not rows.empty:
        result["original_roc_auc"] = float(rows["before"].iloc[0])
        result["leaky_retrained_roc_auc"] = float(rows["after"].iloc[0])
    elif {"value"}.issubset(metrics_frame.columns) and not rows.empty:
        result["original_roc_auc"] = float(rows["value"].iloc[0])
    return result


def md_table(frame: pd.DataFrame, columns: List[str], n: int | None = None) -> str:
    table = frame[columns].head(n).copy() if n else frame[columns].copy()
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in table.iterrows():
        values = []
        for column in columns:
            value = row[column]
            if isinstance(value, float):
                values.append("" if pd.isna(value) else f"{value:.3f}")
            else:
                values.append(str(value).replace("|", "\\|"))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(
    args: argparse.Namespace,
    model_metrics: Dict[str, float],
    old_roc: Dict[str, float],
    importance: pd.DataFrame,
    correlations: pd.DataFrame,
    features: List[str],
) -> None:
    original_roc = old_roc.get("original_roc_auc", np.nan)
    leaky_roc = old_roc.get("leaky_retrained_roc_auc", np.nan)
    lines = [
        "# Adoption Propensity Model Report",
        "",
        f"Generated on {date.today().isoformat()}.",
        "",
        "## Objective",
        "",
        "Rebuild the embedded finance adoption model as a pre-intervention propensity model using only baseline/provider characteristics.",
        "",
        "## Leakage Controls",
        "",
        "Excluded all rollout timing and treatment-state variables:",
        "",
    ]
    for feature in sorted(FORBIDDEN_FEATURES):
        lines.append(f"- `{feature}`")
    lines.extend(
        [
            "",
            "The target is provider-level eventual embedded-finance access from `merchants.csv::treatment_flag`. Predictors are baseline characteristics available before intervention.",
            "",
            "## Model Features",
            "",
        ]
    )
    for feature in features:
        lines.append(f"- `{feature}`")
    lines.extend(
        [
            "",
            "## ROC Comparison",
            "",
            "| Model version | ROC AUC | Interpretation |",
            "|---|---:|---|",
            f"| Original adoption model | {original_roc:.3f} | Earlier baseline metric. |",
            f"| Leaky engineered retrain | {leaky_roc:.3f} | Invalid high score driven by rollout timing leakage. |",
            f"| New pre-intervention propensity model | {model_metrics['roc_auc']:.3f} | Safer estimate using baseline provider characteristics only. |",
            "",
            "## New Model Metrics",
            "",
            "| Metric | Value |",
            "|---|---:|",
        ]
    )
    for key, value in model_metrics.items():
        lines.append(f"| {key} | {value:.3f} |")
    lines.extend(
        [
            "",
            "## Top Predictors",
            "",
            md_table(importance, ["feature", "coefficient", "importance"], 20),
            "",
            "## Feature Correlations With Target",
            "",
            md_table(correlations, ["feature", "correlation_with_target", "abs_correlation"], 20),
            "",
            "## Interpretation",
            "",
            "The new ROC is expected to be materially lower than the leaky retrained model because rollout timing variables have been removed. This is a healthier result: it reflects baseline separability between eventual treated and untreated providers rather than reconstruction of the intervention schedule.",
            "",
            "Use this model as a pre-intervention adoption propensity baseline. It is more credible for dissertation discussion than the previous near-perfect adoption model.",
        ]
    )
    Path(args.report).write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    merchants = pd.read_csv(args.merchants)
    features = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    x, y, feature_names, means, stds, encoded_data = encode(merchants, features, "treatment_flag")
    train_idx, test_idx = split_indices(y, args.test_frac, args.seed)
    weights, bias = train_weighted_logistic(x[train_idx], y[train_idx], args.epochs, args.lr)
    train_scores = expit(x[train_idx] @ weights + bias)
    threshold = tune_threshold(y[train_idx], train_scores)
    test_scores = expit(x[test_idx] @ weights + bias)
    model_metrics = metrics(y[test_idx], test_scores, threshold)
    importance = feature_importance(feature_names, weights)
    correlations = feature_correlations(encoded_data, y)

    artifact = {
        "model_type": "weighted_numpy_logistic_regression",
        "model_name": "embedded_finance_adoption_propensity",
        "target": "treatment_flag",
        "feature_names": feature_names,
        "excluded_features": sorted(FORBIDDEN_FEATURES),
        "means": means,
        "stds": stds,
        "weights": weights,
        "bias": bias,
        "threshold": threshold,
        "metrics": model_metrics,
    }
    with open(os.path.join(args.out_dir, "embedded_finance_adoption_propensity.pkl"), "wb") as handle:
        pickle.dump(artifact, handle)
    importance.to_csv(os.path.join(args.out_dir, "embedded_finance_adoption_propensity_feature_importance.csv"), index=False)
    correlations.to_csv(os.path.join(args.out_dir, "embedded_finance_adoption_propensity_correlations.csv"), index=False)

    old_roc = read_old_roc(args.old_metrics)
    comparison = pd.DataFrame(
        [
            {"model_version": "original_adoption_model", "roc_auc": old_roc.get("original_roc_auc", np.nan)},
            {"model_version": "leaky_engineered_retrain", "roc_auc": old_roc.get("leaky_retrained_roc_auc", np.nan)},
            {"model_version": "pre_intervention_propensity", "roc_auc": model_metrics["roc_auc"]},
        ]
    )
    comparison.to_csv(os.path.join(args.out_dir, "adoption_propensity_roc_comparison.csv"), index=False)
    write_report(args, model_metrics, old_roc, importance, correlations, features)

    print(f"Saved adoption propensity artifacts to {os.path.abspath(args.out_dir)}")
    print(f"Saved report to {os.path.abspath(args.report)}")
    print(f"Old leaky ROC AUC: {old_roc.get('leaky_retrained_roc_auc', np.nan):.3f}")
    print(f"New safe ROC AUC: {model_metrics['roc_auc']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
