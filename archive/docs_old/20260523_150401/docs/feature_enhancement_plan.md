# Feature Enhancement Plan

Generated on 2026-05-22.

## Purpose

This plan proposes engineered features for future model iterations. It is based on `output/primary_vs_synthetic_report.md`, especially the weaker or moderate agreement areas:

- Settlement pain: `0.595`, weak
- Credit need: `0.666`, moderate
- AI usage: `0.792`, moderate
- Retention: high numeric agreement, but only through an indirect repeat-customer proxy

No model retraining is performed in this step.

## Design Principles

- Prefer lagged provider-month features for prediction models.
- Keep primary survey fields separate from synthetic training rows unless creating calibration features or validation priors.
- Avoid using same-period outcomes when predicting future churn, loan default, income growth, or adoption.
- Convert all composite scores to bounded 0-1 variables where possible.
- Preserve interpretability so features can be explained in the dissertation.

## Recommended Features

| Feature | Primary target models | Formula concept | Source variables | Expected interpretation | Leakage note |
|---|---|---|---|---|---|
| `settlement_credit_stress` | loan default, retention | weighted average of payout delay, working-capital gap, cashflow pain, and credit need | `payout_delay_days_lag1`, `working_capital_gap_lag1`, `cashflow_issues_scaled`, `needed_business_credit_binary` | High values indicate providers facing both delayed settlement and financing pressure. | Use lagged synthetic fields and primary-calibrated weights only; do not use same-period default. |
| `digital_growth_index` | embedded finance adoption, retention, income growth | average of digital adoption, payment success, growth perception, and technology adoption | `digital_tool_usage`, `payment_success_rate`, `business_growth_after_digital_scaled`, `technology_adoption_score_lag1` | Captures whether digital behavior is associated with perceived and modeled advancement. | For predictive models, use lagged technology score and baseline merchant fields. |
| `credit_dependency_score` | loan default, embedded finance adoption | credit need multiplied by credit amount intensity and working-capital gap | `needed_business_credit_binary`, `approx_credit_amount_numeric_scaled`, `working_capital_gap_lag1`, `loan_amount_lag1` | Measures how dependent a provider is on external working capital. | Use prior-cycle loan amount only for model-ready training. |
| `payout_pain_gap` | retention, loan default | primary settlement pain minus scaled synthetic payout delay | `settlement_delay_impact_scaled`, `payout_delay_days_lag1` | Flags under-modeled pain where providers feel more stress than delay days alone imply. | For synthetic-only modeling, use this only as a calibration diagnostic, not row-level training input. |
| `credit_offer_mismatch` | embedded finance adoption, retention | primary credit need minus synthetic loan offer probability or flag | `needed_business_credit_binary`, `loan_offer_flag_lag1` | Identifies unmet credit demand. | Use lagged offer flag; do not use post-treatment loan outcomes. |
| `repayment_pressure_index` | loan default | working-capital gap plus credit dependency minus income/growth buffer | `working_capital_gap_lag1`, `loan_amount_lag1`, `income_growth_pct_lag1`, `monthly_income` | High values suggest repayment strain. | Strong candidate for loan default prediction if all inputs are lagged. |
| `digital_finance_readiness` | embedded finance adoption | payment success, UPI usage, KYC, digital tools, and AI usage | `payment_success_rate`, `kyc_flag`, `digital_tool_usage`, `upi_usage_frequency_scaled`, `ai_tool_usage_binary` | Measures provider readiness to adopt embedded finance. | Exclude `treatment_flag` if predicting adoption propensity before rollout. |
| `lockin_resilience_score` | retention | repeat-customer change, lock-in score, active status, digital tool use | `repeat_customer_change_scaled`, `lock_in_score_lag1`, `active_provider_month_flag_lag1`, `digital_tool_usage` | Captures retention resilience beyond simple active/inactive flags. | Use future `retention_flag` only as target, not as input. |
| `agentic_productivity_signal` | embedded finance adoption, retention | AI usage plus forecast usage plus digital growth | `ai_tool_usage_binary`, `forecast_usage_lag1`, `agentic_intelligence_score_lag1`, `business_growth_after_digital_scaled` | Captures whether AI/tool use is associated with operational maturity. | Use lagged forecast and agentic scores for predictive models. |
| `cash_to_digital_transition_score` | embedded finance adoption | UPI usage and digital adoption minus cash dependence | `uses_upi_flag`, `uses_cash_flag`, `upi_usage_frequency_scaled`, `digital_adoption_score_scaled` | Helps explain whether providers are transitioning from cash-heavy to digital finance. | Primary-only calibration feature unless linked to synthetic rows by segment. |

## Feature Details

### 1. `settlement_credit_stress`

Recommended bounded formula:

```text
settlement_credit_stress =
  0.35 * scaled(payout_delay_days_lag1)
+ 0.30 * scaled(working_capital_gap_lag1)
+ 0.20 * cashflow_issues_scaled
+ 0.15 * needed_business_credit_binary
```

Why it matters:

Settlement pain had the weakest agreement score in the validation report. This feature makes settlement stress more explicit by combining operational payout delay with provider-reported cashflow strain and credit need.

Best use:

- Loan default prediction
- Retention prediction
- Explaining why faster payouts may reduce churn

### 2. `digital_growth_index`

Recommended bounded formula:

```text
digital_growth_index =
  0.30 * digital_tool_usage
+ 0.25 * payment_success_rate
+ 0.25 * technology_adoption_score_lag1
+ 0.20 * business_growth_after_digital_scaled
```

Why it matters:

Digital adoption aligned well between primary and synthetic data. This makes it a strong feature family for adoption and advancement models.

Best use:

- Embedded finance adoption
- Income growth
- Retention

