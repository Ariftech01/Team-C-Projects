"""Login Screen for Construction Intelligence Hub."""
from __future__ import annotations

import streamlit as st
from auth.auth import authenticate, get_app_config, login_user, reset_password
from config.settings import BASE_DIR


def render_login() -> None:
    """Render modern centered login card."""
    app_cfg = get_app_config()
    company_name = app_cfg.get("company_name", "Construction Intelligence Hub")
    logo_path = app_cfg.get("logo_path")

    # Center card grid layout
    _, col, _ = st.columns([1, 1.8, 1])

    with col:
        if st.button("← Back to Welcome Page", key="login_back_to_welcome", type="secondary"):
            st.session_state["auth_view"] = "welcome"
            st.rerun()

        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

        # Header block with logo or fallback icon
        logo_html = ""
        if logo_path:
            full_logo_path = BASE_DIR / logo_path
            if full_logo_path.is_file():
                st.image(str(full_logo_path), width=80)
            else:
                logo_html = """<div style="display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px; background: linear-gradient(135deg, #1B3A5B, #0E7C7B); border-radius: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-bottom: 0.5rem;"><span style="font-size: 1.8rem;">🏗️</span></div>"""
        else:
            logo_html = """<div style="display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px; background: linear-gradient(135deg, #1B3A5B, #0E7C7B); border-radius: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-bottom: 0.5rem;"><span style="font-size: 1.8rem;">🏗️</span></div>"""

        if logo_html:
            st.markdown(f"<div style='text-align: center;'>{logo_html}</div>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 1.25rem;">
                <h2 style="margin: 0; font-weight: 800; font-size: 1.5rem; letter-spacing: -0.4px;">Sign In</h2>
                <p style="margin-top: 0.25rem; font-size: 0.85rem; color: #5F6B7A;">{company_name}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        login_tab, reset_tab = st.tabs(["🔑 Sign In", "❓ Forgot Password"])

        with login_tab:
            with st.container(border=True):
                with st.form("login_form", clear_on_submit=False):
                    email = st.text_input(
                        "Email Address",
                        placeholder="name@company.com",
                        key="login_email",
                    )
                    password = st.text_input(
                        "Password",
                        type="password",
                        placeholder="••••••••",
                        key="login_password",
                    )

                    st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
                    login_submitted = st.form_submit_button(
                        "Sign In →",
                        use_container_width=True,
                        type="primary",
                    )

                    if login_submitted:
                        if not email or not password:
                            st.error("Please enter both email and password.")
                        else:
                            success, message, user_info = authenticate(email, password)
                            if success:
                                login_user(user_info)
                                st.rerun()
                            else:
                                st.error(message)

        with reset_tab:
            with st.container(border=True):
                st.caption("Reset your administrator password")
                with st.form("reset_password_form", clear_on_submit=False):
                    reset_email = st.text_input("Registered Email", placeholder="admin@company.com", key="reset_email")
                    new_pwd = st.text_input("New Password", type="password", placeholder="••••••••", key="reset_new_pwd")
                    conf_pwd = st.text_input("Confirm New Password", type="password", placeholder="••••••••", key="reset_conf_pwd")
                    
                    st.markdown("<div style='margin-top: 0.75rem;'></div>", unsafe_allow_html=True)
                    reset_submitted = st.form_submit_button("Reset Password", use_container_width=True, type="secondary")
                    
                    if reset_submitted:
                        ok, msg = reset_password(reset_email, new_pwd, conf_pwd)
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
