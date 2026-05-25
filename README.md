# Razorpay Embedded Finance x Urban Company Providers

## AI Fintech Dissertation Application

This repository contains a dissertation-grade AI analytics application for studying:

> **How Razorpay-style embedded finance affects Urban Company-style service providers in India.**

The project combines synthetic operational datasets, primary survey responses, machine-learning predictions, Power BI planning artifacts, and a Streamlit executive application. It is designed for MBA dissertation analysis where real platform data is unavailable, confidential, or impractical to collect at scale.

## Project Title

**Razorpay Embedded Finance x Urban Company Providers: Business Analysis, FinTech Analytics, AI Decision Support, and Primary Research Intelligence**

## Business Problem

Urban Company-style service providers depend on regular bookings, fast settlement, repeat customers, and short-term liquidity. Embedded finance products such as digital payments, faster payouts, and working-capital loans can improve provider cash flow, but they may also introduce credit risk, platform lock-in, and operational dependency.

This project supports business-analysis and AI decision-support questions:

- Which providers are at higher default or churn risk?
- Does embedded finance appear to support liquidity, retention, and operational resilience before measurable income expansion?
- Which providers are more likely to adopt embedded finance?
- How do primary survey findings compare with synthetic operational trends?
- How can dashboards and model outputs support managerial decisions?

Current evidence should be interpreted carefully: embedded finance and digital adoption appear more strongly associated with operational resilience, retention, liquidity stability, and profit continuity than direct income expansion. Growth appears constrained by churn and provider inactivity rather than technology failure.

## Datasets

Final production datasets are stored in `data/`.

| Dataset | Purpose |
|---|---|
| `data/merchants.csv` | Provider profile, region, city, category, income, digital adoption, AI usage, payment success, and product adoption |
| `data/transactions.csv` | Synthetic customer payment transactions, ticket values, ratings, payment methods, settlement delay, completion, cancellations, and tips |
| `data/payouts_loans.csv` | Provider-month payouts, working-capital gaps, loan offers, loan amounts, disbursal timing, repayments, and defaults |
| `data/provider_kpis.csv` | Provider-month growth, profit, retention, churn probability, treatment timing, lock-in, technology, advancement, and agentic intelligence scores |
| `data/primary_responses_clean.csv` | Cleaned primary survey responses mapped to provider-level dissertation constructs |

The synthetic data follows the DELTA framework:

- **Data**
- **Embedded Finance**
- **Lock-in**
- **Technology**
- **Advancement**
- **Agentic Intelligence**

## Primary Research

The app includes a primary research layer using `data/primary_responses_clean.csv`.

Primary variables include:

- Monthly income estimates
- Transaction volume
- Digital adoption score
- UPI usage
- Cashflow issues
- Settlement delay impact
- Faster payout impact
- Business credit need
- AI tool usage
- Business growth after digital payments
- Repeat customer change

Mapping files:

- `docs/primary_secondary_mapping.csv`
- `docs/primary_secondary_compatibility_report.md`

These documents connect survey variables with synthetic operational variables such as `technology_adoption_score`, `working_capital_gap`, `payout_delay_days`, and `advancement_score`.

## ML Models

Final model artifacts are stored in `output/models_final/`.

| Model | File | Task |
|---|---|---|
| Loan default prediction | `loan_default_model_final.pkl` | Predict default risk using leakage-safe features |
| Churn prediction | `churn_model_final.pkl` | Predict provider churn risk |
| Embedded finance adoption | `adoption_model_final.pkl` | Predict adoption propensity |
| Income growth prediction | `income_growth_model_final.pkl` | Forecast future income growth |

Final prediction outputs are stored in `output/predictions_final/`.

| Output | Purpose |
|---|---|
| `default_predictions_final.csv` | Default probability and class predictions |
| `churn_predictions_final.csv` | Churn probability and class predictions |
| `adoption_predictions_final.csv` | Embedded-finance adoption predictions |
| `income_growth_predictions_final.csv` | Income growth forecasts |
| `output/risk_scores.csv` | Dashboard-ready provider risk bands |

