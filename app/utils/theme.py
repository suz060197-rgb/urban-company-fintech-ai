"""Shared dark fintech theme helpers for the Streamlit app."""

from __future__ import annotations

from pathlib import Path

import plotly.express as px
import plotly.io as pio
import streamlit as st


APP_DIR = Path(__file__).resolve().parents[1]
STYLES_PATH = APP_DIR / "styles.css"

COLORS = {
    "background": "#0F172A",
    "card": "#1E293B",
    "border": "#334155",
    "text": "#F8FAFC",
    "muted": "#CBD5E1",
    "accent": "#38BDF8",
    "cyan": "#22D3EE",
    "success": "#22C55E",
    "warning": "#F59E0B",
    "risk": "#EF4444",
    "purple": "#A78BFA",
}

COLOR_SEQUENCE = [
    COLORS["accent"],
    COLORS["success"],
    COLORS["warning"],
    COLORS["risk"],
    COLORS["purple"],
    COLORS["cyan"],
]

RISK_COLORS = {
    "Low": COLORS["success"],
    "Medium": COLORS["warning"],
    "High": COLORS["risk"],
    "Unknown": COLORS["muted"],
}


def configure_plotly() -> None:
    px.defaults.template = "plotly_dark"
    px.defaults.color_discrete_sequence = COLOR_SEQUENCE
    pio.templates.default = "plotly_dark"


def load_css() -> None:
    if STYLES_PATH.exists():
        st.markdown(f"<style>{STYLES_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def apply_theme() -> None:
    configure_plotly()
    load_css()


def page_header(title: str, subtitle: str, eyebrow: str = "Embedded Finance Intelligence") -> None:
    st.markdown(
        f"""
        <section class="uc-hero">
          <div class="uc-eyebrow">{eyebrow}</div>
          <h1>{title}</h1>
          <p class="uc-subtitle">{subtitle}</p>
          <div class="uc-topbar">
            <span class="uc-chip">AI operating system</span>
            <span class="uc-chip">Risk + growth intelligence</span>
            <span class="uc-chip">Embedded finance decisions</span>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand(active_area: str = "Executive Analytics") -> None:
    st.sidebar.markdown(
        f"""
        <div class="uc-logo">
          <span class="uc-logo-mark">UC</span>
          <span class="uc-sidebar-title">Urban Company AI Intelligence Platform</span>
        </div>
        <div class="uc-section">
          <div><span class="uc-status-dot"></span>Models online</div>
          <div><span class="uc-status-dot"></span>Datasets loaded</div>
          <div class="uc-card-delta">Active module: {active_area}</div>
        </div>
        <div class="uc-section">
          <div class="uc-card-label">Navigation Matrix</div>
          <div class="uc-nav-item">01 Overview</div>
          <div class="uc-nav-item">02 Risk Intelligence</div>
          <div class="uc-nav-item">03 Predictions</div>
          <div class="uc-nav-item">04 Survey Insights</div>
          <div class="uc-nav-item">05 Model Health</div>
          <div class="uc-nav-item">06 Admin Console</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_figure(fig, title: str | None = None):
    if title:
        fig.update_layout(title=title)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.35)",
        font={"color": COLORS["text"], "family": "Inter, Segoe UI, Arial, sans-serif"},
        title={"font": {"size": 18, "color": COLORS["text"]}},
        legend={"bgcolor": "rgba(15,23,42,0)", "font": {"color": COLORS["muted"]}},
        margin={"l": 30, "r": 24, "t": 58, "b": 38},
        hoverlabel={
            "bgcolor": COLORS["card"],
            "bordercolor": COLORS["border"],
            "font": {"color": COLORS["text"]},
        },
    )
    fig.update_xaxes(gridcolor="rgba(51,65,85,0.45)", zerolinecolor="rgba(51,65,85,0.55)")
    fig.update_yaxes(gridcolor="rgba(51,65,85,0.45)", zerolinecolor="rgba(51,65,85,0.55)")
    return fig
