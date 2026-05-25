# Power BI Blueprint

Generated on 2026-05-22.

## Objective

Design a complete Power BI star schema for the Urban Company embedded-finance MBA dissertation project. The model should support analysis of payments, payouts, working-capital loans, DELTA scores, primary survey validation, adoption propensity, and default-risk segmentation.

## Source CSV Inventory

| Source file | Rows | Role |
|---|---:|---|
| `data/merchants.csv` | 1,000 | Provider dimension and baseline attributes |
| `data/transactions.csv` | 403,539 | Transaction/payment fact |
| `data/payouts_loans.csv` | 12,000 | Provider-month payout and loan fact |
| `data/provider_kpis.csv` | 12,000 | Provider-month KPI fact |
| `data/model_ready/provider_month_future_targets.csv` | 12,000 | Model-ready analytical provider-month fact |
| `data/primary_responses_clean.csv` | 30 | Primary survey fact |
| `data/primary_interview_quotes.csv` | 30 | Qualitative quote table |
| `data/provenance.csv` | 60 | Metadata/provenance dimension |
| `docs/primary_secondary_mapping.csv` | 34 | Primary-to-synthetic mapping dimension |
| `output/agreement_scores.csv` | 13 | Primary-vs-synthetic validation fact |
| `output/default_risk_segmentation.csv` | 3 | Default model risk-band summary |
| `output/default_threshold_tuning.csv` | 99 | Default model threshold tuning fact |
| `output/default_model_safe/default_revision_metric_history.csv` | 3 | Default model metric history |
| `output/adoption_propensity/adoption_propensity_roc_comparison.csv` | 3 | Adoption model ROC comparison |

## Recommended Star Schema

### Dimensions

| Table | Build from | Grain | Key | Notes |
|---|---|---|---|---|
| `DimMerchant` | `merchants.csv` | One row per provider | `merchant_id` | Keep baseline provider attributes: region, city, category, tenure, KYC, treatment assignment, DELTA readiness fields. |
| `DimDate` | Generated in Power Query/DAX | One row per date | `Date` | Covers transaction timestamps and provider-month periods. Add month, quarter, year, month index. |
| `DimMonth` | Generated from distinct provider months | One row per month | `MonthKey` | Use `YYYYMM`; easier for monthly facts. |
| `DimGeography` | Distinct `region`, `city` from `merchants.csv` and primary responses | City-region row | `CityRegionKey` | Optional snowflake dimension if you want city maps and regional slicers. |
| `DimCategory` | Distinct `category` and primary `business_type` | One row per category | `CategoryKey` | Add mapped survey category where available. |
| `DimPaymentMethod` | Distinct `payment_method` | One row per method | `payment_method` | UPI, cash, card, wallet, netbanking. |
| `DimLoanStatus` | Distinct `loan_status` | One row per status | `loan_status` | `not_offered`, `declined`, `active`, `repaid`, `defaulted`. |
| `DimRiskBand` | `default_risk_segmentation.csv` | One row per band | `risk_band` | Low, Medium, High. |
| `DimProvenance` | `provenance.csv` | One row per dataset-column | `dataset_column_key` | Explain synthetic/derived/primary-like evidence and DELTA dimension. |
| `DimModelVersion` | Model metric CSVs | One row per version | `model_version` | Supports model performance comparison. |

### Facts

| Table | Build from | Grain | Keys | Main measures |
|---|---|---|---|---|
| `FactTransactions` | `transactions.csv` | One transaction | `transaction_id`, `merchant_id`, `Date` | Payment amount, rating, tips, cancellation, settlement delay. |
| `FactProviderMonth` | Merge `provider_kpis.csv` with `payouts_loans.csv` by `merchant_id`, `month` | One provider-month | `merchant_id`, `MonthKey` | Profit, growth, retention, churn probability, payout amount, payout delay, loan amount, default flag, DELTA scores. |
| `FactModelReadyProviderMonth` | `provider_month_future_targets.csv` | One provider-month | `merchant_id`, `MonthKey` | Lagged features, rolling features, future targets. Use mainly for model diagnostics pages. |
| `FactPrimarySurvey` | `primary_responses_clean.csv` | One survey response | `respondent_id` | Survey income midpoint, transaction estimate, Likert scores, credit need, AI usage. |
| `FactPrimaryQuotes` | `primary_interview_quotes.csv` | One quote | `respondent_id` | Qualitative evidence. Use as detail table, not numeric fact. |
| `FactAgreementScores` | `agreement_scores.csv` | One validation comparison | `construct`, `primary_variable`, `synthetic_variable` | Agreement score, mean gap. |
| `FactDefaultRiskBands` | `default_risk_segmentation.csv` | One risk band | `risk_band` | Cases, default rate, capture rate. |
| `FactThresholdTuning` | `default_threshold_tuning.csv` | One threshold | `threshold` | Precision, recall, F1, F2, predicted positive rate. |
| `FactModelMetrics` | Model metrics/history CSVs | One metric per model version | `model_version`, `metric` | ROC, precision, recall, accuracy. |

