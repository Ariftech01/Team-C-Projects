"""Application preferences, notifications, and email delivery setup."""
from __future__ import annotations

import streamlit as st

from services.notification_service import get_email_settings, save_email_settings, send_email
from ui.i18n import tr


def render_settings() -> None:
    st.title(tr("Settings"))
    st.caption("Configure appearance, language, notifications, and email delivery.")
    with st.container(border=True):
        st.subheader(tr("Appearance"))
        theme = st.radio(tr("Theme"), ["Light", "Dark"], index=0 if st.session_state.get("theme_mode", "Light") == "Light" else 1, horizontal=True)
        if theme != st.session_state.get("theme_mode"):
            st.session_state["theme_mode"] = theme
            st.rerun()
    with st.container(border=True):
        st.subheader(tr("Language"))
        language = st.radio("Interface Language", ["English", "Hindi"], index=0 if st.session_state.get("language", "English") == "English" else 1, horizontal=True)
        if language != st.session_state.get("language"):
            st.session_state["language"] = language
            st.rerun()
        st.caption("The selected language is applied to shared navigation, settings, notifications, and new dashboard guidance.")
    with st.container(border=True):
        st.subheader(tr("Project Manager Alerts"))
        st.session_state["notifications_enabled"] = st.checkbox(tr("Enable notifications"), value=st.session_state.get("notifications_enabled", True))
        st.session_state["daily_digest"] = st.checkbox(tr("Daily project digest"), value=st.session_state.get("daily_digest", True))
        st.session_state["safety_alerts"] = st.checkbox(tr("Safety incident alerts"), value=st.session_state.get("safety_alerts", True))
        st.session_state["cost_alert_threshold"] = st.slider("Budget alert threshold (%)", 50, 100, int(st.session_state.get("cost_alert_threshold", 85)))
        st.caption("The floating bell shows delays, budget risks, and open safety incidents.")
    with st.container(border=True):
        st.subheader(tr("Email delivery"))
        st.caption("Use your organisation's SMTP details. For Gmail, use an App Password—not your normal Gmail password.")
        current = get_email_settings()
        with st.form("email_settings_form"):
            enabled = st.checkbox(tr("Email notifications"), value=bool(current.get("enabled", False)))
            col_a, col_b = st.columns(2)
            with col_a:
                host = st.text_input("SMTP host", value=current.get("smtp_host", "smtp.gmail.com"), placeholder="smtp.gmail.com")
                port = st.number_input("SMTP port", min_value=1, max_value=65535, value=int(current.get("smtp_port", 587)), step=1)
                sender = st.text_input(tr("Sender email"), value=current.get("sender_email", ""), placeholder="alerts@company.com")
            with col_b:
                recipient = st.text_input(tr("Recipient email"), value=current.get("recipient_email", ""), placeholder="manager@company.com")
                password = st.text_input("SMTP password / App Password", value=current.get("sender_password", ""), type="password")
                tls = st.checkbox("Use TLS", value=bool(current.get("use_tls", True)))
            save_col, test_col = st.columns(2)
            with save_col:
                saved = st.form_submit_button(tr("Save email settings"), type="primary", use_container_width=True)
            with test_col:
                test_clicked = st.form_submit_button(tr("Send test email"), use_container_width=True)
            email_config = {"enabled": enabled, "smtp_host": host.strip(), "smtp_port": int(port), "sender_email": sender.strip(), "sender_password": password, "recipient_email": recipient.strip(), "use_tls": tls}
            valid_config = "@" in sender and "@" in recipient and bool(host.strip()) and bool(password.strip())
            if saved:
                if enabled and not valid_config:
                    st.error("Enter valid sender, recipient, SMTP host, and password before enabling email notifications.")
                else:
                    save_email_settings(email_config)
                    st.success("Email settings saved.")
            if test_clicked:
                if not valid_config:
                    st.error("Enter a valid sender, recipient, SMTP host, and App Password before testing.")
                else:
                    # Test exactly the fields currently visible in this form, then persist them on success.
                    email_config["enabled"] = True
                    ok, message = send_email("Construction Intelligence Hub test", "Your Construction Intelligence Hub email notifications are configured correctly.", email_config)
                    if ok:
                        save_email_settings(email_config)
                        st.success(message)
                    else:
                        st.error(message)
    st.success("Settings are applied.")