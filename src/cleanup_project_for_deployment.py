"""
Clean project layout for dissertation deployment without permanent deletion.

The script writes a cleanup audit, archives obsolete artifacts, promotes the
extended data_v2 datasets into data/, renames final model/prediction artifacts,
and writes a deployment inventory.
"""

from __future__ import annotations

import filecmp
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Set


ROOT = Path(".")
RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")

ARCHIVE_DIRS = {
    "models_old": Path("archive/models_old"),
    "metrics_old": Path("archive/metrics_old"),
    "predictions_old": Path("archive/predictions_old"),
    "docs_old": Path("archive/docs_old"),
    "powerbi_old": Path("archive/powerbi_old"),
    "experiments_old": Path("archive/experiments_old"),
}

FINAL_DATA_FILES = {
    Path("data/merchants.csv"),
    Path("data/payouts_loans.csv"),
    Path("data/provider_kpis.csv"),
    Path("data/transactions.csv"),
    Path("data/primary_responses_clean.csv"),
}

FINAL_DOCS = {
    Path("docs/primary_secondary_mapping.csv"),
    Path("docs/primary_secondary_compatibility_report.md"),
    Path("docs/data_recency_audit.md"),
    Path("docs/archive_manifest.md"),
    Path("docs/final_model_metrics.md"),
    Path("docs/deployment_inventory.md"),
    Path("docs/project_cleanup_audit.md"),
}

FINAL_MODEL_RENAMES = {
    Path("output/models_final/loan_default_prediction.pkl"): Path("output/models_final/loan_default_model_final.pkl"),
    Path("output/models_final/churn_prediction.pkl"): Path("output/models_final/churn_model_final.pkl"),
    Path("output/models_final/embedded_finance_adoption.pkl"): Path("output/models_final/adoption_model_final.pkl"),
    Path("output/models_final/income_growth_prediction.pkl"): Path("output/models_final/income_growth_model_final.pkl"),
}

FINAL_PREDICTION_RENAMES = {
    Path("output/predictions_final/loan_default_prediction_predictions.csv"): Path(
        "output/predictions_final/default_predictions_final.csv"
    ),
    Path("output/predictions_final/churn_prediction_predictions.csv"): Path(
        "output/predictions_final/churn_predictions_final.csv"
    ),
    Path("output/predictions_final/embedded_finance_adoption_predictions.csv"): Path(
        "output/predictions_final/adoption_predictions_final.csv"
    ),
    Path("output/predictions_final/income_growth_prediction_predictions.csv"): Path(
        "output/predictions_final/income_growth_predictions_final.csv"
    ),
}

ROOT_PREDICTION_ALIASES = {
    Path("output/predictions_final/default_predictions_final.csv"): Path("output/default_predictions.csv"),
    Path("output/predictions_final/churn_predictions_final.csv"): Path("output/churn_predictions.csv"),
    Path("output/predictions_final/adoption_predictions_final.csv"): Path("output/adoption_predictions.csv"),
}

FINAL_OUTPUT_KEEP_PREFIXES = {
    "output/models_final/",
    "output/predictions_final/",
}
FINAL_OUTPUT_KEEP_FILES = {
    Path("output/risk_scores.csv"),
    Path("output/churn_predictions.csv"),
    Path("output/default_predictions.csv"),
    Path("output/adoption_predictions.csv"),
}

SRC_KEEP = {
    Path("src/generate_uc_dataset.py"),
    Path("src/validation.py"),
    Path("src/provenance.py"),
    Path("src/create_lagged_features.py"),
    Path("src/create_future_targets.py"),
    Path("src/train_final_models.py"),
    Path("src/integrate_primary_features.py"),
    Path("src/preprocess_primary_responses.py"),
    Path("src/create_primary_secondary_mapping.py"),
    Path("src/audit_data_recency.py"),
    Path("src/cleanup_project_for_deployment.py"),
}


def as_posix(path: Path) -> str:
    return path.as_posix()


def ensure_archive_dirs() -> None:
    Path("archive").mkdir(exist_ok=True)
    for directory in ARCHIVE_DIRS.values():
        directory.mkdir(parents=True, exist_ok=True)


def archive_destination(source: Path, bucket: Path) -> Path:
    destination = bucket / RUN_ID / source
    destination.parent.mkdir(parents=True, exist_ok=True)
    return destination


def move_to_archive(source: Path, bucket_key: str, reason: str, manifest: List[Dict[str, str]]) -> None:
    if not source.exists():
        return
    bucket = ARCHIVE_DIRS[bucket_key]
    destination = archive_destination(source, bucket)
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.move(str(source), str(destination))
        final_reason = reason
    except PermissionError:
        shutil.copy2(str(source), str(destination))
        final_reason = f"{reason} Original is locked; archived copy created and original left in place."
    manifest.append(
        {
            "original_path": as_posix(source),
            "archived_path": as_posix(destination),
            "reason": final_reason,
        }
    )


