"""Admin page placeholder."""

from pathlib import Path
import sys

import streamlit as st


APP_DIR = Path(__file__).resolve().parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.append(str(APP_DIR))

from utils.auth import require_login


require_login()


st.title("Admin")
st.write("Dataset health checks, artifact inventory, and app diagnostics will be implemented here.")
