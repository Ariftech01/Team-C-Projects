"""About — platform description, tech stack, architecture."""
from __future__ import annotations

import streamlit as st

from database import init_db, get_settings
from ollama_backend import OLLAMA_HOST, OLLAMA_MODEL, ollama_available
from auth_ui import require_login, render_user_sidebar
from utils import inject_css, render_sidebar_brand, page_header

st.set_page_config(page_title="About • CIH", page_icon="ℹ️", layout="wide")
init_db()
inject_css()
user = require_login()
user_id = user["id"]
settings = get_settings(user_id)
render_sidebar_brand(settings.get("company_name"))
render_user_sidebar()
page_header("About", "Construction Intelligence Hub — architecture & credits.", icon="ℹ️")

st.markdown(
    """
    <div class="cih-card">
      <h3>Overview</h3>
      <p>The <b>Construction Intelligence Hub</b> is an AI-powered platform for
      construction project management. It combines interactive dashboards, a
      quantitative material estimator, professional PDF/Excel reporting, and a
      local large-language-model assistant that can answer questions grounded in
      your own project database.</p>
    </div>

    <div class="cih-card">
      <h3>Technology stack</h3>
      <ul>
        <li><b>Frontend:</b> Streamlit (multi-page app, custom CSS theme)</li>
        <li><b>Backend / storage:</b> SQLite (auto-initialised schema)</li>
        <li><b>AI:</b> Ollama running <code>llama3.2</code> locally, called via <code>/api/chat</code></li>
        <li><b>Charts:</b> Plotly Express + Graph Objects</li>
        <li><b>Reports:</b> ReportLab (PDF) &amp; OpenPyXL (Excel)</li>
        <li><b>Data:</b> Pandas</li>
      </ul>
    </div>

    <div class="cih-card">
      <h3>Architecture</h3>
      <pre>
Streamlit Pages ──▶ utils / database / material_estimator ──▶ SQLite
                 ├─▶ report_generator ─▶ PDF / Excel
                 └─▶ ollama_backend ──▶ Ollama HTTP API (llama3.2)
      </pre>
      <p>Modules are decoupled: pages own presentation, <code>database.py</code>
      owns persistence, <code>material_estimator.py</code> owns engineering
      formulas, <code>ollama_backend.py</code> owns AI + intent classification,
      and <code>report_generator.py</code> owns export.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Runtime status")
ok, msg = ollama_available()
if ok:
    st.success(f"Ollama reachable at {OLLAMA_HOST} with model `{OLLAMA_MODEL}`.")
else:
    st.warning(msg)
st.caption("Database: SQLite (`construction.db`, auto-created on first launch).")
