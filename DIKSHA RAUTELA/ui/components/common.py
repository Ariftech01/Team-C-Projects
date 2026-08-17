"""Reusable UI components."""
from __future__ import annotations

import streamlit as st

from config.settings import APP_NAME, APP_VERSION
from ui.i18n import tr


# Page definitions: (page_key, display_label, icon)
_PAGES = [
    ("Dashboard",        "Dashboard",     "⊞"),
    ("Project Portfolio","Projects",      "◫"),
    ("AI Actions",       "AI Tool Center","✦"),
    ("Analytics",        "Analytics",     "▲"),
    ("Settings",         "Settings",      "⊙"),
]


def render_sidebar(active: str = "Dashboard") -> str:
    language = st.session_state.get("language", "English")

    with st.sidebar:
        # ── Brand ────────────────────────────────────────────────────────────
        st.markdown("""
<div class="sb-brand">
  <span class="sb-brand-icon">🏗</span>
  <div class="sb-brand-text">
    <span class="sb-brand-name">CIH</span>
    <span class="sb-brand-tag">Construction Intelligence</span>
  </div>
</div>""", unsafe_allow_html=True)

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

        # ── Navigation ───────────────────────────────────────────────────────
        pages = list(_PAGES)
        if st.session_state.get("current_project_id"):
            pages.insert(2, ("Project Workspace", "Workspace", "⊟"))

        st.markdown('<nav class="sb-nav">', unsafe_allow_html=True)
        for page_key, label, icon in pages:
            label = tr(label)
            is_active = page_key == active
            active_cls = "sb-nav-item sb-nav-active" if is_active else "sb-nav-item"
            # Render label as HTML; button is a zero-height invisible Streamlit widget
            st.markdown(f"""
                <div class="{active_cls}" id="nav-{page_key.replace(' ','-').lower()}">
                <span class="sb-nav-icon">{icon}</span>
                <span class="sb-nav-label">{label}</span>
                {"<span class='sb-nav-dot'></span>" if is_active else ""}
                </div>""", unsafe_allow_html=True)
            # The real clickable button — styled to overlay the HTML row
            # if st.button(
            #     label,
            #     key=f"nav_{page_key}",
            #     use_container_width=True,
            #     type="primary" if is_active else "secondary",
            # ):
            if st.button(
                "",
                key=f"nav_{page_key}",
                use_container_width=True,
                type="secondary",
            ):
            
                st.session_state["page"] = page_key
                if page_key != "Project Workspace":
                    st.session_state["current_project_id"] = None
                st.rerun()
        st.markdown("</nav>", unsafe_allow_html=True)

        # ── Spacer pushes controls to bottom ─────────────────────────────────
        st.markdown('<div class="sb-spacer"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

        # ── Theme & Language controls ─────────────────────────────────────────
        st.markdown('<p class="sb-ctrl-lbl">Appearance</p>', unsafe_allow_html=True)
        theme_mode = st.selectbox(
            "Theme",
            ["Light", "Dark"],
            index=0 if st.session_state.get("theme_mode", "Light") == "Light" else 1,
            key="sb_theme_select",
            label_visibility="collapsed",
        )
        if theme_mode != st.session_state.get("theme_mode", "Light"):
            st.session_state["theme_mode"] = theme_mode
            st.rerun()

        st.markdown('<p class="sb-ctrl-lbl" style="margin-top:0.5rem;">Language</p>', unsafe_allow_html=True)
        lang = st.selectbox(
            "Language",
            ["English", "Hindi"],
            index=0 if language == "English" else 1,
            key="sb_lang_select",
            label_visibility="collapsed",
        )
        if lang != language:
            st.session_state["language"] = lang
            st.rerun()

        # ── Logout & Account controls ─────────────────────────────────────────
        st.markdown('<p class="sb-ctrl-lbl" style="margin-top:0.5rem;">Account Profile</p>', unsafe_allow_html=True)
        user_info = st.session_state.get("auth_user", {})
        user_name = user_info.get("name", "Project Manager")
        user_role = user_info.get("role", st.session_state.get("pm_role", "Project Manager"))
        user_email = user_info.get("email", "admin@company.com")
        user_company = user_info.get("company", "Construction Intelligence Hub")

        st.markdown(
            f"""
            <div style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 0.6rem 0.75rem; margin-bottom: 0.5rem;">
                <div style="font-weight: 700; font-size: 0.85rem; color: #FFFFFF;">👤 {user_name}</div>
                <div style="font-size: 0.72rem; color: rgba(255,255,255,0.65); margin-top: 0.15rem;">
                    <span style="background: rgba(14,124,123,0.3); border: 1px solid rgba(77,208,200,0.4); border-radius: 10px; padding: 0.1rem 0.45rem; font-size: 0.65rem; color: #4DD0C8; font-weight: 600;">{user_role}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("⚙️ Edit Profile"):
            with st.form("sidebar_edit_profile_form", clear_on_submit=False):
                p_name = st.text_input("Name", value=user_name, key="sb_prof_name")
                p_email = st.text_input("Email", value=user_email, key="sb_prof_email")
                p_role = st.selectbox("Role", ["Administrator", "Project Manager", "Site Engineer", "Viewer"], index=["Administrator", "Project Manager", "Site Engineer", "Viewer"].index(user_role) if user_role in ["Administrator", "Project Manager", "Site Engineer", "Viewer"] else 1, key="sb_prof_role")
                p_company = st.text_input("Company", value=user_company, key="sb_prof_company")
                p_save = st.form_submit_button("Save Profile", use_container_width=True, type="secondary")
                if p_save:
                    from auth.auth import update_user_profile
                    ok, msg = update_user_profile(p_name, p_email, p_role, p_company)
                    if ok:
                        st.success("Updated!")
                        st.rerun()
                    else:
                        st.error(msg)

        st.markdown(f"""
            <div class="sb-nav-item" id="nav-logout">
            <span class="sb-nav-icon">🚪</span>
            <span class="sb-nav-label">Logout</span>
            </div>""", unsafe_allow_html=True)

        if st.button("", key="nav_logout_btn", use_container_width=True, type="secondary"):
            from auth.auth import logout_user
            logout_user()
            st.rerun()

        # ── Version footer ────────────────────────────────────────────────────
        st.markdown(f'<p class="sb-version">v{APP_VERSION}</p>', unsafe_allow_html=True)

    return st.session_state.get("page", "Dashboard")


# ─────────────────────────────────────────────────────────────────────────────
# Helper widgets (unchanged signatures — used by other pages)
# ─────────────────────────────────────────────────────────────────────────────

def kpi_tile(label: str, value: str, delta: str = "", color: str = "", icon: str = "") -> None:
    with st.container(border=True):
        st.metric(label, value, delta or None)


def status_pill(status: str) -> str:
    return status


def priority_pill(priority: str) -> str:
    return priority


def health_pill(score: float) -> str:
    label = "Healthy" if score >= 80 else "At Risk" if score >= 60 else "Critical"
    return f"{label} {score:.0f}"


def progress_bar(progress: float, color: str = "") -> str:
    return f"{max(0, min(100, progress)):.0f}%"


def alert(message: str, kind: str = "info") -> None:
    if kind == "error":
        st.error(message)
    elif kind in {"warn", "warning"}:
        st.warning(message)
    elif kind == "success":
        st.success(message)
    else:
        st.info(message)


def section_header(title: str, subtitle: str = "") -> None:
    st.subheader(title)
    if subtitle:
        st.caption(subtitle)


def empty_state(message: str, icon: str = "") -> None:
    st.info(message)
