"""Core authentication and setup helper functions for Construction Intelligence Hub."""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import streamlit as st

from config.settings import BASE_DIR, DATA_DIR, UPLOADS_DIR

CONFIG_DIR = BASE_DIR / "config"
APP_CONFIG_PATH = CONFIG_DIR / "app_config.json"
CREDENTIALS_PATH = DATA_DIR / "credentials.json"
SALT = b"cih_auth_salt_v1_2026"


def hash_password(password: str) -> str:
    """Hash password securely using PBKDF2 HMAC SHA-256."""
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), SALT, 100000
    ).hex()


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password input against stored PBKDF2 hash."""
    return hash_password(password) == stored_hash


def is_configured() -> bool:
    """Check if application setup has been completed."""
    if not APP_CONFIG_PATH.is_file() or not CREDENTIALS_PATH.is_file():
        return False
    try:
        with open(APP_CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
            creds = json.load(f)
        return bool(cfg.get("company_name") and creds.get("email") and creds.get("password_hash"))
    except Exception:
        return False


def is_logged_in() -> bool:
    """Check if user is logged in via Streamlit session state."""
    return bool(st.session_state.get("logged_in", False))


def get_app_config() -> dict:
    """Load application configuration from JSON."""
    if not APP_CONFIG_PATH.is_file():
        return {}
    try:
        with open(APP_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_credentials() -> dict:
    """Load user credentials from JSON (without returning plaintext password)."""
    if not CREDENTIALS_PATH.is_file():
        return {}
    try:
        with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_setup(
    company_name: str,
    admin_name: str,
    email: str,
    password: str,
    confirm_password: str,
    logo_file=None,
) -> tuple[bool, str]:
    """Validate setup inputs and create configuration/credentials JSON files."""
    company_name = company_name.strip()
    admin_name = admin_name.strip()
    email = email.strip().lower()

    if not company_name:
        return False, "Company Name is required."
    if not admin_name:
        return False, "Admin Name is required."
    if not email:
        return False, "Admin Email cannot be empty."
    if "@" not in email or "." not in email:
        return False, "Please enter a valid email address."
    if not password:
        return False, "Password is required."
    if password != confirm_password:
        return False, "Passwords do not match."

    # Handle logo upload if provided
    logo_rel_path = None
    if logo_file is not None:
        try:
            UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
            suffix = Path(logo_file.name).suffix or ".png"
            logo_filename = f"company_logo{suffix}"
            logo_full_path = UPLOADS_DIR / logo_filename
            with open(logo_full_path, "wb") as f:
                f.write(logo_file.getbuffer())
            logo_rel_path = f"data/uploads/{logo_filename}"
        except Exception as e:
            # Non-blocking error for logo
            pass

    now_iso = datetime.now().isoformat()

    # Save App Config
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    app_config_data = {
        "company_name": company_name,
        "logo_path": logo_rel_path,
        "created_at": now_iso,
    }
    with open(APP_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(app_config_data, f, indent=2)

    # Save Credentials
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    credentials_data = {
        "name": admin_name,
        "email": email,
        "password_hash": hash_password(password),
        "created_at": now_iso,
    }
    with open(CREDENTIALS_PATH, "w", encoding="utf-8") as f:
        json.dump(credentials_data, f, indent=2)

    return True, "Setup completed successfully"


def authenticate(email: str, password: str) -> tuple[bool, str, dict]:
    """Validate credentials against data/credentials.json."""
    creds = get_credentials()
    if not creds:
        return False, "No configured user found. Please complete setup first.", {}

    stored_email = creds.get("email", "").strip().lower()
    stored_hash = creds.get("password_hash", "")

    if email.strip().lower() != stored_email:
        return False, "Invalid email or password.", {}

    if not verify_password(password, stored_hash):
        return False, "Invalid email or password.", {}

    user_info = {
        "name": creds.get("name", "Admin"),
        "email": stored_email,
        "role": creds.get("role", "Administrator"),
        "company": get_app_config().get("company_name", "Construction Intelligence Hub"),
    }
    return True, "Authentication successful", user_info


def reset_password(email: str, new_password: str, confirm_password: str) -> tuple[bool, str]:
    """Reset administrator password given valid email."""
    email = email.strip().lower()
    if not email or "@" not in email:
        return False, "Please enter a valid email address."
    if not new_password:
        return False, "New password is required."
    if new_password != confirm_password:
        return False, "Passwords do not match."

    creds = get_credentials()
    if not creds:
        return False, "No user credentials found."
    if creds.get("email", "").strip().lower() != email:
        return False, "No matching account found for that email."

    creds["password_hash"] = hash_password(new_password)
    creds["updated_at"] = datetime.now().isoformat()
    with open(CREDENTIALS_PATH, "w", encoding="utf-8") as f:
        json.dump(creds, f, indent=2)

    return True, "Password reset successfully. Please log in with your new password."


def update_user_profile(name: str, email: str, role: str, company: str) -> tuple[bool, str]:
    """Update profile information in session state and credentials file."""
    creds = get_credentials()
    if not creds:
        return False, "No profile found to update."

    name = name.strip()
    email = email.strip().lower()
    if not name or not email:
        return False, "Name and Email cannot be empty."

    creds["name"] = name
    creds["email"] = email
    creds["role"] = role
    with open(CREDENTIALS_PATH, "w", encoding="utf-8") as f:
        json.dump(creds, f, indent=2)

    cfg = get_app_config()
    cfg["company_name"] = company
    with open(APP_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

    if "auth_user" in st.session_state:
        st.session_state["auth_user"]["name"] = name
        st.session_state["auth_user"]["email"] = email
        st.session_state["auth_user"]["role"] = role
        st.session_state["auth_user"]["company"] = company
    st.session_state["pm_role"] = role

    return True, "Profile updated successfully."


def login_user(user_info: dict) -> None:
    """Set session state flags upon successful authentication."""
    st.session_state["logged_in"] = True
    st.session_state["auth_user"] = user_info
    st.session_state["pm_role"] = user_info.get("role", "Project Manager")


def logout_user() -> None:
    """Clear authentication session state without disrupting app memory."""
    st.session_state["logged_in"] = False
    st.session_state.pop("auth_user", None)
    st.session_state["auth_view"] = "welcome"

