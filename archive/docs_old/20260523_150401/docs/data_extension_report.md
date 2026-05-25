# Data Extension Report

Extended synthetic provider-month observations from `2024-01` through `2026-05` into `data_v2/`.

The original `data/` directory was left intact as the historical backup. No existing production CSVs were overwritten.

## Pipeline Changes

- `generate_uc_dataset.py` now accepts `--start_month` and `--end_month`.
- Monthly generation now includes UPI growth, recurring seasonality, inflation, increasing digital/AI maturity, credit uptake growth, settlement-delay improvements, treatment-driven liquidity effects, and provider churn.
- `create_lagged_features.py` no longer hardcodes 2024 when computing `months_since_intervention`; it derives month numbering from the panel start.

## Coverage And Row Counts

| dataset | old_rows | new_rows | row_delta | old_earliest | old_latest | new_earliest | new_latest | old_observed_months | new_observed_months |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| merchants.csv | 1000 | 1000 | 0 | 2024-02-01 | 2024-08-01 | 2024-02-01 | 2025-06-01 | 7 | 17 |
| transactions.csv | 403539 | 945233 | 541694 | 2024-01-01 | 2024-12-31 | 2024-01-01 | 2026-05-31 | 12 | 29 |
| payouts_loans.csv | 12000 | 29000 | 17000 | 2024-01-01 | 2024-12-01 | 2024-01-01 | 2026-05-01 | 12 | 29 |
| provider_kpis.csv | 12000 | 29000 | 17000 | 2024-01-01 | 2024-12-01 | 2024-01-01 | 2026-05-01 | 12 | 29 |

## Missing Monthly Periods In New Data

| dataset | missing_months |
| --- | --- |
| merchants.csv | None |
| transactions.csv | None |
| payouts_loans.csv | None |
| provider_kpis.csv | None |

## Distribution Changes

| dataset | metric | old_mean_or_share | new_mean_or_share | delta |
| --- | --- | --- | --- | --- |
| merchants.csv | monthly_income | 39082.4601 | 39082.4601 | 0.0 |
| merchants.csv | avg_ticket | 1108.1582 | 1108.1582 | 0.0 |
| merchants.csv | payment_success_rate | 0.9554 | 0.9542 | -0.0012 |
| merchants.csv | transaction_velocity | 36.0517 | 35.6265 | -0.4252 |
| merchants.csv | multi_product_adoption | 3.612 | 3.162 | -0.45 |
| merchants.csv | digital_tool_usage | 0.6744 | 0.625 | -0.0494 |
| merchants.csv | ai_adoption_score | 0.5312 | 0.4474 | -0.0837 |
| merchants.csv | treatment_flag_rate | 0.456 | 0.456 | 0.0 |
| transactions.csv | amount | 1158.5272 | 1232.1583 | 73.6311 |
| transactions.csv | customer_rating | 4.3522 | 4.3611 | 0.0088 |
| transactions.csv | upi_share | 0.6988 | 0.7624 | 0.0636 |
| transactions.csv | cash_share | 0.0573 | 0.0298 | -0.0275 |
| transactions.csv | settlement_delay | 1.5386 | 1.2422 | -0.2964 |
| transactions.csv | service_completion_rate | 0.9545 | 0.9586 | 0.0041 |
| transactions.csv | cancellation_rate | 0.0559 | 0.0529 | -0.0031 |
| payouts_loans.csv | payout_amount | 28885.076 | 29861.6278 | 976.5518 |
| payouts_loans.csv | payout_delay_days | 4.0101 | 2.9542 | -1.0559 |
| payouts_loans.csv | loan_offer_rate | 0.3071 | 0.3225 | 0.0154 |
| payouts_loans.csv | loan_amount | 1672.511 | 2014.0376 | 341.5266 |
| payouts_loans.csv | working_capital_gap | 2025.8059 | 1492.8538 | -532.9521 |
| payouts_loans.csv | loan_disbursal_time | 0.2012 | 0.2096 | 0.0085 |
| payouts_loans.csv | default_rate | 0.0078 | 0.0063 | -0.0016 |
| payouts_loans.csv | active_provider_month_rate | 0.9044 | 0.8153 | -0.0891 |
| provider_kpis.csv | income_growth_pct | -0.2657 | -0.2544 | 0.0114 |
| provider_kpis.csv | monthly_profit | 14125.7091 | 14612.1878 | 486.4787 |
| provider_kpis.csv | retention_rate | 0.8885 | 0.8042 | -0.0843 |
| provider_kpis.csv | churn_probability | 0.1113 | 0.196 | 0.0846 |
| provider_kpis.csv | post_treatment_rate | 0.3043 | 0.3148 | 0.0105 |
| provider_kpis.csv | lock_in_score | 0.5878 | 0.516 | -0.0717 |
| provider_kpis.csv | technology_adoption_score | 0.7119 | 0.7863 | 0.0744 |
| provider_kpis.csv | advancement_score | 0.4926 | 0.4891 | -0.0035 |
| provider_kpis.csv | agentic_intelligence_score | 0.4687 | 0.4972 | 0.0285 |
| provider_kpis.csv | forecast_usage_rate | 0.267 | 0.2011 | -0.0659 |

## Interpretation

- The new panel reaches May 2026 while preserving the old directory as a backup.
- Transaction volume rises because the panel expands from 12 months to 29 months.
- UPI share, technology adoption, agentic intelligence, and settlement speed should move in dissertation-consistent directions over time.
- `data_v2/` should be used for refreshed Power BI work and any post-extension modeling.