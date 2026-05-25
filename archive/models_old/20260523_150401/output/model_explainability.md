# Model Explainability

Scope: saved artifacts in `output/models/`. No retraining was performed.

## Churn Prediction

Performance:

- Accuracy: 0.973
- Precision: 0.958
- Recall: 0.801
- ROC AUC: 0.934

Top drivers:

- `payout_delay_days`
- `forecast_usage`
- `agentic_intelligence_score`
- `post_treatment_flag`
- `working_capital_gap`

Business interpretation:

The model is primarily explaining liquidity and engagement. Faster payout access, forecast usage, and treatment exposure align with lower churn risk. Working-capital conditions and digital/agentic behavior are also important signals.

Risk factors:

- Delayed payouts
- No forecast usage
- Lack of embedded-finance exposure
- Weak liquidity position
- Weak repeat-customer base

Driver analysis:

The strong role of payout delay confirms the embedded-finance mechanism, but it is same-month information. For operational churn prediction, this should become prior-month payout delay or a rolling payout delay measure.

## Loan Default Prediction

Performance:

- Accuracy: 0.873
- Precision: 0.109
- Recall: 0.227
- ROC AUC: 0.683

Top drivers:

- `loan_disbursal_time`
- `city_Hyderabad`
- `treatment_flag`
- `city_Bhubaneswar`
- `avg_ticket`

Business interpretation:

The model has weak discriminatory power. It picks up disbursal friction, geography, treatment exposure, and provider ticket size, but default events are rare and the model does not capture enough positive cases.

Risk factors:

- Longer loan disbursal time
- Higher working-capital pressure
- Lower ticket size
- Certain synthetic city segments
- Weak repayment behavior, though current `repayment_amount` is leakage

Driver analysis:

This model needs a cleaner origination-time risk table. Current performance is limited by class imbalance and leakage-prone repayment variables.

## Income Growth Prediction

Performance:

- RMSE: 0.105
- MAE: 0.078
- R2: 0.864
- Directional accuracy: 0.903

Top drivers:

- `payout_amount`
- `monthly_income`
- `active_provider_month_flag`
- `lock_in_score`
- `working_capital_gap`

Business interpretation:

The model explains income growth well, but much of the strength comes from payout amount, which is mechanically connected to income growth. Baseline income affects percentage growth, while lock-in and working-capital pressure contribute to advancement outcomes.

Risk factors:

- Low or zero current payout
- Inactive provider-month
- High working-capital gap
- Weak lock-in score
- High baseline denominator with limited incremental payout growth

Driver analysis:

As an explanatory model it is coherent. As a forecasting model it is leaky and should be rebuilt with lagged payout, lagged liquidity, and prior-month engagement variables.

## Embedded Finance Adoption

Performance:

- Accuracy: 0.564
- Precision: 0.537
- Recall: 0.879
- ROC AUC: 0.605

Top drivers:

- `kyc_flag`
- `city_Hyderabad`
- `multi_product_adoption`
- `city_Surat`
- `city_Ahmedabad`

Business interpretation:

The model mostly identifies likely eligible/adopted providers through KYC and rollout geography. Weak ROC is expected if treatment is intentionally quasi-experimental rather than fully behavior-driven.

Risk factors or adoption blockers:

- No KYC completion
- Lower product adoption
- Lower baseline digital readiness
- Region/category combinations assigned to later rollout waves

Driver analysis:

This is better interpreted as an eligibility or propensity model than a causal performance model. If adoption is meant to be randomized, weak predictability is a positive design feature.

## Cross-Model Takeaways

- Liquidity features are consistently important: payout delay, payout amount, working-capital gap, and disbursal time.
- DELTA features matter, especially technology adoption, agentic intelligence, lock-in, and forecast usage.
- Some top features are too close to the outcome timing. Lagged features are needed before using these as operational predictions.
- Loan default and adoption are weak models and should be improved before dissertation claims rely on them.
