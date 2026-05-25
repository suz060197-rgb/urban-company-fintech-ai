# Default Model Improvement Report

Generated on 2026-05-22.

## Objective

Retrain only the loan default model to improve prediction of actual defaults using class weighting, threshold tuning, lagged variables, and default-specific engineered features.

## Target And Data

- Target: `default_flag` actual same-cycle loan default outcome.
- Training rows after active-month filter: `10853`.
- Excluded direct status leakage such as `loan_status`.

## Engineered Features Added

- `prior_default_count`
- `prior_default_flag`
- `loan_to_payout_ratio`
- `loan_to_income_ratio`
- `repayment_ratio`
- `repayment_gap_ratio`
- `digital_readiness`
- `credit_dependency_score`
- `liquidity_stress_index`

## Old Vs New Metrics

| metric | before | after | delta |
| --- | --- | --- | --- |
| accuracy | 0.873 | 0.927 | 0.055 |
| precision | 0.109 | 0.065 | -0.043 |
| recall | 0.227 | 0.542 | 0.314 |
| roc_auc | 0.683 | 0.937 | 0.254 |
| threshold | 0.130 | 0.800 | 0.670 |
| positive_rate | 0.048 | 0.009 | -0.039 |
| tp | 5.000 | 13.000 | 8.000 |
| tn | 393.000 | 2504.000 | 2111.000 |
| fp | 41.000 | 186.000 | 145.000 |
| fn | 17.000 | 11.000 | -6.000 |

## Top Predictors

| feature | coefficient | importance |
| --- | --- | --- |
| repayment_gap_ratio | 1.067 | 1.067 |
| repayment_ratio | 0.653 | 0.653 |
| loan_to_income_ratio | 0.309 | 0.309 |
| loan_to_payout_ratio | 0.284 | 0.284 |
| cancellation_rate_rolling3 | -0.257 | 0.257 |
| city_Bhubaneswar | -0.253 | 0.253 |
| monthly_income | -0.253 | 0.253 |
| payout_delay_days_rolling3 | 0.236 | 0.236 |
| city_Pune | -0.230 | 0.230 |
| forecast_usage_lag1 | 0.210 | 0.210 |
| city_Chandigarh | -0.197 | 0.197 |
| avg_ticket | -0.192 | 0.192 |
| income_growth_pct_lag1 | -0.176 | 0.176 |
| city_Hyderabad | 0.174 | 0.174 |
| city_Mumbai | 0.170 | 0.170 |
| liquidity_stress_index | 0.169 | 0.169 |
| category_appliance_repair | -0.158 | 0.158 |
| city_Delhi NCR | 0.148 | 0.148 |
| platform_commission_pct | 0.132 | 0.132 |
| digital_tool_usage | -0.132 | 0.132 |

## Feature Correlations With Default Target

| feature | correlation_with_target | abs_correlation |
| --- | --- | --- |
| loan_to_payout_ratio | 0.196 | 0.196 |
| loan_to_income_ratio | 0.191 | 0.191 |
| repayment_gap_ratio | 0.182 | 0.182 |
| repayment_ratio | 0.109 | 0.109 |
| liquidity_stress_index | 0.038 | 0.038 |
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
| credit_dependency_score | -0.014 | 0.014 |
| lock_in_score_lag1 | 0.013 | 0.013 |
| forecast_usage_lag1 | 0.013 | 0.013 |
| agent_usage_flag | 0.012 | 0.012 |

## Commentary

- Old ROC AUC: `0.683`.
- New ROC AUC: `0.937`.
- Old recall: `0.227`.
- New recall: `0.542`.

This model is optimized with an F2 threshold, so it intentionally favors recall over precision. That is usually preferable for default-risk screening, where missing a true default can be more costly than flagging extra risk cases.

If ROC or precision remains weak, the limitation is likely structural: the synthetic generator contains limited separability in default outcomes. The next improvement should be generator-side calibration of default risk drivers rather than more complex modeling.