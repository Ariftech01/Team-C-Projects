"""Workspace Settings tab — project configuration and metadata."""
from __future__ import annotations

from datetime import date

import streamlit as st

from config.settings import THEME, PROJECT_STATUSES, PROJECT_TYPES, PRIORITY_LEVELS
from models.domain import Project
from repository import get_repository
from ui.components import section_header, alert
from utils.formatting import fmt_date


def render(project: Project) -> None:
    section_header("Project Settings")

    with st.form("settings_form"):
        st.markdown(f"<div style='font-weight:600;color:{THEME.primary};margin-bottom:0.5rem;'>Project Information</div>",
                    unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Project Name", value=project.name)
            code = st.text_input("Project Code", value=project.code)
            ptype = st.selectbox("Type", list(PROJECT_TYPES), index=list(PROJECT_TYPES).index(project.type) if project.type in PROJECT_TYPES else 0)
            manager = st.text_input("Project Manager", value=project.manager)
            client = st.text_input("Client", value=project.client)
        with c2:
            location = st.text_input("Location", value=project.location)
            status = st.selectbox("Status", list(PROJECT_STATUSES),
                                  index=list(PROJECT_STATUSES).index(project.status) if project.status in PROJECT_STATUSES else 0)
            priority = st.selectbox("Priority", list(PRIORITY_LEVELS),
                                    index=list(PRIORITY_LEVELS).index(project.priority) if project.priority in PRIORITY_LEVELS else 1)
            try:
                sd_val = date.fromisoformat(project.start_date)
            except (ValueError, TypeError):
                sd_val = date.today()
            try:
                ed_val = date.fromisoformat(project.end_date)
            except (ValueError, TypeError):
                ed_val = date.today()
            start_date = st.date_input("Start Date", value=sd_val)
            end_date = st.date_input("End Date", value=ed_val)

        c3, c4 = st.columns(2)
        with c3:
            budget = st.number_input("Budget ($)", min_value=0.0, value=float(project.budget), step=100_000.0)
        with c4:
            spent = st.number_input("Spent ($)", min_value=0.0, value=float(project.spent), step=50_000.0)

        progress = st.slider("Progress (%)", 0, 100, int(project.progress))
        description = st.text_area("Description", value=project.description)

        col_save, col_del = st.columns([1, 1])
        with col_save:
            saved = st.form_submit_button("💾 Save Changes", type="primary")
        with col_del:
            deleted = st.form_submit_button("🗑️ Delete Project")

    if saved:
        project.name = name
        project.code = code
        project.type = ptype
        project.manager = manager
        project.client = client
        project.location = location
        project.status = status
        project.priority = priority
        project.start_date = start_date.isoformat()
        project.end_date = end_date.isoformat()
        project.budget = budget
        project.spent = spent
        project.progress = float(progress)
        project.description = description
        from datetime import datetime
        project.updated_at = datetime.now().isoformat(timespec="seconds")
        get_repository().save_project(project)
        st.success("Project settings saved.")
        st.rerun()

    if deleted:
        repo = get_repository()
        repo.delete_project(project.id)
        st.session_state["current_project_id"] = None
        st.session_state["page"] = "Project Portfolio"
        st.success("Project deleted.")
        st.rerun()
