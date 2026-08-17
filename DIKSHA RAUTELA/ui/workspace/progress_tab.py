"""Workspace Progress tab - task/phase tracking and schedule."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from config.settings import THEME
from models.domain import Project, Task
from repository import get_repository
from services.analytics_service import phase_progress, progress_trend
from ui.components import alert, section_header
from utils.formatting import fmt_date


def render(project: Project) -> None:
    section_header("Progress & Schedule")

    trend = progress_trend(project)
    if trend:
        df_t = pd.DataFrame(trend)
        fig = px.line(
            df_t,
            x="week",
            y="progress",
            markers=True,
            title="Progress Trend (Weekly)",
            template="plotly_white",
            color_discrete_sequence=[THEME.primary],
        )
        fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=280)
        st.plotly_chart(fig, use_container_width=True)

    phases = phase_progress(project)
    if phases:
        section_header("Phase Progress")
        for phase, info in phases.items():
            with st.container(border=True):
                st.write(f"**{phase}**")
                st.caption(f"{info['task_count']} task(s) | {info['progress']:.0f}%")
                st.progress(info["progress"] / 100)

    section_header("Task Schedule")
    if not project.tasks:
        alert("No tasks defined yet.", "info")
    else:
        df = pd.DataFrame([
            {
                "Task": task.name,
                "Phase": task.phase,
                "Status": task.status,
                "Progress": f"{task.progress}%",
                "Assignee": task.assignee,
                "Priority": task.priority,
                "Start": fmt_date(task.start_date),
                "End": fmt_date(task.end_date),
            }
            for task in project.tasks
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

    with st.expander("Add Task"):
        with st.form("add_task"):
            t1, t2 = st.columns(2)
            with t1:
                name = st.text_input("Task Name")
                phase = st.text_input("Phase")
                assignee = st.text_input("Assignee")
            with t2:
                status = st.selectbox("Status", ["Not Started", "In Progress", "Completed", "On Hold"])
                priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
                progress = st.slider("Progress %", 0, 100, 0)
            sd = st.date_input("Start Date")
            ed = st.date_input("End Date")
            notes = st.text_area("Notes")
            if st.form_submit_button("Add Task", type="primary") and name:
                project.tasks.append(Task(
                    name=name,
                    phase=phase,
                    status=status,
                    priority=priority,
                    progress=float(progress),
                    assignee=assignee,
                    start_date=sd.isoformat(),
                    end_date=ed.isoformat(),
                    notes=notes,
                ))
                get_repository().save_project(project)
                st.success("Task added.")
                st.rerun()
