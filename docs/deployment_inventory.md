# Deployment Inventory

Generated on 2026-05-23.

Only deployment-needed files are listed below.

## Power BI

| file | exists |
|---|---|
| `data/merchants.csv` | yes |
| `data/payouts_loans.csv` | yes |
| `data/provider_kpis.csv` | yes |
| `data/transactions.csv` | yes |
| `data/primary_responses_clean.csv` | yes |
| `output/churn_predictions.csv` | yes |
| `output/default_predictions.csv` | yes |
| `output/adoption_predictions.csv` | yes |
| `output/risk_scores.csv` | yes |
| `dashboard/powerbi_blueprint.md` | yes |
| `UC_Razorpay_EmbeddedFinance.pbix` | yes |

## ML app

| file | exists |
|---|---|
| `output/models_final/churn_model_final.pkl` | yes |
| `output/models_final/loan_default_model_final.pkl` | yes |
| `output/models_final/adoption_model_final.pkl` | yes |
| `output/models_final/income_growth_model_final.pkl` | yes |
| `output/predictions_final/churn_predictions_final.csv` | yes |
| `output/predictions_final/default_predictions_final.csv` | yes |
| `output/predictions_final/adoption_predictions_final.csv` | yes |
| `output/predictions_final/income_growth_predictions_final.csv` | yes |
| `output/risk_scores.csv` | yes |

## Future retraining

| file | exists |
|---|---|
| `src/generate_uc_dataset.py` | yes |
| `src/create_lagged_features.py` | yes |
| `src/create_future_targets.py` | yes |
| `src/train_final_models.py` | yes |
| `src/integrate_primary_features.py` | yes |
| `src/preprocess_primary_responses.py` | yes |
| `src/validation.py` | yes |
| `src/provenance.py` | yes |
| `requirements.txt` | yes |
| `README.md` | yes |
| `assumptions.md` | yes |

## Final documentation

| file | exists |
|---|---|
| `docs/primary_secondary_mapping.csv` | yes |
| `docs/primary_secondary_compatibility_report.md` | yes |
| `docs/data_recency_audit.md` | yes |
| `docs/archive_manifest.md` | yes |
| `docs/final_model_metrics.md` | yes |
| `docs/project_cleanup_inventory.md` | yes |
| `docs/deployment_inventory.md` | yes |
