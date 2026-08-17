# Construction Intelligence Hub — main entry point.

# it Don't evaluate type hints now. just store them as text
from __future__ import annotations

import streamlit as st

from config.settings import APP_NAME, APP_TAGLINE
# loads entire design system.
from ui.components.theme import inject_css
from ui.components.common import render_sidebar
from ui.components.notifications import render_notification_center

from ui.pages.dashboard import render_dashboard
from ui.pages.portfolio import render_portfolio
from ui.workspace.workspace import render_workspace

from ui.ai_assistant import render_ai_assistant
from ui.pages.ai_actions import render_ai_actions
from ui.pages.analytics import render_analytics
from ui.pages.settings import render_settings
from ui.pages.welcome import render_welcome
from auth import is_configured, is_logged_in, render_login, render_setup


def _init_state() -> None: #Internal function.
    defaults = { #This dictionary is the application's memory.
        "page": "Dashboard",
        "auth_view": "welcome",
        "current_project_id": None,  #no project is selected initially
        "show_new_project": False, #Whether New Project popup should appear.
        # "open_ai_assistant": False,
        "ai_float_expanded": False,
        "ai_chat_history": [], #empty list.
        "ai_current_context": {},
        "ai_last_page": "Dashboard",
        "ai_suggestions": [],
        "theme_mode": "Dark", #Current application theme.
        "language": "English",
        "notifications_enabled": True, #Whether notifications appear.
        "daily_digest": True, #Daily report emails.
        "cost_alert_threshold": 85, #when exceeded generate alert
        "safety_alerts": True, 
        "pm_role": "Project Manager", #Role Based Access Control
        "report_cadence": "Daily",
        "working_region": "India",
    }
    for k, v in defaults.items(): # Loop through every dictionary item.
        if k not in st.session_state:
            st.session_state[k] = v

def main() -> None:
    st.set_page_config(
        page_title=f"{APP_NAME} — {APP_TAGLINE}", #Browser tab title.
        page_icon="🏗️", #Browser favicon.
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _init_state() # Creates memory.
    inject_css() # Loads styling.

    # ── Authentication Interception & Welcome Experience ──────────────────────
    if not is_logged_in():
        auth_view = st.session_state.get("auth_view", "welcome")
        if auth_view == "login":
            render_login()
            return
        elif auth_view == "setup":
            render_setup()
            return
        else:
            render_welcome()
            return

    # Sidebar navigation
    current_page = st.session_state.get("page", "Dashboard")
    render_sidebar(active=current_page)

    # Route to page (manual routing)
    if current_page == "Dashboard":
        render_dashboard()

    elif current_page == "Project Portfolio":
        render_portfolio()

    elif current_page == "Project Workspace":
        render_workspace()

    elif current_page == "AI Actions":
        render_ai_actions()

    elif current_page == "Analytics":
        render_analytics()

    elif current_page == "Settings":
        render_settings()

    else:
        render_dashboard()

    # Floating notification center and AI assistant on every page
    render_notification_center()
    render_ai_assistant()


if __name__ == "__main__":
    main()
