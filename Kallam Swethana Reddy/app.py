"""Construction Intelligence Hub — main entry point.

Run with:  streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

from database import init_db, get_settings, list_projects, list_estimations
from auth_ui import render_auth_page, render_user_sidebar
from auth import is_authenticated, current_user
from utils import (
    inject_css, render_sidebar_brand, page_header,
    compute_kpis, format_currency, kpi_card, render_kpi_grid,
)

st.set_page_config(
    page_title="Construction Intelligence Hub",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialise database & assets (schema upgrades are applied non-destructively)
init_db()
inject_css()

# ------------------------------------------------------------------ auth gate
if not is_authenticated():
    st.markdown("<style>[data-testid='stSidebar']{display:none;}</style>",
                unsafe_allow_html=True)
    render_auth_page()
    st.stop()

user = current_user()
user_id = user["id"]

settings = get_settings(user_id)
render_sidebar_brand(settings.get("company_name", "Construction Intelligence Hub"))
render_user_sidebar()
st.sidebar.markdown("### Navigation")
st.sidebar.info(
    "Use the pages menu above to open Dashboard, Projects, Estimator, AI Assistant, "
    "Reports, Analytics, Settings, Profile and About."
)
st.sidebar.markdown("---")
st.sidebar.caption("© Construction Intelligence Hub")

# ------------------------------------------------------------------ header
page_header(
    title=f"Welcome back, {user['full_name'].split(' ')[0]}",
    subtitle="AI-powered project management, material estimation, analytics & reporting.",
    icon="🏗️",
)

# ------------------------------------------------------------------ KPIs
projects = list_projects(user_id)
k = compute_kpis(projects)
estimations = list_estimations(user_id)
last_est_total = format_currency(estimations[0]["total_cost"], settings["currency"]) if estimations else "—"

render_kpi_grid([
    kpi_card("Total Projects", str(k["total"]), "Your projects"),
    kpi_card("Active", str(k["active"]), "Currently in progress", variant="success"),
    kpi_card("Completed", str(k["completed"]), "Delivered projects"),
    kpi_card("Total Budget",
             format_currency(k["total_budget"], settings["currency"]),
             "Sum of project budgets", variant="accent"),
    kpi_card("Last Estimation", last_est_total,
             f"{len(estimations)} logged", variant="warn"),
])

# ------------------------------------------------------------------ Quick intro
st.markdown(
    """
    <div class="cih-card">
      <h3>What you can do here</h3>
      <ul>
        <li><b>Dashboard</b> — high-level KPIs and portfolio overview.</li>
        <li><b>Project Management</b> — create, edit, filter and delete projects.</li>
        <li><b>Material Estimator</b> — compute engineering-grade material quantities and cost.</li>
        <li><b>AI Assistant</b> — chat with a local llama3.2 model that understands your database.</li>
        <li><b>Reports</b> — export PDF & Excel reports for individual projects or the whole portfolio.</li>
        <li><b>Analytics</b> — interactive Plotly charts on status, budget, and building types.</li>
        <li><b>Settings</b> — configure your company details, material rates, labor cost, tax and currency.</li>
        <li><b>Profile</b> — update your name, email and password.</li>
      </ul>
      <p><b>Every record you create is private to your account.</b></p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not projects:
    st.info("No projects yet. Open **Project Management** from the sidebar to create your first project.")
else:
    st.markdown("#### Recent projects")
    recent = projects[:5]
    st.dataframe(
        [
            {
                "ID": p["id"],
                "Name": p["name"],
                "Client": p.get("client"),
                "Type": p.get("building_type"),
                "Status": p.get("status"),
                "Budget": format_currency(p.get("budget"), settings["currency"]),
                "Progress %": p.get("progress"),
            }
            for p in recent
        ],
        use_container_width=True,
        hide_index=True,
    )
