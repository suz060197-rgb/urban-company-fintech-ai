# Primary Vs Synthetic Validation Report

Generated on 2026-05-22.

## Inputs

- Primary responses: `data/primary_responses_clean.csv` (30 rows)
- Mapping: `docs/primary_secondary_mapping.csv` (34 rows)
- Synthetic merchants: `data/merchants.csv` (1000 rows)
- Synthetic provider KPIs: `data/provider_kpis.csv` (12000 rows)
- Synthetic payouts/loans: `data/payouts_loans.csv` (12000 rows)

## Agreement Score Method

Variables are converted to comparable 0-1 scales where needed. Agreement score is `1 - absolute(mean gap)`.
Scores are distribution-level checks for pilot validation, not row-level matching and not causal evidence.

## Construct-Level Scores

| construct | agreement_score | agreement_band |
| --- | --- | --- |
| AI usage | 0.792 | Moderate |
| Business growth | 0.829 | High |
| Credit need | 0.666 | Moderate |
| Digital adoption | 0.948 | High |
| Retention | 0.850 | High |
| Settlement pain | 0.595 | Weak |

## Agreement Scores

| construct | primary_variable | synthetic_dataset | synthetic_variable | primary_mean | synthetic_mean | mean_gap | agreement_score | agreement_band | mapping_quality |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Digital adoption | digital_adoption_score_scaled | merchants.csv | digital_tool_usage | 0.642 | 0.674 | 0.033 | 0.967 | High | Direct scaled proxy |
| Digital adoption | digital_adoption_score_scaled | provider_kpis.csv | technology_adoption_score | 0.642 | 0.712 | 0.070 | 0.930 | High | Composite proxy |
| Settlement pain | settlement_delay_impact_scaled | payouts_loans.csv | payout_delay_days_scaled | 0.933 | 0.570 | 0.363 | 0.637 | Moderate | Impact-to-delay proxy |
| Settlement pain | cashflow_issues_scaled | payouts_loans.csv | working_capital_gap_scaled | 0.692 | 0.245 | 0.447 | 0.553 | Weak | Liquidity-pressure proxy |
| Credit need | needed_business_credit_binary | payouts_loans.csv | loan_offer_flag | 0.867 | 0.307 | 0.560 | 0.440 | Weak | Demand-to-offer proxy |
| Credit need | approx_credit_amount_numeric_scaled | payouts_loans.csv | loan_amount_scaled | 0.485 | 0.377 | 0.108 | 0.892 | High | Amount distribution proxy |
| Business growth | business_growth_after_digital_scaled | provider_kpis.csv | advancement_score | 0.758 | 0.493 | 0.266 | 0.734 | Moderate | Direct mechanism proxy |
| Business growth | business_growth_after_digital_scaled | provider_kpis.csv | income_growth_pct_scaled | 0.758 | 0.681 | 0.077 | 0.923 | High | Perception-to-outcome proxy |
| Retention | repeat_customer_change_scaled | provider_kpis.csv | lock_in_score | 0.717 | 0.588 | 0.129 | 0.871 | High | Indirect retention proxy |
| Retention | repeat_customer_change_scaled | provider_kpis.csv | retention_flag | 0.717 | 0.888 | 0.172 | 0.828 | High | Weak indirect proxy |
| AI usage | ai_tool_usage_binary | merchants.csv | agent_usage_flag | 0.600 | 0.439 | 0.161 | 0.839 | High | Direct binary proxy |
| AI usage | ai_tool_usage_binary | provider_kpis.csv | forecast_usage | 0.600 | 0.267 | 0.333 | 0.667 | Moderate | Partial binary proxy |
| AI usage | ai_tool_usage_binary | provider_kpis.csv | agentic_intelligence_score | 0.600 | 0.469 | 0.131 | 0.869 | High | Composite proxy |

## Distribution Comparison Tables

