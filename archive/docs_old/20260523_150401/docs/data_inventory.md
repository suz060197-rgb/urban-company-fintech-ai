# Data And Model Artifact Inventory

Generated on 2026-05-22.

## Scope

This inventory covers project CSV files and model artifacts (`.pkl`) under:

- `data/`
- `data/model_ready/`
- `docs/`
- `output/`
- `output/*/`

It identifies files containing or supporting:

- predictions
- probabilities
- risk bands
- churn outputs
- default outputs
- adoption outputs

## Core Data CSVs

| File | Rows | Columns | Role | Contains predictions/probabilities? |
|---|---:|---:|---|---|
| `data/merchants.csv` | 1,000 | 19 | Synthetic provider baseline table | No |
| `data/transactions.csv` | 403,539 | 11 | Synthetic transaction/payment table | No |
| `data/payouts_loans.csv` | 12,000 | 12 | Synthetic provider-month payouts and loans | Contains actual/default outcome flag, not prediction |
| `data/provider_kpis.csv` | 12,000 | 13 | Synthetic provider-month KPI table | Contains `churn_probability` synthetic modeled probability |
| `data/provenance.csv` | 60 | 5 | Column-level provenance metadata | No |
| `data/primary_responses_clean.csv` | 30 | 43 | Cleaned primary survey responses | No model predictions |
| `data/primary_interview_quotes.csv` | 30 | 4 | Primary interview quote extract | No |
| `data/model_ready/provider_month_lagged.csv` | 12,000 | 61 | Lagged provider-month modeling table | Contains lagged/model-ready features |
| `data/model_ready/provider_month_future_targets.csv` | 12,000 | 67 | Future-target provider-month modeling table | Contains future targets: churn/default/income |

## Documentation CSVs

| File | Rows | Columns | Role |
|---|---:|---:|---|
| `docs/primary_secondary_mapping.csv` | 34 | 9 | Mapping between primary survey fields and synthetic variables |

## Output CSVs

| File | Rows | Columns | Role |
|---|---:|---:|---|
| `output/agreement_scores.csv` | 13 | 11 | Primary-vs-synthetic agreement scores |
| `output/feature_importance.csv` | 48 | 6 | Combined model feature importance/explainability table |
| `output/before_after_model_metrics.csv` | 20 | 5 | Before/after metrics for engineered weak-model retraining |
| `output/adoption_feature_correlations.csv` | 53 | 3 | Adoption leakage audit feature-target correlations |
| `output/default_feature_leakage_ratings.csv` | 10 | 6 | Default feature leakage ratings |
| `output/default_risk_segmentation.csv` | 3 | 10 | Default probability risk-band summary |
| `output/default_score_quantiles.csv` | 9 | 2 | Default model score/probability quantiles |
| `output/default_threshold_tuning.csv` | 99 | 13 | Default threshold precision/recall/F-score table |

## Model Metrics And Importance CSVs

| File | Rows | Columns | Role |
|---|---:|---:|---|
| `output/models/model_metrics.csv` | 34 | 3 | Original model metrics for churn, default, income, adoption |
| `output/models/churn_prediction_feature_importance.csv` | 12 | 4 | Original churn model feature importance |
| `output/models/loan_default_prediction_feature_importance.csv` | 12 | 4 | Original default model feature importance |
| `output/models/income_growth_prediction_feature_importance.csv` | 12 | 4 | Original income model feature importance |
| `output/models/embedded_finance_adoption_feature_importance.csv` | 12 | 4 | Original adoption model feature importance |
| `output/models_retrained/before_vs_after_metrics.csv` | 20 | 5 | First weak-model retraining comparison |
| `output/models_retrained/loan_default_prediction_feature_importance.csv` | 58 | 4 | First retrained default model feature importance |
| `output/models_retrained/embedded_finance_adoption_feature_importance.csv` | 58 | 4 | First retrained adoption model feature importance |
| `output/models_retrained_engineered/before_after_model_metrics.csv` | 20 | 5 | Engineered weak-model comparison |
| `output/models_retrained_engineered/loan_default_prediction_feature_importance.csv` | 78 | 4 | Engineered default model feature importance |
| `output/models_retrained_engineered/embedded_finance_adoption_feature_importance.csv` | 78 | 4 | Engineered adoption model feature importance |
| `output/models_retrained_engineered/engineered_feature_summary.csv` | 20 | 9 | Engineered feature distribution summary |

