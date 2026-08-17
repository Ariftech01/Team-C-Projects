"""Project Workspace - operational area for a single project with modular tabs."""
from __future__ import annotations

import streamlit as st

from repository import get_repository

from .overview_tab import render as render_overview
from .progress_tab import render as render_progress
from .materials_tab import render as render_materials
from .workforce_tab import render as render_workforce
from .equipment_tab import render as render_equipment
from .safety_tab import render as render_safety
from .weather_tab import render as render_weather
from .analytics_tab import render as render_analytics
from .documents_tab import render as render_documents
from .history_tab import render as render_history
from .settings_tab import render as render_settings


TABS = [
    "Overview", "Progress", "Materials", "Workforce", "Equipment",
    "Safety", "Weather", "Analytics", "Documents", "History", "Settings",
]


def render_workspace() -> None:
    project_id = st.session_state.get("current_project_id")
    if not project_id:
        st.warning("No project selected. Return to the Project Portfolio.")
        if st.button("Go to Portfolio", type="primary"):
            st.session_state["page"] = "Project Portfolio"
            st.rerun()
        return

    repo = get_repository()
    project = repo.get_project(project_id)
    if project is None:
        st.error("Project not found.")
        st.session_state["current_project_id"] = None
        st.session_state["page"] = "Project Portfolio"
        if st.button("Go to Portfolio", type="primary"):
            st.rerun()
        return

    with st.container(border=True):
        left, right = st.columns([2.4, 1])
        with left:
            st.title(project.name)
            st.caption(f"{project.code or 'No code'} | {project.location or 'No location'} | {project.manager or 'Unassigned'}")
        with right:
            st.write(f"**Status:** {project.status}")
            st.write(f"**Priority:** {project.priority}")
            st.write(f"**Health:** {project.health_score:.0f}/100")
        st.progress(project.progress / 100)

    tab_objects = st.tabs(TABS)
    renderers = {
        "Overview": render_overview,
        "Progress": render_progress,
        "Materials": render_materials,
        "Workforce": render_workforce,
        "Equipment": render_equipment,
        "Safety": render_safety,
        "Weather": render_weather,
        "Analytics": render_analytics,
        "Documents": render_documents,
        "History": render_history,
        "Settings": render_settings,
    }
    for tab_obj, name in zip(tab_objects, TABS):
        with tab_obj:
            renderers[name](project)
