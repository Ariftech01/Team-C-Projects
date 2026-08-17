"""Organization analytics page with repository-driven portfolio insights."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from repository import get_repository
from services.analytics_service import generate_insights, portfolio_kpis
from utils.formatting import fmt_currency, fmt_pct

# ── Corporate design tokens ───────────────────────────────────────────────────
_COLORS = ["#1B3A5B", "#0E7C7B", "#ED6C02", "#C62828", "#2E7D32", "#5C6BC0"]
_LAYOUT_BASE = dict(
    font=dict(family="Inter, sans-serif", size=12),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=45, b=10),
)


def render_analytics() -> None:
    repo = get_repository()
    projects = repo.list_projects()

    st.title("Portfolio Analytics")
    st.caption(
        "Real-time intelligence across the entire project portfolio — budgets in ₹ Crore."
    )

    if not projects:
        st.info(
            "Create projects first. Analytics will appear when repository data exists."
        )
        return

    kpis = portfolio_kpis(projects)
    total_budget = sum(p.budget for p in projects)
    total_spent = sum(p.spent for p in projects)
    total_remaining = total_budget - total_spent
    workers = sum(w.headcount for p in projects for w in p.workforce)
    open_safety = sum(
        1 for p in projects for i in p.safety_incidents if i.status == "Open"
    )
    delayed_count = sum(1 for p in projects if p.status == "Delayed")

    # ── KPI Banner ─────────────────────────────────────────────────────────────
    r1 = st.columns(6)
    r1[0].metric("Portfolio Budget", fmt_currency(total_budget))
    r1[1].metric(
        "Total Spent",
        fmt_currency(total_spent),
        f"{kpis['budget_utilization']:.1f}% utilised",
    )
    r1[2].metric("Remaining Budget", fmt_currency(total_remaining))
    r1[3].metric("Avg Progress", fmt_pct(kpis["overall_progress"]))
    r1[4].metric("Total Workforce", str(workers))
    r1[5].metric(
        "Open Safety Issues",
        str(open_safety),
        delta=f"{delayed_count} delayed",
        delta_color="inverse",
    )

    st.divider()

    # ── Build base DataFrame ───────────────────────────────────────────────────
    df = pd.DataFrame(
        [
            {
                "Project": p.name[:26],
                "Status": p.status,
                "Priority": p.priority,
                "Manager": p.manager or "Unassigned",
                "Location": p.location,
                "Budget (₹ Cr)": round(p.budget / 1e7, 2),
                "Spent (₹ Cr)": round(p.spent / 1e7, 2),
                "Remaining (₹ Cr)": round(p.remaining_budget / 1e7, 2),
                "Budget Used %": round(p.budget_utilization, 1),
                "Progress %": p.progress,
                "Health Score": p.health_score,
                "Workers": sum(w.headcount for w in p.workforce),
                "Open Safety": sum(
                    1 for i in p.safety_incidents if i.status == "Open"
                ),
                "Weather Impact": p.weather.work_impact,
                "Days to Deadline": (
                    p.days_to_deadline if p.days_to_deadline is not None else 0
                ),
            }
            for p in projects
        ]
    )

    # ── Row 1: Budget vs Spent | Progress vs Budget Exposure ──────────────────
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Total Budget",
                    x=df["Project"],
                    y=df["Budget (₹ Cr)"],
                    marker_color="#1B3A5B",
                    hovertemplate="%{x}<br>Budget: ₹%{y:.2f} Cr<extra></extra>",
                ),
                go.Bar(
                    name="Spent",
                    x=df["Project"],
                    y=df["Spent (₹ Cr)"],
                    marker_color="#0E7C7B",
                    hovertemplate="%{x}<br>Spent: ₹%{y:.2f} Cr<extra></extra>",
                ),
            ]
        )
        fig.update_layout(
            barmode="group",
            title="Budget vs Spent (₹ Crore)",
            height=360,
            **_LAYOUT_BASE,
            legend=dict(orientation="h", y=-0.3),
        )
        fig.update_yaxes(title_text="₹ Crore")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.scatter(
            df,
            x="Progress %",
            y="Budget Used %",
            size="Workers",
            color="Health Score",
            hover_name="Project",
            color_continuous_scale=[
                [0, "#C62828"],
                [0.5, "#ED6C02"],
                [1, "#2E7D32"],
            ],
            title="Progress vs Budget Exposure",
            labels={
                "Budget Used %": "Budget Utilised %",
                "Progress %": "Completion %",
            },
        )
        fig.update_layout(height=360, **_LAYOUT_BASE)
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 2: Status Mix | Health Scores ─────────────────────────────────────
    c3, c4 = st.columns(2)
    with c3:
        status_df = (
            df.groupby("Status", as_index=False)
            .size()
            .rename(columns={"size": "Projects"})
        )
        fig = px.pie(
            status_df,
            names="Status",
            values="Projects",
            hole=0.45,
            title="Portfolio Status Distribution",
            color_discrete_sequence=_COLORS,
        )
        fig.update_layout(height=340, **_LAYOUT_BASE)
        fig.update_traces(textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        health_sorted = df.sort_values("Health Score")
        fig = px.bar(
            health_sorted,
            x="Project",
            y="Health Score",
            color="Priority",
            color_discrete_map={
                "Critical": "#C62828",
                "High": "#ED6C02",
                "Medium": "#0E7C7B",
                "Low": "#6B7280",
            },
            title="Project Health Scores",
        )
        fig.add_hline(
            y=70,
            line_dash="dash",
            line_color="#C62828",
            annotation_text="Risk threshold (70)",
            annotation_position="top right",
        )
        fig.update_layout(height=340, **_LAYOUT_BASE)
        st.plotly_chart(fig, use_container_width=True)

    # ── Row 3: Workforce Deployment | Days to Deadline ────────────────────────
    c5, c6 = st.columns(2)
    with c5:
        if df["Workers"].sum() > 0:
            fig = px.pie(
                df[df["Workers"] > 0],
                names="Project",
                values="Workers",
                hole=0.4,
                title="Workforce Deployment by Project",
                color_discrete_sequence=_COLORS,
            )
            fig.update_layout(height=320, **_LAYOUT_BASE)
            fig.update_traces(textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No workforce data available.")

    with c6:
        deadline_df = df[df["Days to Deadline"] != 0].sort_values("Days to Deadline")
        if not deadline_df.empty:
            fig = px.bar(
                deadline_df,
                x="Project",
                y="Days to Deadline",
                title="Days to Deadline",
                color="Days to Deadline",
                color_continuous_scale=[
                    [0, "#C62828"],
                    [0.3, "#ED6C02"],
                    [1, "#2E7D32"],
                ],
            )
            fig.add_hline(y=0, line_dash="dash", line_color="#C62828")
            fig.update_layout(height=320, **_LAYOUT_BASE)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No deadline data available.")

    # ── Project Comparison Table ───────────────────────────────────────────────
    st.subheader("📋 Project Comparison Table")
    display_df = df.drop(columns=["Days to Deadline", "Manager"], errors="ignore")
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # ── Executive AI Insights ──────────────────────────────────────────────────
    st.subheader("🤖 Executive AI Insights")
    insight_cols = st.columns(2)
    for idx, project in enumerate(
        sorted(projects, key=lambda item: item.health_score)[:4]
    ):
        with insight_cols[idx % 2]:
            with st.container(border=True):
                status_icon = (
                    "🔴"
                    if project.health_score < 60
                    else ("🟡" if project.health_score < 80 else "🟢")
                )
                st.markdown(f"**{status_icon} {project.name}**")
                st.caption(
                    f"{project.location} | {project.status} | "
                    f"₹{project.budget / 1e7:.2f} Cr"
                )
                for insight in generate_insights(project):
                    st.write(f"• {insight}")
