# Minimum Viable Primary Survey

Generated on 2026-05-21.

## Purpose

This survey is designed to collect a small primary dataset of 20 service-provider responses that can validate whether the synthetic variables in the Urban Company embedded-finance dissertation project are directionally realistic.

Target respondents: Indian app-based or platform-enabled service providers, such as beauty, salon, home cleaning, appliance repair, plumbing, electrical, or similar gig/service professionals.

Target completion time: under 5 minutes.

Recommended sample size for pilot validation: 20 completed responses.

## Consent Script

This short survey asks about your work as a service provider, payments, payouts, loans, platform tools, and technology use. It should take less than 5 minutes. Your answers will be used only for academic research validation. Please do not share private account numbers, customer names, phone numbers, or exact platform login details.

Consent question:

Do you agree to participate in this short academic survey?

- Yes
- No

Only continue if the respondent answers `Yes`.

## Likert Scale

Use this same 5-point scale for agreement questions:

| Value | Label |
|---:|---|
| 1 | Strongly disagree |
| 2 | Disagree |
| 3 | Neither agree nor disagree |
| 4 | Agree |
| 5 | Strongly agree |

For frequency questions, use:

| Value | Label |
|---:|---|
| 1 | Never |
| 2 | Rarely |
| 3 | Sometimes |
| 4 | Often |
| 5 | Always |

## Survey Questions

| QID | Question | Response format | Maps to synthetic variables |
|---|---|---|---|
| Q1 | Which city do you mainly work in? | Multiple choice plus Other: Delhi NCR, Mumbai, Bengaluru, Hyderabad, Chennai, Pune, Kolkata, Ahmedabad, Jaipur, Lucknow, Chandigarh, Kochi, Bhubaneswar, Other | `city`, `region` |
| Q2 | What is your main service category? | Multiple choice: Beauty/wellness, Salon/spa premium, Home cleaning, Appliance repair, Plumbing/electrical, Other | `category` |
| Q3 | How long have you been working through apps, marketplaces, or digital booking platforms? | Multiple choice: Less than 3 months, 3-12 months, 1-2 years, 2-4 years, More than 4 years | `tenure_days` |
| Q4 | In a typical month, what is your approximate income from service work? | Multiple choice: Below Rs 15,000; Rs 15,000-30,000; Rs 30,001-50,000; Rs 50,001-75,000; Above Rs 75,000 | `monthly_income`, `monthly_profit` |
| Q5 | What is your approximate average customer order value? | Multiple choice: Below Rs 300; Rs 300-600; Rs 601-1,000; Rs 1,001-1,500; Above Rs 1,500 | `avg_ticket`, `amount` |
| Q6 | About how many customer jobs or bookings do you complete in a typical month? | Multiple choice: 0-10, 11-25, 26-50, 51-75, More than 75 | `transaction_velocity`, `service_completion_rate` |
| Q7 | Which payment method do customers use most often with you? | Single choice: UPI, Cash, Card, Wallet, Netbanking, Platform wallet/settlement, Other | `payment_method`, `payment_success_rate` |
| Q8 | Digital payments from customers are usually successful without retries or failures. | 1-5 agreement Likert | `payment_success_rate`, `cancellation_flag` |
| Q9 | How long does it usually take for your platform or intermediary payout to reach your bank account after work is completed? | Multiple choice: Same day, 1 day, 2-3 days, 4-7 days, More than 7 days, Not applicable | `payout_delay_days`, `settlement_delay` |
| Q10 | Faster payouts help me accept more work or manage expenses better. | 1-5 agreement Likert | `working_capital_gap`, `income_growth_pct`, `advancement_score` |
| Q11 | In the last 6 months, were you offered a short-term loan, advance, or working-capital support through a platform, payment app, bank, or fintech provider? | Single choice: Yes accepted, Yes but declined, No, Not sure | `loan_offer_flag`, `loan_amount`, `loan_status`, `multi_product_adoption` |
| Q12 | If you used a loan or advance, repayment was manageable from my service income. | 1-5 agreement Likert plus Not applicable | `repayment_amount`, `default_flag`, `working_capital_gap` |
| Q13 | I expect to continue using my main service platform or digital work channel for the next 6 months. | 1-5 agreement Likert | `retention_flag`, `churn_probability`, `lock_in_score` |
| Q14 | Repeat customers are an important part of my monthly work. | 1-5 agreement Likert | `repeat_customer_rate`, `lock_in_score` |
| Q15 | How often do you use digital tools such as app dashboards, job calendars, automated reminders, payment links, or earnings reports? | 1-5 frequency Likert | `digital_tool_usage`, `technology_adoption_score` |
| Q16 | How often do you use AI or automated recommendations for pricing, demand planning, customer messages, loan planning, or work scheduling? | 1-5 frequency Likert | `ai_adoption_score`, `agent_usage_flag`, `agentic_intelligence_score`, `forecast_usage` |
| Q17 | Overall, digital payments, faster payouts, or loans have improved my monthly income. | 1-5 agreement Likert | `income_growth_pct`, `monthly_profit`, `advancement_score` |

## Optional Open-Text Prompt

Use only if time remains:

What is the biggest financial challenge you face as a service provider?

This can help interpret `working_capital_gap`, `payout_delay_days`, `loan_offer_flag`, and `retention_flag`, but it is not required for the 5-minute version.

