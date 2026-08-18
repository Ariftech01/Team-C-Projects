"""Reports — generate PDF & Excel reports for projects and portfolio."""
from __future__ import annotations

import streamlit as st

from database import init_db, get_settings, list_projects, get_project
from report_generator import (
    project_pdf, projects_summary_pdf, project_excel,
    projects_summary_excel, budget_summary_pdf,
)
from auth_ui import require_login, render_user_sidebar
from utils import inject_css, render_sidebar_brand, page_header

st.set_page_config(page_title="Reports • CIH", page_icon="📄", layout="wide")
init_db()
inject_css()
user = require_login()
user_id = user["id"]
settings = get_settings(user_id)
render_sidebar_brand(settings.get("company_name"))
render_user_sidebar()
page_header("Reports", "Export professional PDF and Excel reports.", icon="📄")

projects = list_projects(user_id)
if not projects:
    st.info("No projects yet. Create one from **Project Management** to generate reports.")
    st.stop()

report_type = st.selectbox("Report type", [
    "Single project", "Projects summary (all)", "Budget summary",
])

company = settings["company_name"]
currency = settings["currency"]

if report_type == "Single project":
    pid = st.selectbox(
        "Choose project",
        [p["id"] for p in projects],
        format_func=lambda i: next(f"#{p['id']} — {p['name']}" for p in projects if p["id"] == i),
    )
    project = get_project(pid, user_id)
    if not project:
        st.error("That project is not available in your account.")
        st.stop()
    st.json({k: project[k] for k in ("name", "client", "status", "budget", "progress")}, expanded=False)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "⬇️ PDF report",
            project_pdf(project, company=company, currency=currency),
            file_name=f"project_{pid}.pdf", mime="application/pdf",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            "⬇️ Excel report",
            project_excel(project, currency=currency),
            file_name=f"project_{pid}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

elif report_type == "Projects summary (all)":
    st.write(f"Total projects: **{len(projects)}**")
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "⬇️ PDF summary",
            projects_summary_pdf(projects, company=company, currency=currency),
            file_name="projects_summary.pdf", mime="application/pdf",
            use_container_width=True,
        )
    with c2:
        st.download_button(
            "⬇️ Excel summary",
            projects_summary_excel(projects, currency=currency),
            file_name="projects_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

elif report_type == "Budget summary":
    total = sum(float(p.get("budget") or 0) for p in projects)
    st.metric("Grand total budget", f"{currency} {total:,.2f}")
    st.download_button(
        "⬇️ Budget PDF",
        budget_summary_pdf(projects, company=company, currency=currency),
        file_name="budget_summary.pdf", mime="application/pdf",
        use_container_width=True,
    )