## Adoption Propensity Outputs

| File | Rows | Columns | Role |
|---|---:|---:|---|
| `output/adoption_propensity/adoption_propensity_roc_comparison.csv` | 3 | 2 | ROC comparison: original, leaky retrain, safe propensity model |
| `output/adoption_propensity/embedded_finance_adoption_propensity_feature_importance.csv` | 36 | 3 | Leakage-safe adoption propensity feature importance |
| `output/adoption_propensity/embedded_finance_adoption_propensity_correlations.csv` | 36 | 3 | Adoption propensity feature-target correlations |

## Default Model Outputs

| File | Rows | Columns | Role |
|---|---:|---:|---|
| `output/default_model_improved/default_before_after_metrics.csv` | 10 | 5 | Leaky/monitoring default model before-after metrics |
| `output/default_model_improved/default_feature_importance.csv` | 61 | 3 | Leaky/monitoring default model feature importance |
| `output/default_model_improved/default_feature_correlations.csv` | 61 | 3 | Leaky/monitoring default model feature-target correlations |
| `output/default_model_safe/default_revision_metric_history.csv` | 3 | 5 | Old, leaky, and leakage-safe default model metric history |
| `output/default_model_safe/default_safe_metrics.csv` | 1 | 10 | Final leakage-safe default model metrics |
| `output/default_model_safe/default_safe_feature_importance.csv` | 60 | 3 | Final leakage-safe default model feature importance |
| `output/default_model_safe/default_safe_feature_correlations.csv` | 60 | 3 | Final leakage-safe default model feature-target correlations |

## Smoke-Test CSVs

These are small development/test outputs, not final dissertation data.

| Folder | Files |
|---|---|
| `output/step3_smoke/` | `merchants.csv`, `transactions.csv`, `payouts_loans.csv`, `provider_kpis.csv` |
| `output/delta_smoke/` | `merchants.csv`, `transactions.csv`, `payouts_loans.csv`, `provider_kpis.csv`, `provenance.csv` |

## Model Artifacts (`.pkl`)

| File | Model type/purpose | Status |
|---|---|---|
| `output/models/churn_prediction.pkl` | Original churn prediction model | Original |
| `output/models/loan_default_prediction.pkl` | Original loan default prediction model | Original |
| `output/models/income_growth_prediction.pkl` | Original income growth prediction model | Original |
| `output/models/embedded_finance_adoption.pkl` | Original embedded finance adoption model | Original |
| `output/models_retrained/loan_default_prediction.pkl` | First weak-model default retrain | Superseded |
| `output/models_retrained/embedded_finance_adoption.pkl` | First weak-model adoption retrain | Superseded |
| `output/models_retrained_engineered/loan_default_prediction.pkl` | Engineered default retrain | Leaky/monitoring interpretation only |
| `output/models_retrained_engineered/embedded_finance_adoption.pkl` | Engineered adoption retrain | Leaky; do not use for final propensity |
| `output/adoption_propensity/embedded_finance_adoption_propensity.pkl` | Leakage-safe pre-intervention adoption propensity model | Preferred adoption model |
| `output/default_model_improved/loan_default_prediction_improved.pkl` | Default monitoring model with repayment-derived fields | Leaky for origination; monitoring only |
| `output/default_model_safe/loan_default_prediction_leakage_safe.pkl` | Leakage-safe default model using pre-default features | Preferred default model |

## Files Containing Predictions Or Prediction-Like Outputs

Strictly speaking, the project currently stores model artifacts and aggregate metrics, not row-level prediction-score exports for every provider/month. The following files contain prediction-like targets, model outputs, probabilities, thresholds, or risk summaries:

