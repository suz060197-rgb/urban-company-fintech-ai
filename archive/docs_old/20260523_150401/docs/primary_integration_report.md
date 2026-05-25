# Primary Integration Report

Primary survey responses were mapped into provider-level synthetic features using segment-level priors.

No models were retrained.

## Output

- File: `data/provider_features_enriched.csv`
- Provider rows: `1,000`

## Variable Mapping

| Survey variable | Synthetic/provider feature target | Blended output |
|---|---|---|
| `digital_adoption_score_scaled` | `technology_adoption_score` | `technology_adoption_score_blended` |
| `cashflow_issues_scaled` | `working_capital_gap` | `working_capital_gap_blended`, `settlement_credit_stress` |
| `settlement_delay_impact_scaled` | `payout_delay_days`, `settlement_delay` | `payout_delay_days_blended`, `settlement_experience_index` |
| `needed_business_credit_binary` | loan offer and uptake behavior | `loan_uptake_propensity_blended`, `credit_dependency_score_primary_informed` |
| `business_growth_after_digital_scaled` | `advancement_score`, income growth | `advancement_score_blended`, `digital_growth_index` |
| `repeat_customer_change_scaled` | `lock_in_score`, repeat customers | `lock_in_score_blended` |
| `ai_tool_usage_binary` | `agentic_intelligence_score`, forecast usage | `agentic_intelligence_score_blended` |

## Match Quality

| primary_match_level | providers |
| --- | --- |
| overall_prior | 607 |
| business_type_region | 393 |

## Survey Priors By Segment

| business_type | region | survey_response_count | survey_digital_adoption_prior | survey_cashflow_stress_prior | survey_settlement_pain_prior | survey_credit_need_prior | survey_ai_usage_prior |
| --- | --- | --- | --- | --- | --- | --- | --- |
| appliance_repair | West | 1 | 0.5000 | 0.5000 | 0.7500 | 1.0000 | 1.0000 |
| beauty_wellness | South | 1 | 0.7500 | 0.7500 | 1.0000 | 1.0000 | 1.0000 |
| beauty_wellness | West | 17 | 0.7500 | 0.7500 | 1.0000 | 0.9412 | 0.7059 |
| home_cleaning | West | 3 | 0.3333 | 0.5000 | 0.7500 | 0.3333 | 0.0000 |
| home_services_other | West | 1 | 0.5000 | 0.5000 | 0.7500 | 1.0000 | 0.0000 |
| plumbing_electrical | South | 4 | 0.5625 | 0.6875 | 0.8750 | 0.7500 | 0.5000 |
| plumbing_electrical | West | 3 | 0.5000 | 0.6667 | 0.9167 | 1.0000 | 0.6667 |

## Enriched Feature Summary

| statistic | technology_adoption_score_blended | working_capital_gap_blended | payout_delay_days_blended | loan_uptake_propensity_blended | settlement_credit_stress | digital_growth_index | credit_dependency_score_primary_informed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| count | 1000.0000 | 1000.0000 | 1000.0000 | 1000.0000 | 1000.0000 | 1000.0000 | 1000.0000 |
| mean | 0.7386 | 0.4223 | 0.6934 | 0.5005 | 0.6423 | 0.6684 | 0.4762 |
| std | 0.0788 | 0.2016 | 0.2238 | 0.1453 | 0.1330 | 0.0635 | 0.0935 |
| min | 0.4467 | 0.1500 | 0.2250 | 0.1167 | 0.3317 | 0.3981 | 0.1665 |
| 25% | 0.6909 | 0.2702 | 0.4847 | 0.3929 | 0.5308 | 0.6329 | 0.4118 |
| 50% | 0.7488 | 0.3496 | 0.7997 | 0.4787 | 0.6446 | 0.6780 | 0.4748 |
| 75% | 0.7951 | 0.5184 | 0.8674 | 0.5899 | 0.7310 | 0.7135 | 0.5356 |
| max | 0.9199 | 0.9250 | 1.0000 | 0.9173 | 0.9647 | 0.8073 | 0.7521 |

## Method

- Provider-level synthetic summaries were computed from `data_v2/merchants.csv`, `provider_kpis.csv`, `payouts_loans.csv`, and `transactions.csv`.
- Primary priors were estimated by `business_type + region` where survey coverage existed.
- Providers without a matching primary segment received overall survey priors.
- Blended features use synthetic behavior as the main signal and survey responses as calibration priors.
- The enrichment is intended for analysis, dashboards, and dissertation triangulation, not as new primary-observed provider records.