Model documentation:

- `docs/final_model_metrics.md`
- `output/models_final/final_model_metrics.csv`
- Feature-importance CSVs in `output/models_final/`

### Model Caveats

| Model | Caveat |
|---|---|
| Loan default prediction | Usable with caution because defaults are rare and precision is low; risk bands should support human review, not automated credit denial. |
| Churn prediction | Strong discrimination; use for retention operations and intervention prioritization. |
| Embedded finance adoption | Improved with primary-informed and operational features; still interpret as propensity, not causal adoption proof. |
| Income growth prediction | Requires churn-adjusted interpretation because inactive provider-months are coded as `-100%` growth. |

### Growth KPI Definitions

| KPI | Definition | Interpretation |
|---|---|---|
| Churn-adjusted growth | Average `income_growth_pct` across all provider-months, including inactive provider-months coded as `-100%`. | Best for portfolio-level view including churn drag. |
| Growth among active providers | Average `income_growth_pct` where `active_provider_month_flag == True`. | Better indicator of operating performance among providers still active on the platform. |
| Retained-provider growth | Average `income_growth_pct` among retained provider-months. | Links growth interpretation to retention health. |
| Median provider growth | Median `income_growth_pct`. | Reduces distortion from churn and extreme negative outcomes. |

Latest audit finding: retention is the strongest positive growth driver (`+0.87` correlation), while churn probability is the strongest negative driver (`-0.90`). UPI usage has a positive operational effect, but technology adoption alone does not guarantee income expansion.

## Dashboard Pages

The Streamlit app is located in `app/`.

| Page | File | Purpose |
|---|---|---|
| Home | `app/Home.py` | Executive landing page with provider count, high-risk share, retention, and navigation |
| Risk Dashboard | `app/pages/01_Risk_Dashboard.py` | Risk bands, default/churn distributions, regional/category risk, and recommendations |
| Predictions | `app/pages/02_Predictions.py` | Provider-level prediction engine with probability cards, gauges, drivers, and CSV export |
| Primary Insights | `app/pages/03_Primary_Insights.py` | Primary survey findings, cashflow pain, credit need, digital adoption, and survey summary export |
| Model Performance | `app/pages/04_Model_Performance.py` | ROC, precision, recall, F1, confusion matrix summaries, feature importance, and leakage commentary |
| Admin | `app/pages/06_Admin.py` | Dataset status, model status, prediction output checks, archive scanner, and system health |
| Survey Insights | `app/pages/06_Survey_Insights.py` | Expanded survey analytics and primary-vs-secondary comparison |
| AI Report Generator | `app/pages/07_AI_Report_Generator.py` | Executive PDF report generation using ReportLab |

Protected pages use a simple Streamlit session-state login. Default demo credentials are:

```text
username: admin
password: admin123
```

Credentials can be overridden with:

```bash
set UC_APP_USERNAME=your_username
set UC_APP_PASSWORD=your_password
```

## App Architecture

```text
                         +-----------------------------+
                         |        Streamlit App         |
                         |          app/Home.py         |
                         +--------------+--------------+
                                        |
        +-------------------------------+-------------------------------+
        |                               |                               |
+-------v--------+              +-------v--------+              +-------v--------+
| Dashboard Pages |              | App Utilities  |              | Auth Controls  |
| app/pages/      |              | app/utils/     |              | session_state  |
+-------+--------+              +-------+--------+              +----------------+
        |                               |
        |                               |
+-------v-------------------------------v---------------------------------------+
|                            Final Artifacts                                    |
|                                                                               |
|  data/                         output/                     docs/              |
|  - merchants.csv               - risk_scores.csv            - metrics docs     |
|  - transactions.csv            - predictions_final/         - mapping docs     |
|  - payouts_loans.csv           - models_final/              - audit docs       |
|  - provider_kpis.csv           - executive PDF                                  |
|  - primary_responses_clean.csv                                                  |
+-----------------------------------+-------------------------------------------+
                                    |
                                    v
                         +-----------------------------+
                         | Power BI / Dissertation Use |
                         | dashboard/ + final reports  |
                         +-----------------------------+
```

