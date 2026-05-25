"""
Retrain only the loan default model with default-specific engineered features.

Target:
- default_flag (actual same-cycle default outcome)

Leakage guard:
- excludes loan_status and default_flag-derived same-row labels from predictors
- uses prior default count and lagged stress features
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


BASE_FEATURES = [
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
]

ENGINEERED_FEATURES = [
    "prior_default_count",
    "prior_default_flag",
    "loan_to_payout_ratio",
    "loan_to_income_ratio",
    "repayment_ratio",
    "repayment_gap_ratio",
    "digital_readiness",
    "credit_dependency_score",
    "liquidity_stress_index",
]

CATEGORICAL_FEATURES = ["region", "city", "category"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Retrain actual loan default model.")
    parser.add_argument("--data_path", default=os.path.join("data", "model_ready", "provider_month_future_targets.csv"))
    parser.add_argument("--old_metrics", default=os.path.join("output", "models", "model_metrics.csv"))
    parser.add_argument("--out_dir", default=os.path.join("output", "default_model_improved"))
    parser.add_argument("--report", default=os.path.join("output", "default_model_improvement.md"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--test_frac", type=float, default=0.25)
    parser.add_argument("--epochs", type=int, default=1500)
    parser.add_argument("--lr", type=float, default=0.035)
    parser.add_argument("--threshold_metric", choices=["f1", "f2"], default="f2")
    return parser.parse_args()


def boolify(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.astype(float)
    return series.astype(str).str.lower().isin(["true", "1", "yes"]).astype(float)


def scale_01(series: pd.Series, q_low: float = 0.05, q_high: float = 0.95) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    lo = values.quantile(q_low)
    hi = values.quantile(q_high)
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        return pd.Series(np.zeros(len(values)), index=values.index, dtype=float)
    return ((values - lo) / (hi - lo)).clip(0, 1).fillna(0)


def safe_ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    num = pd.to_numeric(numerator, errors="coerce")
    den = pd.to_numeric(denominator, errors="coerce").replace(0, np.nan)
    return (num / den).replace([np.inf, -np.inf], np.nan).fillna(0).clip(lower=0)


def prepare_frame(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path)
    frame = frame.sort_values(["merchant_id", "month"]).copy()
    default_num = boolify(frame["default_flag"])
    prior_default_count = default_num.groupby(frame["merchant_id"]).cumsum() - default_num
    prior_default_flag = (prior_default_count > 0).astype(float)

    loan_to_payout_ratio = safe_ratio(frame["loan_amount"], frame["payout_amount"])
    loan_to_income_ratio = safe_ratio(frame["loan_amount"], frame["monthly_income"])
    repayment_ratio = safe_ratio(frame["repayment_amount"], frame["loan_amount"])
    repayment_gap_ratio = ((1 - repayment_ratio).clip(0, 1) * (pd.to_numeric(frame["loan_amount"], errors="coerce") > 0)).astype(float)
    digital_readiness = (
        pd.to_numeric(frame["payment_success_rate"], errors="coerce").fillna(0)
        + pd.to_numeric(frame["digital_tool_usage"], errors="coerce").fillna(0)
        + boolify(frame["kyc_flag"])
        + pd.to_numeric(frame["ai_adoption_score"], errors="coerce").fillna(0)
    ) / 4

    loan_amount_lag1_scaled = scale_01(frame["loan_amount_lag1"])
    working_gap_scaled = scale_01(frame["working_capital_gap_lag1"])
    payout_delay_scaled = scale_01(frame["payout_delay_days_lag1_imputed"])
    volatility_scaled = scale_01(frame["payout_volatility_rolling3"])
    credit_dependency_score = (
        0.30 * loan_amount_lag1_scaled
        + 0.30 * working_gap_scaled
        + 0.20 * payout_delay_scaled
        + 0.20 * volatility_scaled
    ).clip(0, 1)
    liquidity_stress_index = (
        0.35 * working_gap_scaled
        + 0.25 * payout_delay_scaled
        + 0.20 * volatility_scaled
        + 0.20 * repayment_gap_ratio
    ).clip(0, 1)

    return frame.assign(
        prior_default_count=prior_default_count,
        prior_default_flag=prior_default_flag,
        loan_to_payout_ratio=loan_to_payout_ratio,
        loan_to_income_ratio=loan_to_income_ratio,
        repayment_ratio=repayment_ratio,
        repayment_gap_ratio=repayment_gap_ratio,
        digital_readiness=digital_readiness,
        credit_dependency_score=credit_dependency_score,
        liquidity_stress_index=liquidity_stress_index,
    )


def encode(frame: pd.DataFrame, features: List[str], target: str):
    data = pd.DataFrame(index=frame.index)
    for feature in features:
        if feature in CATEGORICAL_FEATURES:
            continue
        if feature not in frame.columns:
            raise ValueError(f"Missing feature: {feature}")
        if frame[feature].dtype == bool:
            data[feature] = frame[feature].astype(float)
        elif frame[feature].dtype == object and set(frame[feature].dropna().astype(str).str.lower().unique()).issubset({"true", "false"}):
            data[feature] = boolify(frame[feature])
        else:
            data[feature] = pd.to_numeric(frame[feature], errors="coerce")

    for feature in CATEGORICAL_FEATURES:
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
        idx = np.where(y == cls)[0]
        shuffled = rng.permutation(idx)
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


def tune_threshold(y_true: np.ndarray, scores: np.ndarray, metric: str) -> float:
    best_threshold = 0.5
    best_score = -1.0
    beta = 2.0 if metric == "f2" else 1.0
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


def feature_importance(names: List[str], weights: np.ndarray) -> pd.DataFrame:
    table = pd.DataFrame({"feature": names, "coefficient": weights})
    return table.assign(importance=table["coefficient"].abs()).sort_values("importance", ascending=False)


def feature_correlations(data: pd.DataFrame, y: np.ndarray) -> pd.DataFrame:
    target = pd.Series(y, index=data.index)
    rows = []
    for col in data.columns:
        x = pd.to_numeric(data[col], errors="coerce")
        valid = x.notna() & target.notna()
        corr = np.nan if valid.sum() < 2 or x[valid].nunique() < 2 else float(np.corrcoef(x[valid], target[valid])[0, 1])
        rows.append({"feature": col, "correlation_with_target": corr, "abs_correlation": abs(corr) if pd.notna(corr) else np.nan})
    return pd.DataFrame(rows).sort_values("abs_correlation", ascending=False)


def old_metrics(path: str) -> Dict[str, float]:
    old = pd.read_csv(path)
    return old[old["model"].eq("loan_default_prediction")].set_index("metric")["value"].to_dict()


def comparison_frame(old: Dict[str, float], new: Dict[str, float]) -> pd.DataFrame:
    rows = []
    for key, value in new.items():
        before = old.get(key, np.nan)
        rows.append({"model": "loan_default_prediction", "metric": key, "before": before, "after": value, "delta": value - before if pd.notna(before) else np.nan})
    return pd.DataFrame(rows)


def md_table(frame: pd.DataFrame, columns: List[str], n: int | None = None) -> str:
    table = frame[columns].head(n).copy() if n else frame[columns].copy()
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in table.iterrows():
        vals = []
        for col in columns:
            value = row[col]
            vals.append("" if pd.isna(value) else (f"{value:.3f}" if isinstance(value, float) else str(value).replace("|", "\\|")))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_report(args, old: Dict[str, float], new: Dict[str, float], comparison: pd.DataFrame, importance: pd.DataFrame, correlations: pd.DataFrame, row_count: int) -> None:
    lines = [
        "# Default Model Improvement Report",
        "",
        f"Generated on {date.today().isoformat()}.",
        "",
        "## Objective",
        "",
        "Retrain only the loan default model to improve prediction of actual defaults using class weighting, threshold tuning, lagged variables, and default-specific engineered features.",
        "",
        "## Target And Data",
        "",
        "- Target: `default_flag` actual same-cycle loan default outcome.",
        f"- Training rows after active-month filter: `{row_count}`.",
        "- Excluded direct status leakage such as `loan_status`.",
        "",
        "## Engineered Features Added",
        "",
    ]
    for feature in ENGINEERED_FEATURES:
        lines.append(f"- `{feature}`")
    lines.extend(
        [
            "",
            "## Old Vs New Metrics",
            "",
            md_table(comparison, ["metric", "before", "after", "delta"]),
            "",
            "## Top Predictors",
            "",
            md_table(importance, ["feature", "coefficient", "importance"], 20),
            "",
            "## Feature Correlations With Default Target",
            "",
            md_table(correlations, ["feature", "correlation_with_target", "abs_correlation"], 20),
            "",
            "## Commentary",
            "",
            f"- Old ROC AUC: `{old.get('roc_auc', np.nan):.3f}`.",
            f"- New ROC AUC: `{new.get('roc_auc', np.nan):.3f}`.",
            f"- Old recall: `{old.get('recall', np.nan):.3f}`.",
            f"- New recall: `{new.get('recall', np.nan):.3f}`.",
            "",
            "This model is optimized with an F2 threshold, so it intentionally favors recall over precision. That is usually preferable for default-risk screening, where missing a true default can be more costly than flagging extra risk cases.",
            "",
            "If ROC or precision remains weak, the limitation is likely structural: the synthetic generator contains limited separability in default outcomes. The next improvement should be generator-side calibration of default risk drivers rather than more complex modeling.",
        ]
    )
    Path(args.report).write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    frame = prepare_frame(args.data_path)
    frame = frame[frame["active_provider_month_flag"].astype(float).eq(1.0)].copy()
    features = BASE_FEATURES + ENGINEERED_FEATURES + CATEGORICAL_FEATURES
    x, y, names, means, stds, encoded_data = encode(frame, features, "default_flag")
    train_idx, test_idx = split_indices(y, args.test_frac, args.seed)
    weights, bias = train_weighted_logistic(x[train_idx], y[train_idx], args.epochs, args.lr)
    train_scores = expit(x[train_idx] @ weights + bias)
    threshold = tune_threshold(y[train_idx], train_scores, args.threshold_metric)
    test_scores = expit(x[test_idx] @ weights + bias)
    new = metrics(y[test_idx], test_scores, threshold)
    old = old_metrics(args.old_metrics)
    comparison = comparison_frame(old, new)
    importance = feature_importance(names, weights)
    correlations = feature_correlations(encoded_data, y)

    artifact = {
        "model_type": "weighted_numpy_logistic_regression",
        "model_name": "loan_default_prediction_improved",
        "target": "default_flag",
        "feature_names": names,
        "means": means,
        "stds": stds,
        "weights": weights,
        "bias": bias,
        "threshold": threshold,
        "metrics": new,
        "threshold_metric": args.threshold_metric,
    }
    with open(os.path.join(args.out_dir, "loan_default_prediction_improved.pkl"), "wb") as handle:
        pickle.dump(artifact, handle)
    comparison.to_csv(os.path.join(args.out_dir, "default_before_after_metrics.csv"), index=False)
    importance.to_csv(os.path.join(args.out_dir, "default_feature_importance.csv"), index=False)
    correlations.to_csv(os.path.join(args.out_dir, "default_feature_correlations.csv"), index=False)
    write_report(args, old, new, comparison, importance, correlations, len(frame))

    print(f"Saved default model artifacts to {os.path.abspath(args.out_dir)}")
    print(f"Saved report to {os.path.abspath(args.report)}")
    print(f"Old ROC AUC: {old.get('roc_auc', np.nan):.3f}")
    print(f"New ROC AUC: {new['roc_auc']:.3f}")
    print(f"Old recall: {old.get('recall', np.nan):.3f}")
    print(f"New recall: {new['recall']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
