# Streamlit 2026 AI Platform Theme Architecture

Generated: 2026-05-24

## Purpose

The Streamlit app now uses a centralized dark AI operating-system design system inspired by Palantir Foundry, Stripe Analytics, OpenAI enterprise dashboards, Linear, Notion AI, Datadog, Bloomberg Terminal, Tesla Ops, and Google Gemini enterprise UI.

## Theme Files

| File | Purpose |
|---|---|
| `app/styles.css` | Global dark theme, sidebar styling, hero sections, KPI cards, tabs, tables, expanders, and download buttons |
| `app/utils/theme.py` | Shared theme loader, Plotly dark defaults, color palette, page headers, sidebar brand block, and chart styling helper |
| `app/components/cards.py` | Reusable premium KPI cards, status cards, and alert banners |
| `app/components/status.py` | AI system health, operational alerts, risk badges, and "Ask the data" panels |
| `app/components/charts.py` | Centralized themed Plotly chart renderer |

## Palette

| Role | Color |
|---|---|
| Background | `#0F172A` |
| Cards | `#1E293B` |
| Borders | `#334155` |
| Accent | `#38BDF8` / `#22D3EE` |
| Success | `#22C55E` |
| Warning | `#F59E0B` |
| Risk | `#EF4444` |
| Text | `#F8FAFC` / `#CBD5E1` |

## Updated Pages

| Page | Improvements |
|---|---|
| `app/Home.py` | Future Intelligence Platform hero, AI operating-system brief, system health score, executive KPI cards |
| `app/pages/01_Risk_Dashboard.py` | Risk Command Center, operational alert banner, risk-colored charts, recommendation cards |
| `app/pages/02_Predictions.py` | AI Prediction Copilot, ask-the-data panel, probability/confidence cards, styled gauges |
| `app/pages/03_Primary_Insights.py` | Primary Research Intelligence Layer, survey cards, ask-the-data panel, insight callouts |
| `app/pages/04_Model_Performance.py` | AI Model Health Observatory, health score, governance alert, ROC/precision/feature charts |
| `app/pages/06_Admin.py` | System Diagnostics Console, platform health score, dataset/model/prediction diagnostics |
| `app/pages/06_Survey_Insights.py` | Survey Intelligence Command Center, survey cards, ask-the-data panel, primary-vs-secondary comparison |
| `app/pages/07_AI_Report_Generator.py` | AI Executive Report Studio, report cards, ask-the-data panel, PDF controls |

## Before / After Architecture

| Before | After |
|---|---|
| Page-level Streamlit defaults | Centralized 2026 AI platform theme |
| Plain metrics | Glassmorphism KPI and status cards |
| Basic sidebar | Branded operating-system sidebar with navigation matrix and status indicators |
| Isolated dashboards | Unified intelligence surface across risk, predictions, survey, model health, admin, and reports |
| Static interpretation text | Reusable AI insight and ask-the-data panels |
| Ad hoc chart styling | Plotly dark theme with shared typography, transparent backgrounds, and subtle gridlines |

## Validation

Validation performed after the theme update:

- Python compile for all active app pages and shared utilities.
- Streamlit page smoke tests for Home, Risk Dashboard, Predictions, Primary Insights, Model Performance, Admin, Survey Insights, and AI Report Generator.
- Full Streamlit launch with `streamlit run app/Home.py`.
