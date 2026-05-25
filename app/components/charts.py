"""Chart helpers for the 2026 AI intelligence theme."""

from __future__ import annotations

import streamlit as st

from utils.theme import style_figure


def ai_chart(fig, key: str, title: str | None = None) -> None:
    """Render a consistently themed Plotly chart."""
    st.plotly_chart(style_figure(fig, title), width="stretch", key=key)
