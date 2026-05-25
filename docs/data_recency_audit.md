# Data Recency Audit

Audit date: 2026-05-23
Stale cutoff: records/datasets with latest date before 2025-05-23 are flagged.

## Summary

- CSV files scanned: 53
- Files with detected date columns: 17
- Files without detected date columns: 36
- Files flagged older than 12 months: 16
- Files with missing monthly periods inside their own earliest/latest range: 0

## Recency By Dataset

| dataset | rows | primary_date_column | earliest_date | latest_date | observed_months | coverage_months | coverage_pct | stale_flag |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| data/merchants.csv | 1000 | intervention_timestamp | 2024-02-01 | 2024-08-01 | 7 | 7 | 1.0 | STALE >12 months |
| data/model_ready/provider_month_future_targets.csv | 12000 | month | 2024-01-01 | 2024-12-01 | 12 | 12 | 1.0 | STALE >12 months |
| data/model_ready/provider_month_lagged.csv | 12000 | month | 2024-01-01 | 2024-12-01 | 12 | 12 | 1.0 | STALE >12 months |
| data/payouts_loans.csv | 12000 | month | 2024-01-01 | 2024-12-01 | 12 | 12 | 1.0 | STALE >12 months |
| data/primary_interview_quotes.csv | 30 |  |  |  |  |  |  | No date column |
| data/primary_responses_clean.csv | 30 | survey_response_date | 2026-05-02 | 2026-05-17 | 1 | 1 | 1.0 | Current within 12 months |
| data/provenance.csv | 60 |  |  |  |  |  |  | No date column |
| data/provider_kpis.csv | 12000 | month | 2024-01-01 | 2024-12-01 | 12 | 12 | 1.0 | STALE >12 months |
| data/transactions.csv | 403539 | timestamp | 2024-01-01 | 2024-12-31 | 12 | 12 | 1.0 | STALE >12 months |
| docs/primary_secondary_mapping.csv | 34 |  |  |  |  |  |  | No date column |
| output/adoption_feature_correlations.csv | 53 |  |  |  |  |  |  | No date column |
| output/adoption_predictions.csv | 12000 | month | 2024-01-01 | 2024-12-01 | 12 | 12 | 1.0 | STALE >12 months |
| output/adoption_propensity/adoption_propensity_roc_comparison.csv | 3 |  |  |  |  |  |  | No date column |
| output/adoption_propensity/embedded_finance_adoption_propensity_correlations.csv | 36 |  |  |  |  |  |  | No date column |
| output/adoption_propensity/embedded_finance_adoption_propensity_feature_importance.csv | 36 |  |  |  |  |  |  | No date column |
| output/agreement_scores.csv | 13 |  |  |  |  |  |  | No date column |
| output/before_after_model_metrics.csv | 20 |  |  |  |  |  |  | No date column |
| output/churn_predictions.csv | 12000 | month | 2024-01-01 | 2024-12-01 | 12 | 12 | 1.0 | STALE >12 months |
| output/default_feature_leakage_ratings.csv | 10 |  |  |  |  |  |  | No date column |
| output/default_model_improved/default_before_after_metrics.csv | 10 |  |  |  |  |  |  | No date column |
| output/default_model_improved/default_feature_correlations.csv | 61 |  |  |  |  |  |  | No date column |
| output/default_model_improved/default_feature_importance.csv | 61 |  |  |  |  |  |  | No date column |
| output/default_model_safe/default_revision_metric_history.csv | 3 |  |  |  |  |  |  | No date column |
| output/default_model_safe/default_safe_feature_correlations.csv | 60 |  |  |  |  |  |  | No date column |
| output/default_model_safe/default_safe_feature_importance.csv | 60 |  |  |  |  |  |  | No date column |
| output/default_model_safe/default_safe_metrics.csv | 1 |  |  |  |  |  |  | No date column |
| output/default_predictions.csv | 12000 | month | 2024-01-01 | 2024-12-01 | 12 | 12 | 1.0 | STALE >12 months |
| output/default_risk_segmentation.csv | 3 |  |  |  |  |  |  | No date column |
| output/default_score_quantiles.csv | 9 |  |  |  |  |  |  | No date column |
| output/default_threshold_tuning.csv | 99 |  |  |  |  |  |  | No date column |
| output/delta_smoke/merchants.csv | 30 |  |  |  |  |  |  | No date column |
| output/delta_smoke/payouts_loans.csv | 120 | month | 2024-01-01 | 2024-04-01 | 4 | 4 | 1.0 | STALE >12 months |
| output/delta_smoke/provenance.csv | 58 |  |  |  |  |  |  | No date column |
| output/delta_smoke/provider_kpis.csv | 120 | month | 2024-01-01 | 2024-04-01 | 4 | 4 | 1.0 | STALE >12 months |
| output/delta_smoke/transactions.csv | 3754 | timestamp | 2024-01-01 | 2024-04-30 | 4 | 4 | 1.0 | STALE >12 months |
| output/feature_importance.csv | 48 |  |  |  |  |  |  | No date column |
| output/models/churn_prediction_feature_importance.csv | 12 |  |  |  |  |  |  | No date column |
| output/models/embedded_finance_adoption_feature_importance.csv | 12 |  |  |  |  |  |  | No date column |
| output/models/income_growth_prediction_feature_importance.csv | 12 |  |  |  |  |  |  | No date column |
| output/models/loan_default_prediction_feature_importance.csv | 12 |  |  |  |  |  |  | No date column |
| output/models/model_metrics.csv | 34 |  |  |  |  |  |  | No date column |
| output/models_retrained/before_vs_after_metrics.csv | 20 |  |  |  |  |  |  | No date column |
| output/models_retrained/embedded_finance_adoption_feature_importance.csv | 58 |  |  |  |  |  |  | No date column |
| output/models_retrained/loan_default_prediction_feature_importance.csv | 58 |  |  |  |  |  |  | No date column |
| output/models_retrained_engineered/before_after_model_metrics.csv | 20 |  |  |  |  |  |  | No date column |
| output/models_retrained_engineered/embedded_finance_adoption_feature_importance.csv | 78 |  |  |  |  |  |  | No date column |
| output/models_retrained_engineered/engineered_feature_summary.csv | 20 |  |  |  |  |  |  | No date column |
| output/models_retrained_engineered/loan_default_prediction_feature_importance.csv | 78 |  |  |  |  |  |  | No date column |
| output/risk_scores.csv | 12000 | month | 2024-01-01 | 2024-12-01 | 12 | 12 | 1.0 | STALE >12 months |
| output/step3_smoke/merchants.csv | 25 |  |  |  |  |  |  | No date column |
| output/step3_smoke/payouts_loans.csv | 75 | month | 2024-01-01 | 2024-03-01 | 3 | 3 | 1.0 | STALE >12 months |
| output/step3_smoke/provider_kpis.csv | 75 | month | 2024-01-01 | 2024-03-01 | 3 | 3 | 1.0 | STALE >12 months |
| output/step3_smoke/transactions.csv | 2520 | timestamp | 2024-01-01 | 2024-03-31 | 3 | 3 | 1.0 | STALE >12 months |

