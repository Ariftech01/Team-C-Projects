"""Workspace History tab - AI-generated reports and activity log."""
from __future__ import annotations

import os

import streamlit as st

from models.domain import Project
from ui.components import empty_state, section_header
from utils.formatting import fmt_datetime


def render(project: Project) -> None:
    section_header("History & Reports")

    col_gen, col_info = st.columns([1, 3])
    with col_gen:
        if st.button("Generate Today's Report", type="primary", use_container_width=True):
            with st.spinner("Generating comprehensive report..."):
                from services.report_service import generate_report
                filepath = generate_report(project)
                st.success("Report generated and saved to history.")
                with open(filepath, "rb") as file:
                    st.download_button(
                        "Download PDF",
                        file.read(),
                        file_name=os.path.basename(filepath),
                        mime="application/pdf",
                    )
                st.rerun()
    with col_info:
        st.info(
            "Generates a PDF covering progress, budget, workforce, materials, "
            "weather, safety, analytics, and AI insights. The report is saved to project history."
        )

    if not project.history:
        empty_state("No history entries yet. Generate a report to get started.")
        return

    section_header("Activity & Report History")
    for item in project.history:
        with st.container(border=True):
            st.write(f"**{item.title}**")
            st.write(item.content)
            st.caption(f"{item.type.title()} | {fmt_datetime(item.timestamp)} | by {item.author}")

            if item.type == "report" and item.file_path and os.path.exists(item.file_path):
                with open(item.file_path, "rb") as file:
                    st.download_button(
                        "Download PDF",
                        file.read(),
                        file_name=os.path.basename(item.file_path),
                        mime="application/pdf",
                        key=f"dl_{item.id}",
                    )
