# 🏗️ Construction Intelligence Hub

A Streamlit web application for site managers, engineers, and contractors — combining project monitoring, material estimation, and safety analysis with a locally-hosted AI assistant. No cloud APIs, no per-call cost, and no data leaves your machine.

![Status](https://img.shields.io/badge/status-active-brightgreen) ![Python](https://img.shields.io/badge/python-3.9%2B-blue) ![Streamlit](https://img.shields.io/badge/streamlit-frontend-orange)

---

## What this is

Construction Intelligence Hub is a single-file Streamlit application built in three stages:

1. **Frontend** — a full six-page interface with mock project data, custom light-theme styling, and a floating AI chat bubble.
2. **Local AI integration** — real, locally-hosted models (via [Ollama](https://ollama.com)) power the chat assistant, document analysis, and safety scoring — genuinely reading uploaded files and photos rather than simulating it.
3. **Topic guardrails** — chat, image uploads, and document uploads are all checked for construction relevance before the assistant engages, so it won't analyze or discuss unrelated content.

Everything runs locally. No API keys, no external services, no data sent anywhere.

---

## Features

| Page | What it does |
|---|---|
| 📊 **Dashboard** | Weather, a daily site summary, live metric cards (active projects, workers, safety score, material status), AI alerts, quick-action tiles, and a project progress chart |
| 🏢 **Project Monitoring** | Per-project drill-down: progress, materials required vs. in stock, equipment status, timeline, workforce breakdown, and document upload |
| 📄 **Doc Analyzer** | Upload a plan, blueprint image, or PDF — a vision model or extracted PDF text is genuinely read and summarized |
| 🧮 **Material Estimator** | Manual project-spec form (type, area, floors, quality) → formula-based cost/material estimate plus an AI-written planning insight |
| 🦺 **Safety Analysis** | Upload a site photo — a vision model inspects it for real, and a text model scores it and writes up findings |
| 🤖 **AI Assistant** | Full chat page, plus a persistent floating chat bubble on every other page, sharing one conversation history |

All AI features gracefully fall back to clear inline messages (or simple rule-based answers for chat) if the local model isn't running — nothing crashes if Ollama is offline.

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend framework | [Streamlit](https://streamlit.io) (Python) |
| Styling | Custom CSS injected via `st.html()` — forced light theme, cards, floating chat panel |
| Data & charts | Pandas, NumPy, Plotly |
| LLM runtime | [Ollama](https://ollama.com) (local inference server) |
| Text model | `llama3.2:1b` — chat, planning insight, safety scoring, PDF analysis, topic guardrail classifier |
| Vision model | `moondream` — real image understanding for photos and plans |
| PDF text extraction | `pypdf` |
| State management | `st.session_state` |

---

## Getting started

### 1. Prerequisites

- Python 3.9+
- [Ollama](https://ollama.com) installed and runnable locally

### 2. Install Python dependencies

```bash
pip install streamlit pandas numpy plotly pillow ollama pypdf
```

### 3. Pull the local models

```bash
ollama pull llama3.2:1b
ollama pull moondream
```

> **Hardware note:** both models were chosen to run on modest hardware (tested on an i3 / 8GB RAM machine). `moondream` (~1.7GB) is intentionally the lightest available Ollama vision model — if you have more RAM/GPU available, you can swap in a larger vision model (e.g. `llava:7b`) by changing the `VISION_MODEL` constant near the top of `app.py`.

### 4. Start Ollama

```bash
ollama serve
```

(Skip this if you installed Ollama as a desktop app — it's usually already running in the background. Check with `ollama list`.)

### 5. Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`. A sidebar status badge shows whether the text model and vision model are reachable — if either is 🔴, double-check `ollama serve` is running and the models are pulled.

---

## How the AI is grounded

Rather than a general-purpose chatbot, every AI call in the app is scoped to construction:

- **Chat** is grounded with a live text summary of the app's mock project data (materials, alerts, weather) via a shared system prompt, so answers reference actual numbers rather than generic advice.
- **Topic guardrails** run before any AI response: a fast keyword check plus an LLM classifier for chat (with recent conversation context, so follow-ups like "give me a report" aren't wrongly rejected); a description-then-classify pipeline for uploaded images and PDFs, with a curated phrase fast-path (e.g. "floor plan", "hard hat") so common, clear-cut uploads don't depend on a single model call being right.
- **Transparency** — every guardrail decision is logged and viewable in a "Guardrail activity log" expander on the AI Assistant page, so a blocked or allowed decision is never a black box.
- **Graceful degradation** — if a model is unreachable, the app shows a clear inline notice (or falls back to simple rule-based chat answers) instead of crashing.

---

## Project structure

This is intentionally a **single-file application** — no config files, no separate requirements file, no package structure:

```
app.py   # everything: CSS, mock data, AI helpers, guardrails, all 6 pages, routing
```

Rationale: at this project's current scale, one clearly-sectioned file (CSS → mock data → AI/guardrail helpers → page functions → router) is easier to run, share, and reason about than a multi-module package. See the CSS block, `MOCK DATA` section, and `PAGES` dict at the bottom for the three main landmarks when navigating the file.

---

## Known limitations

- **Mock data**: project, material, and safety data are hand-authored sample values, not a live backend or database.
- **Input-side guardrails only**: chat, images, and documents are checked before the model responds, but the model's *output* isn't independently re-checked — a cleverly-phrased on-topic-looking prompt could still coax an off-topic answer.
- **Small local models**: `llama3.2:1b` and `moondream` are fast on CPU but can occasionally misjudge ambiguous edge cases; the guardrail activity log is there specifically so those cases are visible and diagnosable rather than silent.
- **Desktop/tablet-first layout**: the UI isn't yet optimized for small mobile screens.

---

## Roadmap

- Real retrieval-augmented generation (RAG) over actual project documents, replacing the in-memory mock data
- A real backend/database instead of hand-authored sample data
- Output-side guardrails / a dedicated safety-classifier model
- Authentication and role-based views (site engineer / project manager / contractor)
- Containerized deployment
- Mobile-optimized layout

---

## License

Add your license of choice here (e.g. MIT).