| File | Prediction/probability content |
|---|---|
| `data/provider_kpis.csv` | `churn_probability` synthetic modeled churn probability |
| `data/model_ready/provider_month_future_targets.csv` | future targets: `churn_target_tplus1`, `income_growth_tplus1`, `default_next_cycle` |
| `output/default_threshold_tuning.csv` | threshold-level precision, recall, F1/F2, predicted positive rate |
| `output/default_risk_segmentation.csv` | risk bands with mean/median/min/max predicted default probability |
| `output/default_score_quantiles.csv` | predicted default score/probability quantiles |
| `output/default_model_safe/default_safe_metrics.csv` | final default model threshold and classification metrics |
| `output/default_model_safe/default_revision_metric_history.csv` | ROC/precision/recall by default model version |
| `output/adoption_propensity/adoption_propensity_roc_comparison.csv` | adoption model ROC comparison |
| `output/models/model_metrics.csv` | original model performance metrics |
| `output/before_after_model_metrics.csv` | weak-model before/after metrics |

## Files Containing Probabilities

| File | Probability fields |
|---|---|
| `data/provider_kpis.csv` | `churn_probability` |
| `data/model_ready/provider_month_future_targets.csv` | `churn_probability` and future binary targets |
| `output/default_risk_segmentation.csv` | `mean_probability`, `median_probability`, `min_probability`, `max_probability` |
| `output/default_score_quantiles.csv` | `score` probability quantiles |
| `output/default_threshold_tuning.csv` | `positive_rate`, `predicted_positive_rate`, ROC/threshold metrics |

## Files Containing Risk Bands

| File | Risk-band content |
|---|---|
| `output/default_risk_segmentation.csv` | `risk_band`, cases, defaults, default rates, probability range summaries |
| `output/default_risk_segmentation.md` | Markdown interpretation of low/medium/high default risk bands |

## Churn Outputs

| File | Churn content |
|---|---|
| `data/provider_kpis.csv` | `retention_flag`, `churn_probability` |
| `data/model_ready/provider_month_lagged.csv` | lagged provider-month features with `churn_probability` |
| `data/model_ready/provider_month_future_targets.csv` | `churn_target_tplus1`, `retention_flag_tplus1`, `churn_probability` |
| `output/models/churn_prediction.pkl` | original churn model artifact |
| `output/models/churn_prediction_feature_importance.csv` | original churn model feature importance |
| `output/models/model_metrics.csv` | original churn metrics |
| `output/feature_importance.csv` | combined feature importance including churn rows |

No final retrained churn model was created after the leakage/future-target redesign. This matches the user instruction not to retrain churn yet.

## Default Outputs

| File | Default content |
|---|---|
| `data/payouts_loans.csv` | actual/synthetic `default_flag` by provider-month |
| `data/model_ready/provider_month_future_targets.csv` | `default_flag`, `default_next_cycle`, lagged credit features |
| `output/models/loan_default_prediction.pkl` | original default model artifact |
| `output/models/loan_default_prediction_feature_importance.csv` | original default model feature importance |
| `output/models_retrained/loan_default_prediction.pkl` | first weak-model default retrain artifact |
| `output/models_retrained/loan_default_prediction_feature_importance.csv` | first retrained default feature importance |
| `output/models_retrained_engineered/loan_default_prediction.pkl` | engineered default model artifact |
| `output/models_retrained_engineered/loan_default_prediction_feature_importance.csv` | engineered default feature importance |
| `output/default_model_improved/loan_default_prediction_improved.pkl` | improved default monitoring model artifact |
| `output/default_model_improved/default_before_after_metrics.csv` | improved default model metric comparison |
| `output/default_model_improved/default_feature_importance.csv` | improved default feature importance |
| `output/default_model_improved/default_feature_correlations.csv` | improved default feature-target correlations |
| `output/default_model_safe/loan_default_prediction_leakage_safe.pkl` | preferred leakage-safe default model artifact |
| `output/default_model_safe/default_safe_metrics.csv` | preferred default model metrics |
| `output/default_model_safe/default_safe_feature_importance.csv` | preferred default model feature importance |
| `output/default_model_safe/default_safe_feature_correlations.csv` | preferred default feature-target correlations |
| `output/default_model_safe/default_revision_metric_history.csv` | old vs leaky vs safe default model metric history |
| `output/default_threshold_tuning.csv` | threshold tuning for leakage-safe default model |
| `output/default_risk_segmentation.csv` | probability-based default risk bands |

