# Project Cleanup Audit

Generated on 2026-05-23.

Classification definitions:

- `KEEP`: retained in the deployment-ready project tree.
- `ARCHIVE`: moved into archive folders before cleanup.
- `DELETE_CANDIDATE`: temporary/cache artifact; archived rather than deleted.

## Summary

- KEEP: 203
- ARCHIVE: 1
- DELETE_CANDIDATE: 1

## File Classification

| path | classification | reason |
| --- | --- | --- |
| README.md | KEEP | Project root metadata. |
| UC_Razorpay_Dashboard_v1.pbix | ARCHIVE | Duplicate Power BI artifact outside final dashboard folder. |
| archive/docs_old/20260523_150401/docs/data_extension_report.md | KEEP | Already archived historical artifact. |
| archive/docs_old/20260523_150401/docs/data_inventory.md | KEEP | Already archived historical artifact. |
| archive/docs_old/20260523_150401/docs/feature_enhancement_plan.md | KEEP | Already archived historical artifact. |
| archive/docs_old/20260523_150401/docs/file_inventory.md | KEEP | Already archived historical artifact. |
| archive/docs_old/20260523_150401/docs/predictions_export_report.md | KEEP | Already archived historical artifact. |
| archive/docs_old/20260523_150401/docs/primary_cleaning_report.md | KEEP | Already archived historical artifact. |
| archive/docs_old/20260523_150401/docs/primary_data_audit.md | KEEP | Already archived historical artifact. |
| archive/docs_old/20260523_150401/docs/primary_data_questionnaire.md | KEEP | Already archived historical artifact. |
| archive/docs_old/20260523_150401/docs/primary_integration_report.md | KEEP | Already archived historical artifact. |
| archive/docs_old/20260523_150401/docs/target_mapping.md | KEEP | Already archived historical artifact. |
| archive/docs_old/20260523_150401/docs/target_mapping_v2.md | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150231/data/merchants.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150231/data/payouts_loans.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150231/data/provider_kpis.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150231/data/transactions.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/data/model_ready/provider_month_future_targets.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/data/model_ready/provider_month_lagged.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/data/primary_interview_quotes.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/data/provenance.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/data/provider_features_enriched.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/data/survey_data.csv.xlsx | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/data_v2/merchants.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/data_v2/model_ready/provider_month_future_targets.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/data_v2/model_ready/provider_month_lagged.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/data_v2/payouts_loans.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/data_v2/provenance.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/data_v2/provider_kpis.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/data_v2/transactions.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/output/adoption_propensity_report.md | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/output/default_threshold_tuning.md | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/output/delta_smoke/validation_report.txt | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/output/leakage_audit.md | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/output/primary_vs_synthetic_report.md | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/archive_obsolete_artifacts.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/audit_data_recency.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/cleanup_project_for_deployment.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/compare_data_extension.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/compare_primary_synthetic.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/create_future_targets.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/create_lagged_features.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/create_primary_secondary_mapping.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/export_model_predictions.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/generate_uc_dataset.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/integrate_primary_features.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/preprocess_primary_responses.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/provenance.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/retrain_default_model.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/retrain_default_model_safe.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/retrain_weak_models.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/retrain_weak_models_engineered.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/train_adoption_propensity.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/train_final_models.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/train_models.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/tune_default_threshold.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/__pycache__/validation.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/archive_obsolete_artifacts.py | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/compare_data_extension.py | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/compare_primary_synthetic.py | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/export_model_predictions.py | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/retrain_default_model.py | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/retrain_default_model_safe.py | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/retrain_weak_models.py | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/retrain_weak_models_engineered.py | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/train_adoption_propensity.py | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/train_models.py | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/src/tune_default_threshold.py | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150401/validation_report.txt | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150456/data/merchants.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150456/data/payouts_loans.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150456/data/provider_kpis.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150456/data/transactions.csv | KEEP | Already archived historical artifact. |
| archive/experiments_old/20260523_150456/src/__pycache__/cleanup_project_for_deployment.cpython-314.pyc | KEEP | Already archived historical artifact. |
| archive/metrics_old/20260523_150401/output/v2_smoke/merchants.csv | KEEP | Already archived historical artifact. |
| archive/metrics_old/20260523_150401/output/v2_smoke/payouts_loans.csv | KEEP | Already archived historical artifact. |
| archive/metrics_old/20260523_150401/output/v2_smoke/provenance.csv | KEEP | Already archived historical artifact. |
| archive/metrics_old/20260523_150401/output/v2_smoke/provider_kpis.csv | KEEP | Already archived historical artifact. |
| archive/metrics_old/20260523_150401/output/v2_smoke/transactions.csv | KEEP | Already archived historical artifact. |
| archive/models_old/20260523_150401/output/adoption_model_audit.md | KEEP | Already archived historical artifact. |
| archive/models_old/20260523_150401/output/default_model_improvement.md | KEEP | Already archived historical artifact. |
| archive/models_old/20260523_150401/output/default_model_leakage_audit.md | KEEP | Already archived historical artifact. |
| archive/models_old/20260523_150401/output/default_model_revision_history.md | KEEP | Already archived historical artifact. |
| archive/models_old/20260523_150401/output/model_explainability.md | KEEP | Already archived historical artifact. |
| archive/models_old/20260523_150401/output/models_retrained_engineered/engineered_feature_summary.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/adoption_feature_correlations.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/adoption_propensity/embedded_finance_adoption_propensity_correlations.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/agreement_scores.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/before_after_model_metrics.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/default_feature_leakage_ratings.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/default_model_improved/default_before_after_metrics.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/default_model_improved/default_feature_correlations.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/default_model_improved/default_feature_importance.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/default_model_safe/default_revision_metric_history.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/default_model_safe/default_safe_feature_correlations.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/default_score_quantiles.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/default_threshold_tuning.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/feature_importance.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/models/embedded_finance_adoption_feature_importance.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/models/loan_default_prediction_feature_importance.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/models_retrained/before_vs_after_metrics.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/models_retrained/embedded_finance_adoption_feature_importance.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/models_retrained/loan_default_prediction_feature_importance.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/models_retrained_engineered/before_after_model_metrics.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/models_retrained_engineered/embedded_finance_adoption_feature_importance.csv | KEEP | Already archived historical artifact. |
| archive/old_metrics/output/models_retrained_engineered/loan_default_prediction_feature_importance.csv | KEEP | Already archived historical artifact. |
| archive/old_models/output/default_model_improved/loan_default_prediction_improved.pkl | KEEP | Already archived historical artifact. |
| archive/old_models/output/models/embedded_finance_adoption.pkl | KEEP | Already archived historical artifact. |
| archive/old_models/output/models/loan_default_prediction.pkl | KEEP | Already archived historical artifact. |
| archive/old_models/output/models_retrained/embedded_finance_adoption.pkl | KEEP | Already archived historical artifact. |
| archive/old_models/output/models_retrained/loan_default_prediction.pkl | KEEP | Already archived historical artifact. |
| archive/old_models/output/models_retrained_engineered/embedded_finance_adoption.pkl | KEEP | Already archived historical artifact. |
| archive/old_models/output/models_retrained_engineered/loan_default_prediction.pkl | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145519/output/adoption_propensity/adoption_propensity_roc_comparison.csv | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145519/output/adoption_propensity/embedded_finance_adoption_propensity.pkl | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145519/output/adoption_propensity/embedded_finance_adoption_propensity_feature_importance.csv | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145519/output/default_model_safe/default_safe_feature_importance.csv | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145519/output/default_model_safe/default_safe_metrics.csv | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145519/output/default_model_safe/loan_default_prediction_leakage_safe.pkl | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145519/output/models/churn_prediction.pkl | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145519/output/models/churn_prediction_feature_importance.csv | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145519/output/models/income_growth_prediction.pkl | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145519/output/models/income_growth_prediction_feature_importance.csv | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145519/output/models/model_metrics.csv | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145519/output/models/model_report.txt | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145519/output/risk_scores.csv | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145544/output/models_final/churn_prediction.pkl | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145544/output/models_final/churn_prediction_feature_importance.csv | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145544/output/models_final/embedded_finance_adoption.pkl | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145544/output/models_final/embedded_finance_adoption_feature_importance.csv | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145544/output/models_final/final_model_metrics.csv | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145544/output/models_final/income_growth_prediction.pkl | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145544/output/models_final/income_growth_prediction_feature_importance.csv | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145544/output/models_final/loan_default_prediction.pkl | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145544/output/models_final/loan_default_prediction_feature_importance.csv | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145544/output/predictions_final/churn_prediction_predictions.csv | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145544/output/predictions_final/embedded_finance_adoption_predictions.csv | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145544/output/predictions_final/income_growth_prediction_predictions.csv | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145544/output/predictions_final/loan_default_prediction_predictions.csv | KEEP | Already archived historical artifact. |
| archive/old_models/pre_final_v2_20260523_145544/output/risk_scores.csv | KEEP | Already archived historical artifact. |
| archive/old_predictions/output/default_risk_segmentation.csv | KEEP | Already archived historical artifact. |
| archive/old_predictions/output/delta_smoke/merchants.csv | KEEP | Already archived historical artifact. |
| archive/old_predictions/output/delta_smoke/payouts_loans.csv | KEEP | Already archived historical artifact. |
| archive/old_predictions/output/delta_smoke/provenance.csv | KEEP | Already archived historical artifact. |
| archive/old_predictions/output/delta_smoke/provider_kpis.csv | KEEP | Already archived historical artifact. |
| archive/old_predictions/output/delta_smoke/transactions.csv | KEEP | Already archived historical artifact. |
| archive/old_predictions/output/step3_smoke/merchants.csv | KEEP | Already archived historical artifact. |
| archive/old_predictions/output/step3_smoke/payouts_loans.csv | KEEP | Already archived historical artifact. |
| archive/old_predictions/output/step3_smoke/provider_kpis.csv | KEEP | Already archived historical artifact. |
| archive/old_predictions/output/step3_smoke/transactions.csv | KEEP | Already archived historical artifact. |
| archive/powerbi_old/20260523_150401/Power Bi/UC_Razorpay_Dashboard_v1.pbix | KEEP | Already archived historical artifact. |
| archive/powerbi_old/20260523_150401/UC_Razorpay_Dashboard_v1.pbix | KEEP | Already archived historical artifact. |
| archive/powerbi_old/20260523_150456/UC_Razorpay_Dashboard_v1.pbix | KEEP | Already archived historical artifact. |
| archive/predictions_old/20260523_150401/output/adoption_predictions.csv | KEEP | Already archived historical artifact. |
| archive/predictions_old/20260523_150401/output/churn_predictions.csv | KEEP | Already archived historical artifact. |
| archive/predictions_old/20260523_150401/output/default_predictions.csv | KEEP | Already archived historical artifact. |
| archive/predictions_old/20260523_150401/output/default_risk_segmentation.md | KEEP | Already archived historical artifact. |
| archive/predictions_old/20260523_150456/output/adoption_predictions.csv | KEEP | Already archived historical artifact. |
| archive/predictions_old/20260523_150456/output/churn_predictions.csv | KEEP | Already archived historical artifact. |
| archive/predictions_old/20260523_150456/output/default_predictions.csv | KEEP | Already archived historical artifact. |
| assumptions.md | KEEP | Project root metadata. |
| dashboard/UC_Razorpay_Dashboard_v1.pbix | KEEP | Power BI dashboard artifact or layout. |
| dashboard/powerbi_blueprint.md | KEEP | Power BI dashboard artifact or layout. |
| data/merchants.csv | KEEP | Production dataset after promotion. |
| data/payouts_loans.csv | KEEP | Production dataset after promotion. |
| data/primary_responses_clean.csv | KEEP | Production dataset after promotion. |
| data/provider_kpis.csv | KEEP | Production dataset after promotion. |
| data/transactions.csv | KEEP | Production dataset after promotion. |
| docs/archive_manifest.md | KEEP | Deployment/final dissertation documentation. |
| docs/data_recency_audit.md | KEEP | Deployment/final dissertation documentation. |
| docs/deployment_inventory.md | KEEP | Deployment/final dissertation documentation. |
| docs/final_model_metrics.md | KEEP | Deployment/final dissertation documentation. |
| docs/primary_secondary_compatibility_report.md | KEEP | Deployment/final dissertation documentation. |
| docs/primary_secondary_mapping.csv | KEEP | Deployment/final dissertation documentation. |
| docs/project_cleanup_audit.md | KEEP | Deployment/final dissertation documentation. |
| output/adoption_predictions.csv | KEEP | Dashboard-ready final prediction or risk score alias. |
| output/churn_predictions.csv | KEEP | Dashboard-ready final prediction or risk score alias. |
| output/default_predictions.csv | KEEP | Dashboard-ready final prediction or risk score alias. |
| output/models_final/adoption_model_final.pkl | KEEP | Final dissertation model artifact or feature importance. |
| output/models_final/churn_model_final.pkl | KEEP | Final dissertation model artifact or feature importance. |
| output/models_final/churn_prediction_feature_importance.csv | KEEP | Final dissertation model artifact or feature importance. |
| output/models_final/embedded_finance_adoption_feature_importance.csv | KEEP | Final dissertation model artifact or feature importance. |
| output/models_final/final_model_metrics.csv | KEEP | Final dissertation model artifact or feature importance. |
| output/models_final/income_growth_model_final.pkl | KEEP | Final dissertation model artifact or feature importance. |
| output/models_final/income_growth_prediction_feature_importance.csv | KEEP | Final dissertation model artifact or feature importance. |
| output/models_final/loan_default_model_final.pkl | KEEP | Final dissertation model artifact or feature importance. |
| output/models_final/loan_default_prediction_feature_importance.csv | KEEP | Final dissertation model artifact or feature importance. |
| output/predictions_final/adoption_predictions_final.csv | KEEP | Final model prediction export. |
| output/predictions_final/churn_predictions_final.csv | KEEP | Final model prediction export. |
| output/predictions_final/default_predictions_final.csv | KEEP | Final model prediction export. |
| output/predictions_final/income_growth_predictions_final.csv | KEEP | Final model prediction export. |
| output/risk_scores.csv | KEEP | Dashboard-ready final prediction or risk score alias. |
| requirements.txt | KEEP | Project root metadata. |
| src/__pycache__/cleanup_project_for_deployment.cpython-314.pyc | DELETE_CANDIDATE | Python bytecode cache; archived instead of deleted. |
| src/audit_data_recency.py | KEEP | Script needed for generation, validation, integration, cleanup, or final training. |
| src/cleanup_project_for_deployment.py | KEEP | Script needed for generation, validation, integration, cleanup, or final training. |
| src/create_future_targets.py | KEEP | Script needed for generation, validation, integration, cleanup, or final training. |
| src/create_lagged_features.py | KEEP | Script needed for generation, validation, integration, cleanup, or final training. |
| src/create_primary_secondary_mapping.py | KEEP | Script needed for generation, validation, integration, cleanup, or final training. |
| src/generate_uc_dataset.py | KEEP | Script needed for generation, validation, integration, cleanup, or final training. |
| src/integrate_primary_features.py | KEEP | Script needed for generation, validation, integration, cleanup, or final training. |
| src/preprocess_primary_responses.py | KEEP | Script needed for generation, validation, integration, cleanup, or final training. |
| src/provenance.py | KEEP | Script needed for generation, validation, integration, cleanup, or final training. |
| src/train_final_models.py | KEEP | Script needed for generation, validation, integration, cleanup, or final training. |
| src/validation.py | KEEP | Script needed for generation, validation, integration, cleanup, or final training. |