"""SQLite persistence layer for Construction Intelligence Hub.

Multi-user aware: every user-owned record (projects, estimations, chat history
and settings) is scoped by ``user_id``. Schema upgrades are applied in place by
:func:`init_db` so existing databases keep their data.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

DB_PATH = Path(__file__).resolve().parent / "construction.db"

# Settings rows owned by this pseudo-user act as the global defaults that every
# newly created account inherits.
GLOBAL_SETTINGS_USER_ID = 0


DEFAULT_SETTINGS = {
    "company_name": "Construction Intelligence Hub",
    "currency": "INR",
    "tax_percent": 18.0,
    "labor_cost_per_sqft": 250.0,
    "rate_bricks_per_unit": 9.0,          # per brick
    "rate_cement_per_bag": 400.0,         # 50 kg bag
    "rate_sand_per_cum": 1800.0,          # m3
    "rate_aggregate_per_cum": 2200.0,     # m3
    "rate_steel_per_kg": 72.0,            # kg
    "rate_concrete_per_cum": 6500.0,      # m3 ready-mix reference
    "rate_mortar_per_cum": 5200.0,        # m3
    "rate_paint_per_sqft": 22.0,
    "rate_tiles_per_sqft": 85.0,
}


# ---------- connection -----------------------------------------------------
def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------- schema ---------------------------------------------------------
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_login TEXT
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    client TEXT,
    location TEXT,
    building_type TEXT,
    floors INTEGER DEFAULT 1,
    area_sqft REAL DEFAULT 0,
    budget REAL DEFAULT 0,
    status TEXT DEFAULT 'Planning',
    start_date TEXT,
    end_date TEXT,
    progress INTEGER DEFAULT 0,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings (
    user_id INTEGER NOT NULL DEFAULT 0,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY (user_id, key)
);

CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    used_context INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS materials_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    project_id INTEGER,
    length REAL, width REAL, height REAL, floors INTEGER, quality TEXT,
    quantities_json TEXT NOT NULL,
    costs_json TEXT NOT NULL,
    total_cost REAL NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE SET NULL
);
"""

# Indexes are created after the migration step, since legacy databases only
# gain their ``user_id`` columns during that step.
INDEXES = """
CREATE INDEX IF NOT EXISTS idx_projects_user ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_materials_user ON materials_log(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_user ON chat_history(user_id, session_id);
"""


def _columns(c: sqlite3.Connection, table: str) -> set[str]:
    try:
        return {r["name"] for r in c.execute(f"PRAGMA table_info({table})")}
    except sqlite3.Error:
        return set()


def _migrate(c: sqlite3.Connection) -> None:
    """Additive, non-destructive upgrades for databases created before auth."""
    # 1. user_id columns on user-owned tables
    for table in ("projects", "materials_log", "chat_history"):
        cols = _columns(c, table)
        if cols and "user_id" not in cols:
            c.execute(f"ALTER TABLE {table} ADD COLUMN user_id INTEGER")

    # 2. settings: old schema was (key PRIMARY KEY, value). Rebuild it while
    #    preserving the existing rows as the global defaults (user_id = 0).
    scols = _columns(c, "settings")
    if scols and "user_id" not in scols:
        legacy = c.execute("SELECT key, value FROM settings").fetchall()
        c.execute("ALTER TABLE settings RENAME TO settings_legacy")
        c.execute(
            "CREATE TABLE settings ("
            " user_id INTEGER NOT NULL DEFAULT 0,"
            " key TEXT NOT NULL,"
            " value TEXT NOT NULL,"
            " PRIMARY KEY (user_id, key))"
        )
        for row in legacy:
            c.execute(
                "INSERT OR REPLACE INTO settings(user_id, key, value) VALUES(?,?,?)",
                (GLOBAL_SETTINGS_USER_ID, row["key"], row["value"]),
            )
        c.execute("DROP TABLE settings_legacy")


def init_db() -> None:
    with get_conn() as c:
        for stmt in SCHEMA.strip().split(";"):
            s = stmt.strip()
            if s:
                c.execute(s)
        _migrate(c)
        for stmt in INDEXES.strip().split(";"):
            s2 = stmt.strip()
            if s2:
                c.execute(s2)
        # seed global default settings
        existing = {
            r["key"]
            for r in c.execute(
                "SELECT key FROM settings WHERE user_id=?", (GLOBAL_SETTINGS_USER_ID,)
            )
        }
        for k, v in DEFAULT_SETTINGS.items():
            if k not in existing:
                c.execute(
                    "INSERT INTO settings(user_id, key, value) VALUES(?, ?, ?)",
                    (GLOBAL_SETTINGS_USER_ID, k, json.dumps(v)),
                )


