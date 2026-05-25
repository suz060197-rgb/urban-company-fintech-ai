"""Simple session-state authentication for the Streamlit app."""

from __future__ import annotations

import os

import streamlit as st


DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin123"


def _credentials() -> tuple[str, str]:
    username = os.getenv("UC_APP_USERNAME", DEFAULT_USERNAME)
    password = os.getenv("UC_APP_PASSWORD", DEFAULT_PASSWORD)
    return username, password


def is_authenticated() -> bool:
    return bool(st.session_state.get("authenticated", False))


def current_user() -> str:
    return str(st.session_state.get("username", ""))


def render_auth_controls() -> bool:
    """Render login/logout controls in the sidebar and return auth status."""
    st.sidebar.divider()
    st.sidebar.subheader("Access")

    if is_authenticated():
        st.sidebar.success(f"Signed in as {current_user()}")
        if st.sidebar.button("Logout", key="auth_logout"):
            st.session_state["authenticated"] = False
            st.session_state["username"] = ""
            st.rerun()
        return True

    expected_username, expected_password = _credentials()
    with st.sidebar.form("auth_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    st.sidebar.caption("Demo credentials: admin / admin123")

    if submitted:
        if username == expected_username and password == expected_password:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.rerun()
        st.sidebar.error("Invalid username or password.")

    return False


def require_login() -> None:
    """Stop protected pages until the user logs in."""
    if render_auth_controls():
        return

    st.warning("Please log in from the sidebar to access this protected page.")
    st.stop()
