# PROJECT_CONTEXT.md
# Construction Intelligent Hub (CIH)

> **Living document** — updated continuously as the project evolves.
> Last updated: 2026-08-15

---

## 1. Project Overview

**Construction Intelligent Hub (CIH)** is a fully offline, browser-based intelligent management dashboard for the Indian construction industry. It provides real-time project monitoring, budget tracking, equipment management, materials management, team management, risk analysis, AI-powered reporting, and local LLM-driven insights — all without any cloud dependency.

- **Type:** Static Multi-Page Application (MPA)
- **Stack:** Vanilla HTML5 + CSS3 + JavaScript (ES6+), no frameworks, no build tools
- **AI Backend:** Ollama (local LLM server) — Primary model: **Llama 3.2**
- **Data Layer:** In-memory JS objects (`js/data.js`) + mirrored JSON/CSV files in `data/`

---

## 2. Development Servers & Ports

| Server | Port | URL | Purpose |
|---|---|---|---|
| Python HTTP Server | **8000** | `http://127.0.0.1:8000` | Serves the static frontend (run via `python -m http.server 8000`) |
| VS Code Live Server | `5500` | `http://127.0.0.1:5500` | VS Code extension server (not the project's own server) |
| Ollama AI Daemon | **11434** | `http://localhost:11434` | Local LLM inference API (configured in `ai/config.js`) |

> **How to start:**
> ```bash
> cd d:\Construction_Intelligent_Hub
> python -m http.server 8000
> ```
> Then open `http://127.0.0.1:8000` in your browser.

---

## 3. Project File Structure

```
Construction_Intelligent_Hub/
│
├── index.html                  # Landing / Marketing page (entry point)
├── dashboard.html              # Main app dashboard (post-login)
├── project-management.html     # Project CRUD & Kanban tracker
├── budget.html                 # Budget & financial tracking
├── materials.html              # Materials inventory management
├── team-management.html        # Team & HR management
├── reports.html                # Report generation & export
├── ai-insights.html            # AI-powered insights page
├── risk-analysis.html          # Neural risk assessment (Llama 3.2)
├── profile.html                # User profile page
│
├── styles/
│   └── style.css               # Single global stylesheet (40 KB, all pages)
│
├── js/
│   ├── main.js                 # Main application logic (120 KB — largest file)
│   └── data.js                 # In-memory mock data store (34 KB)
│
├── ai/
│   ├── config.js               # Ollama AI configuration (model, endpoint, timeouts)
│   ├── ai_service.js           # High-level AI service facade (business logic)
│   ├── ollama_client.js        # Low-level Ollama HTTP client (22 KB)
│   ├── prompt_manager.js       # Prompt templates & context builders (16 KB)
│   └── utils.js                # AI utility helpers
│
├── data/
│   ├── json/                   # JSON snapshots of mock data
│   │   ├── projects.json
│   │   ├── equipment.json
│   │   ├── expenses.json
│   │   ├── materials.json
│   │   ├── reports.json
│   │   ├── risk_incidents.json
│   │   └── team.json
│   └── csv/                    # CSV exports of the same data
│       ├── projects.csv
│       ├── equipment.csv
│       ├── expenses.csv
│       ├── materials.csv
│       ├── reports.csv
│       ├── risk_incidents.csv
│       └── team.csv
│
├── assets/
│   ├── hero_ai.png             # Hero section AI graphic
│   ├── skyscraper.png          # Construction/landing page image
│   └── equipment.png           # Equipment section image
│
├── requirements.txt            # Python/Flask optional backend deps
├── .gitignore                  # Excludes: node_modules, .env, repopack-output.txt, TECH_STACK_DOCUMENTATION.md
└── PROJECT_CONTEXT.md          # This file
```

---

## 4. AI Layer Architecture

The AI layer is fully local and offline-first, powered by **Ollama**.

```
ai/config.js          →  Single source of truth for model & endpoint config
ai/ollama_client.js   →  Raw HTTP calls to Ollama REST API (http://localhost:11434)
ai/prompt_manager.js  →  Builds prompts with project context injected
ai/ai_service.js      →  High-level methods consumed by HTML pages & main.js
```

### AI Config (`ai/config.js`)

| Setting | Value |
|---|---|
| Endpoint | `http://localhost:11434` |
| Default Model | `llama3.2` |
| Fallback Models | `mistral`, `deepseek-r1`, `codellama` |
| Temperature | `0.4` |
| Top-P | `0.9` |
| Max Tokens (`num_predict`) | `450` |
| Request Timeout | `90,000 ms` (90 seconds) |
| Health Check Timeout | `1,500 ms` |
| Streaming | `false` |
| Offline Fallback | Enabled |

### Key AI Features

- **Risk Analysis** (`risk-analysis.html`) — Neural risk report powered by Llama 3.2
- **Executive Report Generator** (`reports.html`) — AI-generated daily/weekly/monthly reports
- **AI Insights** (`ai-insights.html`) — General construction intelligence powered by local LLM
- **Document Upload** — PDF/TXT/CSV/JSON/MD files (up to 15 MB) processed via `ai_service.js`

---

## 5. Data Layer

All data is **mock/simulated** — no real backend database. Data flows:

```
js/data.js  (primary in-memory store, loaded by main.js)
    mirrors
data/json/  (JSON snapshots — read/reference only)
data/csv/   (CSV exports — read/reference only)
```

### Data Entities

| Entity | File | Description |
|---|---|---|
| Projects | `data/json/projects.json` | Construction projects (id, name, budget, status, dates) |
| Equipment | `data/json/equipment.json` | Heavy machinery with health %, hours, fuel rate |
| Expenses | `data/json/expenses.json` | Budget expense line items |
| Materials | `data/json/materials.json` | Material inventory (stock, units, costs) |
| Reports | `data/json/reports.json` | Generated report records |
| Risk Incidents | `data/json/risk_incidents.json` | Risk events with severity & status |
| Team | `data/json/team.json` | Team members with roles & assignments |

---

## 6. Styling System

- **Single CSS file:** `styles/style.css` (~40 KB) handles all pages
- **Design language:** Dark mode, glassmorphism, gradient accents
- **Color scheme:** Slate-based dark UI with vibrant accent colors
- **Typography:** Modern sans-serif (system fonts / Google Fonts)
- **No CSS frameworks** (no Tailwind, no Bootstrap)

---

## 7. Pages & Navigation

| Page | File | Description |
|---|---|---|
| Landing | `index.html` | Marketing/home page with hero, solutions, pricing |
| Dashboard | `dashboard.html` | Post-login main KPI overview |
| Projects | `project-management.html` | Project list, Kanban, CRUD modals |
| Budget | `budget.html` | Financial tracking & charts |
| Materials | `materials.html` | Inventory management |
| Team | `team-management.html` | HR & team assignment |
| Reports | `reports.html` | Report generation + AI Executive Report |
| AI Insights | `ai-insights.html` | Local LLM-powered insights |
| Risk Analysis | `risk-analysis.html` | Neural risk assessment |
| Profile | `profile.html` | User profile & settings |

---

## 8. Key Conventions & Rules

1. **No build step** — Everything runs directly in the browser; no npm, no webpack, no transpilation.
2. **No cloud APIs** — All AI inference is local via Ollama. No OpenAI/Gemini keys needed.
3. **Offline-first** — App functions fully without internet. Ollama fallback mode activates if the daemon is offline.
4. **Single stylesheet** — All CSS lives in `styles/style.css`. No per-page CSS files.
5. **main.js is the hub** — All page-level JS logic and DOM manipulation goes through `js/main.js`.
6. **Data mutations are in-memory** — No persistence between sessions (no localStorage, no IndexedDB currently).
7. **`.gitignore` exclusions** — `repopack-output.txt` and `TECH_STACK_DOCUMENTATION.md` are excluded from git and should NOT be referenced for project context — use this file instead.

---

## 9. Dependencies

| Dependency | Type | Purpose |
|---|---|---|
| Ollama | External local service | LLM inference (Llama 3.2, Mistral, etc.) |
| PDF.js (CDN) | Optional runtime | PDF text extraction in AI document upload |
| Flask >= 3.0.0 | Optional Python | Backend integration (not currently active) |
| requests >= 2.31.0 | Optional Python | HTTP client for backend |
| ollama >= 0.1.0 | Optional Python | Python Ollama SDK |
| Python `http.server` | Dev server | Zero-dep static file server on port 8000 |

---

## 10. Change Log

| Date | Change | Notes |
|---|---|---|
| 2026-08-15 | Project structure explored & `PROJECT_CONTEXT.md` created | Initial context capture |
| 2026-08-15 | AI Material Estimation — conversational wizard implemented | Replaced static form modal in `materials.html` with a 6-question wizard UI; added `submitMaterialWizard()`, `selectWizardOption()`, `changeFloors()`, `deriveWizardParams()` in `main.js`; added wizard CSS in `style.css`; user can estimate for any project worldwide (not restricted to app projects); Llama 3.2 via Ollama enforced |

---

> **Note to AI assistants:** Always update the **Change Log** section (Section 10) when making significant changes to this project. Do not reference `repopack-output.txt` or `TECH_STACK_DOCUMENTATION.md` for project context — use this file instead.