# ---------- users ----------------------------------------------------------
USER_PUBLIC_FIELDS = ("id", "full_name", "email", "username", "created_at", "last_login")


def _public_user(row: sqlite3.Row | dict | None) -> dict | None:
    """Strip the password hash before a user record leaves this module."""
    if row is None:
        return None
    d = dict(row)
    d.pop("password_hash", None)
    return d


def email_exists(email: str) -> bool:
    with get_conn() as c:
        row = c.execute(
            "SELECT 1 FROM users WHERE LOWER(email)=LOWER(?)", (email.strip(),)
        ).fetchone()
    return row is not None


def username_exists(username: str) -> bool:
    with get_conn() as c:
        row = c.execute(
            "SELECT 1 FROM users WHERE LOWER(username)=LOWER(?)", (username.strip(),)
        ).fetchone()
    return row is not None


def create_user(full_name: str, email: str, username: str, password_hash: str) -> int:
    with get_conn() as c:
        first_user = c.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"] == 0
        cur = c.execute(
            "INSERT INTO users(full_name, email, username, password_hash) VALUES(?,?,?,?)",
            (full_name.strip(), email.strip().lower(), username.strip(), password_hash),
        )
        user_id = int(cur.lastrowid)
        if first_user:
            # Records created before authentication existed have no owner.
            # The very first account adopts them so no pre-existing data is lost.
            for table in ("projects", "materials_log", "chat_history"):
                c.execute(f"UPDATE {table} SET user_id=? WHERE user_id IS NULL", (user_id,))
        return user_id


def get_user_by_id(user_id: int) -> dict | None:
    with get_conn() as c:
        row = c.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    return _public_user(row)


def get_user_credentials(identifier: str) -> dict | None:
    """Internal use by :mod:`auth` — includes the password hash."""
    with get_conn() as c:
        row = c.execute(
            "SELECT * FROM users WHERE LOWER(email)=LOWER(?) OR LOWER(username)=LOWER(?)",
            (identifier.strip(), identifier.strip()),
        ).fetchone()
    return dict(row) if row else None


def touch_last_login(user_id: int) -> None:
    with get_conn() as c:
        c.execute(
            "UPDATE users SET last_login=? WHERE id=?",
            (datetime.utcnow().isoformat(timespec="seconds"), user_id),
        )


def update_user_profile(user_id: int, full_name: str, email: str) -> None:
    with get_conn() as c:
        c.execute(
            "UPDATE users SET full_name=?, email=? WHERE id=?",
            (full_name.strip(), email.strip().lower(), user_id),
        )


def update_user_password(user_id: int, password_hash: str) -> None:
    with get_conn() as c:
        c.execute("UPDATE users SET password_hash=? WHERE id=?", (password_hash, user_id))


