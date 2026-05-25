"""Reusable premium dashboard cards."""

from __future__ import annotations

import html

import streamlit as st


def _escape(value: object) -> str:
    return html.escape(str(value))


def metric_card(
    label: str,
    value: object,
    delta: str = "",
    icon: str = "*",
    tone: str = "accent",
) -> None:
    st.markdown(
        f"""
        <div class="uc-card">
          <div class="uc-card-label"><span class="uc-{tone}">{_escape(icon)}</span>{_escape(label)}</div>
          <div class="uc-card-value">{_escape(value)}</div>
          <div class="uc-card-delta">{_escape(delta)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_card(title: str, body: str, tone: str = "accent", icon: str = "*") -> None:
    st.markdown(
        f"""
        <div class="uc-card small">
          <div class="uc-card-label"><span class="uc-{tone}">{_escape(icon)}</span>{_escape(title)}</div>
          <div class="uc-card-delta">{_escape(body)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def alert_banner(message: str, tone: str = "warn") -> None:
    st.markdown(f'<div class="uc-alert"><span class="uc-{tone}">!</span> {_escape(message)}</div>', unsafe_allow_html=True)


def ai_panel(title: str, body: str, prompt: str = "Ask the data: Why is risk changing?") -> None:
    st.markdown(
        f"""
        <div class="uc-ai-panel">
          <div class="uc-panel-title">{_escape(title)}</div>
          <div class="uc-card-delta">{_escape(body)}</div>
          <div class="uc-section">{_escape(prompt)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
