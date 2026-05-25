# Cleanup Changelog

Generated: 2026-05-24 16:36

## Archived Files

| Old path | New archive path | Reason | Dependency risk |
|---|---|---|---|
| `cleanup_report.md` | `archive/20260524_cleanup/old_reports/cleanup_report.md` | Superseded cleanup report replaced by CHANGELOG_cleanup.md and docs/project_cleanup_inventory.md. | Low |
| `output/embedded_finance_executive_report.pdf` | `archive/20260524_cleanup/old_reports/output/embedded_finance_executive_report.pdf` | Duplicate older executive PDF; output/Executive_Report.pdf is the regenerated final report. | Low |
| `dashboard/UC_Razorpay_Dashboard_v1.pbix` | `archive/20260524_cleanup/deprecated_outputs/dashboard/UC_Razorpay_Dashboard_v1.pbix` | Older small PBIX copy; latest PBIX retained at project root as UC_Razorpay_EmbeddedFinance.pbix. | Medium: Power BI blueprint retained; deployment inventory updated to root PBIX. |
| `app/__pycache__/Home.cpython-314.pyc` | `archive/20260524_cleanup/deprecated_outputs/app/__pycache__/Home.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | Low |
| `app/__pycache__/__init__.cpython-314.pyc` | `archive/20260524_cleanup/deprecated_outputs/app/__pycache__/__init__.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | Low |
| `app/utils/__pycache__/auth.cpython-314.pyc` | `archive/20260524_cleanup/deprecated_outputs/app/utils/__pycache__/auth.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | Low |
| `app/utils/__pycache__/report_generator.cpython-314.pyc` | `archive/20260524_cleanup/deprecated_outputs/app/utils/__pycache__/report_generator.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | Low |
| `app/utils/__pycache__/theme.cpython-314.pyc` | `archive/20260524_cleanup/deprecated_outputs/app/utils/__pycache__/theme.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | Low |
| `app/utils/__pycache__/__init__.cpython-314.pyc` | `archive/20260524_cleanup/deprecated_outputs/app/utils/__pycache__/__init__.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | Low |
| `app/pages/__pycache__/01_Risk_Dashboard.cpython-314.pyc` | `archive/20260524_cleanup/deprecated_outputs/app/pages/__pycache__/01_Risk_Dashboard.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | Low |
| `app/pages/__pycache__/02_Predictions.cpython-314.pyc` | `archive/20260524_cleanup/deprecated_outputs/app/pages/__pycache__/02_Predictions.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | Low |
| `app/pages/__pycache__/03_Primary_Insights.cpython-314.pyc` | `archive/20260524_cleanup/deprecated_outputs/app/pages/__pycache__/03_Primary_Insights.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | Low |
| `app/pages/__pycache__/04_Model_Performance.cpython-314.pyc` | `archive/20260524_cleanup/deprecated_outputs/app/pages/__pycache__/04_Model_Performance.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | Low |
| `app/pages/__pycache__/06_Admin.cpython-314.pyc` | `archive/20260524_cleanup/deprecated_outputs/app/pages/__pycache__/06_Admin.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | Low |
| `app/pages/__pycache__/06_Survey_Insights.cpython-314.pyc` | `archive/20260524_cleanup/deprecated_outputs/app/pages/__pycache__/06_Survey_Insights.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | Low |
| `app/pages/__pycache__/07_AI_Report_Generator.cpython-314.pyc` | `archive/20260524_cleanup/deprecated_outputs/app/pages/__pycache__/07_AI_Report_Generator.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | Low |
| `app/components/__pycache__/cards.cpython-314.pyc` | `archive/20260524_cleanup/deprecated_outputs/app/components/__pycache__/cards.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | Low |
| `app/components/__pycache__/charts.cpython-314.pyc` | `archive/20260524_cleanup/deprecated_outputs/app/components/__pycache__/charts.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | Low |
| `app/components/__pycache__/status.cpython-314.pyc` | `archive/20260524_cleanup/deprecated_outputs/app/components/__pycache__/status.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | Low |
| `app/components/__pycache__/__init__.cpython-314.pyc` | `archive/20260524_cleanup/deprecated_outputs/app/components/__pycache__/__init__.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | Low |
| `src/__pycache__/mba_ba_ml_improvements.cpython-314.pyc` | `archive/20260524_cleanup/deprecated_outputs/src/__pycache__/mba_ba_ml_improvements.cpython-314.pyc` | Generated Python bytecode cache; safe to regenerate. | Low |

## Updated Reports And Wording

- Regenerated `output/Executive_Report.pdf` with corrected growth interpretation.
- Updated `app/utils/report_generator.py` so future PDFs describe churn-adjusted and active-provider growth separately.
- Updated `README.md` with Business Analysis, FinTech Analytics, AI Decision Support, model caveats, and growth KPI definitions.
- Updated deployment inventory to point to the latest root PBIX: `UC_Razorpay_EmbeddedFinance.pbix`.

## KPI Wording

- `Average income growth` relabeled as `Churn-adjusted growth` in generated reports.
- Added active-provider, retained-provider, and median growth definitions.

## Business Interpretation

Embedded finance and digital adoption appear more strongly associated with operational resilience, retention, liquidity stability, and profit continuity than direct income expansion. Growth appears constrained by churn and provider inactivity rather than technology failure.