## Table Relationships

Use single-direction filtering from dimensions to facts unless a specific page needs bidirectional behavior.

| From table | From column | To table | To column | Cardinality | Filter direction |
|---|---|---|---|---|---|
| `DimMerchant` | `merchant_id` | `FactTransactions` | `merchant_id` | 1:* | Single |
| `DimMerchant` | `merchant_id` | `FactProviderMonth` | `merchant_id` | 1:* | Single |
| `DimMerchant` | `merchant_id` | `FactModelReadyProviderMonth` | `merchant_id` | 1:* | Single |
| `DimDate` | `Date` | `FactTransactions` | `TransactionDate` | 1:* | Single |
| `DimMonth` | `MonthKey` | `FactProviderMonth` | `MonthKey` | 1:* | Single |
| `DimMonth` | `MonthKey` | `FactModelReadyProviderMonth` | `MonthKey` | 1:* | Single |
| `DimPaymentMethod` | `payment_method` | `FactTransactions` | `payment_method` | 1:* | Single |
| `DimLoanStatus` | `loan_status` | `FactProviderMonth` | `loan_status` | 1:* | Single |
| `DimCategory` | `category` | `DimMerchant` | `category` | 1:* | Single |
| `DimGeography` | `CityRegionKey` | `DimMerchant` | `CityRegionKey` | 1:* | Single |
| `DimRiskBand` | `risk_band` | `FactDefaultRiskBands` | `risk_band` | 1:1 | Single |
| `DimModelVersion` | `model_version` | `FactModelMetrics` | `model_version` | 1:* | Single |
| `FactPrimarySurvey` | `respondent_id` | `FactPrimaryQuotes` | `respondent_id` | 1:1 | Single |
| `DimProvenance` | `dataset` | Metadata only | N/A | N/A | Do not relate to main facts unless building a provenance drill page. |

## Power Query Transformations

### `FactTransactions`

- Convert `timestamp` to datetime.
- Create:
  - `TransactionDate = Date.From([timestamp])`
  - `TransactionMonthKey = Date.Year([timestamp]) * 100 + Date.Month([timestamp])`
  - `IsCancellation = if [cancellation_flag] = true then 1 else 0`
  - `TreatmentActiveFlag = if [treatment_active] = true then 1 else 0`

### `FactProviderMonth`

Merge:

- `provider_kpis.csv`
- `payouts_loans.csv`

Join keys:

- `merchant_id`
- `month`

Create:

- `MonthDate = Date.FromText([month] & "-01")`
- `MonthKey = Date.Year([MonthDate]) * 100 + Date.Month([MonthDate])`
- Boolean flags as 0/1 numeric columns.
- `PayoutDelayApplicableFlag = if [active_provider_month_flag] = true then 1 else 0`

Keep `payout_delay_days` as blank where inactive after churn.

### `DimMerchant`

From `merchants.csv`, create:

- `CityRegionKey = [region] & "|" & [city]`
- `CategoryKey = [category]`
- `TreatmentAssignedFlag`
- `KYCFlag`
- `AgentUsageFlag`

### `FactPrimarySurvey`

Use `primary_responses_clean.csv` as already cleaned. Confirm:

- Likert fields are numeric.
- Scaled fields are 0-1.
- Binary fields are 0/1.
- Quotes are not loaded into the numeric survey fact except `has_interview_quote`.

## DAX Measures

### Core Volume Measures

