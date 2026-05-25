# Default Risk Segmentation

Generated on 2026-05-22.

## Scope

Segments leakage-safe default model probabilities into low, medium, and high risk bands. No model retraining was performed.

Inputs:

- Model: `output/default_model_safe/loan_default_prediction_leakage_safe.pkl`
- Scored sample: held-out test split recreated with seed `42`
- Target: `default_flag`

## Band Definitions

| Risk band | Probability range | Business use |
|---|---:|---|
| Low risk | `< 0.46` | Standard servicing; no special intervention. |
| Medium risk | `0.46 to < 0.96` | Review queue; proactive reminders or lighter credit controls. |
| High risk | `>= 0.96` | Priority review; manual underwriting/collections attention. |

These thresholds align with the prior threshold tuning: `0.46` was the high-recall threshold and `0.96` was the balanced-F1 threshold.

## Risk Distribution And Default Rates

| risk_band | cases | case_share | defaults | default_rate | default_capture_rate | mean_probability | median_probability | min_probability | max_probability |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Low risk | 2347 | 0.865 | 1 | 0.000 | 0.042 | 0.086 | 0.057 | 0.001 | 0.455 |
| Medium risk | 313 | 0.115 | 18 | 0.058 | 0.750 | 0.754 | 0.763 | 0.463 | 0.960 |
| High risk | 54 | 0.020 | 5 | 0.093 | 0.208 | 0.981 | 0.979 | 0.960 | 0.999 |

## Score Quantiles

| quantile | score |
| --- | --- |
| 0.010 | 0.004 |
| 0.050 | 0.010 |
| 0.100 | 0.015 |
| 0.250 | 0.033 |
| 0.500 | 0.070 |
| 0.750 | 0.165 |
| 0.900 | 0.676 |
| 0.950 | 0.884 |
| 0.990 | 0.978 |

## Model Context

| Metric | Value |
|---|---:|
| ROC AUC | 0.926 |
| Total test cases | 2714 |
| Actual defaults | 24 |
| Overall default rate | 0.009 |

## Business Interpretation

- Low risk contains `2347` cases (86.5%) and `1` observed defaults. It is suitable for standard servicing.
- Medium risk contains `313` cases (11.5%) and captures `75.0%` of defaults. This is the broad screening group if the business wants high recall.
- High risk contains `54` cases (2.0%) with a higher observed default rate than the portfolio average. This is the best band for constrained manual review capacity.

Because defaults are rare, even the high-risk band has modest precision. The segmentation is most useful for ranking and workflow prioritization, not automatic loan rejection.

## Recommended Use

- Use `Low risk` for normal payout/loan servicing.
- Use `Medium risk` for automated nudges, repayment reminders, or light-touch risk monitoring.
- Use `High risk` for manual review, loan-size caps, stricter repayment checks, or collection-prevention workflows.

## Caveat

The model is leakage-safe relative to repayment-derived features, but the dataset is synthetic. Treat these bands as dissertation-ready scenario segmentation rather than real underwriting policy.