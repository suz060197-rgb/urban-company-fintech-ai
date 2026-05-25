"""Evaluate churn and embedded-finance adoption prediction outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import joblib

from mba_ba_ml_improvements import (
    add_engineered_adoption_features,
    prepare_model_matrix,
    read_model_ready,
    sigmoid,
)


OUTPUT_DIR = Path("output")
MODELS_DIR = OUTPUT_DIR / "models_final"
EVAL_DIR = OUTPUT_DIR / "model_evaluation"


MODEL_CONFIG = {
    "churn_prediction": {
        "prediction_file": OUTPUT_DIR / "predictions_final" / "churn_predictions_final.csv",
        "model_file": MODELS_DIR / "churn_model_final.pkl",
        "importance_file": MODELS_DIR / "churn_prediction_feature_importance.csv",
        "display_name": "Churn Prediction",
        "positive_label": "Churn",
    },
    "embedded_finance_adoption": {
        "prediction_file": OUTPUT_DIR / "predictions_final" / "adoption_predictions_final.csv",
        "model_file": MODELS_DIR / "adoption_model_final.pkl",
        "importance_file": MODELS_DIR / "embedded_finance_adoption_feature_importance.csv",
        "display_name": "Embedded Finance Adoption",
        "positive_label": "Adoption",
    },
}


def roc_curve_manual(y_true: np.ndarray, scores: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    order = np.argsort(-scores)
    y = y_true[order].astype(int)
    positives = max(int(y.sum()), 1)
    negatives = max(int(len(y) - y.sum()), 1)
    tps = np.cumsum(y == 1)
    fps = np.cumsum(y == 0)
    tpr = np.r_[0, tps / positives, 1]
    fpr = np.r_[0, fps / negatives, 1]
    integrate = getattr(np, "trapezoid", None)
    auc = float(integrate(tpr, fpr) if integrate else np.trapz(tpr, fpr))
    return fpr, tpr, auc


def classification_metrics(frame: pd.DataFrame) -> dict[str, float]:
    actual = pd.to_numeric(frame["actual"], errors="coerce").astype(int).to_numpy()
    pred = pd.to_numeric(frame["predicted_class"], errors="coerce").astype(int).to_numpy()
    scores = pd.to_numeric(frame["prediction_probability"], errors="coerce").to_numpy(dtype=float)
    tp = int(((pred == 1) & (actual == 1)).sum())
    fp = int(((pred == 1) & (actual == 0)).sum())
    tn = int(((pred == 0) & (actual == 0)).sum())
    fn = int(((pred == 0) & (actual == 1)).sum())
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-12)
    accuracy = (tp + tn) / max(len(actual), 1)
    _, _, auc = roc_curve_manual(actual, scores)
    return {
        "roc_auc": auc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": accuracy,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "support": len(actual),
        "positive_rate": float(actual.mean()),
        "predicted_positive_rate": float(pred.mean()),
    }


def score_current_model(model_key: str, model_path: Path) -> pd.DataFrame:
    model = joblib.load(model_path)
    model_ready, _ = read_model_ready()
    frame = add_engineered_adoption_features(model_ready) if model_key == "embedded_finance_adoption" else model_ready.copy()
    target = model["target"]
    frame = frame[pd.to_numeric(frame[target], errors="coerce").notna()].copy()
    frame.loc[:, "month_period"] = pd.PeriodIndex(frame["month"], freq="M")
    months = pd.PeriodIndex(sorted(frame["month_period"].unique()), freq="M")
    test_start = months[max(0, len(months) - 6)]
    split = np.where(frame["month_period"] >= test_start, "test", "train")
    x = prepare_model_matrix(frame, model)
    means = np.asarray(model["means"], dtype=float)
    stds = np.asarray(model["stds"], dtype=float)
    weights = np.asarray(model["weights"], dtype=float)
    scores = sigmoid(((x.to_numpy(dtype=float) - means) / stds) @ weights + float(model["bias"]))
    threshold = float(model.get("threshold", 0.5))
    return pd.DataFrame(
        {
            "provider_id": frame["merchant_id"].to_numpy(),
            "month": frame["month"].to_numpy(),
            "target_month": frame.get("target_month", pd.Series([None] * len(frame))).to_numpy(),
            "prediction_probability": scores,
            "predicted_class": (scores >= threshold).astype(int),
            "actual": pd.to_numeric(frame[target], errors="coerce").to_numpy(dtype=float),
            "model_name": model_key,
            "split": split,
        }
    )


def plot_roc(frame: pd.DataFrame, model_key: str, display_name: str) -> Path:
    actual = pd.to_numeric(frame["actual"], errors="coerce").astype(int).to_numpy()
    scores = pd.to_numeric(frame["prediction_probability"], errors="coerce").to_numpy(dtype=float)
    fpr, tpr, auc = roc_curve_manual(actual, scores)
    path = EVAL_DIR / f"{model_key}_roc_curve.png"
    plt.figure(figsize=(7, 5))
    plt.plot(fpr, tpr, color="#06b6d4", linewidth=2.5, label=f"ROC AUC = {auc:.3f}")
    plt.plot([0, 1], [0, 1], color="#64748b", linestyle="--", linewidth=1.3, label="Random")
    plt.title(f"{display_name} ROC Curve")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.grid(alpha=0.25)
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(path, dpi=170, bbox_inches="tight")
    plt.close()
    return path


def plot_importance(path: Path, model_key: str, display_name: str) -> Path:
    importance = pd.read_csv(path)
    feature_col = "feature" if "feature" in importance.columns else importance.columns[0]
    value_col = "importance" if "importance" in importance.columns else importance.columns[-1]
    importance[value_col] = pd.to_numeric(importance[value_col], errors="coerce").abs()
    top = importance.sort_values(value_col, ascending=False).head(15).iloc[::-1]
    out_path = EVAL_DIR / f"{model_key}_feature_importance.png"
    plt.figure(figsize=(8, 6))
    plt.barh(top[feature_col].astype(str), top[value_col], color="#38bdf8")
    plt.title(f"{display_name} - Top Feature Importance")
    plt.xlabel("Absolute importance")
    plt.grid(axis="x", alpha=0.2)
    plt.tight_layout()
    plt.savefig(out_path, dpi=170, bbox_inches="tight")
    plt.close()
    return out_path


def final_metrics_lookup() -> pd.DataFrame:
    path = MODELS_DIR / "final_model_metrics.csv"
    if not path.exists():
        return pd.DataFrame()
    metrics = pd.read_csv(path)
    return metrics.pivot_table(index="model", columns="metric", values="value", aggfunc="first").reset_index()


def business_interpretation(model_key: str, metrics: dict[str, float]) -> str:
    if model_key == "churn_prediction":
        return (
            "For an MSME/Razorpay-style embedded-finance use case, the churn model is suitable for retention "
            "operations: identify service providers likely to disengage, prioritize faster settlement support, "
            "repeat-customer enablement, payout reliability, and working-capital nudges. Strong recall means the "
            "model can catch most churn-risk providers, while high precision limits wasted interventions."
        )
    return (
        "For Razorpay embedded-finance adoption, the prediction output supports propensity-based targeting: "
        "identify providers likely to accept digital payouts, payment tools, or working-capital products. Use this "
        "for education, onboarding, and product-fit segmentation. Treat adoption propensity as commercial decision "
        "support rather than causal proof that finance products directly expand income."
    )


def main() -> int:
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    summary_rows = []
    final_metrics = final_metrics_lookup()
    lines = [
        "# Churn And Adoption Model Evaluation",
        "",
        "Evaluation uses the saved prediction CSV test split and final feature-importance artifacts.",
        "",
    ]
    for model_key, config in MODEL_CONFIG.items():
        try:
            predictions = score_current_model(model_key, config["model_file"])
            source = "current final model artifact"
        except Exception:
            predictions = pd.read_csv(config["prediction_file"])
            source = "saved prediction CSV fallback"
        test = predictions[predictions["split"].astype(str).str.lower().eq("test")].copy()
        if test.empty:
            test = predictions.copy()
        test = test.dropna(subset=["actual", "prediction_probability", "predicted_class"])
        metrics = classification_metrics(test)
        roc_path = plot_roc(test, model_key, config["display_name"])
        importance_path = plot_importance(config["importance_file"], model_key, config["display_name"])
        confusion_path = EVAL_DIR / f"{model_key}_confusion_matrix.csv"
        pd.DataFrame(
            [
                {"actual": "Negative", "predicted": "Negative", "count": metrics["tn"]},
                {"actual": "Negative", "predicted": "Positive", "count": metrics["fp"]},
                {"actual": "Positive", "predicted": "Negative", "count": metrics["fn"]},
                {"actual": "Positive", "predicted": "Positive", "count": metrics["tp"]},
            ]
        ).to_csv(confusion_path, index=False)
        row = {
            "model": model_key,
            "roc_auc": metrics["roc_auc"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "accuracy": metrics["accuracy"],
            "tp": metrics["tp"],
            "fp": metrics["fp"],
            "tn": metrics["tn"],
            "fn": metrics["fn"],
            "support": metrics["support"],
            "positive_rate": metrics["positive_rate"],
            "predicted_positive_rate": metrics["predicted_positive_rate"],
            "roc_curve_image": roc_path.as_posix(),
            "feature_importance_chart": importance_path.as_posix(),
            "confusion_matrix_csv": confusion_path.as_posix(),
        }
        summary_rows.append(row)

        lines.extend(
            [
                f"## {config['display_name']}",
                "",
                f"- ROC-AUC: `{metrics['roc_auc']:.3f}`",
                f"- Precision: `{metrics['precision']:.3f}`",
                f"- Recall: `{metrics['recall']:.3f}`",
                f"- F1 score: `{metrics['f1']:.3f}`",
                f"- Confusion matrix: TP `{metrics['tp']}`, FP `{metrics['fp']}`, TN `{metrics['tn']}`, FN `{metrics['fn']}`",
                f"- ROC curve image: `{roc_path.as_posix()}`",
                f"- Feature importance chart: `{importance_path.as_posix()}`",
                f"- Evaluation source: `{source}`",
                "",
                business_interpretation(model_key, metrics),
                "",
            ]
        )

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(EVAL_DIR / "churn_adoption_evaluation_summary.csv", index=False)

    if not final_metrics.empty:
        check = final_metrics[final_metrics["model"].isin(["churn_prediction", "embedded_finance_adoption"])]
        lines.extend(["## Consistency Note", ""])
        lines.append(
            "The saved final metrics file may reflect the latest model artifact, while prediction CSVs reflect the "
            "last exported prediction run. If these differ, regenerate predictions before final submission."
        )
        lines.append("")
        lines.append(check.to_csv(index=False))

    (EVAL_DIR / "churn_adoption_evaluation.md").write_text("\n".join(lines), encoding="utf-8")
    print(summary.to_string(index=False))
    print(f"Saved evaluation outputs to {EVAL_DIR.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
