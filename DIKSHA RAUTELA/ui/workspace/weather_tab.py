"""Workspace Weather tab - current conditions and impact analysis."""
from __future__ import annotations

import streamlit as st

from models.domain import Project
from repository import get_repository
from services import ai_chat
from services.weather_service import refresh_project_weather
from ui.components import section_header
from utils.formatting import fmt_date


def render(project: Project) -> None:
    section_header("Weather & Environmental Conditions")
    weather = project.weather

    with st.container(border=True):
        st.subheader(weather.condition or "Weather unavailable")
        st.metric("Temperature", f"{weather.temp_c}C")
        st.write(f"**Work Impact:** {weather.work_impact}")
        st.caption(f"{project.location or 'No location'} | {fmt_date(weather.date)}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Wind", f"{weather.wind_kph} km/h")
    c2.metric("Precipitation", f"{weather.precipitation_mm} mm")
    c3.metric("Humidity", f"{weather.humidity}%")
    c4.metric("UV Index", f"{weather.uv_index}")

    if st.button("Refresh Weather"):
        project.weather = refresh_project_weather(project)
        get_repository().save_project(project)
        st.rerun()

    section_header("AI Weather Impact Analysis")
    analysis = ai_chat(
        "Analyze the weather impact on this project and recommend adjustments.",
        context={"page": "Weather", "project": project},
    )
    with st.container(border=True):
        st.write(analysis)
