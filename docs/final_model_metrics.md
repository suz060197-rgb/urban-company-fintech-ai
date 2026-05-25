# Final Model Metrics

Generated on 2026-05-23.

Models were retrained on the extended `data_v2` panel using leakage-safe month-t predictors and t+1 targets.

## Outputs

- Models: `output/models_final/`
- Predictions: `output/predictions_final/`
- Risk scores: `output/risk_scores.csv`

## Leakage Controls

- Used baseline provider fields plus lagged/rolling provider-month fields.
- Excluded same-period outcomes such as `retention_flag`, `income_growth_pct`, `monthly_profit`, `default_flag`, current payout/loan amount fields, and repayment fields.
- Excluded treatment rollout timing fields from predictors, including `treatment_flag`, `post_treatment_flag`, `treatment_start_month`, `intervention_timestamp`, and `months_since_intervention`.
- Evaluation uses a temporal split: the latest six feature months are test rows.

## Metrics

| model | target | split | metric | value |
|---|---|---|---|---:|
| churn_prediction | churn_target_tplus1 | test | accuracy | 0.9777 |
| churn_prediction | churn_target_tplus1 | test | precision | 1.0000 |
| churn_prediction | churn_target_tplus1 | test | recall | 0.9267 |
| churn_prediction | churn_target_tplus1 | test | f1 | 0.9619 |
| churn_prediction | churn_target_tplus1 | test | roc_auc | 0.9672 |
| churn_prediction | churn_target_tplus1 | test | threshold | 0.7000 |
| churn_prediction | churn_target_tplus1 | test | positive_rate | 0.3045 |
| churn_prediction | churn_target_tplus1 | test | tp | 1693.0000 |
| churn_prediction | churn_target_tplus1 | test | tn | 4173.0000 |
| churn_prediction | churn_target_tplus1 | test | fp | 0.0000 |
| churn_prediction | churn_target_tplus1 | test | fn | 134.0000 |
| loan_default_prediction | default_next_cycle | test | accuracy | 0.7840 |
| loan_default_prediction | default_next_cycle | test | precision | 0.0093 |
| loan_default_prediction | default_next_cycle | test | recall | 0.4138 |
| loan_default_prediction | default_next_cycle | test | f1 | 0.0182 |
| loan_default_prediction | default_next_cycle | test | roc_auc | 0.7061 |
| loan_default_prediction | default_next_cycle | test | threshold | 0.6600 |
| loan_default_prediction | default_next_cycle | test | positive_rate | 0.0048 |
| loan_default_prediction | default_next_cycle | test | tp | 12.0000 |
| loan_default_prediction | default_next_cycle | test | tn | 4692.0000 |
| loan_default_prediction | default_next_cycle | test | fp | 1279.0000 |
| loan_default_prediction | default_next_cycle | test | fn | 17.0000 |
| embedded_finance_adoption | embedded_finance_adoption_tplus1 | test | accuracy | 0.5680 |
| embedded_finance_adoption | embedded_finance_adoption_tplus1 | test | precision | 0.5159 |
| embedded_finance_adoption | embedded_finance_adoption_tplus1 | test | recall | 0.8553 |
| embedded_finance_adoption | embedded_finance_adoption_tplus1 | test | f1 | 0.6436 |
| embedded_finance_adoption | embedded_finance_adoption_tplus1 | test | roc_auc | 0.6120 |
| embedded_finance_adoption | embedded_finance_adoption_tplus1 | test | threshold | 0.4000 |
| embedded_finance_adoption | embedded_finance_adoption_tplus1 | test | positive_rate | 0.4560 |
| embedded_finance_adoption | embedded_finance_adoption_tplus1 | test | tp | 2340.0000 |
| embedded_finance_adoption | embedded_finance_adoption_tplus1 | test | tn | 1068.0000 |
| embedded_finance_adoption | embedded_finance_adoption_tplus1 | test | fp | 2196.0000 |
| embedded_finance_adoption | embedded_finance_adoption_tplus1 | test | fn | 396.0000 |
| income_growth_prediction | income_growth_tplus1 | test | rmse | 0.2094 |
| income_growth_prediction | income_growth_tplus1 | test | mae | 0.1382 |
| income_growth_prediction | income_growth_tplus1 | test | r2 | 0.8229 |
| income_growth_prediction | income_growth_tplus1 | test | directional_accuracy | 0.6705 |

## Feature Sets

### churn_prediction

- `tenure_days`
- `avg_ticket`
- `monthly_income`
- `repeat_customer_rate`
- `platform_commission_pct`
- `kyc_flag`
- `payment_success_rate`
- `transaction_velocity`
- `multi_product_adoption`
- `digital_tool_usage`
- `ai_adoption_score`
- `agent_usage_flag`
- `payout_delay_days_lag1_imputed`
- `working_capital_gap_lag1`
- `income_growth_pct_lag1`
- `forecast_usage_lag1`
- `technology_adoption_score_lag1`
- `agentic_intelligence_score_lag1`
- `loan_amount_lag1`
- `loan_offer_flag_lag1`
- `active_provider_month_flag_lag1`
- `lock_in_score_lag1`
- `payout_delay_days_rolling3`
- `working_capital_gap_rolling3`
- `payout_volatility_rolling3`
- `rating_rolling3`
- `cancellation_rate_rolling3`
- `region`
- `city`
- `category`

