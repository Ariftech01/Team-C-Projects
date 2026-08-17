"""Workspace Analytics tab — charts and insights only."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config.settings import THEME
from models.domain import Project
from services.analytics_service import (
    phase_progress, budget_breakdown, spend_trend, progress_trend,
    workforce_distribution, material_utilization, safety_summary, generate_insights,
)
from ui.components import section_header, alert
from utils.formatting import fmt_currency, fmt_pct


def render(project: Project) -> None:
    section_header("Analytics & Insights")

    # Row 1: Budget breakdown + Phase progress
    c1, c2 = st.columns(2)
    with c1:
        budget = budget_breakdown(project)
        if budget:
            df_b = pd.DataFrame(list(budget.items()), columns=["Category", "Amount"])
            fig = px.pie(df_b, values="Amount", names="Category", title="Budget Breakdown",
                         template="plotly_white", hole=0.4,
                         color_discrete_sequence=[THEME.primary, THEME.accent, THEME.success, THEME.warning, THEME.text_muted])
            fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=320)
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        phases = phase_progress(project)
        if phases:
            df_p = pd.DataFrame([
                {"Phase": k, "Progress": v["progress"], "Tasks": v["task_count"]}
                for k, v in phases.items()
            ])
            fig = px.bar(df_p, x="Phase", y="Progress", title="Phase Progress (%)",
                         template="plotly_white", color_discrete_sequence=[THEME.primary])
            fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=320)
            st.plotly_chart(fig, use_container_width=True)

    # Row 2: Spend trend + Material utilization
    c3, c4 = st.columns(2)
    with c3:
        trend = spend_trend(project)
        if trend:
            df_s = pd.DataFrame(trend)
            fig = px.area(df_s, x="date", y="spend", title="Cumulative Spend Trend",
                          template="plotly_white", color_discrete_sequence=[THEME.accent])
            fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=320, xaxis_title="Date", yaxis_title="Spend ($)")
            st.plotly_chart(fig, use_container_width=True)

    with c4:
        util = material_utilization(project)
        if util:
            df_u = pd.DataFrame(util)
            fig = px.bar(df_u, x="name", y="utilization", title="Material Utilization (%)",
                         template="plotly_white", color_discrete_sequence=[THEME.success])
            fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=320, xaxis_title="Material", yaxis_title="% Used")
            st.plotly_chart(fig, use_container_width=True)

    # Row 3: Workforce distribution + Safety
    c5, c6 = st.columns(2)
    with c5:
        dist = workforce_distribution(project)
        if dist:
            df_w = pd.DataFrame(list(dist.items()), columns=["Trade", "Headcount"])
            fig = px.bar(df_w, x="Trade", y="Headcount", title="Workforce Distribution",
                         template="plotly_white", color_discrete_sequence=[THEME.primary_light])
            fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=320)
            st.plotly_chart(fig, use_container_width=True)

    with c6:
        safety = safety_summary(project)
        if safety["by_severity"]:
            df_s = pd.DataFrame(list(safety["by_severity"].items()), columns=["Severity", "Count"])
            fig = px.bar(df_s, x="Severity", y="Count", title="Safety Incidents by Severity",
                         template="plotly_white", color_discrete_sequence=[THEME.error, THEME.warning, THEME.success])
            fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=320)
            st.plotly_chart(fig, use_container_width=True)

    # AI Insights
    st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)
    section_header("AI-Generated Insights")
    insights = generate_insights(project)
    for ins in insights:
        kind = "error" if "WARNING" in ins or "delayed" in ins.lower() else "warn" if "risk" in ins.lower() or "reorder" in ins.lower() else "info"
        alert(ins, kind)
