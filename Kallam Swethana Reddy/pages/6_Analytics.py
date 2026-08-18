"""Analytics — deeper Plotly charts on the project portfolio."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from database import init_db, get_settings, list_projects
from auth_ui import require_login, render_user_sidebar
from utils import inject_css, render_sidebar_brand, page_header, compute_kpis, format_currency

st.set_page_config(page_title="Analytics • CIH", page_icon="📈", layout="wide")
init_db()
inject_css()
user = require_login()
user_id = user["id"]
settings = get_settings(user_id)
render_sidebar_brand(settings.get("company_name"))
render_user_sidebar()
page_header("Analytics", "Interactive charts driven live from your project database.", icon="📈")

projects = list_projects(user_id)
if not projects:
    st.info("Add projects to unlock analytics.")
    st.stop()

df = pd.DataFrame(projects)
df["budget"] = pd.to_numeric(df["budget"], errors="coerce").fillna(0)
df["area_sqft"] = pd.to_numeric(df["area_sqft"], errors="coerce").fillna(0)
df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")

k = compute_kpis(projects)
c1, c2, c3 = st.columns(3)
c1.metric("Portfolio value", format_currency(k["total_budget"], settings["currency"]))
c2.metric("Avg budget / project",
          format_currency(k["total_budget"] / max(k["total"], 1), settings["currency"]))
c3.metric("Avg progress",
          f"{df['progress'].fillna(0).astype(float).mean():.1f} %")

# ----- charts --------------------------------------------------------------
r1c1, r1c2 = st.columns(2)
with r1c1:
    st.markdown("#### Status distribution")
    sd = df["status"].fillna("Unknown").value_counts().reset_index()
    sd.columns = ["status", "count"]
    fig = px.pie(sd, names="status", values="count", hole=0.5)
    st.plotly_chart(fig, use_container_width=True)

with r1c2:
    st.markdown("#### Budget by building type")
    bt = df.groupby(df["building_type"].fillna("Unknown"))["budget"].sum().reset_index()
    fig = px.bar(bt, x="building_type", y="budget", color="building_type", text_auto=".2s")
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title=settings["currency"])
    st.plotly_chart(fig, use_container_width=True)

r2c1, r2c2 = st.columns(2)
with r2c1:
    st.markdown("#### Monthly project starts")
    ts = df.dropna(subset=["start_date"]).copy()
    if not ts.empty:
        ts["month"] = ts["start_date"].dt.to_period("M").dt.to_timestamp()
        monthly = ts.groupby("month").size().reset_index(name="projects")
        fig = px.line(monthly, x="month", y="projects", markers=True)
        fig.update_layout(xaxis_title="", yaxis_title="Projects started")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No start dates recorded.")

with r2c2:
    st.markdown("#### Area vs Budget")
    fig = px.scatter(df, x="area_sqft", y="budget", color="status",
                     size="floors", hover_data=["name"])
    fig.update_layout(xaxis_title="Area (sqft)", yaxis_title=f"Budget ({settings['currency']})")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("#### Portfolio progress gauges")
gcols = st.columns(min(4, len(df)))
for i, (_, row) in enumerate(df.head(len(gcols)).iterrows()):
    with gcols[i]:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=float(row.get("progress") or 0),
            title={"text": row["name"][:22]},
            gauge={"axis": {"range": [0, 100]},
                   "bar": {"color": "#1E4FD8"},
                   "steps": [
                       {"range": [0, 40], "color": "#FBE3E6"},
                       {"range": [40, 75], "color": "#FFF4D6"},
                       {"range": [75, 100], "color": "#E6F7EF"},
                   ]},
        ))
        fig.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=220)
        st.plotly_chart(fig, use_container_width=True)
