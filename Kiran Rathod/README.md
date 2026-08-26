# Construction Intelligent Hub

A simple browser app for construction project management with **local AI** (Ollama + Llama 3.2).

Built with HTML, CSS, and JavaScript. No React, no npm build. Data is saved in the browser (`localStorage`).

## What you can do

- Manage **projects**, **team**, **budget**, **materials**, **risk**, and **reports**
- Use an **AI material estimator** (quantity and cost)
- Chat with a **construction AI assistant** (Ollama)
- Upload documents (PDF, TXT, CSV, JSON, MD) for AI analysis
- View a dashboard with live project KPIs


## Requirements

- Python 3 (to run a local web server)
- A modern browser
- [Ollama](https://ollama.com) with `llama3.2` (for AI features)

## How to run

1. Open a terminal in the project folder.
2. Start the server:

```bash
python -m http.server 8000
```

3. Open in your browser:

**http://localhost:8000/** or **http://127.0.0.1:8000**

4. Click **Log In** on the home page to open the dashboard.  

## Ollama (for AI)

```bash
ollama pull llama3.2
ollama serve
```

AI settings are in `ai/config.js` (default: `http://localhost:11434`, model `llama3.2`).

- **Without Ollama:** pages and data still work; AI features will fail or use a basic fallback.
- **Document analysis and forecast** need Ollama running.

## Project structure

```
.
├── index.html                 Home / landing
├── dashboard.html             Main dashboard
├── project-management.html
├── team-management.html
├── budget.html
├── materials.html
├── risk-analysis.html
├── reports.html
├── ai-insights.html
├── profile.html
├── styles/style.css           All page styles
├── js/
│   ├── data.js                App data
│   └── main.js                Page logic
├── ai/                        Ollama / AI code
├── data/                      Sample JSON & CSV (reference only)
└── assets/                    Images
```

## How data works

- Live data is stored in the **browser** (`localStorage`).
- Everything links to a **project** (budget, materials, risks, team, etc.).
- Files in `data/json` and `data/csv` are sample copies — not the live database.
- Clear site data in the browser to reset to the default sample projects.

   