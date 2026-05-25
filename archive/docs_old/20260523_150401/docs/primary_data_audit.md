# Primary Data Audit

Generated on 2026-05-21.

## Scope

Audited datasets:

- `data/merchants.csv`
- `data/transactions.csv`
- `data/payouts_loans.csv`
- `data/provider_kpis.csv`
- `data/provenance.csv`

This audit classifies variables by evidentiary character. The project uses synthetic data only, so "Primary-like proxy" means the field mimics a behavioral, transactional, provider-state, or respondent-like observation that could serve as primary evidence if collected from actual providers, platform logs, interviews, or surveys. It does not mean this generated project already contains real primary data.

## Classification Rules

- `Primary-like proxy`: Synthetic field that resembles direct behavior, transaction logs, provider status, customer feedback, or survey/respondent-style data.
- `Secondary`: Synthetic value or category calibrated from public market, fintech, or platform-context priors.
- `Synthetic`: Simulator identifier, time index, or generated control field with no standalone behavioral evidence.
- `Derived`: Rule-based field from treatment timing, status, or project metadata.
- `Engineered`: Composite, modeled, or feature-engineered variable calculated from other synthetic fields.

## Variable Classification Table

| Variable | Dataset | Generation method | Source | Classification |
|---|---|---|---|---|
| merchant_id | merchants.csv | Direct simulator identifier, time index, or generated control field with no standalone evidentiary behavior. | Synthetic simulator output | Synthetic |
| region | merchants.csv | Synthetic value or category calibrated from public market/platform-context priors, not direct field evidence. | Public prior/calibration, synthetic row values | Secondary |
| city | merchants.csv | Synthetic value or category calibrated from public market/platform-context priors, not direct field evidence. | Public prior/calibration, synthetic row values | Secondary |
| category | merchants.csv | Synthetic value or category calibrated from public market/platform-context priors, not direct field evidence. | Public prior/calibration, synthetic row values | Secondary |
| tenure_days | merchants.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Synthetic simulator output | Primary-like proxy |
| avg_ticket | merchants.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Synthetic simulator output | Primary-like proxy |
| monthly_income | merchants.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Synthetic simulator output | Primary-like proxy |
| repeat_customer_rate | merchants.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Synthetic simulator output | Primary-like proxy |
| platform_commission_pct | merchants.csv | Synthetic value or category calibrated from public market/platform-context priors, not direct field evidence. | Public prior/calibration, synthetic row values | Secondary |
| kyc_flag | merchants.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Synthetic simulator output | Primary-like proxy |
| treatment_flag | merchants.csv | Rule-based field from treatment timing, status, or project metadata. | Assigned by treatment design | Derived |
| treatment_start_month | merchants.csv | Rule-based field from treatment timing, status, or project metadata. | Assigned by treatment design | Derived |
| intervention_timestamp | merchants.csv | Rule-based field from treatment timing, status, or project metadata. | Assigned by treatment design | Derived |
| payment_success_rate | merchants.csv | Composite, modeled, or feature-engineered variable calculated from other synthetic fields. | Derived from synthetic simulator fields | Engineered |
| transaction_velocity | merchants.csv | Composite, modeled, or feature-engineered variable calculated from other synthetic fields. | Derived from synthetic simulator fields | Engineered |
| multi_product_adoption | merchants.csv | Composite, modeled, or feature-engineered variable calculated from other synthetic fields. | Derived from synthetic simulator fields | Engineered |
| digital_tool_usage | merchants.csv | Composite, modeled, or feature-engineered variable calculated from other synthetic fields. | Derived from synthetic simulator fields | Engineered |
| ai_adoption_score | merchants.csv | Composite, modeled, or feature-engineered variable calculated from other synthetic fields. | Derived from synthetic simulator fields | Engineered |
| agent_usage_flag | merchants.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Derived from synthetic simulator fields | Primary-like proxy |
| transaction_id | transactions.csv | Direct simulator identifier, time index, or generated control field with no standalone evidentiary behavior. | Synthetic simulator output | Synthetic |
| merchant_id | transactions.csv | Direct simulator identifier, time index, or generated control field with no standalone evidentiary behavior. | Synthetic simulator output | Synthetic |
| timestamp | transactions.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Synthetic simulator output | Primary-like proxy |
| amount | transactions.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Synthetic simulator output | Primary-like proxy |
| customer_rating | transactions.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Synthetic simulator output | Primary-like proxy |
| payment_method | transactions.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Public prior/calibration, synthetic row values | Primary-like proxy |
| cancellation_flag | transactions.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Synthetic simulator output | Primary-like proxy |
| tip_amount | transactions.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Synthetic simulator output | Primary-like proxy |
| treatment_active | transactions.csv | Rule-based field from treatment timing, status, or project metadata. | Assigned by treatment design | Derived |
| settlement_delay | transactions.csv | Composite, modeled, or feature-engineered variable calculated from other synthetic fields. | Derived from synthetic simulator fields | Engineered |
| service_completion_rate | transactions.csv | Composite, modeled, or feature-engineered variable calculated from other synthetic fields. | Derived from synthetic simulator fields | Engineered |
| merchant_id | payouts_loans.csv | Direct simulator identifier, time index, or generated control field with no standalone evidentiary behavior. | Synthetic simulator output | Synthetic |
| month | payouts_loans.csv | Direct simulator identifier, time index, or generated control field with no standalone evidentiary behavior. | Synthetic simulator output | Synthetic |
| payout_amount | payouts_loans.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Synthetic simulator output | Primary-like proxy |
| payout_delay_days | payouts_loans.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Synthetic simulator output | Primary-like proxy |
| active_provider_month_flag | payouts_loans.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Derived from synthetic simulator fields | Primary-like proxy |
| loan_offer_flag | payouts_loans.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Synthetic simulator output | Primary-like proxy |
| loan_amount | payouts_loans.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Synthetic simulator output | Primary-like proxy |
| loan_status | payouts_loans.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Synthetic simulator output | Primary-like proxy |
| repayment_amount | payouts_loans.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Synthetic simulator output | Primary-like proxy |
| working_capital_gap | payouts_loans.csv | Composite, modeled, or feature-engineered variable calculated from other synthetic fields. | Derived from synthetic simulator fields | Engineered |
| loan_disbursal_time | payouts_loans.csv | Composite, modeled, or feature-engineered variable calculated from other synthetic fields. | Derived from synthetic simulator fields | Engineered |
| default_flag | payouts_loans.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Derived from synthetic simulator fields | Primary-like proxy |
| merchant_id | provider_kpis.csv | Direct simulator identifier, time index, or generated control field with no standalone evidentiary behavior. | Synthetic simulator output | Synthetic |
| month | provider_kpis.csv | Direct simulator identifier, time index, or generated control field with no standalone evidentiary behavior. | Synthetic simulator output | Synthetic |
| income_growth_pct | provider_kpis.csv | Composite, modeled, or feature-engineered variable calculated from other synthetic fields. | Synthetic simulator output | Engineered |
| monthly_profit | provider_kpis.csv | Composite, modeled, or feature-engineered variable calculated from other synthetic fields. | Synthetic simulator output | Engineered |
| retention_flag | provider_kpis.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Synthetic simulator output | Primary-like proxy |
| churn_probability | provider_kpis.csv | Composite, modeled, or feature-engineered variable calculated from other synthetic fields. | Synthetic simulator output | Engineered |
| treatment_flag | provider_kpis.csv | Rule-based field from treatment timing, status, or project metadata. | Assigned by treatment design | Derived |
| post_treatment_flag | provider_kpis.csv | Rule-based field from treatment timing, status, or project metadata. | Assigned by treatment design | Derived |
| lock_in_score | provider_kpis.csv | Composite, modeled, or feature-engineered variable calculated from other synthetic fields. | Derived from synthetic simulator fields | Engineered |
| technology_adoption_score | provider_kpis.csv | Composite, modeled, or feature-engineered variable calculated from other synthetic fields. | Derived from synthetic simulator fields | Engineered |
| advancement_score | provider_kpis.csv | Composite, modeled, or feature-engineered variable calculated from other synthetic fields. | Derived from synthetic simulator fields | Engineered |
| agentic_intelligence_score | provider_kpis.csv | Composite, modeled, or feature-engineered variable calculated from other synthetic fields. | Derived from synthetic simulator fields | Engineered |
| forecast_usage | provider_kpis.csv | Synthetic simulation of a transactional, behavioral, provider-state, or respondent-like observation. | Derived from synthetic simulator fields | Primary-like proxy |
| dataset | provenance.csv | Rule-based field from treatment timing, status, or project metadata. | Project metadata | Derived |
| column_name | provenance.csv | Rule-based field from treatment timing, status, or project metadata. | Project metadata | Derived |
| delta_dimension | provenance.csv | Rule-based field from treatment timing, status, or project metadata. | Project metadata | Derived |
| source_type | provenance.csv | Rule-based field from treatment timing, status, or project metadata. | Project metadata | Derived |
| description | provenance.csv | Rule-based field from treatment timing, status, or project metadata. | Project metadata | Derived |

