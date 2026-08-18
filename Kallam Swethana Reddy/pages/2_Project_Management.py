"""Project Management — full CRUD."""
from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from database import (
    init_db, get_settings, list_projects, add_project,
    update_project, delete_project, get_project,
)
from auth_ui import require_login, render_user_sidebar
from utils import (
    inject_css, render_sidebar_brand, page_header,
    STATUS_OPTIONS, BUILDING_TYPES, format_currency, status_pill,
    safe_float, safe_int,
)

st.set_page_config(page_title="Projects • CIH", page_icon="🏢", layout="wide")
init_db()
inject_css()
user = require_login()
user_id = user["id"]
settings = get_settings(user_id)
render_sidebar_brand(settings.get("company_name"))
render_user_sidebar()
page_header("Project Management", "Create, filter, edit and delete construction projects.", icon="🏢")


def project_form(existing: dict | None = None, form_key: str = "new_project") -> dict | None:
    with st.form(form_key, clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Project name*", value=(existing or {}).get("name", ""))
            client = st.text_input("Client", value=(existing or {}).get("client", ""))
            location = st.text_input("Location", value=(existing or {}).get("location", ""))
            building_type = st.selectbox(
                "Building type", BUILDING_TYPES,
                index=BUILDING_TYPES.index((existing or {}).get("building_type") or "Residential")
                if (existing or {}).get("building_type") in BUILDING_TYPES else 0,
            )
            floors = st.number_input("Floors", min_value=1, max_value=200,
                                     value=safe_int((existing or {}).get("floors"), 1))
            area = st.number_input("Built-up area (sqft)", min_value=0.0,
                                   value=safe_float((existing or {}).get("area_sqft"), 0.0),
                                   step=100.0)
        with c2:
            status = st.selectbox(
                "Status", STATUS_OPTIONS,
                index=STATUS_OPTIONS.index((existing or {}).get("status") or "Planning")
                if (existing or {}).get("status") in STATUS_OPTIONS else 0,
            )
            budget = st.number_input(
                f"Budget ({settings['currency']})", min_value=0.0,
                value=safe_float((existing or {}).get("budget"), 0.0), step=10000.0,
            )
            progress = st.slider("Progress %", 0, 100,
                                 value=safe_int((existing or {}).get("progress"), 0))
            start_date = st.date_input(
                "Start date",
                value=pd.to_datetime((existing or {}).get("start_date") or date.today()).date(),
            )
            end_date = st.date_input(
                "Expected completion",
                value=pd.to_datetime((existing or {}).get("end_date") or date.today()).date(),
            )
        notes = st.text_area("Notes", value=(existing or {}).get("notes", ""), height=90)
        submitted = st.form_submit_button("Save project", use_container_width=True)
        if not submitted:
            return None
        if not name.strip():
            st.error("Project name is required.")
            return None
        return {
            "name": name.strip(), "client": client.strip(), "location": location.strip(),
            "building_type": building_type, "floors": int(floors),
            "area_sqft": float(area), "budget": float(budget), "status": status,
            "start_date": str(start_date), "end_date": str(end_date),
            "progress": int(progress), "notes": notes.strip(),
        }


tab_list, tab_new = st.tabs(["📋 Projects", "➕ New Project"])

with tab_list:
    f1, f2, f3 = st.columns([2, 1, 1])
    search = f1.text_input("Search", placeholder="Search by name, client, location")
    status_filter = f2.selectbox("Status", ["All"] + STATUS_OPTIONS)
    type_filter = f3.selectbox("Type", ["All"] + BUILDING_TYPES)
    projects = list_projects(user_id, search=search or None,
                             status=status_filter, building_type=type_filter)

    if not projects:
        st.info("No projects match the current filters.")
    else:
        df = pd.DataFrame([{
            "ID": p["id"], "Name": p["name"], "Client": p.get("client"),
            "Location": p.get("location"), "Type": p.get("building_type"),
            "Status": p.get("status"), "Floors": p.get("floors"),
            "Area (sqft)": p.get("area_sqft"),
            "Budget": format_currency(p.get("budget"), settings["currency"]),
            "Progress %": p.get("progress"),
            "Start": p.get("start_date"), "End": p.get("end_date"),
        } for p in projects])
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("### Edit or delete a project")
        ids = [p["id"] for p in projects]
        sel = st.selectbox(
            "Select project",
            ids,
            format_func=lambda i: next(f"#{p['id']} — {p['name']}" for p in projects if p["id"] == i),
        )
        current = get_project(sel, user_id)
        if not current:
            st.error("That project is not available in your account.")
            st.stop()
        st.markdown(f"**Status:** {status_pill(current.get('status') or '')}", unsafe_allow_html=True)

        col_e, col_d = st.columns([3, 1])
        with col_e:
            updates = project_form(current, form_key=f"edit_{sel}")
            if updates:
                if update_project(sel, updates, user_id):
                    st.success("Project updated.")
                else:
                    st.error("Update failed — the project does not belong to your account.")
                st.rerun()
        with col_d:
            st.markdown("#### Danger zone")
            confirm = st.checkbox("I confirm I want to delete this project.", key=f"cd_{sel}")
            if st.button("Delete project", type="secondary", use_container_width=True, disabled=not confirm):
                if delete_project(sel, user_id):
                    st.success("Project deleted.")
                else:
                    st.error("Delete failed — the project does not belong to your account.")
                st.rerun()

with tab_new:
    st.markdown("Fill in the details below to create a new project.")
    data = project_form(None, form_key="create_project")
    if data:
        pid = add_project(data, user_id)
        st.success(f"Project created with ID #{pid}.")
        st.rerun()
