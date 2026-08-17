"""Workspace Overview tab - high-level project snapshot."""
from __future__ import annotations

import streamlit as st

from models.domain import Project
from services import generate_insights
from ui.components import alert, section_header
from utils.formatting import fmt_currency, fmt_pct, fmt_date


def render(project: Project) -> None:
    section_header("Project Overview", subtitle=f"{project.code or 'No code'} | {project.type}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Progress", f"{project.progress:.0f}%", f"{project.progress:.0f}% complete")
    c2.metric("Budget Used", fmt_pct(project.budget_utilization), f"{fmt_currency(project.remaining_budget)} left")
    dtd = project.days_to_deadline
    c3.metric("Days to Deadline", str(dtd) if dtd is not None else "N/A", "Delayed" if project.is_delayed else "On track")
    c4.metric("Health Score", f"{project.health_score:.0f}/100")

    left, right = st.columns([1.3, 1])
    with left:
        with st.container(border=True):
            st.subheader("Project Details")
            st.write(f"**Manager:** {project.manager or 'Unassigned'}")
            st.write(f"**Client:** {project.client or 'Not set'}")
            st.write(f"**Location:** {project.location or 'Not set'}")
            st.write(f"**Start Date:** {fmt_date(project.start_date)}")
            st.write(f"**End Date:** {fmt_date(project.end_date)}")
            st.write(f"**Budget:** {fmt_currency(project.budget)}")
            st.write(f"**Spent:** {fmt_currency(project.spent)}")
            st.write(f"**Status:** {project.status}")
            st.write(f"**Priority:** {project.priority}")
    with right:
        with st.container(border=True):
            st.subheader("Description")
            st.write(project.description or "No description provided.")

    section_header("AI Insights")
    for insight in generate_insights(project):
        kind = "error" if "warning" in insight.lower() or "delayed" in insight.lower() else "warn" if "risk" in insight.lower() or "reorder" in insight.lower() else "info"
        alert(insight, kind)

    section_header("At a Glance")
    g1, g2, g3, g4, g5 = st.columns(5)
    g1.metric("Tasks", str(len(project.tasks)))
    g2.metric("Materials", str(len(project.materials)))
    g3.metric("Workforce", str(sum(worker.headcount for worker in project.workforce)))
    g4.metric("Equipment", str(len(project.equipment)))
    g5.metric("Open Safety", str(sum(1 for item in project.safety_incidents if item.status == "Open")))
