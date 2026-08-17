"""Workspace Materials tab — material tracking and estimation."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from config.settings import THEME
from models.domain import Project, Material
from repository import get_repository
from services.analytics_service import material_utilization
from ui.components import section_header, alert, progress_bar
from utils.formatting import fmt_currency, fmt_pct


def render(project: Project) -> None:
    section_header("Materials Management")

    if not project.materials:
        alert("No materials recorded yet.", "info")
    else:
        # Utilization chart
        util = material_utilization(project)
        df_u = pd.DataFrame(util)
        fig = px.bar(df_u, x="name", y="utilization", title="Material Utilization (%)",
                     template="plotly_white", color_discrete_sequence=[THEME.accent])
        fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=300)
        st.plotly_chart(fig, use_container_width=True)

        # Summary metrics
        total_cost = sum(m.total_cost for m in project.materials)
        total_used = sum(m.used * m.unit_cost for m in project.materials)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Material Cost", fmt_currency(total_cost))
        with c2:
            st.metric("Consumed Value", fmt_currency(total_used))
        with c3:
            st.metric("Remaining Value", fmt_currency(total_cost - total_used))

        # Materials table
        section_header("Material Inventory")
        df = pd.DataFrame([
            {
                "Material": m.name, "Category": m.category,
                "Qty": f"{m.quantity} {m.unit}", "Unit Cost": f"${m.unit_cost:,.0f}",
                "Total Cost": fmt_currency(m.total_cost), "Used": f"{m.utilization:.0f}%",
                "Supplier": m.supplier, "Status": m.status,
            }
            for m in project.materials
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

    # Add material
    with st.expander("➕ Add Material"):
        with st.form("add_material"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Material Name")
                category = st.text_input("Category")
                quantity = st.number_input("Quantity", min_value=0.0, value=100.0)
                unit = st.text_input("Unit", value="m³")
            with c2:
                unit_cost = st.number_input("Unit Cost ($)", min_value=0.0, value=50.0)
                supplier = st.text_input("Supplier")
                status = st.selectbox("Status", ["Quoted", "Ordered", "Partially Delivered", "Delivered", "Installed"])
                used = st.number_input("Used", min_value=0.0, value=0.0)
            if st.form_submit_button("Add Material", type="primary"):
                if name:
                    project.materials.append(Material(
                        name=name, category=category, quantity=quantity, unit=unit,
                        unit_cost=unit_cost, used=used, supplier=supplier, status=status,
                    ))
                    get_repository().save_project(project)
                    st.success("Material added.")
                    st.rerun()