## Missing Periods

No monthly gaps were detected within each dated dataset's own coverage window.

## Stale Dataset Flags

| dataset | latest_date | stale_flag | stale_records |
| --- | --- | --- | --- |
| data/merchants.csv | 2024-08-01 | STALE >12 months | 456 |
| data/model_ready/provider_month_future_targets.csv | 2024-12-01 | STALE >12 months | 12000 |
| data/model_ready/provider_month_lagged.csv | 2024-12-01 | STALE >12 months | 12000 |
| data/payouts_loans.csv | 2024-12-01 | STALE >12 months | 12000 |
| data/provider_kpis.csv | 2024-12-01 | STALE >12 months | 12000 |
| data/transactions.csv | 2024-12-31 | STALE >12 months | 403539 |
| output/adoption_predictions.csv | 2024-12-01 | STALE >12 months | 12000 |
| output/churn_predictions.csv | 2024-12-01 | STALE >12 months | 12000 |
| output/default_predictions.csv | 2024-12-01 | STALE >12 months | 12000 |
| output/delta_smoke/payouts_loans.csv | 2024-04-01 | STALE >12 months | 120 |
| output/delta_smoke/provider_kpis.csv | 2024-04-01 | STALE >12 months | 120 |
| output/delta_smoke/transactions.csv | 2024-04-30 | STALE >12 months | 3754 |
| output/risk_scores.csv | 2024-12-01 | STALE >12 months | 12000 |
| output/step3_smoke/payouts_loans.csv | 2024-03-01 | STALE >12 months | 75 |
| output/step3_smoke/provider_kpis.csv | 2024-03-01 | STALE >12 months | 75 |
| output/step3_smoke/transactions.csv | 2024-03-31 | STALE >12 months | 2520 |

