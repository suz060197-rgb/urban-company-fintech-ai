# Assumptions and Limitations

## Objective

This project creates synthetic datasets for studying how Razorpay-style embedded finance could affect Urban Company-style service providers in India through payments, faster payouts, working-capital loans, digital tools, and agentic AI assistance.

The core causal pathway represented in the simulator is:

embedded finance -> faster payouts -> better liquidity -> lower churn -> higher retention -> higher income.

The upgraded dissertation structure uses the DELTA framework:

- Data
- Embedded Finance
- Lock-in
- Technology
- Advancement
- Agentic Intelligence

## Synthetic Population

- Providers represent Urban Company-style service professionals, not actual Urban Company workers.
- Cities are grouped into broad Indian regions: North, West, South, and East.
- Service categories include beauty and wellness, home cleaning, appliance repair, plumbing/electrical, and premium salon/spa services.
- Provider tenure is skewed, with many newer providers and fewer very long-tenure providers.
- KYC completion is high because embedded finance eligibility typically requires identity and compliance checks.

## Public Data Priors

The generator uses qualitative public-market priors rather than proprietary platform data:

- UPI has the highest payment share in India.
- Digital payment adoption is stronger among embedded-finance users.
- Platform services have meaningful commission rates that vary by category.
- Service providers may face liquidity pressure when payout delays are longer.
- Shorter payout cycles can reduce churn risk.
- Working-capital offers are more likely for KYC-complete providers with higher payout volumes.
- Loan default risk falls modestly when payout volumes and embedded-finance visibility improve.
- AI and agentic intelligence variables are synthetic adoption proxies calibrated from digital readiness, not public measured adoption rates.

## Treatment Design

- `treatment_flag` identifies providers assigned embedded finance access.
- `treatment_start_month` identifies when treatment begins.
- Without `--phased_rollout`, treated providers begin in month 1.
- With `--phased_rollout`, treated providers start in staggered months, which improves pre/post research design.
- Treatment is available only to providers who pass KYC in the current implementation.

## Behavioral Assumptions

- Treatment slightly increases digital payment share and reduces cash use.
- Treatment reduces payout delay from several days to roughly same-day or next-day settlement.
- Faster payouts improve liquidity and reduce provider churn probability.
- Working-capital access can increase income by helping providers accept more jobs or manage expenses.
- Defaults remain possible and are affected by payout volume, treatment status, and random provider-level variation.
- Ratings, cancellations, repeat-customer rates, and ticket sizes affect income and churn.
- Digital tool usage improves service completion and transaction reliability in the synthetic mechanism.
- AI adoption and agent usage modestly improve advancement outcomes through better planning, forecasting, and operational consistency.
- Lock-in is modeled as a composite of repeat customers, product adoption, retention, and customer experience.

## DELTA Variable Assumptions

- `payment_success_rate` captures expected payment reliability and is influenced by KYC, digital usage, and provider readiness.
- `transaction_velocity` captures expected monthly transaction throughput.
- `multi_product_adoption` counts adoption across embedded finance and digital/AI products.
- `digital_tool_usage` captures platform tool usage such as digital scheduling, payment links, reconciliation, and dashboards.
- `ai_adoption_score` captures synthetic use of AI-assisted recommendations or decision support.
- `agent_usage_flag` identifies providers who use agentic support for planning, support, or forecasting.
- `settlement_delay` is lower for treated providers and for providers with stronger digital readiness.
- `service_completion_rate` is higher when cancellations are less likely and digital maturity is stronger.
- `working_capital_gap` measures the estimated shortfall between monthly liquidity needs and available payout buffers.
- `loan_disbursal_time` is faster for treated providers with embedded finance access.
- `default_flag` is derived from the synthetic monthly loan status.
- `lock_in_score`, `technology_adoption_score`, `advancement_score`, and `agentic_intelligence_score` are composite provider-month indices bounded from 0 to 1.
- `forecast_usage` is a boolean indicator for AI-enabled demand, income, or cash-flow forecast usage.

## Dataset Limitations

- No real Razorpay, Urban Company, or provider-level confidential data is used.
- Parameter values are plausible assumptions, not empirical estimates.
- Treatment assignment is simplified and may not reflect actual operational rollout.
- The generator models causal mechanisms directly, so analysis should be framed as synthetic causal-design testing.
- The monthly panel keeps rows for churned providers, with zero payouts and non-retention indicators, to preserve panel completeness.
- `payout_delay_days` is `NaN` only when `active_provider_month_flag` is `False`; this means payout delay is not applicable after churn.
- Faker is optional; if unavailable, deterministic merchant IDs are generated instead.
- Composite DELTA scores are intended for research design and scenario analysis, not as validated psychometric or operational indices.

## Recommended Dissertation Framing

Use this dataset to demonstrate:

- how an MBA dissertation would structure platform-fintech hypotheses;
- how synthetic data can support method development before real data access;
- how embedded-finance mechanisms can be decomposed into payouts, loans, retention, and income;
- how validation reports can document whether the synthetic panel is credible enough for analysis.

Avoid claiming that the generated numbers measure actual market effects.