| construct | source | variable | n | mean | median | q25 | q75 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Digital adoption | Primary | digital_adoption_score_scaled | 30 | 0.642 | 0.750 | 0.500 | 0.750 |
| Digital adoption | Synthetic | merchants.csv::digital_tool_usage | 1000 | 0.674 | 0.677 | 0.572 | 0.781 |
| Digital adoption | Synthetic | provider_kpis.csv::technology_adoption_score | 12000 | 0.712 | 0.718 | 0.646 | 0.782 |
| Settlement pain | Primary | settlement_delay_impact_scaled | 30 | 0.933 | 1.000 | 0.812 | 1.000 |
| Settlement pain | Synthetic | payouts_loans.csv::payout_delay_days_scaled | 10853 | 0.570 | 0.609 | 0.226 | 0.839 |
| Settlement pain | Primary | cashflow_issues_scaled | 30 | 0.692 | 0.750 | 0.750 | 0.750 |
| Settlement pain | Synthetic | payouts_loans.csv::working_capital_gap_scaled | 12000 | 0.245 | 0.116 | 0.000 | 0.405 |
| Credit need | Primary | needed_business_credit_binary | 30 | 0.867 | 1.000 | 1.000 | 1.000 |
| Credit need | Synthetic | payouts_loans.csv::loan_offer_flag | 12000 | 0.307 | 0.000 | 0.000 | 1.000 |
| Credit need | Primary | approx_credit_amount_numeric_scaled | 26 | 0.485 | 0.488 | 0.198 | 0.733 |
| Credit need | Synthetic | payouts_loans.csv::loan_amount_scaled | 1823 | 0.377 | 0.326 | 0.150 | 0.547 |
| Business growth | Primary | business_growth_after_digital_scaled | 30 | 0.758 | 0.750 | 0.750 | 0.938 |
| Business growth | Synthetic | provider_kpis.csv::advancement_score | 12000 | 0.493 | 0.527 | 0.459 | 0.591 |
| Business growth | Synthetic | provider_kpis.csv::income_growth_pct_scaled | 12000 | 0.681 | 0.732 | 0.619 | 0.841 |
| Retention | Primary | repeat_customer_change_scaled | 30 | 0.717 | 0.750 | 0.500 | 0.750 |
| Retention | Synthetic | provider_kpis.csv::lock_in_score | 12000 | 0.588 | 0.625 | 0.559 | 0.707 |
| Retention | Synthetic | provider_kpis.csv::retention_flag | 12000 | 0.888 | 1.000 | 1.000 | 1.000 |
| AI usage | Primary | ai_tool_usage_binary | 30 | 0.600 | 1.000 | 0.000 | 1.000 |
| AI usage | Synthetic | merchants.csv::agent_usage_flag | 1000 | 0.439 | 0.000 | 0.000 | 1.000 |
| AI usage | Synthetic | provider_kpis.csv::forecast_usage | 12000 | 0.267 | 0.000 | 0.000 | 1.000 |
| AI usage | Synthetic | provider_kpis.csv::agentic_intelligence_score | 12000 | 0.469 | 0.401 | 0.276 | 0.696 |

## Mapping Compatibility Context

| compatibility_band | mapping_rows |
| --- | --- |
| Context only | 2 |
| High | 11 |
| Low | 5 |
| Medium | 16 |

## Validation Commentary

### AI usage

Mean agreement score: `0.792` (Moderate).
- `ai_tool_usage_binary` vs `merchants.csv::agent_usage_flag`: 0.839. Primary AI usage maps directly to synthetic agent usage flag.
- `ai_tool_usage_binary` vs `provider_kpis.csv::forecast_usage`: 0.667. Forecast usage is narrower than general AI-tool use.
- `ai_tool_usage_binary` vs `provider_kpis.csv::agentic_intelligence_score`: 0.869. Primary AI use is compared with the broader agentic-intelligence score.

### Business growth

Mean agreement score: `0.829` (High).
- `business_growth_after_digital_scaled` vs `provider_kpis.csv::advancement_score`: 0.734. Primary perceived growth is aligned with synthetic advancement score.
- `business_growth_after_digital_scaled` vs `provider_kpis.csv::income_growth_pct_scaled`: 0.923. Perceived growth is compared with synthetic income growth after percentile scaling.

### Credit need

Mean agreement score: `0.666` (Moderate).
- `needed_business_credit_binary` vs `payouts_loans.csv::loan_offer_flag`: 0.440. Primary credit need is not the same as synthetic loan offer; compare directionally.
- `approx_credit_amount_numeric_scaled` vs `payouts_loans.csv::loan_amount_scaled`: 0.892. Compares requested/needed credit size with positive synthetic loan amounts.

### Digital adoption

Mean agreement score: `0.948` (High).
- `digital_adoption_score_scaled` vs `merchants.csv::digital_tool_usage`: 0.967. Survey digital adoption is directly comparable to synthetic digital tool usage.
- `digital_adoption_score_scaled` vs `provider_kpis.csv::technology_adoption_score`: 0.930. Synthetic technology score includes digital tools and payment reliability, so exact agreement is not expected.

### Retention

Mean agreement score: `0.850` (High).
- `repeat_customer_change_scaled` vs `provider_kpis.csv::lock_in_score`: 0.871. The uploaded survey does not contain explicit retention intent; repeat-customer change is used as a lock-in proxy.
- `repeat_customer_change_scaled` vs `provider_kpis.csv::retention_flag`: 0.828. Repeat-customer improvement is only a weak proxy for actual provider retention.
- Limitation: the uploaded primary survey does not include an explicit retention-intent question, so retention uses repeat-customer change as an indirect proxy.

### Settlement pain

Mean agreement score: `0.595` (Weak).
- `settlement_delay_impact_scaled` vs `payouts_loans.csv::payout_delay_days_scaled`: 0.637. Survey measures perceived pain; synthetic variable measures payout delay days.
- `cashflow_issues_scaled` vs `payouts_loans.csv::working_capital_gap_scaled`: 0.553. Cashflow pain is compared with synthetic working-capital pressure.

## Overall Interpretation

Average agreement across all comparisons is `0.781`.
The primary survey aligns best where respondent-observable constructs map directly to synthetic variables, especially digital adoption, business growth, and broad lock-in signals.
Agreement is weaker where the survey measures perceived pain or need while the synthetic variable is an administrative or modeled construct, such as payout delay days, loan offers, or forecast usage.
Use these results as calibration and face-validity evidence for the synthetic dissertation dataset.