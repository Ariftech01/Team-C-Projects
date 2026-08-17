"""Workspace Workforce tab — crew and labor management."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from config.settings import THEME
from models.domain import Project, WorkforceMember
from repository import get_repository
from services.analytics_service import workforce_distribution
from ui.components import section_header, alert
from utils.formatting import fmt_currency


def render(project: Project) -> None:
    section_header("Workforce Management")

    if not project.workforce:
        alert("No workforce entries yet.", "info")
    else:
        # Distribution chart
        dist = workforce_distribution(project)
        if dist:
            df_d = pd.DataFrame(list(dist.items()), columns=["Trade", "Headcount"])
            fig = px.bar(df_d, x="Trade", y="Headcount", title="Workforce Distribution",
                         template="plotly_white", color_discrete_sequence=[THEME.primary])
            fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=300)
            st.plotly_chart(fig, use_container_width=True)

        # Summary
        on_site = sum(w.headcount for w in project.workforce if w.status == "On Site")
        total = sum(w.headcount for w in project.workforce)
        labor_cost = sum(w.hourly_rate * w.hours_today * w.headcount for w in project.workforce)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Headcount", str(total))
        with c2:
            st.metric("On Site Today", str(on_site))
        with c3:
            st.metric("Today's Labor Cost", fmt_currency(labor_cost))

        # Workforce table
        section_header("Crew Roster")
        df = pd.DataFrame([
            {
                "Name": w.name, "Role": w.role, "Trade": w.trade,
                "Crew": w.crew, "Headcount": w.headcount,
                "Hourly Rate": f"${w.hourly_rate}/h", "Hours Today": f"{w.hours_today}h",
                "Status": w.status,
            }
            for w in project.workforce
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

    # Add workforce
    with st.expander("➕ Add Workforce Entry"):
        with st.form("add_workforce"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Name / Crew Name")
                role = st.text_input("Role")
                trade = st.text_input("Trade")
                crew = st.text_input("Crew ID")
            with c2:
                headcount = st.number_input("Headcount", min_value=1, value=1)
                hourly_rate = st.number_input("Hourly Rate ($)", min_value=0.0, value=50.0)
                hours_today = st.number_input("Hours Today", min_value=0.0, value=8.0)
                status = st.selectbox("Status", ["On Site", "Off Site", "Weather Hold", "Break"])
            if st.form_submit_button("Add", type="primary"):
                if name:
                    project.workforce.append(WorkforceMember(
                        name=name, role=role, trade=trade, crew=crew,
                        headcount=headcount, hourly_rate=hourly_rate,
                        hours_today=hours_today, status=status,
                    ))
                    get_repository().save_project(project)
                    st.success("Workforce entry added.")
                    st.rerun()