### loan_default_prediction

- `tenure_days`
- `avg_ticket`
- `monthly_income`
- `repeat_customer_rate`
- `platform_commission_pct`
- `kyc_flag`
- `payment_success_rate`
- `transaction_velocity`
- `multi_product_adoption`
- `digital_tool_usage`
- `ai_adoption_score`
- `agent_usage_flag`
- `payout_delay_days_lag1_imputed`
- `working_capital_gap_lag1`
- `income_growth_pct_lag1`
- `forecast_usage_lag1`
- `technology_adoption_score_lag1`
- `agentic_intelligence_score_lag1`
- `loan_amount_lag1`
- `loan_offer_flag_lag1`
- `active_provider_month_flag_lag1`
- `lock_in_score_lag1`
- `payout_delay_days_rolling3`
- `working_capital_gap_rolling3`
- `payout_volatility_rolling3`
- `rating_rolling3`
- `cancellation_rate_rolling3`
- `region`
- `city`
- `category`

### embedded_finance_adoption

- `tenure_days`
- `avg_ticket`
- `monthly_income`
- `repeat_customer_rate`
- `platform_commission_pct`
- `kyc_flag`
- `payment_success_rate`
- `transaction_velocity`
- `multi_product_adoption`
- `digital_tool_usage`
- `ai_adoption_score`
- `agent_usage_flag`
- `region`
- `city`
- `category`

### income_growth_prediction

- `tenure_days`
- `avg_ticket`
- `monthly_income`
- `repeat_customer_rate`
- `platform_commission_pct`
- `kyc_flag`
- `payment_success_rate`
- `transaction_velocity`
- `multi_product_adoption`
- `digital_tool_usage`
- `ai_adoption_score`
- `agent_usage_flag`
- `payout_delay_days_lag1_imputed`
- `working_capital_gap_lag1`
- `income_growth_pct_lag1`
- `forecast_usage_lag1`
- `technology_adoption_score_lag1`
- `agentic_intelligence_score_lag1`
- `loan_amount_lag1`
- `loan_offer_flag_lag1`
- `active_provider_month_flag_lag1`
- `lock_in_score_lag1`
- `payout_delay_days_rolling3`
- `working_capital_gap_rolling3`
- `payout_volatility_rolling3`
- `rating_rolling3`
- `cancellation_rate_rolling3`
- `region`
- `city`
- `category`

## Archived Previous Models

| source | destination |
|---|---|
| `output/models_final/churn_prediction.pkl` | `archive/old_models/pre_final_v2_20260523_145544/output/models_final/churn_prediction.pkl` |
| `output/models_final/churn_prediction_feature_importance.csv` | `archive/old_models/pre_final_v2_20260523_145544/output/models_final/churn_prediction_feature_importance.csv` |
| `output/models_final/embedded_finance_adoption.pkl` | `archive/old_models/pre_final_v2_20260523_145544/output/models_final/embedded_finance_adoption.pkl` |
| `output/models_final/embedded_finance_adoption_feature_importance.csv` | `archive/old_models/pre_final_v2_20260523_145544/output/models_final/embedded_finance_adoption_feature_importance.csv` |
| `output/models_final/final_model_metrics.csv` | `archive/old_models/pre_final_v2_20260523_145544/output/models_final/final_model_metrics.csv` |
| `output/models_final/income_growth_prediction.pkl` | `archive/old_models/pre_final_v2_20260523_145544/output/models_final/income_growth_prediction.pkl` |
| `output/models_final/income_growth_prediction_feature_importance.csv` | `archive/old_models/pre_final_v2_20260523_145544/output/models_final/income_growth_prediction_feature_importance.csv` |
| `output/models_final/loan_default_prediction.pkl` | `archive/old_models/pre_final_v2_20260523_145544/output/models_final/loan_default_prediction.pkl` |
| `output/models_final/loan_default_prediction_feature_importance.csv` | `archive/old_models/pre_final_v2_20260523_145544/output/models_final/loan_default_prediction_feature_importance.csv` |
| `output/predictions_final/churn_prediction_predictions.csv` | `archive/old_models/pre_final_v2_20260523_145544/output/predictions_final/churn_prediction_predictions.csv` |
| `output/predictions_final/embedded_finance_adoption_predictions.csv` | `archive/old_models/pre_final_v2_20260523_145544/output/predictions_final/embedded_finance_adoption_predictions.csv` |
| `output/predictions_final/income_growth_prediction_predictions.csv` | `archive/old_models/pre_final_v2_20260523_145544/output/predictions_final/income_growth_prediction_predictions.csv` |
| `output/predictions_final/loan_default_prediction_predictions.csv` | `archive/old_models/pre_final_v2_20260523_145544/output/predictions_final/loan_default_prediction_predictions.csv` |
| `output/risk_scores.csv` | `archive/old_models/pre_final_v2_20260523_145544/output/risk_scores.csv` |