"""Reusable status and AI operating-system panels."""

from __future__ import annotations

import html

import streamlit as st


def _escape(value: object) -> str:
    return html.escape(str(value))


def system_health_panel(score: float, label: str = "AI System Health") -> None:
    bounded = max(0.0, min(1.0, float(score)))
    st.markdown(
        f"""
        <div class="uc-card">
          <div class="uc-card-label"><span class="uc-good">*</span>{_escape(label)}</div>
          <div class="uc-card-value">{bounded:.0%}</div>
          <div class="uc-card-delta">Models, datasets, predictions, and report services operational.</div>
          <div class="uc-progress-track"><div class="uc-progress-fill" style="width:{bounded * 100:.0f}%"></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def operational_alert(title: str, detail: str, severity: str = "warn") -> None:
    st.markdown(
        f"""
        <div class="uc-alert">
          <span class="uc-{_escape(severity)}">!</span>
          <strong>{_escape(title)}</strong><br />
          <span>{_escape(detail)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def risk_badge(label: str, tone: str = "accent") -> None:
    st.markdown(f'<span class="uc-badge uc-{tone}">{_escape(label)}</span>', unsafe_allow_html=True)


def ask_data_panel(example: str = "Why is churn increasing? Which region has the highest default risk?") -> None:
    st.markdown(
        f"""
        <div class="uc-ai-panel">
          <div class="uc-panel-title">Ask the data</div>
          <div class="uc-card-delta">Natural-language query surface for future AI analysis workflows.</div>
          <div class="uc-section">{_escape(example)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
