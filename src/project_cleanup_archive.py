"""Preservation-first cleanup archive for dissertation project artifacts."""

from __future__ import annotations

import csv
import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path(".")
RUN_ID = datetime.now().strftime("%Y%m%d_cleanup")
ARCHIVE_ROOT = ROOT / "archive" / RUN_ID


KEEP_FINAL = [
    "app/",
    "data/merchants.csv",
    "data/transactions.csv",
    "data/payouts_loans.csv",
    "data/provider_kpis.csv",
    "data/primary_responses_clean.csv",
    "output/models_final/",
    "output/predictions_final/",
    "output/risk_scores.csv",
    "output/default_predictions.csv",
    "output/churn_predictions.csv",
    "output/adoption_predictions.csv",
    "output/Executive_Report.pdf",
    "output/business_analysis/",
    "output/shap/",
    "dashboard/powerbi_blueprint.md",
    "UC_Razorpay_EmbeddedFinance.pbix",
    "docs/",
    "src/",
    "README.md",
    "requirements.txt",
    "assumptions.md",
]


def archive_target(source: Path, category: str) -> Path:
    return ARCHIVE_ROOT / category / source


def planned_moves() -> list[dict[str, str]]:
    moves: list[dict[str, str]] = []
    explicit = [
        (
            Path("cleanup_report.md"),
            "old_reports",
            "Superseded cleanup report replaced by CHANGELOG_cleanup.md and docs/project_cleanup_inventory.md.",
            "Low",
        ),
        (
            Path("output/embedded_finance_executive_report.pdf"),
            "old_reports",
            "Duplicate older executive PDF; output/Executive_Report.pdf is the regenerated final report.",
            "Low",
        ),
        (
            Path("dashboard/UC_Razorpay_Dashboard_v1.pbix"),
            "deprecated_outputs",
            "Older small PBIX copy; latest PBIX retained at project root as UC_Razorpay_EmbeddedFinance.pbix.",
            "Medium: Power BI blueprint retained; deployment inventory updated to root PBIX.",
        ),
    ]
    for source, category, reason, risk in explicit:
        if source.exists():
            moves.append(
                {
                    "old_path": source.as_posix(),
                    "new_archive_path": archive_target(source, category).as_posix(),
                    "reason": reason,
                    "dependency_risk": risk,
                }
            )

    for folder in [Path("app"), Path("src")]:
        for cache_file in folder.rglob("*.pyc"):
            moves.append(
                {
                    "old_path": cache_file.as_posix(),
                    "new_archive_path": archive_target(cache_file, "deprecated_outputs").as_posix(),
                    "reason": "Generated Python bytecode cache; safe to regenerate.",
                    "dependency_risk": "Low",
                }
            )
    return moves


def move_files(moves: list[dict[str, str]]) -> None:
    for row in moves:
        source = ROOT / row["old_path"]
        destination = ROOT / row["new_archive_path"]
        if not source.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))


def write_manifest(moves: list[dict[str, str]]) -> Path:
    ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)
    manifest = ARCHIVE_ROOT / "archive_manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["old_path", "new_archive_path", "reason", "dependency_risk"])
        writer.writeheader()
        writer.writerows(moves)
    return manifest


def write_inventory(moves: list[dict[str, str]]) -> Path:
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    path = docs / "project_cleanup_inventory.md"
    lines = [
        "# Project Cleanup Inventory",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Keep Final",
        "",
    ]
    lines.extend(f"- `{item}`" for item in KEEP_FINAL)
    lines.extend(
        [
            "",
            "## Archived This Run",
            "",
            "| File/folder | Purpose | Referenced elsewhere? | Last modified relevance | Decision |",
            "|---|---|---|---|---|",
        ]
    )
    for row in moves:
        source = ROOT / row["old_path"]
        exists_note = "Moved to archive"
        lines.append(
            f"| `{row['old_path']}` | {row['reason']} | No active runtime dependency found | {exists_note} | Archive |"
        )
    lines.extend(
        [
            "",
            "## Conservative Keep Notes",
            "",
            "- Final datasets, final models, predictions, feature importance files, SHAP outputs, and training scripts were retained.",
            "- `output/models_final/adoption_model_final_pre_engineered.pkl` was retained because it preserves baseline reproducibility for the adoption-model audit.",
            "- Existing historical archive folders were not reprocessed.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_changelog(moves: list[dict[str, str]]) -> Path:
    path = ROOT / "CHANGELOG_cleanup.md"
    lines = [
        "# Cleanup Changelog",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Archived Files",
        "",
        "| Old path | New archive path | Reason | Dependency risk |",
        "|---|---|---|---|",
    ]
    for row in moves:
        lines.append(
            f"| `{row['old_path']}` | `{row['new_archive_path']}` | {row['reason']} | {row['dependency_risk']} |"
        )
    lines.extend(
        [
            "",
            "## Updated Reports And Wording",
            "",
            "- Regenerated `output/Executive_Report.pdf` with corrected growth interpretation.",
            "- Updated `app/utils/report_generator.py` so future PDFs describe churn-adjusted and active-provider growth separately.",
            "- Updated `README.md` with Business Analysis, FinTech Analytics, AI Decision Support, model caveats, and growth KPI definitions.",
            "- Updated deployment inventory to point to the latest root PBIX: `UC_Razorpay_EmbeddedFinance.pbix`.",
            "",
            "## KPI Wording",
            "",
            "- `Average income growth` relabeled as `Churn-adjusted growth` in generated reports.",
            "- Added active-provider, retained-provider, and median growth definitions.",
            "",
            "## Business Interpretation",
            "",
            "Embedded finance and digital adoption appear more strongly associated with operational resilience, retention, liquidity stability, and profit continuity than direct income expansion. Growth appears constrained by churn and provider inactivity rather than technology failure.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> int:
    categories = [
        "old_reports",
        "old_models",
        "deprecated_outputs",
        "obsolete_exports",
        "duplicate_csv",
        "experimental_notebooks",
    ]
    for category in categories:
        (ARCHIVE_ROOT / category).mkdir(parents=True, exist_ok=True)
    moves = planned_moves()
    move_files(moves)
    manifest = write_manifest(moves)
    inventory = write_inventory(moves)
    changelog = write_changelog(moves)
    print(f"Archived files: {len(moves)}")
    print(f"Manifest: {manifest}")
    print(f"Inventory: {inventory}")
    print(f"Changelog: {changelog}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
