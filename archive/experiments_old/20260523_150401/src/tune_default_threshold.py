"""
Tune classification thresholds for the leakage-safe default model.

No model weights are retrained. The script reloads the saved model artifact,
recreates the same holdout split, scores it, and evaluates threshold tradeoffs.
"""

from __future__ import annotations

import argparse
import os
import pickle
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit

from retrain_default_model_safe import encode, metrics, prepare_frame, roc_auc, split_indices


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Tune default model threshold without retraining.")
    parser.add_argument("--data_path", default=os.path.join("data", "model_ready", "provider_month_future_targets.csv"))
    parser.add_argument("--model_path", default=os.path.join("output", "default_model_safe", "loan_default_prediction_leakage_safe.pkl"))
    parser.add_argument("--out_report", default=os.path.join("output", "default_threshold_tuning.md"))
    parser.add_argument("--out_table", default=os.path.join("output", "default_threshold_tuning.csv"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--test_frac", type=float, default=0.25)
    return parser.parse_args()


def threshold_metrics(y_true: np.ndarray, scores: np.ndarray, threshold: float) -> dict:
    result = metrics(y_true, scores, threshold)
    precision = result["precision"]
    recall = result["recall"]
    result["f1"] = 2 * precision * recall / max(precision + recall, 1e-12)
    result["f2"] = 5 * precision * recall / max(4 * precision + recall, 1e-12)
    result["predicted_positive_rate"] = float((scores >= threshold).mean())
    return result


def build_table(y_true: np.ndarray, scores: np.ndarray) -> pd.DataFrame:
    rows = []
    for threshold in np.linspace(0.01, 0.99, 99):
        row = {"threshold": float(threshold)}
        row.update(threshold_metrics(y_true, scores, float(threshold)))
        rows.append(row)
    return pd.DataFrame(rows)


def choose_thresholds(table: pd.DataFrame) -> pd.DataFrame:
    balanced = table.sort_values(["f1", "recall", "precision"], ascending=False).iloc[0].copy()
    balanced["strategy"] = "balanced_f1"

    high_recall_candidates = table[table["recall"] >= 0.80]
    if high_recall_candidates.empty:
        high_recall = table.sort_values(["recall", "f2", "precision"], ascending=False).iloc[0].copy()
        high_recall["strategy"] = "highest_available_recall"
    else:
        high_recall = high_recall_candidates.sort_values(["f2", "precision"], ascending=False).iloc[0].copy()
        high_recall["strategy"] = "high_recall_recall_ge_0_80"

    high_precision_candidates = table[(table["tp"] >= 3) & (table["recall"] >= 0.10)]
    if high_precision_candidates.empty:
        high_precision_candidates = table[table["tp"] >= 1]
    high_precision = high_precision_candidates.sort_values(["precision", "f1", "recall"], ascending=False).iloc[0].copy()
    high_precision["strategy"] = "high_precision_min_3_tp"

    return pd.DataFrame([balanced, high_recall, high_precision])


def md_table(frame: pd.DataFrame, columns: list[str], n: int | None = None) -> str:
    table = frame[columns].head(n).copy() if n else frame[columns].copy()
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in table.iterrows():
        vals = []
        for column in columns:
            value = row[column]
            if isinstance(value, float):
                vals.append("" if pd.isna(value) else f"{value:.3f}")
            else:
                vals.append(str(value).replace("|", "\\|"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_report(args: argparse.Namespace, table: pd.DataFrame, chosen: pd.DataFrame, auc: float, current_threshold: float, current: dict) -> None:
    display_cols = [
        "strategy",
        "threshold",
        "precision",
        "recall",
        "f1",
        "f2",
        "accuracy",
        "tp",
        "fp",
        "fn",
        "tn",
        "predicted_positive_rate",
    ]
    sample_thresholds = table[table["threshold"].round(2).isin([0.10, 0.30, 0.50, 0.69, 0.70, 0.80, 0.90])]
    sample_cols = [
        "threshold",
        "precision",
        "recall",
        "f1",
        "f2",
        "accuracy",
        "tp",
        "fp",
        "fn",
        "tn",
        "predicted_positive_rate",
    ]

    lines = [
        "# Default Threshold Tuning",
        "",
        f"Generated on {date.today().isoformat()}.",
        "",
        "## Scope",
        "",
        "This audit tunes classification thresholds for the leakage-safe default model without retraining model weights.",
        "",
        f"- Model: `{args.model_path}`",
        f"- ROC AUC: `{auc:.3f}`",
        f"- Saved model threshold: `{current_threshold:.3f}`",
        "",
        "## Current Saved Threshold",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key in ["threshold", "precision", "recall", "f1", "f2", "accuracy", "tp", "fp", "fn", "tn", "predicted_positive_rate"]:
        value = current_threshold if key == "threshold" else current[key]
        lines.append(f"| {key} | {value:.3f} |")

    lines.extend(
        [
            "",
            "## Recommended Operating Thresholds",
            "",
            md_table(chosen, display_cols),
            "",
            "## Threshold Comparison Table",
            "",
            md_table(sample_thresholds, sample_cols),
            "",
            "## Interpretation",
            "",
            "- `balanced_f1` is the best default choice when false positives and false negatives both matter.",
            "- `high_recall_recall_ge_0_80` is useful for screening, where missing likely defaults is costly.",
            "- `high_precision_min_3_tp` is useful for tighter intervention queues, but it catches fewer true defaults.",
            "",
            "Because defaults are rare, precision remains low even at stronger thresholds. Operationally, this model should be used to rank risk or trigger review, not as an automatic rejection rule.",
        ]
    )
    Path(args.out_report).write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    with open(args.model_path, "rb") as handle:
        artifact = pickle.load(handle)
    frame = prepare_frame(args.data_path)
    frame = frame[frame["active_provider_month_flag"].astype(float).eq(1.0)].copy()
    # The feature list in the artifact includes one-hot columns; encode with the source feature list used by the safe script.
    from retrain_default_model_safe import BASE_FEATURES, CATEGORICAL_FEATURES, ENGINEERED_FEATURES

    x, y, _, _, _, _ = encode(frame, BASE_FEATURES + ENGINEERED_FEATURES + CATEGORICAL_FEATURES, "default_flag")
    _, test_idx = split_indices(y, args.test_frac, args.seed)
    scores = expit(x[test_idx] @ artifact["weights"] + artifact["bias"])
    y_test = y[test_idx]

    table = build_table(y_test, scores)
    auc = roc_auc(y_test, scores)
    table["roc_auc"] = auc
    chosen = choose_thresholds(table)
    current_threshold = float(artifact["threshold"])
    current = threshold_metrics(y_test, scores, current_threshold)

    Path(args.out_table).parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.out_table, index=False)
    write_report(args, table, chosen, auc, current_threshold, current)
    print(f"Saved threshold table to {args.out_table}")
    print(f"Saved report to {args.out_report}")
    print(f"ROC AUC: {auc:.3f}")
    for _, row in chosen.iterrows():
        print(f"{row['strategy']}: threshold={row['threshold']:.2f}, precision={row['precision']:.3f}, recall={row['recall']:.3f}, f1={row['f1']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
