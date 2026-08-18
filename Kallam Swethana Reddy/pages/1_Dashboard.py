"""Dashboard — KPIs, portfolio charts, recent activity."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from database import init_db, get_settings, list_projects, list_estimations
from auth_ui import require_login, render_user_sidebar
from utils import (
    inject_css, render_sidebar_brand, page_header,
    compute_kpis, format_currency, kpi_card, render_kpi_grid,
)

st.set_page_config(page_title="Dashboard • CIH", page_icon="📊", layout="wide")
init_db()
inject_css()
user = require_login()
user_id = user["id"]

settings = get_settings(user_id)
render_sidebar_brand(settings.get("company_name"))
render_user_sidebar()
page_header("Dashboard", "Portfolio-wide KPIs and construction analytics.", icon="📊")

projects = list_projects(user_id)
k = compute_kpis(projects)

render_kpi_grid([
    kpi_card("Total Projects", str(k["total"]), "In database"),
    kpi_card("Active", str(k["active"]), "In progress", variant="success"),
    kpi_card("Completed", str(k["completed"]), "Delivered"),
    kpi_card("On Hold", str(k["on_hold"]), "Paused", variant="warn"),
    kpi_card("Total Budget",
             format_currency(k["total_budget"], settings["currency"]),
             "Sum of budgets", variant="accent"),
    kpi_card("Built-up Area", f"{k['total_area']:,.0f} sqft", "All projects combined"),
])

if not projects:
    st.info("Add projects from the **Project Management** page to see charts and analytics here.")
    st.stop()

df = pd.DataFrame(projects)

c1, c2 = st.columns(2)
with c1:
    st.markdown("#### Projects by status")
    status_counts = df["status"].fillna("Unknown").value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    fig = px.pie(status_counts, names="status", values="count", hole=0.55,
                 color_discrete_sequence=px.colors.sequential.Blues_r)
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown("#### Budget by project")
    top = df.sort_values("budget", ascending=False).head(10)
    fig = px.bar(top, x="name", y="budget",
                 color="status", text_auto=".2s",
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(xaxis_title="", yaxis_title=f"Budget ({settings['currency']})",
                      margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    st.markdown("#### Building type mix")
    tmix = df["building_type"].fillna("Unknown").value_counts().reset_index()
    tmix.columns = ["building_type", "count"]
    fig = px.bar(tmix, x="building_type", y="count",
                 color="building_type", text_auto=True)
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Projects",
                      margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.markdown("#### Progress overview")
    prog = df[["name", "progress"]].fillna(0).sort_values("progress", ascending=True).tail(10)
    fig = px.bar(prog, x="progress", y="name", orientation="h", text="progress",
                 range_x=[0, 100], color="progress",
                 color_continuous_scale="Blues")
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10),
                      yaxis_title="", xaxis_title="Progress %")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("#### Recent estimations")
est = list_estimations(user_id)[:8]
if est:
    st.dataframe(
        [{
            "Date": r["created_at"],
            "Dim (m)": f"{r.get('length')}×{r.get('width')}×{r.get('height')}",
            "Floors": r.get("floors"),
            "Quality": r.get("quality"),
            "Total": format_currency(r.get("total_cost"), settings["currency"]),
        } for r in est],
        use_container_width=True, hide_index=True,
    )
else:
    st.caption("No material estimations logged yet.")