### 3. `credit_dependency_score`

Recommended bounded formula:

```text
credit_dependency_score =
  0.35 * needed_business_credit_binary
+ 0.30 * scaled(approx_credit_amount_numeric)
+ 0.25 * scaled(working_capital_gap_lag1)
+ 0.10 * scaled(loan_amount_lag1)
```

Why it matters:

Primary respondents reported much higher credit need than synthetic loan-offer rates. This feature captures unmet or latent demand rather than only observed loan offers.

Best use:

- Embedded finance adoption
- Loan default
- Loan offer propensity

### 4. `repayment_pressure_index`

Recommended synthetic-only formula:

```text
repayment_pressure_index =
  0.40 * scaled(working_capital_gap_lag1)
+ 0.30 * scaled(loan_amount_lag1)
+ 0.20 * scaled(payout_delay_days_lag1)
- 0.10 * scaled(income_growth_pct_lag1)
```

Why it matters:

The previous loan default model remained weak after retraining. This feature gives the model a more direct financial-stress signal while staying interpretable.

Best use:

- Loan default prediction

### 5. `digital_finance_readiness`

Recommended formula:

```text
digital_finance_readiness =
  0.25 * payment_success_rate
+ 0.20 * digital_tool_usage
+ 0.20 * kyc_flag
+ 0.20 * upi_usage_frequency_scaled
+ 0.15 * ai_tool_usage_binary
```

Why it matters:

Embedded finance adoption should depend not only on treatment assignment, but also on whether the provider is operationally ready to use digital finance products.

Best use:

- Embedded finance adoption
- Multi-product adoption

### 6. `lockin_resilience_score`

Recommended formula:

```text
lockin_resilience_score =
  0.30 * lock_in_score_lag1
+ 0.25 * repeat_customer_change_scaled
+ 0.20 * active_provider_month_flag_lag1
+ 0.15 * digital_tool_usage
+ 0.10 * payment_success_rate
```

Why it matters:

Retention was validated only indirectly because the primary survey lacks an explicit retention-intent question. This feature treats retention as a resilience construct rather than a single flag.

Best use:

- Retention prediction
- Churn-risk segmentation

## Model-Specific Recommendations

### Loan Default

Prioritize these features:

- `settlement_credit_stress`
- `credit_dependency_score`
- `repayment_pressure_index`
- `payout_pain_gap`
- `working_capital_gap_lag1`
- `loan_amount_lag1`
- `payout_delay_days_rolling3`
- `income_growth_pct_lag1`

Rationale:

The default model needs sharper financial-stress signals. The strongest candidates combine liquidity pressure, payout delay, credit dependence, and income buffer.

### Embedded Finance Adoption

Prioritize these features:

- `digital_finance_readiness`
- `digital_growth_index`
- `cash_to_digital_transition_score`
- `credit_dependency_score`
- `agentic_productivity_signal`
- `multi_product_adoption`
- `payment_success_rate`
- `kyc_flag`

Rationale:

Adoption should be modeled as both eligibility and readiness. These features reduce over-reliance on treatment timing fields.

### Retention

Prioritize these features:

- `lockin_resilience_score`
- `settlement_credit_stress`
- `digital_growth_index`
- `payout_pain_gap`
- `repeat_customer_change_scaled`
- `active_provider_month_flag_lag1`
- `lock_in_score_lag1`

Rationale:

Retention should capture lock-in, liquidity stability, repeat-customer strength, and digital support. The current primary survey does not directly ask retention intent, so future data collection should add that item.

## Primary Survey Gaps To Fix

Add these questions to improve future validation:

| Gap | Suggested question | Target variables |
|---|---|---|
| Direct retention intent | "I expect to continue using my main service platform or digital work channel for the next 6 months." | `retention_flag`, `churn_probability`, `lock_in_score` |
| Actual payout delay | "How many days does payout usually take after work completion?" | `payout_delay_days`, `settlement_delay` |
| Loan offer vs credit need | "Were you offered credit, and did you accept it?" | `loan_offer_flag`, `loan_status`, `loan_amount` |
| Repayment stress | "Loan repayments are manageable from my monthly service income." | `default_flag`, `repayment_amount`, `working_capital_gap` |
| Forecast-specific AI use | "Do you use forecasts for demand, income, or cashflow planning?" | `forecast_usage`, `agentic_intelligence_score` |

## Implementation Sequence

Recommended next steps, without retraining yet:

1. Add feature formulas to a new feature-building script or extend `src/create_lagged_features.py`.
2. Generate a feature dictionary documenting each engineered variable.
3. Run distribution checks for each new feature.
4. Run leakage audit before any retraining.
5. Retrain only after confirming that future-state targets use lagged or baseline predictors.

## Expected Impact

| Model | Expected benefit | Risk |
|---|---|---|
| Loan default | Better recall and ROC AUC from explicit repayment and liquidity stress features. | Default remains rare, so threshold tuning and class weighting still matter. |
| Embedded finance adoption | Less dependence on treatment flags; better interpretation of readiness and demand. | Adoption may still be partly policy-driven by rollout timing. |
| Retention | More interpretable churn drivers through lock-in, liquidity, and digital support. | Current primary survey validates retention indirectly, not directly. |

## Dissertation Framing

These features convert the DELTA framework into measurable modeling constructs:

- Data: transaction velocity, payment reliability, primary survey signals
- Embedded Finance: credit dependency, payout stress, finance readiness
- Lock-in: repeat customers, lock-in resilience
- Technology: digital growth and automation usage
- Advancement: perceived and modeled business growth
- Agentic Intelligence: AI usage and forecast/productivity signals

They should be described as engineered constructs for prediction and scenario analysis, not as directly observed administrative facts.
