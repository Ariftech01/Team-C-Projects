"""Authentication UI — premium login / sign-up screen, guard and sidebar profile."""
from __future__ import annotations

import streamlit as st

from auth import (
    MIN_PASSWORD_LENGTH, authenticate, current_user, is_authenticated,
    login_session, logout_session, register_user,
)
from utils import inject_css


def _auth_hero() -> None:
    st.markdown(
        """
        <div class="cih-auth-hero">
          <div class="cih-auth-logo">CI</div>
          <h1>Construction Intelligence Hub</h1>
          <p>
            The AI-powered command centre for construction projects — estimating,
            analytics, reporting and a project-aware assistant, all in one place.
          </p>
          <ul class="cih-auth-points">
            <li><span>🏗️</span> Portfolio &amp; project management</li>
            <li><span>🧮</span> Engineering-grade material estimation</li>
            <li><span>🤖</span> Local AI assistant grounded in your own data</li>
            <li><span>📄</span> Professional PDF &amp; Excel reporting</li>
          </ul>
          <div class="cih-auth-hero-foot">Your data stays on your machine — SQLite + local Ollama.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _login_form() -> None:
    st.markdown('<div class="cih-auth-form-title">Sign in to your workspace</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="cih-auth-form-sub">Use your email address or username.</div>',
                unsafe_allow_html=True)

    remembered = st.session_state.get("cih_remembered_identifier", "")
    with st.form("cih_login_form", clear_on_submit=False):
        identifier = st.text_input("Email or username", value=remembered,
                                   placeholder="you@company.com")
        show_pwd = st.checkbox("Show password", key="cih_show_login_pwd")
        password = st.text_input("Password", type="default" if show_pwd else "password",
                                 placeholder="Enter your password")
        remember = st.checkbox("Remember me on this device", value=bool(remembered))
        submitted = st.form_submit_button("Log in", use_container_width=True, type="primary")

    if submitted:
        result = authenticate(identifier, password)
        if result.ok and result.user:
            if remember:
                st.session_state["cih_remembered_identifier"] = identifier.strip()
            else:
                st.session_state.pop("cih_remembered_identifier", None)
            login_session(result.user)
            st.success(result.message)
            st.rerun()
        else:
            st.error(result.message)


def _signup_form() -> None:
    st.markdown('<div class="cih-auth-form-title">Create your account</div>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div class="cih-auth-form-sub">Passwords need at least {MIN_PASSWORD_LENGTH} '
        "characters, including one letter and one number.</div>",
        unsafe_allow_html=True,
    )

    with st.form("cih_signup_form", clear_on_submit=False):
        full_name = st.text_input("Full name", placeholder="Jane Doe")
        c1, c2 = st.columns(2)
        email = c1.text_input("Email", placeholder="you@company.com")
        username = c2.text_input("Username", placeholder="jane.doe")
        show_pwd = st.checkbox("Show passwords", key="cih_show_signup_pwd")
        kind = "default" if show_pwd else "password"
        c3, c4 = st.columns(2)
        password = c3.text_input("Password", type=kind)
        confirm = c4.text_input("Confirm password", type=kind)
        submitted = st.form_submit_button("Create account", use_container_width=True,
                                          type="primary")

    if submitted:
        result = register_user(full_name, email, username, password, confirm)
        if result.ok:
            st.success(result.message + " Switch to the **Login** tab to continue.")
        else:
            st.error(result.message)


def render_auth_page() -> None:
    """Full-screen login / sign-up experience."""
    inject_css()
    st.markdown('<div class="cih-auth-wrap">', unsafe_allow_html=True)
    left, right = st.columns([1.05, 1], gap="large")
    with left:
        _auth_hero()
    with right:
        st.markdown('<div class="cih-auth-card">', unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["🔐  Login", "✨  Create account"])
        with tab_login:
            _login_form()
        with tab_signup:
            _signup_form()
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        '<div class="cih-auth-footer">© Construction Intelligence Hub — '
        "Streamlit · Python · SQLite · Ollama llama3.2</div>",
        unsafe_allow_html=True,
    )


def render_user_sidebar() -> None:
    """Logged-in profile block with a working logout button."""
    user = current_user()
    if not user:
        return
    initials = "".join(part[0] for part in user["full_name"].split()[:2]).upper() or "U"
    st.sidebar.markdown(
        f"""
        <div class="cih-user-card">
          <div class="cih-user-avatar">{initials}</div>
          <div class="cih-user-meta">
            <div class="cih-user-name">{user['full_name']}</div>
            <div class="cih-user-mail">{user['email']}</div>
            <div class="cih-user-status"><span class="cih-dot"></span> Signed in</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.sidebar.button("🚪 Log out", use_container_width=True, key="cih_logout_btn"):
        logout_session()
        st.success("You have been logged out.")
        st.rerun()


def require_login() -> dict:
    """Guard for every page. Returns the authenticated user or stops the page."""
    if not is_authenticated():
        st.markdown(
            "<style>[data-testid='stSidebar']{display:none;}</style>",
            unsafe_allow_html=True,
        )
        st.warning("Please log in to access Construction Intelligence Hub.")
        render_auth_page()
        st.stop()
    return current_user()  # type: ignore[return-value]