def copy_final(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def move_or_replace(source: Path, destination: Path, manifest: List[Dict[str, str]], reason: str) -> None:
    if not source.exists():
        return
    if destination.exists():
        move_to_archive(destination, "experiments_old", f"Existing destination archived before replace: {reason}", manifest)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(destination))


def classify_file(path: Path) -> Dict[str, str]:
    path = Path(path.as_posix())
    text = as_posix(path)
    name = path.name.lower()

    if text.startswith("archive/"):
        return {"classification": "KEEP", "reason": "Already archived historical artifact."}
    if path in FINAL_DATA_FILES:
        return {"classification": "KEEP", "reason": "Production dataset after promotion."}
    if path in FINAL_DOCS:
        return {"classification": "KEEP", "reason": "Deployment/final dissertation documentation."}
    if text.startswith("output/models_final/"):
        return {"classification": "KEEP", "reason": "Final dissertation model artifact or feature importance."}
    if text.startswith("output/predictions_final/"):
        return {"classification": "KEEP", "reason": "Final model prediction export."}
    if path in FINAL_OUTPUT_KEEP_FILES:
        return {"classification": "KEEP", "reason": "Dashboard-ready final prediction or risk score alias."}
    if text.startswith("dashboard/"):
        return {"classification": "KEEP", "reason": "Power BI dashboard artifact or layout."}
    if path in SRC_KEEP:
        return {"classification": "KEEP", "reason": "Script needed for generation, validation, integration, cleanup, or final training."}
    if path.name in {"README.md", "requirements.txt", "assumptions.md"}:
        return {"classification": "KEEP", "reason": "Project root metadata."}

    if text.startswith("data_v2/"):
        return {"classification": "ARCHIVE", "reason": "Final v2 source promoted into data/; archive duplicate source folder."}
    if text.startswith("data/model_ready/"):
        return {"classification": "ARCHIVE", "reason": "Intermediate model-ready data can be regenerated."}
    if text.startswith("data/") and path not in FINAL_DATA_FILES:
        return {"classification": "ARCHIVE", "reason": "Raw, auxiliary, or non-deployment data file."}
    if text.startswith("output/"):
        if name.endswith(".pkl"):
            return {"classification": "ARCHIVE", "reason": "Obsolete or duplicate model artifact."}
        if "prediction" in name or "risk" in name:
            return {"classification": "ARCHIVE", "reason": "Duplicate or experimental prediction/risk output."}
        if name.endswith(".csv") or "metric" in name or "importance" in name or "correlation" in name:
            return {"classification": "ARCHIVE", "reason": "Intermediate metrics, feature importance, or experiment CSV."}
        return {"classification": "ARCHIVE", "reason": "Experimental output/report not needed for deployment."}
    if text.startswith("docs/"):
        return {"classification": "ARCHIVE", "reason": "Development documentation not required for deployment package."}
    if text.startswith("Power Bi/") or path.suffix.lower() == ".pbix":
        return {"classification": "ARCHIVE", "reason": "Duplicate Power BI artifact outside final dashboard folder."}
    if "__pycache__" in path.parts or path.suffix.lower() == ".pyc":
        return {"classification": "DELETE_CANDIDATE", "reason": "Python bytecode cache; archived instead of deleted."}
    if text.startswith("src/"):
        return {"classification": "ARCHIVE", "reason": "Experimental training/audit script not needed for deployment."}
    if path.name == "validation_report.txt":
        return {"classification": "ARCHIVE", "reason": "Old validation output superseded by final metrics and recency audit."}
    return {"classification": "ARCHIVE", "reason": "Unclassified non-final project artifact; archived conservatively."}


