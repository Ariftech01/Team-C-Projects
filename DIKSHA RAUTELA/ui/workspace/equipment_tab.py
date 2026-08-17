"""Workspace Equipment tab — equipment status and maintenance."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from config.settings import THEME
from models.domain import Project, Equipment
from repository import get_repository
from ui.components import section_header, alert
from utils.formatting import fmt_currency, fmt_date


def render(project: Project) -> None:
    section_header("Equipment Management")

    if not project.equipment:
        alert("No equipment assigned yet.", "info")
    else:
        # Status summary
        operational = sum(1 for e in project.equipment if e.status == "Operational")
        maintenance = sum(1 for e in project.equipment if e.status == "Maintenance")
        down = sum(1 for e in project.equipment if e.status == "Down")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Total Units", str(len(project.equipment)))
        with c2:
            st.metric("Operational", str(operational))
        with c3:
            st.metric("In Maintenance", str(maintenance))
        with c4:
            st.metric("Down", str(down))

        # Equipment table
        df = pd.DataFrame([
            {
                "Name": e.name, "Type": e.type, "Status": e.status,
                "Operator": e.operator, "Fuel Hours": f"{e.fuel_hours}h",
                "Last Service": fmt_date(e.last_service),
                "Next Service": fmt_date(e.next_service),
                "Daily Rate": fmt_currency(e.daily_rate),
            }
            for e in project.equipment
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Alerts for overdue service
        from datetime import date
        overdue = [e for e in project.equipment if e.next_service and e.next_service < date.today().isoformat()]
        if overdue:
            for e in overdue:
                alert(f"**{e.name}** service is overdue (due {fmt_date(e.next_service)}).", "error")

    # Add equipment
    with st.expander("➕ Add Equipment"):
        with st.form("add_equipment"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Equipment Name")
                etype = st.text_input("Type")
                status = st.selectbox("Status", ["Operational", "Maintenance", "Down"])
                operator = st.text_input("Operator")
            with c2:
                fuel_hours = st.number_input("Fuel Hours", min_value=0.0, value=0.0)
                daily_rate = st.number_input("Daily Rate ($)", min_value=0.0, value=500.0)
                last_service = st.date_input("Last Service Date")
                next_service = st.date_input("Next Service Date")
            if st.form_submit_button("Add", type="primary"):
                if name:
                    project.equipment.append(Equipment(
                        name=name, type=etype, status=status, operator=operator,
                        fuel_hours=fuel_hours, daily_rate=daily_rate,
                        last_service=last_service.isoformat(),
                        next_service=next_service.isoformat(),
                    ))
                    get_repository().save_project(project)
                    st.success("Equipment added.")
                    st.rerun()
