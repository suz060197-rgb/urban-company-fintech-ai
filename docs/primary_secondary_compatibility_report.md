# Primary-Secondary Compatibility Report

Generated on 2026-05-22.

## Compatibility Score

- Overall compatibility score: `0.694` out of `1.000`
- Primary column coverage: `100.0%`
- Compatibility interpretation: `Medium`

The score is the mean of row-level mapping scores where the cleaned primary column is present.

## Dataset-Level Scores

| Synthetic dataset | Mean score |
|---|---:|
| merchants.csv | 0.787 |
| payouts_loans.csv | 0.606 |
| provider_kpis.csv | 0.635 |

## Mapping Bands

| Band | Count |
|---|---:|
| High | 11 |
| Medium | 16 |
| Low | 5 |
| Context only | 2 |

## Validation

- PASS `data/primary_responses_clean.csv` was read successfully.
- PASS generated `34` primary-secondary mapping rows.
- PASS all mapped primary columns are present in the cleaned primary dataset.

## Interpretation

The cleaned primary survey is compatible with the synthetic datasets for pilot validation and calibration.
The strongest matches are city, region, business category, tenure, income midpoint, transaction volume, digital adoption, repeat-customer change, and AI usage.
Lower-scoring mappings are mostly qualitative or perception-based fields that support interpretation but should not be treated as exact administrative measurements.