def count_users() -> int:
    with get_conn() as c:
        return int(c.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"])


# ---------- settings -------------------------------------------------------
def get_settings(user_id: int | None = None) -> dict[str, Any]:
    """Defaults <- global settings <- this user's overrides."""
    out = dict(DEFAULT_SETTINGS)
    with get_conn() as c:
        rows = c.execute(
            "SELECT key, value FROM settings WHERE user_id=?", (GLOBAL_SETTINGS_USER_ID,)
        ).fetchall()
        if user_id:
            rows = list(rows) + list(
                c.execute(
                    "SELECT key, value FROM settings WHERE user_id=?", (user_id,)
                ).fetchall()
            )
    for r in rows:
        try:
            out[r["key"]] = json.loads(r["value"])
        except json.JSONDecodeError:
            out[r["key"]] = r["value"]
    return out


def update_settings(values: dict[str, Any], user_id: int | None = None) -> None:
    uid = user_id if user_id else GLOBAL_SETTINGS_USER_ID
    with get_conn() as c:
        for k, v in values.items():
            c.execute(
                "INSERT INTO settings(user_id, key, value) VALUES(?, ?, ?) "
                "ON CONFLICT(user_id, key) DO UPDATE SET value=excluded.value",
                (uid, k, json.dumps(v)),
            )


def reset_settings(user_id: int) -> None:
    """Drop a user's overrides so global defaults apply again."""
    with get_conn() as c:
        c.execute("DELETE FROM settings WHERE user_id=?", (user_id,))


# ---------- projects -------------------------------------------------------
PROJECT_FIELDS = (
    "name", "client", "location", "building_type", "floors",
    "area_sqft", "budget", "status", "start_date", "end_date",
    "progress", "notes",
)


def _row_to_dict(row: sqlite3.Row | None) -> dict | None:
    return dict(row) if row else None


def add_project(data: dict, user_id: int) -> int:
    cols = ", ".join(PROJECT_FIELDS)
    placeholders = ", ".join(["?"] * len(PROJECT_FIELDS))
    values = [data.get(k) for k in PROJECT_FIELDS] + [user_id]
    with get_conn() as c:
        cur = c.execute(
            f"INSERT INTO projects ({cols}, user_id) VALUES ({placeholders}, ?)", values
        )
        return int(cur.lastrowid)


def update_project(project_id: int, data: dict, user_id: int) -> bool:
    fields = [k for k in PROJECT_FIELDS if k in data]
    if not fields:
        return False
    assignments = ", ".join(f"{k}=?" for k in fields)
    values = [data[k] for k in fields] + [
        datetime.utcnow().isoformat(), project_id, user_id
    ]
    with get_conn() as c:
        cur = c.execute(
            f"UPDATE projects SET {assignments}, updated_at=? WHERE id=? AND user_id=?",
            values,
        )
        return cur.rowcount > 0


def delete_project(project_id: int, user_id: int) -> bool:
    with get_conn() as c:
        cur = c.execute(
            "DELETE FROM projects WHERE id=? AND user_id=?", (project_id, user_id)
        )
        return cur.rowcount > 0


def get_project(project_id: int, user_id: int) -> dict | None:
    """Ownership is enforced in SQL — a foreign id simply returns None."""
    with get_conn() as c:
        row = c.execute(
            "SELECT * FROM projects WHERE id=? AND user_id=?", (project_id, user_id)
        ).fetchone()
    return _row_to_dict(row)


def list_projects(
    user_id: int,
    search: str | None = None,
    status: str | None = None,
    building_type: str | None = None,
) -> list[dict]:
    query = "SELECT * FROM projects WHERE user_id = ?"
    params: list[Any] = [user_id]
    if search:
        query += " AND (LOWER(name) LIKE ? OR LOWER(client) LIKE ? OR LOWER(location) LIKE ?)"
        like = f"%{search.lower()}%"
        params += [like, like, like]
    if status and status != "All":
        query += " AND status = ?"
        params.append(status)
    if building_type and building_type != "All":
        query += " AND building_type = ?"
        params.append(building_type)
    query += " ORDER BY datetime(created_at) DESC"
    with get_conn() as c:
        rows = c.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def user_owns_project(project_id: int, user_id: int) -> bool:
    with get_conn() as c:
        row = c.execute(
            "SELECT 1 FROM projects WHERE id=? AND user_id=?", (project_id, user_id)
        ).fetchone()
    return row is not None


# ---------- chat -----------------------------------------------------------
def add_chat_message(
    user_id: int, session_id: str, role: str, content: str, used_context: bool = False
) -> None:
    with get_conn() as c:
        c.execute(
            "INSERT INTO chat_history(user_id, session_id, role, content, used_context) "
            "VALUES(?,?,?,?,?)",
            (user_id, session_id, role, content, 1 if used_context else 0),
        )


def get_chat_history(user_id: int, session_id: str, limit: int = 200) -> list[dict]:
    with get_conn() as c:
        rows = c.execute(
            "SELECT role, content, used_context, created_at FROM chat_history "
            "WHERE user_id=? AND session_id=? ORDER BY id ASC LIMIT ?",
            (user_id, session_id, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def clear_chat_history(user_id: int, session_id: str) -> None:
    with get_conn() as c:
        c.execute(
            "DELETE FROM chat_history WHERE user_id=? AND session_id=?",
            (user_id, session_id),
        )


# ---------- materials log --------------------------------------------------
def log_estimation(
    user_id: int,
    project_id: int | None,
    inputs: dict,
    quantities: dict,
    costs: dict,
    total_cost: float,
) -> int:
    # never attach an estimation to a project the user does not own
    if project_id is not None and not user_owns_project(project_id, user_id):
        project_id = None
    with get_conn() as c:
        cur = c.execute(
            "INSERT INTO materials_log(user_id, project_id, length, width, height, floors, "
            "quality, quantities_json, costs_json, total_cost) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (
                user_id,
                project_id,
                inputs.get("length"),
                inputs.get("width"),
                inputs.get("height"),
                inputs.get("floors"),
                inputs.get("quality"),
                json.dumps(quantities),
                json.dumps(costs),
                total_cost,
            ),
        )
        return int(cur.lastrowid)


def list_estimations(user_id: int, project_id: int | None = None) -> list[dict]:
    q = "SELECT * FROM materials_log WHERE user_id=?"
    params: list[Any] = [user_id]
    if project_id is not None:
        q += " AND project_id=?"
        params.append(project_id)
    q += " ORDER BY datetime(created_at) DESC"
    with get_conn() as c:
        rows = c.execute(q, params).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["quantities"] = json.loads(d.pop("quantities_json"))
        d["costs"] = json.loads(d.pop("costs_json"))
        out.append(d)
    return out
