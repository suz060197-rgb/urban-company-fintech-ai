# Target Mapping

This document maps leakage-safe provider-month features at month `t` to future-state outcomes at month `t+1`.

No models are trained in this step.

## Output

- Dataset: `data/model_ready/provider_month_future_targets.csv`
- Rows: 29,000
- Rows with t+1 targets: 28,000
- Rows without t+1 targets: 1,000

## Targets

| Target | Definition | Source month | Notes |
|---|---|---|---|
| `churn_target_tplus1` | `1` if provider is not retained in month `t+1`, else `0` | Future month `t+1` | Derived from next-month `retention_flag`; final panel month is not targetable. |
| `income_growth_tplus1` | Next-month income growth percentage | Future month `t+1` | Derived from next-month `income_growth_pct`. |
| `default_next_cycle` | `1` if next provider-month loan state defaults, else `0` | Future month `t+1` | Derived from next-month `default_flag`; can be filtered to loan-active cases for credit-risk analysis. |

## Treatment Timing Fields Preserved

- `treatment_flag`
- `treatment_start_month`
- `intervention_timestamp`
- `months_since_intervention`
- `pre_treatment_flag`
- `post_treatment_flag`

## Recommended Modeling Use

- Use rows where `has_tplus1_target == True`.
- Use lagged and rolling predictors from month `t`.
- Exclude same-month outcome variables when training forecasting models.
- Keep treatment timing explicit for DiD, event-study, and post-treatment forecasting designs.