## Summary Counts

| Classification | Variable count | Share of audited variables |
|---|---:|---:|
| Primary-like proxy | 22 | 36.7% |
| Secondary | 4 | 6.7% |
| Synthetic | 7 | 11.7% |
| Derived | 11 | 18.3% |
| Engineered | 16 | 26.7% |
| Total | 60 | 100.0% |

For the requested headline estimates:

- `% primary-like`: 36.7%
- `% synthetic`: 11.7% under the narrow classification for direct simulator identifiers, time indexes, and non-behavioral generated fields
- `% engineered`: 45.0% if `Derived` and `Engineered` are combined as the broader engineered/computational family

## Can Existing Variables Be Claimed As Primary Evidence?

No. The current project should not claim any existing variable as actual primary evidence.

Several fields are credible primary-observation proxies because they resemble data that could be collected directly from platform logs, provider surveys, customer ratings, or payment/payout systems. Examples include `amount`, `customer_rating`, `cancellation_flag`, `payout_amount`, `payout_delay_days`, `loan_status`, `retention_flag`, and `forecast_usage`.

However, these values are generated by the simulator. They are not observed from real Urban Company providers, Razorpay systems, customer surveys, interviews, administrative logs, payment processors, or loan ledgers. The defensible dissertation wording is:

> This project uses synthetic primary-like behavioral proxies calibrated with public Indian fintech and platform-economy priors.

The project can credibly support methods development, causal-design demonstration, scenario analysis, and dissertation model prototyping. It cannot, by itself, support empirical claims about real provider behavior or measured Razorpay/Urban Company outcomes.

## Recommended Evidence Framing

- Treat `Secondary` fields as public-prior calibration inputs, not direct secondary observations.
- Treat `Primary-like proxy` fields as synthetic analogues of potential primary evidence.
- Treat `Engineered` and `Derived` fields as analysis features, causal-design indicators, or DELTA framework indices.
- If real dissertation evidence is later collected, add a separate raw-data layer and update provenance with source labels such as `survey`, `interview`, `platform_log`, `payment_record`, or `loan_record`.
