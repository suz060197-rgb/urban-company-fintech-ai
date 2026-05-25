# Predictions Export Report

Generated provider-month prediction exports from existing artifacts in `output/models/`.
No models were retrained.

Provider-month scoring rows: 12000

## Model Exports

| Model | Artifact | Output | Target | Threshold | Rows | Missing feature fallbacks |
|---|---|---|---|---:|---:|---:|
| churn_prediction | `output/models/churn_prediction.pkl` | `output/churn_predictions.csv` | churn_target | 0.38 | 12000 | 0 |
| embedded_finance_adoption | `output/models/embedded_finance_adoption.pkl` | `output/adoption_predictions.csv` | adoption_target | 0.37 | 12000 | 0 |
| loan_default_prediction | `output/models/loan_default_prediction.pkl` | `output/default_predictions.csv` | default_target | 0.13 | 12000 | 0 |

## Feature Alignment

All saved model features were reconstructed from the current datasets.

## Default Risk Bands

| Risk band | Rows | Share | Mean default probability |
|---|---:|---:|---:|
| Low | 12000 | 1.000 | 0.088 |

## Notes

- `risk_scores.csv` uses the requested bands: Low `<0.30`, Medium `0.30-0.70`, High `>=0.70`.
- Predictions are provider-month records, keyed by `provider_id` and `month`.
- The default risk file enriches default probabilities with `city` and `business_type` from `merchants.csv`.