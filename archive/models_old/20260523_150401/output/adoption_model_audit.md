# Embedded Finance Adoption Model Audit

Generated on 2026-05-22.

## Summary

- Audited model: `output/models_retrained_engineered/embedded_finance_adoption.pkl`
- Reported ROC AUC: `0.999`
- Reported accuracy: `0.980`
- Target: `adoption_state_tplus1`, a one-period-ahead version of `post_treatment_flag`
- Leakage risk rating: `Critical`

The ROC AUC near `0.999` is primarily explained by target leakage from treatment timing variables. The model includes current-period and assignment-derived fields that almost directly determine whether the next period is post-treatment. This makes the model excellent at reconstructing the rollout schedule, but not credible as a behavioral adoption propensity model.

## Top Predictors

| feature | coefficient | importance | leakage_category |
| --- | --- | --- | --- |
| treatment_flag | 1.550 | 1.550 | Direct/derived treatment timing leakage |
| post_treatment_flag | 1.517 | 1.517 | Direct/derived treatment timing leakage |
| months_since_intervention | 1.340 | 1.340 | Direct/derived treatment timing leakage |
| treatment_start_month | 0.788 | 0.788 | Direct/derived treatment timing leakage |
| tenure_days | 0.284 | 0.284 | Lower leakage risk |
| pre_treatment_flag | 0.188 | 0.188 | Direct/derived treatment timing leakage |
| kyc_flag | 0.179 | 0.179 | Lower leakage risk |
| lock_in_score_lag1 | 0.172 | 0.172 | Lower leakage risk |
| payout_pain_gap | 0.130 | 0.130 | Lower leakage risk |
| category_plumbing_electrical | -0.129 | 0.129 | Potential rollout proxy |
| category_beauty_wellness | 0.119 | 0.119 | Potential rollout proxy |
| payout_delay_days_lag1_imputed | -0.102 | 0.102 | Lower leakage risk |
| category_appliance_repair | -0.101 | 0.101 | Potential rollout proxy |
| digital_finance_readiness | 0.096 | 0.096 | Lower leakage risk |
| lockin_resilience_score | 0.091 | 0.091 | Lower leakage risk |
| platform_commission_pct | 0.091 | 0.091 | Lower leakage risk |
| city_Chennai | 0.090 | 0.090 | Potential rollout proxy |
| city_Kochi | 0.089 | 0.089 | Potential rollout proxy |
| region_South | 0.089 | 0.089 | Potential rollout proxy |
| settlement_credit_stress | -0.088 | 0.088 | Lower leakage risk |

## Feature Correlations With Target

| feature | correlation_with_target | abs_correlation |
| --- | --- | --- |
| post_treatment_flag | 0.917 | 0.917 |
| treatment_flag | 0.817 | 0.817 |
| treatment_flag_merchant | 0.817 | 0.817 |
| months_since_intervention | 0.721 | 0.721 |
| treatment_start_month | 0.597 | 0.597 |
| payout_delay_days_rolling3 | -0.594 | 0.594 |
| payout_pain_gap | 0.386 | 0.386 |
| payout_delay_days_lag1_imputed | -0.384 | 0.384 |
| settlement_credit_stress | -0.381 | 0.381 |
| working_capital_gap_lag1 | -0.291 | 0.291 |
| working_capital_gap_rolling3 | -0.275 | 0.275 |
| lock_in_score_lag1 | 0.269 | 0.269 |
| rating_rolling3 | 0.267 | 0.267 |
| kyc_flag | 0.231 | 0.231 |
| lockin_resilience_score | 0.222 | 0.222 |
| repayment_pressure_index | -0.219 | 0.219 |
| credit_offer_mismatch | -0.217 | 0.217 |
| loan_amount_lag1 | 0.201 | 0.201 |
| loan_offer_flag_lag1 | 0.196 | 0.196 |
| digital_finance_readiness | 0.188 | 0.188 |
| digital_growth_index | 0.177 | 0.177 |
| credit_dependency_score | -0.138 | 0.138 |
| multi_product_adoption | 0.123 | 0.123 |
| payout_volatility_rolling3 | 0.109 | 0.109 |
| cancellation_rate_rolling3 | -0.106 | 0.106 |

## Direct Leakage Evidence

- `post_treatment_flag` correlation with target: `0.917`
- `treatment_flag` correlation with target: `0.817`
- `treatment_start_month` correlation with target: `0.597`

Current `post_treatment_flag` is especially problematic because once a provider is post-treatment in month `t`, the provider is always post-treatment in month `t+1`. For providers immediately before rollout, `pre_treatment_flag`, `months_since_intervention`, and `treatment_start_month` reveal when adoption will occur.

## Cross-Tab Checks

### Current Post-Treatment Flag Vs Future Adoption Target

| post_treatment_flag | False | True |
| --- | --- | --- |
| False | 0.943 | 0.057 |
| True | 0.000 | 1.000 |

### Treatment Assignment Vs Future Adoption Target

| treatment_flag | False | True |
| --- | --- | --- |
| 0.000 | 1.000 | 0.000 |
| 1.000 | 0.214 | 0.786 |

## Duplicate Or Treatment-Derived Feature Findings

- `treatment_flag` and `treatment_flag_merchant` duplicate the assignment concept.
- `post_treatment_flag` is same-period treatment state and is nearly the target shifted by one month.
- `months_since_intervention` is mechanically derived from intervention timing.
- `treatment_start_month` reveals the rollout month.
- `pre_treatment_flag` identifies providers immediately before treatment.
- `intervention_timestamp`, when encoded, would also reveal rollout timing.
- Region/category/city can become rollout proxies because phased rollout was structured across region, tenure, and category.

## Leakage Risk Rating

| Area | Rating | Reason |
|---|---|---|
| Target leakage | Critical | Current post-treatment and rollout timing fields mechanically determine future post-treatment state. |
| Duplicate features | High | Assignment appears as both `treatment_flag` and `treatment_flag_merchant`; timing appears in several derived forms. |
| Post-treatment variables | Critical | `post_treatment_flag` is included as a predictor for future post-treatment target. |
| Treatment-derived variables | Critical | `months_since_intervention`, `treatment_start_month`, and `pre_treatment_flag` encode intervention schedule. |
| Behavioral feature validity | Medium | Safer behavioral features exist, but they are dominated by leakage predictors. |

## Recommendation

Do not treat the `0.999` ROC AUC as valid evidence of predictive performance. For a credible embedded-finance adoption model, retrain later using a redesigned target and excluding:

- `post_treatment_flag`
- `treatment_flag` when predicting organic adoption propensity
- `treatment_flag_merchant`
- `treatment_start_month`
- `months_since_intervention`
- `pre_treatment_flag`
- `intervention_timestamp`

Safer predictors would include baseline and lagged readiness variables such as `kyc_flag`, `payment_success_rate`, `digital_tool_usage`, `transaction_velocity`, `multi_product_adoption`, `lock_in_score_lag1`, `technology_adoption_score_lag1`, `agentic_intelligence_score_lag1`, `digital_finance_readiness`, and `credit_dependency_score`.

A cleaner target would be either:

- adoption propensity among not-yet-treated eligible providers, excluding rollout schedule variables; or
- treatment uptake conditional on being offered embedded finance, using only pre-offer features.