# Primary Response Cleaning Report

Generated on 2026-05-22.

## Input And Output

- Raw input rows: 30
- Raw input columns: 25
- Blank rows removed: 0
- Blank columns removed: 0
- Duplicate full rows removed: 0
- Duplicate respondent IDs removed: 0
- Prepared raw rows after cleaning: 30
- Clean output rows: 30
- Clean output columns: 43
- Preserved interview quotes: 30

Outputs:

- `data/primary_responses_clean.csv`
- `data/primary_interview_quotes.csv`

## Cleaning Rules Applied

- Income ranges were converted to numeric midpoint rupee estimates.
- Monthly transaction ranges were converted to numeric midpoint estimates.
- Yes/No variables were converted to binary values: Yes = 1, No = 0.
- Daily/Weekly-style frequency variables were converted to ordinal scores.
- Likert variables were preserved on a 1-5 scale and standardized to 0-1 scaled fields.
- Missing values such as blank, `NULL`, `NA`, and `Not applicable` were treated as missing.
- Blank rows and blank columns were removed before transformation.
- Duplicate full rows and duplicate respondent IDs were removed, keeping the first observed response.
- City and business category values were normalized to consistent labels.
- Output column names were standardized to lower snake_case.
- Interview quotes were excluded from the main analytical table and preserved separately.

## Validation Results

- PASS required cleaned columns are present.
- PASS respondent_id values are unique.
- PASS digital_adoption_score_likert values are within 1-5.
- PASS cashflow_issues_likert values are within 1-5.
- PASS settlement_delay_impact_likert values are within 1-5.
- PASS faster_payout_impact_likert values are within 1-5.
- PASS business_growth_after_digital_likert values are within 1-5.
- PASS repeat_customer_change_likert values are within 1-5.
- PASS upi_usage_frequency_scaled values are within 0-1.
- PASS digital_adoption_score_scaled values are within 0-1.
- PASS cashflow_issues_scaled values are within 0-1.
- PASS settlement_delay_impact_scaled values are within 0-1.
- PASS faster_payout_impact_scaled values are within 0-1.
- PASS business_growth_after_digital_scaled values are within 0-1.
- PASS repeat_customer_change_scaled values are within 0-1.
- PASS needed_business_credit_binary is binary.
- PASS ai_tool_usage_binary is binary.

## Numeric Summary

| statistic | experience_years | monthly_income_midpoint | monthly_transaction_estimate | upi_usage_frequency_score | needed_business_credit_binary | approx_credit_amount_numeric | ai_tool_usage_binary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| count | 30.0 | 30.0 | 30.0 | 30.0 | 30.0 | 26.0 | 30.0 |
| mean | 5.0 | 25833.33 | 98.5 | 5.0 | 0.87 | 19153.85 | 0.6 |
| std | 1.44 | 9589.27 | 23.86 | 0.0 | 0.35 | 8038.37 | 0.5 |
| min | 3.0 | 12500.0 | 60.0 | 5.0 | 0.0 | 5000.0 | 0.0 |
| 25% | 4.0 | 12500.0 | 105.0 | 5.0 | 1.0 | 12750.0 | 0.0 |
| 50% | 5.0 | 32500.0 | 105.0 | 5.0 | 1.0 | 19000.0 | 1.0 |
| 75% | 6.0 | 32500.0 | 105.0 | 5.0 | 1.0 | 24250.0 | 1.0 |
| max | 7.0 | 32500.0 | 135.0 | 5.0 | 1.0 | 40000.0 | 1.0 |

## Missing Value Summary

| column | missing_count |
| --- | --- |
| approx_credit_amount_numeric | 4 |
| data_type | 0 |
| respondent_id | 0 |
| business_type_raw | 0 |
| business_type | 0 |
| city | 0 |
| region | 0 |
| experience_years | 0 |
| tenure_days_estimate | 0 |
| monthly_income_range_raw | 0 |
| respondent_category | 0 |
| monthly_income_midpoint | 0 |
| monthly_transaction_volume_raw | 0 |
| payment_methods_standardized | 0 |
| monthly_transaction_estimate | 0 |
| uses_cash_flag | 0 |
| uses_card_flag | 0 |
| uses_wallet_flag | 0 |
| uses_upi_flag | 0 |
| upi_usage_frequency_raw | 0 |
| upi_usage_frequency_score | 0 |
| needed_business_credit_binary | 0 |
| upi_usage_frequency_scaled | 0 |
| approx_credit_amount_raw | 0 |
| credit_purpose | 0 |
| ai_tool_usage_binary | 0 |
| automation_usage | 0 |
| platform_used_raw | 0 |
| key_pain_points | 0 |
| survey_response_date | 0 |
| digital_adoption_score_likert | 0 |
| digital_adoption_score_scaled | 0 |
| cashflow_issues_likert | 0 |
| cashflow_issues_scaled | 0 |
| settlement_delay_impact_likert | 0 |
| settlement_delay_impact_scaled | 0 |
| faster_payout_impact_likert | 0 |
| faster_payout_impact_scaled | 0 |
| business_growth_after_digital_likert | 0 |
| business_growth_after_digital_scaled | 0 |
| repeat_customer_change_likert | 0 |
| repeat_customer_change_scaled | 0 |
| has_interview_quote | 0 |

## Category Summary

### business_type

- beauty_wellness: 18
- plumbing_electrical: 7
- home_cleaning: 3
- home_services_other: 1
- appliance_repair: 1

### city

- Thane: 12
- Mumbai: 8
- Bangalore: 4
- Navi Mumbai: 2
- Surat: 1
- Indore: 1
- Hyderabad: 1
- Pune: 1

### region

- West: 25
- South: 5

### data_type

- interview: 20
- survey: 10