```DAX
Providers :=
DISTINCTCOUNT(DimMerchant[merchant_id])

Active Provider Months :=
SUM(FactProviderMonth[active_provider_month_flag])

Transactions :=
COUNTROWS(FactTransactions)

Total GMV :=
SUM(FactTransactions[amount])

Total Tips :=
SUM(FactTransactions[tip_amount])

Average Ticket :=
DIVIDE([Total GMV], [Transactions])
```

### Payment And Service Quality

```DAX
Cancellation Rate :=
AVERAGE(FactTransactions[cancellation_flag])

Average Rating :=
AVERAGE(FactTransactions[customer_rating])

Payment Success Rate :=
AVERAGE(DimMerchant[payment_success_rate])

Average Settlement Delay :=
AVERAGE(FactTransactions[settlement_delay])

UPI Share :=
DIVIDE(
    CALCULATE([Transactions], DimPaymentMethod[payment_method] = "UPI"),
    [Transactions]
)
```

### Payouts And Loans

```DAX
Total Payouts :=
SUM(FactProviderMonth[payout_amount])

Average Payout Delay :=
AVERAGE(FactProviderMonth[payout_delay_days])

Loan Offer Rate :=
AVERAGE(FactProviderMonth[loan_offer_flag])

Total Loan Amount :=
SUM(FactProviderMonth[loan_amount])

Average Loan Amount :=
AVERAGE(FactProviderMonth[loan_amount])

Default Count :=
SUM(FactProviderMonth[default_flag])

Default Rate :=
AVERAGE(FactProviderMonth[default_flag])

Repayment Amount :=
SUM(FactProviderMonth[repayment_amount])

Working Capital Gap :=
AVERAGE(FactProviderMonth[working_capital_gap])
```

### Provider Outcomes

```DAX
Average Monthly Profit :=
AVERAGE(FactProviderMonth[monthly_profit])

Average Income Growth :=
AVERAGE(FactProviderMonth[income_growth_pct])

Retention Rate :=
AVERAGE(FactProviderMonth[retention_flag])

Churn Probability :=
AVERAGE(FactProviderMonth[churn_probability])

Treated Provider Months :=
SUM(FactProviderMonth[post_treatment_flag])

Treatment Share :=
DIVIDE([Treated Provider Months], COUNTROWS(FactProviderMonth))
```

### DELTA Scores

```DAX
Lock-In Score :=
AVERAGE(FactProviderMonth[lock_in_score])

Technology Adoption Score :=
AVERAGE(FactProviderMonth[technology_adoption_score])

Advancement Score :=
AVERAGE(FactProviderMonth[advancement_score])

Agentic Intelligence Score :=
AVERAGE(FactProviderMonth[agentic_intelligence_score])

Forecast Usage Rate :=
AVERAGE(FactProviderMonth[forecast_usage])

Digital Tool Usage :=
AVERAGE(DimMerchant[digital_tool_usage])

AI Adoption Score :=
AVERAGE(DimMerchant[ai_adoption_score])
```

### Treatment Impact Measures

```DAX
Treated Profit :=
CALCULATE([Average Monthly Profit], FactProviderMonth[post_treatment_flag] = TRUE())

Control Profit :=
CALCULATE([Average Monthly Profit], FactProviderMonth[post_treatment_flag] = FALSE())

Profit Gap Treated Vs Control :=
[Treated Profit] - [Control Profit]

Treated Retention :=
CALCULATE([Retention Rate], FactProviderMonth[post_treatment_flag] = TRUE())

Control Retention :=
CALCULATE([Retention Rate], FactProviderMonth[post_treatment_flag] = FALSE())

Retention Gap Treated Vs Control :=
[Treated Retention] - [Control Retention]

Treated Payout Delay :=
CALCULATE([Average Payout Delay], FactProviderMonth[post_treatment_flag] = TRUE())

Control Payout Delay :=
CALCULATE([Average Payout Delay], FactProviderMonth[post_treatment_flag] = FALSE())

Payout Delay Reduction :=
[Control Payout Delay] - [Treated Payout Delay]
```

### Primary Survey Validation