def markdown_table(rows: List[Dict[str, str]], columns: List[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = [str(row.get(column, "")).replace("|", "\\|") for column in columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_cleanup_audit(paths: Iterable[Path]) -> List[Dict[str, str]]:
    rows = []
    for path in sorted(paths, key=lambda p: as_posix(p)):
        result = classify_file(path)
        rows.append(
            {
                "path": as_posix(path),
                "classification": result["classification"],
                "reason": result["reason"],
            }
        )
    summary = {}
    for row in rows:
        summary[row["classification"]] = summary.get(row["classification"], 0) + 1

    lines = [
        "# Project Cleanup Audit",
        "",
        f"Generated on {datetime.now().date().isoformat()}.",
        "",
        "Classification definitions:",
        "",
        "- `KEEP`: retained in the deployment-ready project tree.",
        "- `ARCHIVE`: moved into archive folders before cleanup.",
        "- `DELETE_CANDIDATE`: temporary/cache artifact; archived rather than deleted.",
        "",
        "## Summary",
        "",
    ]
    for key in ["KEEP", "ARCHIVE", "DELETE_CANDIDATE"]:
        lines.append(f"- {key}: {summary.get(key, 0)}")
    lines.extend(["", "## File Classification", "", markdown_table(rows, ["path", "classification", "reason"])])
    Path("docs").mkdir(exist_ok=True)
    Path("docs/project_cleanup_audit.md").write_text("\n".join(lines), encoding="utf-8")
    return rows


def promote_final_data(manifest: List[Dict[str, str]]) -> None:
    final_v2 = {
        Path("data_v2/merchants.csv"): Path("data/merchants.csv"),
        Path("data_v2/payouts_loans.csv"): Path("data/payouts_loans.csv"),
        Path("data_v2/provider_kpis.csv"): Path("data/provider_kpis.csv"),
        Path("data_v2/transactions.csv"): Path("data/transactions.csv"),
    }
    for source, destination in final_v2.items():
        if not source.exists():
            continue
        if destination.exists() and source.exists() and filecmp.cmp(source, destination, shallow=False):
            continue
        if destination.exists():
            move_to_archive(destination, "experiments_old", "Old production data archived before data_v2 promotion.", manifest)
        copy_final(source, destination)


def archive_nonfinal_files(classification_rows: List[Dict[str, str]], manifest: List[Dict[str, str]]) -> None:
    for row in classification_rows:
        source = Path(row["path"])
        if not source.exists() or row["classification"] == "KEEP":
            continue
        if row["classification"] == "DELETE_CANDIDATE":
            move_to_archive(source, "experiments_old", row["reason"], manifest)
        elif row["path"].startswith("docs/"):
            move_to_archive(source, "docs_old", row["reason"], manifest)
        elif row["path"].startswith("output/"):
            lower = source.name.lower()
            if lower.endswith(".pkl") or "model" in as_posix(source).lower():
                move_to_archive(source, "models_old", row["reason"], manifest)
            elif "prediction" in lower or "risk" in lower:
                move_to_archive(source, "predictions_old", row["reason"], manifest)
            elif lower.endswith(".csv") or "metric" in lower or "importance" in lower:
                move_to_archive(source, "metrics_old", row["reason"], manifest)
            else:
                move_to_archive(source, "experiments_old", row["reason"], manifest)
        elif row["path"].startswith("data"):
            move_to_archive(source, "experiments_old", row["reason"], manifest)
        elif row["path"].startswith("Power Bi/") or source.suffix.lower() == ".pbix":
            move_to_archive(source, "powerbi_old", row["reason"], manifest)
        elif row["path"].startswith("src/"):
            move_to_archive(source, "experiments_old", row["reason"], manifest)
        else:
            move_to_archive(source, "experiments_old", row["reason"], manifest)


def rename_final_artifacts(manifest: List[Dict[str, str]]) -> None:
    for source, destination in FINAL_MODEL_RENAMES.items():
        move_or_replace(source, destination, manifest, "Final model artifact renamed consistently.")
    for source, destination in FINAL_PREDICTION_RENAMES.items():
        move_or_replace(source, destination, manifest, "Final prediction artifact renamed consistently.")
    for source, destination in ROOT_PREDICTION_ALIASES.items():
        if destination.exists():
            move_to_archive(destination, "predictions_old", "Old root prediction alias archived before final alias refresh.", manifest)
        copy_final(source, destination)


def move_powerbi_to_dashboard(manifest: List[Dict[str, str]]) -> None:
    latest_pbix = Path("UC_Razorpay_EmbeddedFinance.pbix")
    dashboard_target = Path("dashboard/UC_Razorpay_Dashboard_v1.pbix")
    root_pbix = Path("UC_Razorpay_Dashboard_v1.pbix")
    if latest_pbix.exists():
        if dashboard_target.exists():
            move_to_archive(dashboard_target, "powerbi_old", "Older dashboard PBIX archived; latest root PBIX retained.", manifest)
        if root_pbix.exists():
            move_to_archive(root_pbix, "powerbi_old", "Older root PBIX archived; latest embedded-finance PBIX retained.", manifest)
        return
    duplicate = Path("Power Bi/UC_Razorpay_Dashboard_v1.pbix")
    if duplicate.exists():
        move_to_archive(duplicate, "powerbi_old", "Duplicate PBIX outside dashboard folder archived.", manifest)


def cleanup_empty_dirs() -> None:
    # Empty directories are harmless, but removing empty experiment shells makes
    # the tree easier to read. No files are deleted here.
    for directory in sorted([p for p in ROOT.rglob("*") if p.is_dir() and not as_posix(p).startswith("archive/")], reverse=True):
        if directory == ROOT:
            continue
        try:
            directory.rmdir()
        except OSError:
            pass


def write_archive_manifest(manifest: List[Dict[str, str]]) -> None:
    lines = [
        "# Archive Manifest",
        "",
        f"Generated on {datetime.now().date().isoformat()}.",
        "",
        "No files were permanently deleted. Obsolete, duplicate, temporary, and pre-deployment artifacts were moved into archive folders.",
        "",
        "## Moved Files",
        "",
    ]
    lines.append(markdown_table(manifest, ["original_path", "archived_path", "reason"]) if manifest else "No files moved.")
    lines.extend(
        [
            "",
            "## Archive Folders",
            "",
            "- `archive/models_old/`",
            "- `archive/metrics_old/`",
            "- `archive/predictions_old/`",
            "- `archive/docs_old/`",
            "- `archive/powerbi_old/`",
            "- `archive/experiments_old/`",
        ]
    )
    Path("docs/archive_manifest.md").write_text("\n".join(lines), encoding="utf-8")


def write_deployment_inventory() -> None:
    groups = {
        "Power BI": [
            Path("data/merchants.csv"),
            Path("data/payouts_loans.csv"),
            Path("data/provider_kpis.csv"),
            Path("data/transactions.csv"),
            Path("data/primary_responses_clean.csv"),
            Path("output/churn_predictions.csv"),
            Path("output/default_predictions.csv"),
            Path("output/adoption_predictions.csv"),
            Path("output/risk_scores.csv"),
            Path("dashboard/powerbi_blueprint.md"),
            Path("UC_Razorpay_EmbeddedFinance.pbix"),
        ],
        "ML app": [
            Path("output/models_final/churn_model_final.pkl"),
            Path("output/models_final/loan_default_model_final.pkl"),
            Path("output/models_final/adoption_model_final.pkl"),
            Path("output/models_final/income_growth_model_final.pkl"),
            Path("output/predictions_final/churn_predictions_final.csv"),
            Path("output/predictions_final/default_predictions_final.csv"),
            Path("output/predictions_final/adoption_predictions_final.csv"),
            Path("output/predictions_final/income_growth_predictions_final.csv"),
            Path("output/risk_scores.csv"),
        ],
        "Future retraining": [
            Path("src/generate_uc_dataset.py"),
            Path("src/create_lagged_features.py"),
            Path("src/create_future_targets.py"),
            Path("src/train_final_models.py"),
            Path("src/integrate_primary_features.py"),
            Path("src/preprocess_primary_responses.py"),
            Path("src/validation.py"),
            Path("src/provenance.py"),
            Path("requirements.txt"),
            Path("README.md"),
            Path("assumptions.md"),
        ],
        "Final documentation": [
            Path("docs/primary_secondary_mapping.csv"),
            Path("docs/primary_secondary_compatibility_report.md"),
            Path("docs/data_recency_audit.md"),
            Path("docs/archive_manifest.md"),
            Path("docs/final_model_metrics.md"),
            Path("docs/project_cleanup_inventory.md"),
            Path("docs/deployment_inventory.md"),
        ],
    }
    lines = [
        "# Deployment Inventory",
        "",
        f"Generated on {datetime.now().date().isoformat()}.",
        "",
        "Only deployment-needed files are listed below.",
        "",
    ]
    for group, paths in groups.items():
        lines.append(f"## {group}")
        lines.append("")
        lines.extend(["| file | exists |", "|---|---|"])
        for path in paths:
            lines.append(f"| `{as_posix(path)}` | {'yes' if path.exists() else 'missing'} |")
        lines.append("")
    Path("docs/deployment_inventory.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ensure_archive_dirs()
    initial_paths = [p for p in ROOT.rglob("*") if p.is_file()]
    classification_rows = write_cleanup_audit(initial_paths)

    manifest: List[Dict[str, str]] = []
    promote_final_data(manifest)
    move_powerbi_to_dashboard(manifest)
    archive_nonfinal_files(classification_rows, manifest)
    rename_final_artifacts(manifest)
    cleanup_empty_dirs()
    write_archive_manifest(manifest)
    write_deployment_inventory()

    print(f"Cleanup audit written to docs/project_cleanup_audit.md")
    print(f"Archive manifest written to docs/archive_manifest.md")
    print(f"Deployment inventory written to docs/deployment_inventory.md")
    print(f"Moved or archived {len(manifest)} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
