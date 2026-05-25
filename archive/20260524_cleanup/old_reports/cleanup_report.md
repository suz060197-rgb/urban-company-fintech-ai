# Repository Cleanup Report

Generated: 2026-05-24

## Deployment Status

**CLEANUP RESULT: PASS**

The project was cleaned safely by archiving obsolete files only. No files were permanently deleted. The Streamlit app, Power BI artifacts, final datasets, final model artifacts, prediction outputs, model performance pages, and primary research pages were preserved.

## Cleanup Policy Used

Production files that are directly referenced by the Streamlit app were kept in their current locations to avoid broken paths. In particular, the app currently reads final CSVs from `data/` and final prediction aliases from `output/`, so those files were not moved into nested folders during this pass.

## Classification Summary

| Category | Meaning | Action |
|---|---|---|
| KEEP_FINAL | Required by the app, dashboard, final ML outputs, dissertation docs, or retraining workflow. | Kept active |
| ARCHIVE | Obsolete, duplicated, superseded, historical, or generated cache file. | Moved to `archive/2026_05_24_074310/` |
| DELETE_SAFE | Runtime cache regenerated automatically. | Archived, not deleted |
| UNKNOWN | Not moved because dependency risk was unclear. | None identified in active production paths |

## Archived Files

Archive root: `archive/2026_05_24_074310/`

| Original path | Archived path | Reason |
|---|---|---|
| `app/__pycache__/` | `archive/2026_05_24_074310/cache/app__pycache__/` | Python bytecode cache; regenerated automatically |
| `app/pages/__pycache__/` | `archive/2026_05_24_074310/cache/app_pages__pycache__/` | Python bytecode cache; regenerated automatically |
| `app/utils/__pycache__/` | `archive/2026_05_24_074310/cache/app_utils__pycache__/` | Python bytecode cache; regenerated automatically |
| `app/pages/05_Admin_Legacy.py` | `archive/2026_05_24_074310/legacy_pages/05_Admin_Legacy.py` | Legacy placeholder page superseded by `app/pages/06_Admin.py` |
| `docs/project_cleanup_audit.md` | `archive/2026_05_24_074310/docs_old/project_cleanup_audit.md` | Historical cleanup audit superseded by this report |
| `docs/post_cleanup_validation.md` | `archive/2026_05_24_074310/docs_old/post_cleanup_validation.md` | Historical validation report superseded by this report |
| `UC_Razorpay_Dashboard_v1.pbix` | `archive/2026_05_24_074310/powerbi_old/UC_Razorpay_Dashboard_v1.pbix` | Older duplicate root Power BI file; dashboard copy and latest embedded-finance PBIX retained |
| `app/__pycache__/` | `archive/2026_05_24_074310/cache/regenerated_after_validation/app__pycache__/` | Python bytecode cache regenerated during validation |
| `app/pages/__pycache__/` | `archive/2026_05_24_074310/cache/regenerated_after_validation/app_pages__pycache__/` | Python bytecode cache regenerated during validation |
| `app/utils/__pycache__/` | `archive/2026_05_24_074310/cache/regenerated_after_validation/app_utils__pycache__/` | Python bytecode cache regenerated during validation |

The archive manifest is also saved at `archive/2026_05_24_074310/manifest.csv`.

## Remaining Active Files

### Streamlit App

| Path | Status |
|---|---|
| `app/Home.py` | KEEP_FINAL |
| `app/pages/01_Risk_Dashboard.py` | KEEP_FINAL |
| `app/pages/02_Predictions.py` | KEEP_FINAL |
| `app/pages/03_Primary_Insights.py` | KEEP_FINAL |
| `app/pages/04_Model_Performance.py` | KEEP_FINAL |
| `app/pages/06_Admin.py` | KEEP_FINAL |
| `app/pages/06_Survey_Insights.py` | KEEP_FINAL |
| `app/pages/07_AI_Report_Generator.py` | KEEP_FINAL |
| `app/utils/auth.py` | KEEP_FINAL |
| `app/utils/report_generator.py` | KEEP_FINAL |
| `app/requirements.txt` | KEEP_FINAL |

### Final Datasets

| Path | Status |
|---|---|
| `data/merchants.csv` | KEEP_FINAL |
| `data/transactions.csv` | KEEP_FINAL |
| `data/payouts_loans.csv` | KEEP_FINAL |
| `data/provider_kpis.csv` | KEEP_FINAL |
| `data/primary_responses_clean.csv` | KEEP_FINAL |

### Final Models And Predictions

| Path | Status |
|---|---|
| `output/models_final/` | KEEP_FINAL |
| `output/predictions_final/` | KEEP_FINAL |
| `output/risk_scores.csv` | KEEP_FINAL |
| `output/default_predictions.csv` | KEEP_FINAL |
| `output/churn_predictions.csv` | KEEP_FINAL |
| `output/adoption_predictions.csv` | KEEP_FINAL |
| `output/embedded_finance_executive_report.pdf` | KEEP_FINAL |

### Dissertation And Dashboard Outputs

| Path | Status |
|---|---|
| `docs/archive_manifest.md` | KEEP_FINAL |
| `docs/data_recency_audit.md` | KEEP_FINAL |
| `docs/deployment_inventory.md` | KEEP_FINAL |
| `docs/final_model_metrics.md` | KEEP_FINAL |
| `docs/primary_secondary_compatibility_report.md` | KEEP_FINAL |
| `docs/primary_secondary_mapping.csv` | KEEP_FINAL |
| `dashboard/powerbi_blueprint.md` | KEEP_FINAL |
| `dashboard/UC_Razorpay_Dashboard_v1.pbix` | KEEP_FINAL |
| `UC_Razorpay_EmbeddedFinance.pbix` | KEEP_FINAL |

### Retraining And Maintenance Scripts

| Path | Status |
|---|---|
| `src/generate_uc_dataset.py` | KEEP_FINAL |
| `src/train_final_models.py` | KEEP_FINAL |
| `src/validation.py` | KEEP_FINAL |
| `src/preprocess_primary_responses.py` | KEEP_FINAL |
| `src/create_lagged_features.py` | KEEP_FINAL |
| `src/create_future_targets.py` | KEEP_FINAL |
| `src/create_primary_secondary_mapping.py` | KEEP_FINAL |
| `src/integrate_primary_features.py` | KEEP_FINAL |
| `src/audit_data_recency.py` | KEEP_FINAL |
| `src/provenance.py` | KEEP_FINAL |
| `src/cleanup_project_for_deployment.py` | KEEP_FINAL |

## Validation Results

| Check | Result |
|---|---|
| Python compile for all live app pages/utilities | PASS |
| Home page AppTest smoke test | PASS |
| Risk Dashboard AppTest smoke test | PASS |
| Predictions AppTest smoke test | PASS |
| Primary Insights AppTest smoke test | PASS |
| Model Performance AppTest smoke test | PASS |
| Admin AppTest smoke test | PASS |
| Survey Insights AppTest smoke test | PASS |
| AI Report Generator AppTest smoke test | PASS |
| Full Streamlit launch | PASS |

## Path Fixes Applied

| File | Fix |
|---|---|
| `app/Home.py` | Added explicit `app/` path insertion before importing `utils.auth`, making Home robust in both Streamlit and test harness execution |

## Warnings

- Running compile and page smoke tests regenerated `__pycache__` folders; these regenerated caches were also archived after validation.
- Active production files were intentionally not moved into `data/current/` or `output/final/` because the current app and training scripts reference `data/`, `output/models_final/`, `output/predictions_final/`, and root prediction aliases directly.
- No permanent deletion was performed.