## Folder Structure

```text
urban_company_fintech_mba/
├── app/
│   ├── Home.py
│   ├── pages/
│   ├── utils/
│   └── requirements.txt
├── data/
│   ├── merchants.csv
│   ├── transactions.csv
│   ├── payouts_loans.csv
│   ├── provider_kpis.csv
│   └── primary_responses_clean.csv
├── output/
│   ├── models_final/
│   ├── predictions_final/
│   ├── risk_scores.csv
│   ├── default_predictions.csv
│   ├── churn_predictions.csv
│   ├── adoption_predictions.csv
│   └── Executive_Report.pdf
├── docs/
│   ├── final_model_metrics.md
│   ├── primary_secondary_mapping.csv
│   ├── primary_secondary_compatibility_report.md
│   ├── data_recency_audit.md
│   └── deployment_inventory.md
├── dashboard/
│   ├── powerbi_blueprint.md
│   └── Power BI blueprint and dashboard support files
├── src/
│   ├── generate_uc_dataset.py
│   ├── train_final_models.py
│   ├── validation.py
│   └── preprocessing / feature scripts
├── archive/
├── requirements.txt
└── README.md
```

## How To Run Locally

Create and activate a Python environment, then install production requirements:

```bash
pip install -r requirements.txt
```

Launch the app:

```bash
streamlit run app/Home.py
```

Open the local URL shown by Streamlit, usually:

```text
http://localhost:8501
```

## Deployment

Recommended deployment steps:

1. Use `requirements.txt` as the production dependency file.
2. Keep the following folders in the deployment bundle:
   - `app/`
   - `data/`
   - `output/models_final/`
   - `output/predictions_final/`
   - `output/risk_scores.csv`
   - `output/default_predictions.csv`
   - `output/churn_predictions.csv`
   - `output/adoption_predictions.csv`
   - `docs/`
3. Set authentication environment variables before deployment:

```bash
set UC_APP_USERNAME=admin
set UC_APP_PASSWORD=change_this_password
```

4. Run:

```bash
streamlit run app/Home.py
```

For Streamlit Community Cloud, use:

```text
Main file path: app/Home.py
Requirements file: requirements.txt
```

## Screenshots Placeholder

Add screenshots here before submission or viva presentation.

```text
screenshots/
├── 01_home.png
├── 02_risk_dashboard.png
├── 03_predictions.png
├── 04_primary_insights.png
├── 05_model_performance.png
├── 06_admin.png
└── 07_ai_report_generator.png
```

Suggested screenshots:

- Home KPI view
- Risk dashboard with filters
- Prediction engine for a selected provider
- Primary research insight panel
- Model performance comparison
- AI-generated PDF report download
- Power BI dashboard overview

## Future Enhancements

- Replace demo authentication with enterprise SSO or role-based access control.
- Add live database support instead of CSV-only loading.
- Add scheduled retraining with model registry metadata.
- Add drift monitoring for risk scores, default rates, and survey-to-synthetic agreement.
- Add SHAP-style explainability if additional dependencies are allowed.
- Add PDF charts and page-level screenshots into the AI report generator.
- Add Power BI refresh automation.
- Add confidence intervals for primary survey findings.
- Add deployment configuration for Docker, Azure App Service, or Streamlit Community Cloud.

## Important Limitation

The operational datasets are synthetic and calibrated to public Indian fintech trends and dissertation assumptions. The project is suitable for research design, dissertation demonstration, dashboard prototyping, and methodology explanation. It should not be presented as estimating actual Razorpay or Urban Company causal effects without real production data access and formal causal validation.
