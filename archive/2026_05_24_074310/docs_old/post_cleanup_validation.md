# Post-Cleanup Validation

Generated on 2026-05-23.

## Decision

**CLEAN FOR DEPLOYMENT = YES**

The deployment inventory is complete, final Power BI and ML artifacts are present, and obsolete model/metric/prediction experiment outputs have been removed from active folders. One non-blocking duplicate Power BI file remains in the project root because Windows reports it as locked by another process.

## Validation Results

| Check | Status | Evidence |
|---|---|---|
| Archive folders exist | PASS | `archive/models_old`, `archive/metrics_old`, `archive/predictions_old`, `archive/docs_old`, `archive/powerbi_old`, `archive/experiments_old` exist. Historical `old_models`, `old_metrics`, and `old_predictions` also remain as prior archive buckets. |
| Obsolete models moved | PASS | Active `output/` contains only `models_final/`, `predictions_final/`, root prediction aliases, and `risk_scores.csv`. Older model folders are no longer active. |
| Duplicate metrics removed | PASS | Active metric files are limited to final model metrics and final feature-importance CSVs inside `output/models_final/`. Intermediate ROC, threshold, leakage, before/after, and correlation metrics are archived. |
| Deployment inventory production-only | PASS | `docs/deployment_inventory.md` lists only Power BI inputs, final ML artifacts, future retraining scripts, and final documentation. |
| Power BI files intact | PASS | `dashboard/powerbi_blueprint.md` and `dashboard/UC_Razorpay_Dashboard_v1.pbix` exist. |

## Active Production Files

### Data

- `data/merchants.csv`
- `data/payouts_loans.csv`
- `data/provider_kpis.csv`
- `data/transactions.csv`
- `data/primary_responses_clean.csv`

### Models

- `output/models_final/churn_model_final.pkl`
- `output/models_final/loan_default_model_final.pkl`
- `output/models_final/adoption_model_final.pkl`
- `output/models_final/income_growth_model_final.pkl`

### Predictions And Risk

- `output/predictions_final/churn_predictions_final.csv`
- `output/predictions_final/default_predictions_final.csv`
- `output/predictions_final/adoption_predictions_final.csv`
- `output/predictions_final/income_growth_predictions_final.csv`
- `output/churn_predictions.csv`
- `output/default_predictions.csv`
- `output/adoption_predictions.csv`
- `output/risk_scores.csv`

### Documentation

- `docs/primary_secondary_mapping.csv`
- `docs/primary_secondary_compatibility_report.md`
- `docs/data_recency_audit.md`
- `docs/archive_manifest.md`
- `docs/final_model_metrics.md`
- `docs/project_cleanup_audit.md`
- `docs/deployment_inventory.md`

### Dashboard

- `dashboard/powerbi_blueprint.md`
- `dashboard/UC_Razorpay_Dashboard_v1.pbix`

## Remaining Clutter

| Path | Severity | Reason |
|---|---|---|
| `UC_Razorpay_Dashboard_v1.pbix` | Low | Duplicate root-level PBIX remains because the file is locked by another process. A valid deployment copy exists in `dashboard/`, and archived copies exist under `archive/powerbi_old/`. |
| `archive/old_models`, `archive/old_metrics`, `archive/old_predictions` | Low | Legacy archive buckets from earlier cleanup passes. They are already under `archive/` and do not affect deployment. |

## Notes

- No files were permanently deleted during cleanup.
- `src/` contains only generation, preprocessing, validation, integration, final training, and cleanup scripts.
- No non-archive `*.pyc` files or active smoke/retrained/leakage experiment files were found, aside from `preprocess_primary_responses.py`, whose name matched the search pattern because it contains `responses`.