Preferred final default artifact:

```text
output/default_model_safe/loan_default_prediction_leakage_safe.pkl
```

Preferred final default reporting files:

```text
output/default_model_revision_history.md
output/default_threshold_tuning.md
output/default_risk_segmentation.md
```

## Adoption Outputs

| File | Adoption content |
|---|---|
| `data/merchants.csv` | `treatment_flag`, `treatment_start_month`, `intervention_timestamp` |
| `data/provider_kpis.csv` | `treatment_flag`, `post_treatment_flag` |
| `data/model_ready/provider_month_future_targets.csv` | `treatment_flag`, `post_treatment_flag`, `months_since_intervention`, `pre_treatment_flag` |
| `output/models/embedded_finance_adoption.pkl` | original adoption model artifact |
| `output/models/embedded_finance_adoption_feature_importance.csv` | original adoption feature importance |
| `output/models_retrained/embedded_finance_adoption.pkl` | first retrained adoption model |
| `output/models_retrained/embedded_finance_adoption_feature_importance.csv` | first retrained adoption importance |
| `output/models_retrained_engineered/embedded_finance_adoption.pkl` | engineered adoption model; leakage-audited |
| `output/models_retrained_engineered/embedded_finance_adoption_feature_importance.csv` | engineered adoption importance |
| `output/adoption_feature_correlations.csv` | adoption feature-target correlations from leakage audit |
| `output/adoption_propensity/embedded_finance_adoption_propensity.pkl` | preferred pre-intervention adoption propensity artifact |
| `output/adoption_propensity/embedded_finance_adoption_propensity_feature_importance.csv` | safe propensity model importance |
| `output/adoption_propensity/embedded_finance_adoption_propensity_correlations.csv` | safe propensity model correlations |
| `output/adoption_propensity/adoption_propensity_roc_comparison.csv` | original vs leaky vs safe adoption ROC |

Preferred final adoption artifact:

```text
output/adoption_propensity/embedded_finance_adoption_propensity.pkl
```

Preferred final adoption reporting files:

```text
output/adoption_model_audit.md
output/adoption_propensity_report.md
```

## Income Growth Outputs

| File | Income-growth content |
|---|---|
| `data/provider_kpis.csv` | `income_growth_pct`, `monthly_profit`, `advancement_score` |
| `data/model_ready/provider_month_future_targets.csv` | `income_growth_tplus1`, `income_growth_pct_lag1` |
| `output/models/income_growth_prediction.pkl` | original income growth model artifact |
| `output/models/income_growth_prediction_feature_importance.csv` | original income growth model feature importance |
| `output/models/model_metrics.csv` | original income growth metrics |

No final retrained income model was created after the leakage/future-target redesign.

## Recommended Files For Final Dissertation Dashboard

Use these primary/final files for Power BI and dissertation reporting:

```text
data/merchants.csv
data/transactions.csv
data/payouts_loans.csv
data/provider_kpis.csv
data/model_ready/provider_month_future_targets.csv
data/primary_responses_clean.csv
data/primary_interview_quotes.csv
data/provenance.csv
docs/primary_secondary_mapping.csv
output/agreement_scores.csv
output/adoption_propensity/adoption_propensity_roc_comparison.csv
output/adoption_propensity/embedded_finance_adoption_propensity_feature_importance.csv
output/default_model_safe/default_revision_metric_history.csv
output/default_model_safe/default_safe_metrics.csv
output/default_model_safe/default_safe_feature_importance.csv
output/default_threshold_tuning.csv
output/default_risk_segmentation.csv
output/default_score_quantiles.csv
```

Avoid using these as final performance evidence:

```text
output/models_retrained_engineered/embedded_finance_adoption.pkl
output/models_retrained_engineered/embedded_finance_adoption_feature_importance.csv
output/default_model_improved/loan_default_prediction_improved.pkl
```

Reason:

- engineered adoption retrain is dominated by rollout/treatment leakage;
- improved default model is valid mainly as monitoring/collections risk, not origination;
- final adoption and default reporting should use leakage-audited safe versions.