```DAX
Primary Responses :=
COUNTROWS(FactPrimarySurvey)

Primary Credit Need Rate :=
AVERAGE(FactPrimarySurvey[needed_business_credit_binary])

Primary AI Usage Rate :=
AVERAGE(FactPrimarySurvey[ai_tool_usage_binary])

Primary Digital Adoption :=
AVERAGE(FactPrimarySurvey[digital_adoption_score_scaled])

Primary Settlement Pain :=
AVERAGE(FactPrimarySurvey[settlement_delay_impact_scaled])

Primary Business Growth :=
AVERAGE(FactPrimarySurvey[business_growth_after_digital_scaled])

Average Agreement Score :=
AVERAGE(FactAgreementScores[agreement_score])

Mean Primary Synthetic Gap :=
AVERAGE(FactAgreementScores[mean_gap])
```

### Model And Risk Measures

```DAX
Default Model ROC :=
CALCULATE(
    MAX(FactModelMetrics[value]),
    FactModelMetrics[model] = "loan_default_prediction",
    FactModelMetrics[metric] = "roc_auc"
)

Risk Band Cases :=
SUM(FactDefaultRiskBands[cases])

Risk Band Defaults :=
SUM(FactDefaultRiskBands[defaults])

Risk Band Default Rate :=
DIVIDE([Risk Band Defaults], [Risk Band Cases])

Risk Band Capture Rate :=
SUM(FactDefaultRiskBands[default_capture_rate])

Threshold Precision :=
AVERAGE(FactThresholdTuning[precision])

Threshold Recall :=
AVERAGE(FactThresholdTuning[recall])

Threshold F1 :=
AVERAGE(FactThresholdTuning[f1])

Threshold F2 :=
AVERAGE(FactThresholdTuning[f2])
```

## KPI Definitions

| KPI | Definition | Primary table | Business meaning |
|---|---|---|---|
| GMV | Sum of transaction amount | `FactTransactions` | Total customer payment volume |
| Average Ticket | GMV / transactions | `FactTransactions` | Average order value |
| Payment Success Rate | Mean provider-level payment reliability | `DimMerchant` | Digital payment reliability |
| Average Settlement Delay | Mean transaction settlement delay | `FactTransactions` | Payment rail speed |
| Average Payout Delay | Mean provider payout delay, active months only | `FactProviderMonth` | Provider liquidity timing |
| Loan Offer Rate | Share of provider-months receiving loan offer | `FactProviderMonth` | Embedded credit reach |
| Default Rate | Mean default flag | `FactProviderMonth` | Working-capital risk |
| Retention Rate | Mean retention flag | `FactProviderMonth` | Provider platform stickiness |
| Churn Probability | Mean modeled churn probability | `FactProviderMonth` | Churn risk |
| Monthly Profit | Mean modeled profit | `FactProviderMonth` | Provider economic outcome |
| Income Growth | Mean income growth percentage | `FactProviderMonth` | Advancement outcome |
| Lock-In Score | Mean lock-in score | `FactProviderMonth` | Repeat behavior and retention |
| Technology Score | Mean technology adoption score | `FactProviderMonth` | Tool usage maturity |
| Advancement Score | Mean advancement score | `FactProviderMonth` | Income/profit/retention composite |
| Agentic Intelligence Score | Mean agentic score | `FactProviderMonth` | AI/forecast maturity |
| Primary Agreement Score | Mean agreement score from primary-vs-synthetic comparison | `FactAgreementScores` | Validation strength |
| Default Risk Band Default Rate | Defaults / cases per band | `FactDefaultRiskBands` | Risk stratification quality |

## Dashboard Pages

### Page 1: Executive Overview

Purpose: Show the headline dissertation story.

Visuals:

- KPI cards: Providers, GMV, Average Ticket, Retention Rate, Average Monthly Profit, Default Rate.
- Line chart: monthly profit and retention over time.
- Clustered bar: treated vs control payout delay, profit, and retention.
- Map or bar: providers by city/region.
- Slicers: region, city, category, treatment status, month.

### Page 2: Embedded Finance Impact

Purpose: Analyze payments, payouts, loans, and intervention effects.

Visuals:

- Line chart: average payout delay by month and treatment status.
- Bar chart: loan offer rate by category and region.
- Matrix: payout amount, working capital gap, loan amount, default rate by category.
- Scatter: payout delay vs monthly profit, colored by treatment.
- KPI cards: payout delay reduction, treated retention, control retention, profit gap.

### Page 3: Provider Economics And Retention

Purpose: Explain provider outcomes.

Visuals:

