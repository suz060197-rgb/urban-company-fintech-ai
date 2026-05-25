"""
Archive obsolete model experiment artifacts without deleting them.

The script keeps dissertation-final artifacts in their current locations and
moves older duplicate model, metric, feature-importance, prediction, risk, and
smoke-test output files into archive buckets while preserving relative paths.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Set


ROOT = Path(".")
ARCHIVE_ROOT = ROOT / "archive"
OLD_MODELS = ARCHIVE_ROOT / "old_models"
OLD_METRICS = ARCHIVE_ROOT / "old_metrics"
OLD_PREDICTIONS = ARCHIVE_ROOT / "old_predictions"
MANIFEST = ROOT / "docs" / "archive_manifest.md"


FINAL_MODELS: Set[Path] = {
    Path("output/models/churn_prediction.pkl"),
    Path("output/models/income_growth_prediction.pkl"),
    Path("output/adoption_propensity/embedded_finance_adoption_propensity.pkl"),
    Path("output/default_model_safe/loan_default_prediction_leakage_safe.pkl"),
}

FINAL_METRICS: Set[Path] = {
    Path("output/models/model_metrics.csv"),
    Path("output/adoption_propensity/adoption_propensity_roc_comparison.csv"),
    Path("output/default_model_safe/default_safe_metrics.csv"),
}

FINAL_FEATURE_IMPORTANCE: Set[Path] = {
    Path("output/models/churn_prediction_feature_importance.csv"),
    Path("output/models/income_growth_prediction_feature_importance.csv"),
    Path("output/adoption_propensity/embedded_finance_adoption_propensity_feature_importance.csv"),
    Path("output/default_model_safe/default_safe_feature_importance.csv"),
}

FINAL_PREDICTIONS: Set[Path] = {
    Path("output/churn_predictions.csv"),
    Path("output/adoption_predictions.csv"),
    Path("output/default_predictions.csv"),
    Path("output/risk_scores.csv"),
}

FINAL_FILES: Set[Path] = FINAL_MODELS | FINAL_METRICS | FINAL_FEATURE_IMPORTANCE | FINAL_PREDICTIONS


def normalize(path: Path) -> Path:
    return Path(path.as_posix())


def existing(paths: Iterable[Path]) -> List[Path]:
    return [path for path in paths if path.exists()]


def destination_for(source: Path, bucket: Path) -> Path:
    destination = bucket / source
    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent
    counter = 1
    while True:
        candidate = parent / f"{stem}_archived_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def archive_file(source: Path, bucket: Path) -> Dict[str, str]:
    destination = destination_for(source, bucket)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))
    return {
        "source": source.as_posix(),
        "destination": destination.as_posix(),
        "bucket": bucket.as_posix(),
    }


def classify_obsolete_csv(path: Path) -> Path | None:
    normalized = normalize(path)
    if normalized in FINAL_FILES:
        return None

    lower = normalized.as_posix().lower()
    name = normalized.name.lower()

    if not lower.startswith("output/"):
        return None

    if any(
        token in name
        for token in [
            "metric",
            "metrics",
            "feature_importance",
            "correlation",
            "threshold",
            "quantile",
            "leakage_rating",
            "before_after",
            "before_vs_after",
            "score",
        ]
    ):
        return OLD_METRICS
    if "/delta_smoke/" in lower or "/step3_smoke/" in lower:
        return OLD_PREDICTIONS
    if "prediction" in name or name == "risk_scores.csv" or "risk_segmentation" in name:
        return OLD_PREDICTIONS
    return None


def collect_moves() -> List[Dict[str, object]]:
    planned: List[Dict[str, object]] = []

    for path in sorted(Path("output").rglob("*.pkl")):
        normalized = normalize(path)
        if normalized not in FINAL_MODELS:
            planned.append({"path": normalized, "bucket": OLD_MODELS, "reason": "Older duplicate model artifact"})

    for path in sorted(Path("output").rglob("*.csv")):
        normalized = normalize(path)
        bucket = classify_obsolete_csv(normalized)
        if bucket is not None:
            planned.append({"path": normalized, "bucket": bucket, "reason": "Older duplicate output CSV"})

    return planned


def markdown_table(rows: List[Dict[str, str]], headers: List[str]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        values = [str(row.get(header, "")).replace("|", "\\|") for header in headers]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def retained_rows() -> List[Dict[str, str]]:
    groups = {
        "Final model": FINAL_MODELS,
        "Final metric": FINAL_METRICS,
        "Final feature importance": FINAL_FEATURE_IMPORTANCE,
        "Final prediction/risk": FINAL_PREDICTIONS,
    }
    rows: List[Dict[str, str]] = []
    for group, paths in groups.items():
        for path in sorted(paths):
            rows.append(
                {
                    "category": group,
                    "path": path.as_posix(),
                    "exists": "yes" if path.exists() else "missing",
                }
            )
    return rows


def write_manifest(moved: List[Dict[str, str]], retained: List[Dict[str, str]]) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Archive Manifest",
        "",
        f"Generated on {datetime.now().date().isoformat()}.",
        "",
        "No files were deleted permanently. Obsolete model-experiment artifacts were moved into `archive/` buckets.",
        "",
        "## Retained Dissertation-Final Files",
        "",
        markdown_table(retained, ["category", "path", "exists"]),
        "",
        "## Moved Files",
        "",
    ]
    if moved:
        lines.append(markdown_table(moved, ["source", "destination", "bucket"]))
    else:
        lines.append("No files needed to be moved.")

    lines.extend(
        [
            "",
            "## Archive Buckets",
            "",
            "- `archive/old_models/`: superseded `.pkl` model artifacts.",
            "- `archive/old_metrics/`: superseded metrics, feature-importance, correlation, threshold, and score CSVs.",
            "- `archive/old_predictions/`: superseded prediction/risk/smoke-output CSVs.",
        ]
    )
    MANIFEST.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    for directory in [OLD_MODELS, OLD_METRICS, OLD_PREDICTIONS]:
        directory.mkdir(parents=True, exist_ok=True)

    planned = collect_moves()
    moved: List[Dict[str, str]] = []
    for item in planned:
        path = item["path"]
        bucket = item["bucket"]
        if path.exists():
            moved.append(archive_file(path, bucket))

    retained = retained_rows()
    write_manifest(moved, retained)

    print(f"Moved {len(moved)} obsolete artifacts.")
    print(f"Retained {len(retained)} final artifact references.")
    print(f"Saved manifest to {MANIFEST.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