## Dataset Variable Mapping

| Synthetic variable group | Survey validation items | Validation role |
|---|---|---|
| `region`, `city`, `category` | Q1, Q2 | Checks whether synthetic provider mix resembles reachable respondents. |
| `tenure_days` | Q3 | Validates tenure distribution bins. |
| `monthly_income`, `monthly_profit` | Q4 | Validates monthly income and broad profit realism. |
| `avg_ticket`, `amount` | Q5 | Validates service ticket-size ranges. |
| `transaction_velocity` | Q6 | Validates monthly booking volume. |
| `payment_method`, `payment_success_rate` | Q7, Q8 | Validates digital payment adoption and reliability assumptions. |
| `payout_delay_days`, `settlement_delay` | Q9 | Validates payout timing assumptions. |
| `working_capital_gap`, `income_growth_pct`, `advancement_score` | Q10, Q17 | Validates liquidity-to-income mechanism. |
| `loan_offer_flag`, `loan_amount`, `loan_status` | Q11 | Validates working-capital access and take-up. |
| `repayment_amount`, `default_flag` | Q12 | Provides a soft proxy for repayment stress, not a direct default measure. |
| `retention_flag`, `churn_probability` | Q13 | Validates expected platform continuation. |
| `repeat_customer_rate`, `lock_in_score` | Q14 | Validates repeat-customer and lock-in logic. |
| `digital_tool_usage`, `technology_adoption_score` | Q15 | Validates technology dimension. |
| `ai_adoption_score`, `agent_usage_flag`, `agentic_intelligence_score`, `forecast_usage` | Q16 | Validates agentic intelligence dimension. |
| `multi_product_adoption` | Q7, Q11, Q15, Q16 | Approximate count of digital payments, finance, digital tools, and AI/forecast use. |

## Suggested Survey Coding

| Survey response | Coding suggestion |
|---|---|
| Tenure bins | Convert to approximate days: 45, 180, 545, 1095, 1825. |
| Monthly income bins | Use midpoint values: 10000, 22500, 40000, 62500, 85000. |
| Average ticket bins | Use midpoint values: 200, 450, 800, 1250, 1800. |
| Monthly job bins | Use midpoint values: 5, 18, 38, 63, 85. |
| Payout delay bins | Use days: 0, 1, 2.5, 5.5, 8. |
| Likert agreement | Keep as 1-5; optionally rescale to 0-1 using `(value - 1) / 4`. |
| Frequency Likert | Keep as 1-5; optionally rescale to 0-1 using `(value - 1) / 4`. |
| Loan offer | Accepted = offered and adopted; declined = offered but not adopted; no = not offered. |
| Repayment manageability | Low scores indicate higher repayment stress; do not label as actual default. |

## Analysis Plan

1. Screen responses.

Remove non-consenting respondents and responses with large missing sections. Keep `Not applicable` responses as missing only for the specific mapped variable.

2. Create survey-derived validation variables.

Construct approximate survey measures:

- `survey_monthly_income`
- `survey_avg_ticket`
- `survey_transaction_velocity`
- `survey_payout_delay_days`
- `survey_payment_success_score`
- `survey_digital_tool_usage`
- `survey_ai_usage_score`
- `survey_retention_intent`
- `survey_repeat_customer_score`
- `survey_liquidity_benefit_score`
- `survey_repayment_stress_score`

3. Compare survey ranges to synthetic data.

For each mapped variable, compare:

- survey median vs synthetic median
- survey interquartile range vs synthetic interquartile range
- survey minimum/maximum bins vs synthetic 5th/95th percentiles
- share using UPI or other digital methods vs synthetic payment-method shares
- share reporting same-day or next-day payout vs synthetic payout-delay distribution
- share offered or accepting credit vs synthetic `loan_offer_flag` and `loan_status`

4. Validate DELTA dimensions.

Use simple 20-response pilot checks:

- Data: income, ticket size, transaction volume, payment method.
- Embedded Finance: payout delay, loan offer, repayment manageability.
- Lock-in: repeat customers and intention to continue.
- Technology: digital tool frequency.
- Advancement: perceived income improvement.
- Agentic Intelligence: AI or automated recommendation use.

5. Identify calibration gaps.

Flag a synthetic variable as needing recalibration when the survey median is outside the synthetic interquartile range, or when a categorical share differs by more than 20 percentage points.

6. Interpret carefully.

With only 20 responses, do not run causal inference. Use the survey as a face-validity and calibration pilot. The results can support dissertation methodology by showing whether the synthetic generator is directionally plausible, but not by proving real market effects.

## Minimum Viable Fielding Plan

- Target `n = 20` respondents.
- Aim for at least 3 service categories represented.
- Aim for at least 3 cities or regions represented.
- Collect responses using a simple mobile form.
- Avoid collecting names, phone numbers, account details, exact addresses, loan account IDs, or customer identities.
- Keep all questions optional except consent, city, category, and main work tenure.

## Recommended Dissertation Wording

This dissertation uses a 20-response primary pilot survey to validate the plausibility of synthetic variables used in the DELTA framework. The survey does not replace real transaction, payout, or loan records. It provides directional evidence on whether provider income, payout delay, credit access, digital tool use, retention intent, and AI adoption assumptions are realistic enough for synthetic scenario analysis.
