"""Profile — view and update account details, change password."""
from __future__ import annotations

import streamlit as st

from auth import change_password, refresh_session_user, update_profile
from auth_ui import require_login, render_user_sidebar
from database import (
    init_db, get_settings, list_projects, list_estimations, get_user_by_id,
)
from utils import inject_css, render_sidebar_brand, page_header, format_currency

st.set_page_config(page_title="Profile • CIH", page_icon="👤", layout="wide")
init_db()
inject_css()
user = require_login()
user_id = user["id"]
settings = get_settings(user_id)
render_sidebar_brand(settings.get("company_name"))
render_user_sidebar()
page_header("My Profile", "Manage your account details and password.", icon="👤")

record = get_user_by_id(user_id) or user  # password hash is never returned

c1, c2, c3 = st.columns(3)
c1.metric("Projects", len(list_projects(user_id)))
c2.metric("Saved estimations", len(list_estimations(user_id)))
c3.metric("Member since", str(record.get("created_at") or "—")[:10])

st.markdown("### Account details")
with st.form("profile_form"):
    p1, p2 = st.columns(2)
    full_name = p1.text_input("Full name", value=record.get("full_name", ""))
    email = p2.text_input("Email", value=record.get("email", ""))
    st.text_input("Username (cannot be changed)", value=record.get("username", ""),
                  disabled=True)
    if st.form_submit_button("Save profile", use_container_width=True):
        result = update_profile(user_id, full_name, email)
        if result.ok:
            refresh_session_user()
            st.success(result.message)
            st.rerun()
        else:
            st.error(result.message)

st.markdown("### Change password")
with st.form("password_form", clear_on_submit=True):
    show = st.checkbox("Show passwords", key="profile_show_pwd")
    kind = "default" if show else "password"
    current_pwd = st.text_input("Current password", type=kind)
    q1, q2 = st.columns(2)
    new_pwd = q1.text_input("New password", type=kind)
    confirm_pwd = q2.text_input("Confirm new password", type=kind)
    st.caption("Minimum 8 characters, including at least one letter and one number.")
    if st.form_submit_button("Update password", use_container_width=True):
        result = change_password(user_id, current_pwd, new_pwd, confirm_pwd)
        if result.ok:
            st.success(result.message)
        else:
            st.error(result.message)

st.markdown("---")
st.caption(
    "Your password is stored only as a PBKDF2-SHA256 hash. "
    f"Portfolio value: {format_currency(sum(float(p.get('budget') or 0) for p in list_projects(user_id)), settings['currency'])}."
)
