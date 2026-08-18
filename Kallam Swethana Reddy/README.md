# Construction Intelligence Hub

A production-quality AI-powered construction management platform built with
**Streamlit**, **SQLite**, and **Ollama (llama3.2)**.

## Features

- **Multi-user authentication** (sign up / login) with PBKDF2-SHA256 password hashing
- **Per-user data isolation** — projects, estimations, chat history and settings are private
- Project management (CRUD) with search & filters
- Engineering-grade material estimator (bricks, cement, sand, aggregate, steel, concrete, mortar)
- AI Assistant powered by local Ollama `llama3.2` with database-aware answers
- PDF & Excel reports (ReportLab + OpenPyXL)
- Interactive analytics dashboards (Plotly)
- Configurable settings (company info, material rates, labor cost, tax, currency)
- Custom professional light theme

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) running locally with the `llama3.2` model

## Install

```bash
cd streamlit_app
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Ollama setup

```bash
ollama pull llama3.2
ollama serve         # usually starts automatically
```

Optional environment variables:

```bash
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=llama3.2
```

## Run

```bash
streamlit run app.py
```

The SQLite database `construction.db` is created automatically on first launch
and seeded with default settings.

## Project structure

```
streamlit_app/
├── app.py
├── auth.py
├── auth_ui.py
├── database.py
├── material_estimator.py
├── ollama_backend.py
├── report_generator.py
├── utils.py
├── requirements.txt
├── assets/styles.css
└── pages/
    ├── 1_Dashboard.py
    ├── 2_Project_Management.py
    ├── 3_Material_Estimator.py
    ├── 4_AI_Assistant.py
    ├── 5_Reports.py
    ├── 6_Analytics.py
    ├── 7_Settings.py
    ├── 8_About.py
    └── 9_Profile.py
```

## Authentication

The app opens on a Login / Create Account screen. Nothing in the platform is
reachable until you are signed in — every page calls `require_login()` and stops
rendering otherwise.

### Sign up rules

- Full name, email, username, password and confirm password are all required
- Email must be a valid address and must not already exist
- Username: 3–32 characters (letters, numbers, `.`, `_`, `-`) and must be unique
- Password: at least **8 characters**, containing at least one letter and one number
- Password and confirmation must match

### How passwords are stored

Passwords are never stored in plain text. `auth.py` hashes them with
`werkzeug.security.generate_password_hash` (PBKDF2-SHA256). If Werkzeug is not
installed, an equivalent stdlib PBKDF2-SHA256 implementation with a random salt
and 260,000 iterations is used automatically. Password hashes are stripped from
every user record before it leaves `database.py`, so they are never displayed.

Install the dependency with:

```bash
pip install -r requirements.txt      # includes Werkzeug>=3.0
```

### Sessions

After a successful login, only `id`, `full_name`, `email` and `username` are kept
in `st.session_state`. Streamlit shares session state across all pages, so you stay
logged in while navigating. **Log out** in the sidebar clears the session (and any
cached chat/estimate state) and returns you to the login screen. *Remember me*
keeps your email/username prefilled for the current browser session.

## User-specific data

| Table | Ownership |
|-------|-----------|
| `users` | account records (`id`, `full_name`, `email`, `username`, `password_hash`) |
| `projects` | `user_id` column — all queries filter and enforce it |
| `materials_log` | `user_id` column; an estimation can only be attached to a project you own |
| `chat_history` | `user_id` + `session_id` — each user sees only their own conversation |
| `settings` | composite key `(user_id, key)`; `user_id = 0` holds the global defaults |

All SQL uses parameterised queries. Ownership is enforced **in SQL**, not in the UI:
`get_project`, `update_project` and `delete_project` all include `AND user_id = ?`,
so guessing another user's project id simply returns nothing.

The AI assistant receives only the signed-in user's rows as database context, and
Reports/Analytics/Dashboard are built from the same user-scoped queries.

Each user gets their own company name, currency, tax percentage, labor cost and
material rates. Values fall back to the global defaults until the user overrides
them in **Settings**; *Reset to defaults* removes only that user's overrides.

## Database migration (existing installations)

`init_db()` upgrades an existing `construction.db` in place and never drops data:

1. Creates the `users` table if missing.
2. Adds a `user_id` column to `projects`, `materials_log` and `chat_history` if absent.
3. Rebuilds `settings` from `(key, value)` to `(user_id, key, value)`, preserving the
   old rows as the global defaults (`user_id = 0`).
4. Creates the supporting indexes.

Records that existed before authentication have no owner; the **first account you
create adopts them**, so your previous projects remain accessible.
