"""Persistent in-app and SMTP email notification support."""
from __future__ import annotations

import json
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from typing import Any

from config.settings import DATA_DIR
from models.domain import Project

NOTIFICATIONS_PATH = DATA_DIR / "notifications.json"
EMAIL_SETTINGS_PATH = DATA_DIR / "email_settings.json"


def _read(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else default
    except (OSError, json.JSONDecodeError):
        return default


def _write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(path)


def list_notifications() -> list[dict[str, Any]]:
    return sorted(_read(NOTIFICATIONS_PATH, {"items": []}).get("items", []), key=lambda item: item.get("created_at", ""), reverse=True)


def unread_count() -> int:
    return sum(1 for item in list_notifications() if not item.get("read", False))


def mark_all_read() -> None:
    data = _read(NOTIFICATIONS_PATH, {"items": []})
    for item in data.get("items", []):
        item["read"] = True
    _write(NOTIFICATIONS_PATH, data)


def _add_once(key: str, title: str, message: str, level: str) -> None:
    data = _read(NOTIFICATIONS_PATH, {"items": []})
    if any(item.get("key") == key for item in data.get("items", [])):
        return
    data.setdefault("items", []).append({"key": key, "title": title, "message": message, "level": level, "read": False, "created_at": datetime.now().isoformat(timespec="seconds")})
    _write(NOTIFICATIONS_PATH, data)
    # Deliver each newly-created required alert when SMTP email is enabled.
    if get_email_settings().get("enabled", False):
        send_email(f"Construction Intelligence Hub: {title}", message)


def refresh_project_notifications(projects: list[Project], budget_threshold: int, safety_enabled: bool) -> None:
    """Create one current alert per project risk; safe to call on every rerun."""
    today = datetime.now().date().isoformat()
    for project in projects:
        if project.is_delayed:
            _add_once(f"{today}:{project.id}:delay", "Schedule delay", f"{project.name} is delayed. Review its recovery plan.", "warning")
        if project.budget_utilization >= budget_threshold:
            _add_once(f"{today}:{project.id}:budget", "Budget alert", f"{project.name} has used {project.budget_utilization:.0f}% of its budget.", "warning")
        if safety_enabled:
            open_incidents = sum(1 for incident in project.safety_incidents if incident.status == "Open")
            if open_incidents:
                _add_once(f"{today}:{project.id}:safety", "Safety action required", f"{project.name} has {open_incidents} open safety incident(s).", "critical")


def get_email_settings() -> dict[str, Any]:
    return _read(EMAIL_SETTINGS_PATH, {"enabled": False, "smtp_host": "smtp.gmail.com", "smtp_port": 587, "sender_email": "", "sender_password": "", "recipient_email": "", "use_tls": True})


def save_email_settings(settings: dict[str, Any]) -> None:
    _write(EMAIL_SETTINGS_PATH, settings)


def send_email(subject: str, body: str, settings: dict[str, Any] | None = None) -> tuple[bool, str]:
    """Send email using saved settings or the values currently entered in Settings."""
    settings = settings or get_email_settings()
    required = ("smtp_host", "smtp_port", "sender_email", "sender_password", "recipient_email")
    if not settings.get("enabled") or any(not settings.get(key) for key in required):
        return False, "Email notifications are disabled or SMTP details are incomplete."
    try:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = settings["sender_email"]
        message["To"] = settings["recipient_email"]
        message.set_content(body)
        password = "".join(str(settings["sender_password"]).split())
        with smtplib.SMTP(settings["smtp_host"], int(settings["smtp_port"]), timeout=10) as server:
            server.ehlo()
            if settings.get("use_tls", True):
                server.starttls()
                server.ehlo()
            server.login(settings["sender_email"], password)
            server.send_message(message)
        return True, "Email sent successfully."
    except smtplib.SMTPAuthenticationError:
        return False, ("Gmail rejected the login. The sender must be the Gmail account that created the App Password. "
                       "Create a fresh 16-character App Password after enabling 2-Step Verification; do not use your normal Gmail password. "
                       "Google Workspace administrators can disable App Passwords.")
    except Exception as exc:
        return False, f"Email could not be sent: {exc}"