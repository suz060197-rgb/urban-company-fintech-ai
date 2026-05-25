# Leakage Audit

Scope: saved models in `output/models/`. No retraining was performed.

## Summary

The saved models are useful as explanatory baseline models, but several are not yet clean forecasting models. The highest leakage risk is in `income_growth_prediction`, followed by `churn_prediction` and `loan_default_prediction`. `embedded_finance_adoption` is mostly safe if interpreted as treatment assignment propensity, but it still includes some features that may be post-assignment adoption proxies.

## Churn Prediction

Target: `churn_target`, derived from same-month `retention_flag`.

Leakage risks:

- `payout_delay_days`: current-month payout outcome; unavailable before the month closes.
- `loan_offer_flag`, `loan_amount`, `repayment_amount`, `loan_disbursal_time`, `loan_status_*`: current-month credit outcomes.
- `working_capital_gap`: current-month engineered liquidity outcome.
- `post_treatment_flag`: safe only if predicting after rollout schedule is known; risky if predicting pre-period churn without known intervention timing.
- `forecast_usage`, `technology_adoption_score`, `agentic_intelligence_score`: may be same-period behavioral/composite features.

Recommended lagged replacements:

- `payout_delay_days_lag1`, `payout_delay_days_rolling3`
- `working_capital_gap_lag1`, `working_capital_gap_rolling3`
- `loan_offer_flag_lag1`, `prior_loan_default_flag`, `prior_loan_status`
- `forecast_usage_lag1`
- `technology_adoption_score_lag1`, `agentic_intelligence_score_lag1`
- Known-at-start fields: `treatment_flag`, `intervention_timestamp`, `tenure_days`, `category`, `city`, baseline `monthly_income`

Recommendation: retrain as next-month churn: predict `retention_flag` in month `t+1` from features observed through month `t`.

## Loan Default Prediction

Target: `default_flag` in the same provider-month.

Leakage risks:

- `repayment_amount`: post-outcome repayment realization and direct leakage.
- `loan_status_*` was excluded from this model, which is good.
- `payout_amount`, `payout_delay_days`, `working_capital_gap`: current-month outcomes; safe only if measured before credit decision.
- `lock_in_score`, `advancement_score`, `agentic_intelligence_score`: same-period composites and should be lagged.
- `post_treatment_flag`: acceptable if treatment state is known at loan offer time.

Recommended lagged or origination-time replacements:

- `loan_amount_at_origination`
- `loan_to_payout_ratio_lag1`
- `working_capital_gap_lag1`
- `payout_amount_lag1`, `payout_volatility_rolling3`
- `prior_default_count`, `prior_repayment_ratio`
- `digital_tool_usage_baseline`, `payment_success_rate_baseline`
- Exclude `repayment_amount` and any realized `loan_status`.

Recommendation: train only on accepted/disbursed loans, and predict default using features known at disbursal.

## Income Growth Prediction

Target: same-month `income_growth_pct`.

High leakage risks:

- `payout_amount`: direct leakage because income growth is mechanically derived from payout relative to baseline.
- `active_provider_month_flag`: post-outcome inactivity signal.
- `lock_in_score`: composite partly reflects retention and same-period outcomes.
- `working_capital_gap`, `loan_offer_flag`, `loan_amount`, `repayment_amount`, `loan_status_*`: same-month financing and payout outcomes.
- `post_treatment_flag`: valid as an intervention indicator, but current-month treatment effects should be modeled carefully.

Recommended lagged replacements:

- `payout_amount_lag1`, not current payout
- `income_growth_pct_lag1`
- `active_provider_month_flag_lag1`
- `working_capital_gap_lag1`
- `loan_amount_lag1`, `loan_offer_flag_lag1`
- `lock_in_score_lag1`, `technology_adoption_score_lag1`
- Treatment event-study features: `months_since_intervention`, `post_treatment_flag`

Recommendation: predict next-month `income_growth_pct` using prior-month features, or estimate treatment effects using DiD rather than same-month supervised prediction.

## Embedded Finance Adoption

Target: `adoption_target`, derived from `treatment_flag`.

Leakage risks:

- `multi_product_adoption`: may include embedded-finance product adoption and can leak treatment status.
- `agent_usage_flag`, `ai_adoption_score`, `digital_tool_usage`: safe only if measured before treatment assignment.
- City/category variables are intentional rollout drivers, not leakage, if predicting assignment propensity.

Recommended replacements:

- Use baseline-only variables measured before rollout: KYC, city, region, category, tenure, baseline income, baseline repeat rate.
- Replace `multi_product_adoption` with `pre_rollout_product_count`.
- Replace `agent_usage_flag` with `pre_rollout_agent_readiness_flag` if needed.

Recommendation: keep this model as a propensity/eligibility model, not a causal outcome model.

## Overall Leakage Rating

- Churn prediction: medium-high leakage risk.
- Loan default prediction: high leakage risk due to `repayment_amount`.
- Income growth prediction: very high leakage risk due to `payout_amount`.
- Embedded finance adoption: medium leakage risk, mostly from post-adoption product variables.

## Next Safe Modeling Design

Create a lagged provider-month training table:

- For each provider-month `t`, compute features from months `<= t`.
- Predict outcomes in month `t+1`.
- Preserve baseline merchant features separately.
- Add rolling 3-month features for payout, settlement, cancellation, working-capital gap, and ratings.
- Keep intervention timing as known schedule data: `intervention_timestamp`, `months_since_intervention`, `post_treatment_flag`.