## Files Without Date Columns

| dataset | rows | columns | read_status |
| --- | --- | --- | --- |
| data/primary_interview_quotes.csv | 30 | 4 | OK |
| data/provenance.csv | 60 | 5 | OK |
| docs/primary_secondary_mapping.csv | 34 | 9 | OK |
| output/adoption_feature_correlations.csv | 53 | 3 | OK |
| output/adoption_propensity/adoption_propensity_roc_comparison.csv | 3 | 2 | OK |
| output/adoption_propensity/embedded_finance_adoption_propensity_correlations.csv | 36 | 3 | OK |
| output/adoption_propensity/embedded_finance_adoption_propensity_feature_importance.csv | 36 | 3 | OK |
| output/agreement_scores.csv | 13 | 11 | OK |
| output/before_after_model_metrics.csv | 20 | 5 | OK |
| output/default_feature_leakage_ratings.csv | 10 | 6 | OK |
| output/default_model_improved/default_before_after_metrics.csv | 10 | 5 | OK |
| output/default_model_improved/default_feature_correlations.csv | 61 | 3 | OK |
| output/default_model_improved/default_feature_importance.csv | 61 | 3 | OK |
| output/default_model_safe/default_revision_metric_history.csv | 3 | 5 | OK |
| output/default_model_safe/default_safe_feature_correlations.csv | 60 | 3 | OK |
| output/default_model_safe/default_safe_feature_importance.csv | 60 | 3 | OK |
| output/default_model_safe/default_safe_metrics.csv | 1 | 10 | OK |
| output/default_risk_segmentation.csv | 3 | 10 | OK |
| output/default_score_quantiles.csv | 9 | 2 | OK |
| output/default_threshold_tuning.csv | 99 | 13 | OK |
| output/delta_smoke/merchants.csv | 30 | 18 | OK |
| output/delta_smoke/provenance.csv | 58 | 5 | OK |
| output/feature_importance.csv | 48 | 6 | OK |
| output/models/churn_prediction_feature_importance.csv | 12 | 4 | OK |
| output/models/embedded_finance_adoption_feature_importance.csv | 12 | 4 | OK |
| output/models/income_growth_prediction_feature_importance.csv | 12 | 4 | OK |
| output/models/loan_default_prediction_feature_importance.csv | 12 | 4 | OK |
| output/models/model_metrics.csv | 34 | 3 | OK |
| output/models_retrained/before_vs_after_metrics.csv | 20 | 5 | OK |
| output/models_retrained/embedded_finance_adoption_feature_importance.csv | 58 | 4 | OK |
| output/models_retrained/loan_default_prediction_feature_importance.csv | 58 | 4 | OK |
| output/models_retrained_engineered/before_after_model_metrics.csv | 20 | 5 | OK |
| output/models_retrained_engineered/embedded_finance_adoption_feature_importance.csv | 78 | 4 | OK |
| output/models_retrained_engineered/engineered_feature_summary.csv | 20 | 9 | OK |
| output/models_retrained_engineered/loan_default_prediction_feature_importance.csv | 78 | 4 | OK |
| output/step3_smoke/merchants.csv | 25 | 12 | OK |

## Method

- Date-like columns were detected from column names containing `date`, `time`, `timestamp`, or `month`.
- A column was treated as date-bearing when at least 60% of non-null values parsed as dates.
- Monthly coverage compares observed months against a continuous month range from earliest to latest date.
- Stale dataset flags are based on each dataset's latest parsed date, not file modification time.