"""Floating notification center shared by all authenticated pages."""
from __future__ import annotations

import streamlit as st

from repository import get_repository
from services.notification_service import list_notifications, mark_all_read, refresh_project_notifications, unread_count
from ui.i18n import tr


@st.dialog("Notifications", width="small")
def _notification_dialog() -> None:
    items = list_notifications()
    if not items:
        st.info(tr("No notifications"))
        return
    if st.button(tr("Mark all as read"), use_container_width=True, key="mark_notifications_read"):
        mark_all_read()
        st.rerun()
    for item in items[:20]:
        icon = "🚨" if item.get("level") == "critical" else "⚠️"
        st.markdown(f"**{icon} {item.get('title', 'Notification')}**")
        st.caption(item.get("message", ""))
        st.divider()


def render_notification_center() -> None:
    if not st.session_state.get("notifications_enabled", True):
        return
    projects = get_repository().list_projects()
    refresh_project_notifications(projects, int(st.session_state.get("cost_alert_threshold", 85)), bool(st.session_state.get("safety_alerts", True)))
    count = unread_count()
    st.markdown("""<style>.st-key-notification_launcher {position:fixed;right:1.5rem;bottom:6rem;z-index:999;width:auto}.st-key-notification_launcher button{border-radius:999px;min-height:2.75rem;background:var(--cih-surface);color:var(--cih-text);border:1px solid var(--cih-border);box-shadow:0 6px 18px rgba(0,0,0,.18)}</style>""", unsafe_allow_html=True)
    label = f"🔔 {count}" if count else "🔔"
    if st.button(label, key="notification_launcher", help=tr("Notifications")):
        _notification_dialog()