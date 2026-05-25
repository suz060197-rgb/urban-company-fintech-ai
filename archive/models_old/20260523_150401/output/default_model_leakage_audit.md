# Default Model Leakage Audit

Generated on 2026-05-22.

## Summary

- Audited model: `output/default_model_improved/loan_default_prediction_improved.pkl`
- Target: `default_flag` actual same-cycle default outcome.
- Improved model ROC AUC: `0.937` versus old ROC AUC `0.683`.
- Improved model recall: `0.542` versus old recall `0.227`.
- Origination-time leakage risk rating: `High`.

The improved model is useful as an ongoing default-monitoring model, but it is not fully valid as a loan-origination scorecard. The strongest predictors are repayment-derived fields, especially `repayment_gap_ratio` and `repayment_ratio`, which would not be known before or at loan origination.

## Feature Leakage Ratings

| feature | leakage_rating | coefficient | importance | correlation_with_target | rationale |
| --- | --- | --- | --- | --- | --- |
| repayment_ratio | Critical | 0.653 | 0.653 | 0.109 | Not available at loan origination; depends on repayment behavior that occurs after loan disbursal and close to default outcome. |
| repayment_gap_ratio | Critical | 1.067 | 1.067 | 0.182 | Derived from repayment ratio and current loan amount; directly reflects repayment shortfall after origination. |
| prior_default_count | Low | -0.040 | 0.040 | -0.001 | Valid at origination if based only on historical defaults before the current loan/month. |
| prior_default_flag | Low | -0.007 | 0.007 | -0.001 | Valid at origination if based only on historical default count before the current loan/month. |
| credit_dependency_score | Low-Medium | -0.074 | 0.074 | -0.014 | Mostly lagged/ex-ante stress signal if built from lagged loan amount, lagged gap, lagged delay, and rolling volatility. |
| loan_to_payout_ratio | Medium-High | 0.284 | 0.284 | 0.196 | Uses same-cycle loan amount and payout amount; may be known only after payout cycle, not necessarily at origination. |
| loan_to_income_ratio | Medium | 0.309 | 0.309 | 0.191 | Loan amount may be known at origination and income baseline is known; acceptable if loan amount is requested/approved amount before disbursal. |
| payout_volatility_rolling3 | Low | -0.074 | 0.074 | -0.004 | Valid if computed from prior rolling payout history only. |
| working_capital_gap_lag1 | Low | -0.072 | 0.072 | -0.006 | Valid because it is explicitly lagged one provider-month. |
| digital_readiness | Low | -0.074 | 0.074 | 0.005 | Baseline/provider readiness feature available before loan origination. |

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

## Correlation With Default Target

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

## Origination-Time Assessment

### High-Risk Or Invalid At Origination

- `repayment_ratio`: repayment behavior is observed after loan disbursal and therefore leaks post-origination information.
- `repayment_gap_ratio`: even stronger leakage because it encodes unpaid or underpaid loan exposure.
- `loan_to_payout_ratio`: borderline-to-high risk if it uses current-cycle payout amount that is not finalized at origination. For an origination model, replace with `loan_amount / payout_amount_lag1` or `requested_loan_amount / avg_prior_payout_3m`.

### Acceptable At Origination If Strictly Historical

- `prior_default_count`: acceptable because it uses only defaults before the current row.
- `prior_default_flag`: acceptable for the same reason.
- `working_capital_gap_lag1`: acceptable because it is lagged.
- `payout_volatility_rolling3`: acceptable if the rolling window excludes current-month payout.
- `credit_dependency_score`: acceptable only if all components are lagged or known before loan decisioning.
- `digital_readiness`: acceptable as a baseline/provider readiness feature.

## Why Performance Improved

The model improved mainly because it introduced features close to the repayment/default mechanism:

- `repayment_gap_ratio` is the top predictor by coefficient importance (`1.067`).
- `repayment_ratio` is the second strongest predictor (`0.653`).
- `loan_to_income_ratio` and `loan_to_payout_ratio` capture loan burden relative to provider capacity.

These features are valid for monitoring default risk during the loan cycle, but `repayment_ratio` and `repayment_gap_ratio` should be removed for true pre-origination prediction.

## Recommendation

For a clean loan-origination model, retrain later after removing:

- `repayment_ratio`
- `repayment_gap_ratio`
- any same-cycle `repayment_amount`-derived feature
- same-cycle `payout_amount` in `loan_to_payout_ratio`, unless payout is already known at decision time

Use these safer replacements:

- `prior_default_count`
- `prior_default_flag`
- `loan_amount_lag1` or requested loan amount if available before disbursal
- `loan_amount / payout_amount_lag1`
- `loan_amount / rolling3_prior_payout_mean`
- `working_capital_gap_lag1`
- `payout_volatility_rolling3` computed from prior months only
- `digital_readiness`
- `credit_dependency_score` built only from lagged components

Final judgment: retain the improved model only as a default monitoring or collections-risk model. Do not present it as a pure origination scorecard without removing repayment-derived features.