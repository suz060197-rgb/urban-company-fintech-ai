# Adoption Propensity Model Report

Generated on 2026-05-22.

## Objective

Rebuild the embedded finance adoption model as a pre-intervention propensity model using only baseline/provider characteristics.

## Leakage Controls

Excluded all rollout timing and treatment-state variables:

- `intervention_timestamp`
- `months_since_intervention`
- `post_treatment_flag`
- `pre_treatment_flag`
- `treatment_flag`
- `treatment_flag_merchant`
- `treatment_start_month`

The target is provider-level eventual embedded-finance access from `merchants.csv::treatment_flag`. Predictors are baseline characteristics available before intervention.

## Model Features

- `tenure_days`
- `kyc_flag`
- `digital_tool_usage`
- `monthly_income`
- `transaction_velocity`
- `ai_adoption_score`
- `agent_usage_flag`
- `repeat_customer_rate`
- `avg_ticket`
- `payment_success_rate`
- `multi_product_adoption`
- `city`
- `category`
- `region`

## ROC Comparison

| Model version | ROC AUC | Interpretation |
|---|---:|---|
| Original adoption model | 0.605 | Earlier baseline metric. |
| Leaky engineered retrain | 0.999 | Invalid high score driven by rollout timing leakage. |
| New pre-intervention propensity model | 0.663 | Safer estimate using baseline provider characteristics only. |

## New Model Metrics

| Metric | Value |
|---|---:|
| accuracy | 0.544 |
| precision | 0.500 |
| recall | 1.000 |
| roc_auc | 0.663 |
| threshold | 0.350 |
| positive_rate | 0.456 |
| tp | 114.000 |
| tn | 22.000 |
| fp | 114.000 |
| fn | 0.000 |

## Top Predictors

| feature | coefficient | importance |
| --- | --- | --- |
| kyc_flag | 0.982 | 0.982 |
| city_Surat | 0.184 | 0.184 |
| category_home_cleaning | 0.119 | 0.119 |
| multi_product_adoption | 0.094 | 0.094 |
| city_Ahmedabad | -0.091 | 0.091 |
| category_beauty_wellness | -0.078 | 0.078 |
| city_Kochi | 0.074 | 0.074 |
| digital_tool_usage | 0.055 | 0.055 |
| city_Patna | 0.054 | 0.054 |
| city_Mumbai | -0.054 | 0.054 |
| city_Chandigarh | 0.052 | 0.052 |
| city_Bhubaneswar | -0.051 | 0.051 |
| city_Hyderabad | -0.050 | 0.050 |
| city_Bengaluru | -0.050 | 0.050 |
| category_plumbing_electrical | 0.049 | 0.049 |
| ai_adoption_score | 0.049 | 0.049 |
| region_North | 0.048 | 0.048 |
| region_South | -0.037 | 0.037 |
| category_salon_spa_premium | -0.037 | 0.037 |
| city_Kolkata | -0.036 | 0.036 |

## Feature Correlations With Target

| feature | correlation_with_target | abs_correlation |
| --- | --- | --- |
| kyc_flag | 0.283 | 0.283 |
| multi_product_adoption | 0.139 | 0.139 |
| digital_tool_usage | 0.097 | 0.097 |
| region_North | 0.088 | 0.088 |
| category_home_cleaning | 0.072 | 0.072 |
| city_Ahmedabad | -0.065 | 0.065 |
| city_Mumbai | -0.064 | 0.064 |
| city_Hyderabad | -0.061 | 0.061 |
| city_Delhi NCR | 0.060 | 0.060 |
| ai_adoption_score | 0.057 | 0.057 |
| city_Surat | 0.053 | 0.053 |
| city_Kolkata | -0.048 | 0.048 |
| city_Kochi | 0.043 | 0.043 |
| category_appliance_repair | -0.042 | 0.042 |
| region_West | -0.040 | 0.040 |
| city_Jaipur | 0.039 | 0.039 |
| payment_success_rate | 0.038 | 0.038 |
| city_Bengaluru | -0.035 | 0.035 |
| city_Bhubaneswar | -0.034 | 0.034 |
| region_East | -0.032 | 0.032 |

## Interpretation

The new ROC is expected to be materially lower than the leaky retrained model because rollout timing variables have been removed. This is a healthier result: it reflects baseline separability between eventual treated and untreated providers rather than reconstruction of the intervention schedule.

Use this model as a pre-intervention adoption propensity baseline. It is more credible for dissertation discussion than the previous near-perfect adoption model.