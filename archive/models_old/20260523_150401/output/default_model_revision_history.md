# Default Model Revision History

Generated on 2026-05-22.

## Objective

Rebuild the loan default model using only information available before the default event.

## Leakage-Safe Changes

- Removed `repayment_ratio`.
- Removed `repayment_gap_ratio`.
- Redesigned `loan_to_payout_ratio` as `loan_to_prior_payout_ratio` and `loan_to_prior_payout_rolling3_ratio`.
- Kept `prior_default_count`, `credit_dependency_score`, `working_capital_gap_lag1`, `digital_readiness`, and `payout_volatility_rolling3`.
- Excluded `loan_status` and direct default labels from predictors.

## Data And Target

- Target: `default_flag` actual default outcome.
- Training rows after active provider-month filter: `10853`.
- Threshold tuning: F2 score, favoring recall for default-risk screening.

## Metric History

| model_version | roc_auc | precision | recall | notes |
| --- | --- | --- | --- | --- |
| old_baseline | 0.683 | 0.109 | 0.227 | Original default model. |
| leaky_monitoring_model | 0.937 | 0.065 | 0.542 | High leakage risk from repayment-derived features. |
| leakage_safe_revision | 0.926 | 0.054 | 0.583 | Repayment features removed; loan burden uses prior payout history. |

## Leakage-Safe Top Predictors

| feature | coefficient | importance |
| --- | --- | --- |
| loan_to_income_ratio | 1.293 | 1.293 |
| loan_to_prior_payout_ratio | 0.389 | 0.389 |
| cancellation_rate_rolling3 | -0.362 | 0.362 |
| city_Bhubaneswar | -0.303 | 0.303 |
| payout_delay_days_rolling3 | 0.264 | 0.264 |
| platform_commission_pct | 0.258 | 0.258 |
| city_Pune | -0.237 | 0.237 |
| monthly_income | -0.228 | 0.228 |
| forecast_usage_lag1 | 0.204 | 0.204 |
| avg_ticket | -0.201 | 0.201 |
| digital_tool_usage | -0.191 | 0.191 |
| city_Hyderabad | 0.190 | 0.190 |
| city_Mumbai | 0.187 | 0.187 |
| city_Chandigarh | -0.173 | 0.173 |
| working_capital_gap_rolling3 | -0.163 | 0.163 |
| category_appliance_repair | -0.153 | 0.153 |
| income_growth_pct_lag1 | -0.153 | 0.153 |
| technology_adoption_score_lag1 | -0.149 | 0.149 |
| city_Delhi NCR | 0.134 | 0.134 |
| lock_in_score_lag1 | -0.132 | 0.132 |

## Leakage-Safe Feature Correlations

| feature | correlation_with_target | abs_correlation |
| --- | --- | --- |
| loan_to_income_ratio | 0.191 | 0.191 |
| loan_to_prior_payout_ratio | 0.183 | 0.183 |
| loan_to_prior_payout_rolling3_ratio | 0.176 | 0.176 |
| liquidity_stress_index_safe | 0.031 | 0.031 |
| credit_dependency_score | 0.022 | 0.022 |
| city_Hyderabad | 0.022 | 0.022 |
| payout_delay_days_lag1_imputed | -0.018 | 0.018 |
| city_Ahmedabad | -0.018 | 0.018 |
| income_growth_pct_lag1 | -0.016 | 0.016 |
| cancellation_rate_rolling3 | -0.016 | 0.016 |
| city_Bhubaneswar | -0.016 | 0.016 |
| working_capital_gap_rolling3 | -0.015 | 0.015 |
| city_Patna | 0.015 | 0.015 |
| category_home_cleaning | 0.015 | 0.015 |
| city_Chandigarh | -0.015 | 0.015 |
| city_Delhi NCR | 0.015 | 0.015 |
| lock_in_score_lag1 | 0.013 | 0.013 |
| forecast_usage_lag1 | 0.013 | 0.013 |
| agent_usage_flag | 0.012 | 0.012 |
| multi_product_adoption | 0.012 | 0.012 |

## Interpretation

The leakage-safe ROC AUC is `0.926` versus the leaky model ROC AUC of `0.937` and old ROC AUC of `0.683`.

The revision gives up the inflated performance from repayment-derived features, but it is more appropriate for a pre-default or origination-style model. It can be used to discuss default risk before repayment outcomes are observed.

If stronger origination performance is required, the next step should be generator-side calibration of default risk drivers, especially stronger relationships between prior liquidity stress, loan burden, and later default.