- Line chart: income growth over time.
- Decomposition tree: monthly profit by region, category, KYC, digital adoption.
- Histogram: churn probability.
- Bar: retention rate by category.
- Matrix: provider economic KPIs by region/city.

### Page 4: DELTA Framework

Purpose: Present the dissertation framework.

Visuals:

- Radar-style custom visual or grouped bar: Data, Embedded Finance, Lock-in, Technology, Advancement, Agentic Intelligence.
- KPI cards: Lock-In Score, Technology Score, Advancement Score, Agentic Intelligence Score.
- Scatter: technology adoption vs advancement score.
- Bar: forecast usage rate by category.
- Table: DELTA variables from `DimProvenance`.

### Page 5: Primary Data Validation

Purpose: Show how the 30 primary responses validate the synthetic design.

Visuals:

- KPI cards: Primary Responses, Primary Credit Need Rate, Primary Digital Adoption, Primary Settlement Pain, Average Agreement Score.
- Bar chart: agreement score by construct.
- Table: primary vs synthetic mean gap.
- Bar: primary respondents by city/category.
- Quote table: interview quote and pain point.

### Page 6: Model Performance

Purpose: Communicate model evolution and leakage handling.

Visuals:

- Line/bar: ROC AUC by model version for adoption and default models.
- Table: precision, recall, F1, ROC by model.
- Bar: top feature importances for default and adoption propensity.
- Callout text box: leaky adoption model excluded due rollout timing leakage.
- Slicers: model type, metric.

### Page 7: Default Risk Segmentation

Purpose: Turn model output into business action.

Visuals:

- Bar: cases by risk band.
- Bar/line combo: default rate by risk band.
- Funnel: default capture rate by risk band.
- Threshold tuning line chart: precision, recall, F1 by threshold.
- KPI cards: High-risk default rate, medium-risk capture rate, ROC AUC.

### Page 8: Data Provenance And Limitations

Purpose: Make synthetic/primary/derived evidence transparent.

Visuals:

- Matrix: dataset, column, source type, DELTA dimension.
- Donut: variables by source type.
- Table: primary-like proxy, secondary, synthetic, derived, engineered classifications.
- Text boxes: limitations and dissertation framing.

## Recommended Report Navigation

Use a left vertical navigation menu:

1. Overview
2. Embedded Finance
3. Provider Economics
4. DELTA
5. Primary Validation
6. Models
7. Default Risk
8. Provenance

## Visual Design Guidance

- Use a clean MBA research aesthetic: white background, muted blue/teal accent, restrained red for risk/default.
- Keep all model-risk visuals clearly labeled as synthetic scenario analysis.
- Add footnotes where primary survey is used: `n = 30 primary pilot responses`.
- Add warning badges on pages using leaky model history: `Leakage-audited; not used for final propensity interpretation`.

## Power BI Implementation Order

1. Load `merchants.csv`, `transactions.csv`, `provider_kpis.csv`, `payouts_loans.csv`.
2. Build `DimDate`, `DimMonth`, `DimMerchant`, `DimPaymentMethod`, `DimLoanStatus`.
3. Merge `provider_kpis.csv` and `payouts_loans.csv` into `FactProviderMonth`.
4. Load primary response and validation CSVs.
5. Load model/risk CSVs.
6. Create relationships.
7. Add DAX measures.
8. Build pages in the order above.
9. Validate totals against CSV row counts.
10. Add provenance/limitation page last.

## Row Count Checks

Create a small QA table or hidden page with these expected counts:

| Table | Expected rows |
|---|---:|
| `DimMerchant` | 1,000 |
| `FactTransactions` | 403,539 |
| `FactProviderMonth` | 12,000 |
| `FactModelReadyProviderMonth` | 12,000 |
| `FactPrimarySurvey` | 30 |
| `FactPrimaryQuotes` | 30 |
| `DimProvenance` | 60 |
| `FactAgreementScores` | 13 |
| `FactDefaultRiskBands` | 3 |
| `FactThresholdTuning` | 99 |

## Dissertation Framing

The dashboard should be described as a decision-support and research-validation artifact. It does not claim real Razorpay or Urban Company administrative data. It combines:

- synthetic provider/payment/loan panel data;
- primary pilot survey validation;
- leakage-audited model outputs;
- transparent DELTA framework provenance.

This is enough to support MBA dissertation analysis, scenario storytelling, and research methodology demonstration.
