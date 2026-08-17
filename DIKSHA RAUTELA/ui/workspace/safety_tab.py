"""Workspace Safety tab — incidents and checklists."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from config.settings import THEME
from models.domain import Project, SafetyIncident, SafetyChecklist
from repository import get_repository
from services.analytics_service import safety_summary
from ui.components import section_header, alert
from utils.formatting import fmt_date


def render(project: Project) -> None:
    section_header("Safety Management")

    summary = safety_summary(project)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Incidents", str(summary["total"]))
    with c2:
        st.metric("Open", str(summary["open"]))
    with c3:
        st.metric("Resolved", str(summary["resolved"]))
    with c4:
        st.metric("Checklist", f"{summary['checklist_completion']:.0f}%")

    # Severity chart
    if summary["by_severity"]:
        df_s = pd.DataFrame(list(summary["by_severity"].items()), columns=["Severity", "Count"])
        fig = px.bar(df_s, x="Severity", y="Count", title="Incidents by Severity",
                     template="plotly_white",
                     color_discrete_sequence=[THEME.error, THEME.warning, THEME.success])
        fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=280)
        st.plotly_chart(fig, use_container_width=True)

    # Open incidents
    open_inc = [s for s in project.safety_incidents if s.status == "Open"]
    if open_inc:
        section_header("Open Incidents")
        for s in open_inc:
            alert(f"**[{s.severity}] {s.type}** — {s.description} (reported {fmt_date(s.date)} by {s.reported_by}) — Action: {s.action_taken or 'Pending'}", "error")

    # Incidents table
    section_header("All Incidents")
    if project.safety_incidents:
        df = pd.DataFrame([
            {
                "Date": fmt_date(s.date), "Type": s.type, "Severity": s.severity,
                "Description": s.description[:60], "Reported By": s.reported_by,
                "Status": s.status, "Action": s.action_taken[:50],
            }
            for s in project.safety_incidents
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

    # Checklist
    section_header("Safety Checklist")
    if project.safety_checklist:
        for c in project.safety_checklist:
            icon = "✅" if c.completed else "⬜"
            st.markdown(f"{icon} **{c.item}** — last checked: {fmt_date(c.last_checked)} (responsible: {c.responsible})")
    else:
        alert("No safety checklist items.", "info")

    # Add incident
    with st.expander("➕ Report Incident"):
        with st.form("add_incident"):
            c1, c2 = st.columns(2)
            with c1:
                itype = st.text_input("Incident Type")
                severity = st.selectbox("Severity", ["Low", "Medium", "High"])
                reported_by = st.text_input("Reported By")
            with c2:
                status = st.selectbox("Status", ["Open", "Investigating", "Resolved"])
                action = st.text_input("Action Taken")
            description = st.text_area("Description")
            if st.form_submit_button("Report", type="primary"):
                if itype:
                    project.safety_incidents.append(SafetyIncident(
                        type=itype, severity=severity, description=description,
                        reported_by=reported_by, status=status, action_taken=action,
                        date=__import__("datetime").date.today().isoformat(),
                    ))
                    get_repository().save_project(project)
                    st.success("Incident reported.")
                    st.rerun()
