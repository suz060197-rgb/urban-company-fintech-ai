# Project Cleanup Inventory

Generated: 2026-05-24 16:36

## Keep Final

- `app/`
- `data/merchants.csv`
- `data/transactions.csv`
- `data/payouts_loans.csv`
- `data/provider_kpis.csv`
- `data/primary_responses_clean.csv`
- `output/models_final/`
- `output/predictions_final/`
- `output/risk_scores.csv`
- `output/default_predictions.csv`
- `output/churn_predictions.csv`
- `output/adoption_predictions.csv`
- `output/Executive_Report.pdf`
- `output/business_analysis/`
- `output/shap/`
- `dashboard/powerbi_blueprint.md`
- `UC_Razorpay_EmbeddedFinance.pbix`
- `docs/`
- `src/`
- `README.md`
- `requirements.txt`
- `assumptions.md`

## Archived This Run

| File/folder | Purpose | Referenced elsewhere? | Last modified relevance | Decision |
|---|---|---|---|---|
| `cleanup_report.md` | Superseded cleanup report replaced by CHANGELOG_cleanup.md and docs/project_cleanup_inventory.md. | No active runtime dependency found | Moved to archive | Archive |
| `output/embedded_finance_executive_report.pdf` | Duplicate older executive PDF; output/Executive_Report.pdf is the regenerated final report. | No active runtime dependency found | Moved to archive | Archive |
| `dashboard/UC_Razorpay_Dashboard_v1.pbix` | Older small PBIX copy; latest PBIX retained at project root as UC_Razorpay_EmbeddedFinance.pbix. | No active runtime dependency found | Moved to archive | Archive |
| `app/__pycache__/Home.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | No active runtime dependency found | Moved to archive | Archive |
| `app/__pycache__/__init__.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | No active runtime dependency found | Moved to archive | Archive |
| `app/utils/__pycache__/auth.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | No active runtime dependency found | Moved to archive | Archive |
| `app/utils/__pycache__/report_generator.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | No active runtime dependency found | Moved to archive | Archive |
| `app/utils/__pycache__/theme.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | No active runtime dependency found | Moved to archive | Archive |
| `app/utils/__pycache__/__init__.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | No active runtime dependency found | Moved to archive | Archive |
| `app/pages/__pycache__/01_Risk_Dashboard.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | No active runtime dependency found | Moved to archive | Archive |
| `app/pages/__pycache__/02_Predictions.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | No active runtime dependency found | Moved to archive | Archive |
| `app/pages/__pycache__/03_Primary_Insights.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | No active runtime dependency found | Moved to archive | Archive |
| `app/pages/__pycache__/04_Model_Performance.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | No active runtime dependency found | Moved to archive | Archive |
| `app/pages/__pycache__/06_Admin.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | No active runtime dependency found | Moved to archive | Archive |
| `app/pages/__pycache__/06_Survey_Insights.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | No active runtime dependency found | Moved to archive | Archive |
| `app/pages/__pycache__/07_AI_Report_Generator.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | No active runtime dependency found | Moved to archive | Archive |
| `app/components/__pycache__/cards.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | No active runtime dependency found | Moved to archive | Archive |
| `app/components/__pycache__/charts.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | No active runtime dependency found | Moved to archive | Archive |
| `app/components/__pycache__/status.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | No active runtime dependency found | Moved to archive | Archive |
| `app/components/__pycache__/__init__.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | No active runtime dependency found | Moved to archive | Archive |
| `src/__pycache__/mba_ba_ml_improvements.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | No active runtime dependency found | Moved to archive | Archive |

## Conservative Keep Notes

- Final datasets, final models, predictions, feature importance files, SHAP outputs, and training scripts were retained.
- `output/models_final/adoption_model_final_pre_engineered.pkl` was retained because it preserves baseline reproducibility for the adoption-model audit.
- Existing historical archive folders were not reprocessed.