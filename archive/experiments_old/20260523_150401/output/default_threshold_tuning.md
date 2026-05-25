# Default Threshold Tuning

Generated on 2026-05-22.

## Scope

This audit tunes classification thresholds for the leakage-safe default model without retraining model weights.

- Model: `output/default_model_safe/loan_default_prediction_leakage_safe.pkl`
- ROC AUC: `0.926`
- Saved model threshold: `0.690`

## Current Saved Threshold

| Metric | Value |
|---|---:|
| threshold | 0.690 |
| precision | 0.054 |
| recall | 0.583 |
| f1 | 0.098 |
| f2 | 0.196 |
| accuracy | 0.905 |
| tp | 14.000 |
| fp | 247.000 |
| fn | 10.000 |
| tn | 2443.000 |
| predicted_positive_rate | 0.096 |

## Recommended Operating Thresholds

| strategy | threshold | precision | recall | f1 | f2 | accuracy | tp | fp | fn | tn | predicted_positive_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| balanced_f1 | 0.960 | 0.093 | 0.208 | 0.128 | 0.167 | 0.975 | 5.000 | 49.000 | 19.000 | 2641.000 | 0.020 |
| high_recall_recall_ge_0_80 | 0.460 | 0.063 | 0.958 | 0.118 | 0.248 | 0.873 | 23.000 | 344.000 | 1.000 | 2346.000 | 0.135 |
| high_precision_min_3_tp | 0.980 | 0.115 | 0.125 | 0.120 | 0.123 | 0.984 | 3.000 | 23.000 | 21.000 | 2667.000 | 0.010 |

## Threshold Comparison Table

| threshold | precision | recall | f1 | f2 | accuracy | tp | fp | fn | tn | predicted_positive_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.100 | 0.023 | 1.000 | 0.045 | 0.106 | 0.626 | 24.000 | 1015.000 | 0.000 | 1675.000 | 0.383 |
| 0.300 | 0.052 | 1.000 | 0.099 | 0.215 | 0.838 | 24.000 | 439.000 | 0.000 | 2251.000 | 0.171 |
| 0.500 | 0.058 | 0.833 | 0.108 | 0.226 | 0.878 | 20.000 | 326.000 | 4.000 | 2364.000 | 0.127 |
| 0.690 | 0.054 | 0.583 | 0.098 | 0.196 | 0.905 | 14.000 | 247.000 | 10.000 | 2443.000 | 0.096 |
| 0.700 | 0.055 | 0.583 | 0.100 | 0.199 | 0.907 | 14.000 | 242.000 | 10.000 | 2448.000 | 0.094 |
| 0.800 | 0.052 | 0.417 | 0.092 | 0.172 | 0.927 | 10.000 | 184.000 | 14.000 | 2506.000 | 0.071 |
| 0.900 | 0.057 | 0.292 | 0.095 | 0.160 | 0.951 | 7.000 | 116.000 | 17.000 | 2574.000 | 0.045 |

## Interpretation

- `balanced_f1` is the best default choice when false positives and false negatives both matter.
- `high_recall_recall_ge_0_80` is useful for screening, where missing likely defaults is costly.
- `high_precision_min_3_tp` is useful for tighter intervention queues, but it catches fewer true defaults.

Because defaults are rare, precision remains low even at stronger thresholds. Operationally, this model should be used to rank risk or trigger review, not as an automatic rejection rule.