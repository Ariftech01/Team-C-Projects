"""Authentication layer — password hashing, validation and session handling.

Passwords are never stored in plain text. Hashing uses
``werkzeug.security`` (PBKDF2-SHA256) when available, with an equivalent
stdlib PBKDF2-SHA256 implementation as a fallback so the app still runs if
Werkzeug is missing.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
from dataclasses import dataclass

import streamlit as st

from database import (
    create_user, email_exists, get_user_by_id, get_user_credentials,
    touch_last_login, update_user_password, update_user_profile,
    username_exists,
)

try:  # preferred implementation
    from werkzeug.security import check_password_hash as _wz_check
    from werkzeug.security import generate_password_hash as _wz_generate
    _HAS_WERKZEUG = True
except Exception:  # pragma: no cover - fallback path
    _HAS_WERKZEUG = False

PBKDF2_ITERATIONS = 260_000
MIN_PASSWORD_LENGTH = 8
SESSION_KEY = "cih_user"

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.\-]{3,32}$")


# --------------------------------------------------------------------- hashing
def hash_password(password: str) -> str:
    if _HAS_WERKZEUG:
        return _wz_generate(password, method="pbkdf2:sha256")
    salt = base64.b64encode(os.urandom(16)).decode()
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), PBKDF2_ITERATIONS
    )
    return f"pbkdf2:sha256:{PBKDF2_ITERATIONS}${salt}${dk.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash:
        return False
    try:
        if _HAS_WERKZEUG and stored_hash.startswith("pbkdf2:"):
            return _wz_check(stored_hash, password)
        algo, salt, hexdigest = stored_hash.split("$")
        iterations = int(algo.split(":")[2])
        dk = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), iterations
        )
        return hmac.compare_digest(dk.hex(), hexdigest)
    except Exception:
        return False


# ------------------------------------------------------------------ validation
def password_problems(password: str) -> list[str]:
    problems: list[str] = []
    if len(password) < MIN_PASSWORD_LENGTH:
        problems.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
    if not re.search(r"[A-Za-z]", password):
        problems.append("Password must contain at least one letter.")
    if not re.search(r"\d", password):
        problems.append("Password must contain at least one number.")
    return problems


def valid_email(email: str) -> bool:
    return bool(EMAIL_RE.match((email or "").strip()))


def valid_username(username: str) -> bool:
    return bool(USERNAME_RE.match((username or "").strip()))


@dataclass
class AuthResult:
    ok: bool
    message: str
    user: dict | None = None


# ------------------------------------------------------------------- registration
def register_user(full_name: str, email: str, username: str,
                  password: str, confirm: str) -> AuthResult:
    full_name = (full_name or "").strip()
    email = (email or "").strip()
    username = (username or "").strip()

    if not full_name or not email or not username or not password or not confirm:
        return AuthResult(False, "All fields are required.")
    if len(full_name) < 2:
        return AuthResult(False, "Please enter your full name.")
    if not valid_email(email):
        return AuthResult(False, "Please enter a valid email address.")
    if not valid_username(username):
        return AuthResult(
            False,
            "Username must be 3-32 characters and may contain letters, numbers, "
            ". _ and - only.",
        )
    problems = password_problems(password)
    if problems:
        return AuthResult(False, " ".join(problems))
    if password != confirm:
        return AuthResult(False, "Passwords do not match.")
    if email_exists(email):
        return AuthResult(False, "An account with this email already exists.")
    if username_exists(username):
        return AuthResult(False, "This username is already taken.")

    user_id = create_user(full_name, email, username, hash_password(password))
    user = get_user_by_id(user_id)
    return AuthResult(True, "Account created successfully. You can now log in.", user)


# ------------------------------------------------------------------------ login
def authenticate(identifier: str, password: str) -> AuthResult:
    identifier = (identifier or "").strip()
    if not identifier or not password:
        return AuthResult(False, "Please enter both your credentials and password.")
    record = get_user_credentials(identifier)
    if not record or not verify_password(password, record.get("password_hash", "")):
        # deliberately generic to avoid leaking which accounts exist
        return AuthResult(False, "Invalid credentials. Please check and try again.")
    touch_last_login(record["id"])
    record.pop("password_hash", None)
    return AuthResult(True, f"Welcome back, {record['full_name'].split(' ')[0]}!", record)


def change_password(user_id: int, current_password: str,
                    new_password: str, confirm: str) -> AuthResult:
    record = get_user_credentials_by_id(user_id)
    if not record:
        return AuthResult(False, "User not found.")
    if not verify_password(current_password, record.get("password_hash", "")):
        return AuthResult(False, "Your current password is incorrect.")
    problems = password_problems(new_password)
    if problems:
        return AuthResult(False, " ".join(problems))
    if new_password != confirm:
        return AuthResult(False, "New passwords do not match.")
    if verify_password(new_password, record.get("password_hash", "")):
        return AuthResult(False, "The new password must be different from the current one.")
    update_user_password(user_id, hash_password(new_password))
    return AuthResult(True, "Password updated successfully.")


def get_user_credentials_by_id(user_id: int) -> dict | None:
    user = get_user_by_id(user_id)
    if not user:
        return None
    return get_user_credentials(user["username"])


def update_profile(user_id: int, full_name: str, email: str) -> AuthResult:
    full_name = (full_name or "").strip()
    email = (email or "").strip()
    if len(full_name) < 2:
        return AuthResult(False, "Please enter your full name.")
    if not valid_email(email):
        return AuthResult(False, "Please enter a valid email address.")
    current = get_user_by_id(user_id)
    if not current:
        return AuthResult(False, "User not found.")
    if email.lower() != (current["email"] or "").lower() and email_exists(email):
        return AuthResult(False, "That email is already used by another account.")
    update_user_profile(user_id, full_name, email)
    return AuthResult(True, "Profile updated.", get_user_by_id(user_id))


# ---------------------------------------------------------------------- session
def login_session(user: dict) -> None:
    st.session_state[SESSION_KEY] = {
        "id": user["id"],
        "full_name": user["full_name"],
        "email": user["email"],
        "username": user["username"],
    }


def logout_session() -> None:
    st.session_state.pop(SESSION_KEY, None)
    # drop per-user working state so nothing leaks between accounts
    for key in ("chat_session_id", "last_estimate"):
        st.session_state.pop(key, None)


def current_user() -> dict | None:
    return st.session_state.get(SESSION_KEY)


def is_authenticated() -> bool:
    user = current_user()
    return bool(user and user.get("id"))


def current_user_id() -> int | None:
    user = current_user()
    return user["id"] if user else None


def refresh_session_user() -> None:
    """Re-read the profile from SQLite after an update."""
    uid = current_user_id()
    if uid:
        fresh = get_user_by_id(uid)
        if fresh:
            login_session(fresh)
