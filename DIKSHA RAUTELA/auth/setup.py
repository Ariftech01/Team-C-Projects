"""First-Time Setup Wizard for Construction Intelligence Hub."""
from __future__ import annotations

import streamlit as st
from auth.auth import save_setup


def render_setup() -> None:
    """Render onboarding setup wizard centered card."""
    # Outer layout container centering the card
    _, col, _ = st.columns([1, 2.2, 1])

    with col:
        if st.button("← Back to Welcome Page", key="setup_back_to_welcome", type="secondary"):
            st.session_state["auth_view"] = "welcome"
            st.rerun()

        st.markdown(
            """
            <div style="text-align: center; margin-top: 1.5rem; margin-bottom: 1.5rem;">
                <div style="display: inline-flex; align-items: center; justify-content: center; width: 64px; height: 64px; background: linear-gradient(135deg, #1B3A5B, #0E7C7B); border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); margin-bottom: 0.75rem;">
                    <span style="font-size: 2.2rem;">🏗️</span>
                </div>
                <h2 style="margin: 0; font-weight: 800; font-size: 1.6rem; letter-spacing: -0.5px;">Initial System Setup</h2>
                <p style="margin-top: 0.3rem; font-size: 0.88rem; color: #5F6B7A;">Welcome to Construction Intelligence Hub. Please configure your administrator account to begin.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.subheader("Account & Workspace Configuration")
            st.caption("Step 1 of 1 — Required system setup")

            with st.form("setup_form", clear_on_submit=False):
                company_name = st.text_input(
                    "Company Name *",
                    placeholder="e.g. Apex Infrastructure Ltd.",
                    help="Enter your organization or company name",
                )

                admin_name = st.text_input(
                    "Administrator Full Name *",
                    placeholder="e.g. Sarah Jenkins",
                    help="Name of the primary system administrator",
                )

                email = st.text_input(
                    "Administrator Email *",
                    placeholder="e.g. admin@company.com",
                    help="Will be used for sign in credentials",
                )

                col1, col2 = st.columns(2)
                with col1:
                    password = st.text_input(
                        "Password *",
                        type="password",
                        placeholder="••••••••",
                        help="Secure password",
                    )
                with col2:
                    confirm_password = st.text_input(
                        "Confirm Password *",
                        type="password",
                        placeholder="••••••••",
                        help="Re-enter password",
                    )

                logo_file = st.file_uploader(
                    "Company Logo (Optional)",
                    type=["png", "jpg", "jpeg", "svg"],
                    help="Upload your corporate logo for reports and headers",
                )

                st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
                submit_button = st.form_submit_button(
                    "Finish Setup →",
                    use_container_width=True,
                    type="primary",
                )

                if submit_button:
                    success, message = save_setup(
                        company_name=company_name,
                        admin_name=admin_name,
                        email=email,
                        password=password,
                        confirm_password=confirm_password,
                        logo_file=logo_file,
                    )

                    if success:
                        st.success("Setup completed successfully! Redirecting to Login...")
                        st.rerun()
                    else:
                        st.error(message)
