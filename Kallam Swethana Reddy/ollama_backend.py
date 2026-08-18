"""Ollama (llama3.2) integration with database-aware answering.

The backend exposes two entry points:

- ``chat(messages)`` — raw chat completion against the local Ollama server.
- ``answer_with_context(user_msg)`` — classifies user intent, pulls SQLite
  context when relevant, injects it as a system message and asks the model
  to phrase a natural answer.

Intent classification is modular: a structured classifier
(``classify_intent``) inspects the message and returns an ``Intent`` object.
Keyword matching is used as a robust fallback. New intents can be added by
registering a handler in ``INTENT_HANDLERS``.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Callable

import requests

from database import get_settings, list_projects, list_estimations
from material_estimator import estimate, cost_breakdown
from utils import format_currency, get_logger

log = get_logger()

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
REQUEST_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "120"))

SYSTEM_PROMPT = (
    "You are the AI assistant for the Construction Intelligence Hub, a "
    "professional construction management platform. Answer clearly and "
    "concisely, focused on construction, civil engineering, project "
    "management, material estimation, safety, and cost planning. When "
    "database context is provided, ground your answer in it and cite exact "
    "figures. Never invent project data. If a question is unrelated to "
    "construction, politely steer the user back to the platform's scope."
)


# --------------------------------------------------------------------------- #
# Low-level Ollama client
# --------------------------------------------------------------------------- #
def ollama_available() -> tuple[bool, str]:
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        r.raise_for_status()
        models = [m.get("name", "") for m in r.json().get("models", [])]
        if not any(OLLAMA_MODEL in m for m in models):
            return False, (
                f"Ollama is running but model '{OLLAMA_MODEL}' is not installed. "
                f"Run: ollama pull {OLLAMA_MODEL}"
            )
        return True, "ok"
    except requests.RequestException as e:
        return False, f"Cannot reach Ollama at {OLLAMA_HOST}: {e}"


def chat(messages: list[dict], stream: bool = False, temperature: float = 0.3) -> str:
    """Call Ollama /api/chat and return the assistant message content."""
    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
    }
    try:
        r = requests.post(f"{OLLAMA_HOST}/api/chat", json=payload, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        return data.get("message", {}).get("content", "").strip()
    except requests.RequestException as e:
        log.error("Ollama request failed: %s", e)
        return (
            "⚠️ I could not reach the local Ollama server. "
            "Make sure `ollama serve` is running and the `llama3.2` model is pulled."
        )


# --------------------------------------------------------------------------- #
# Intent classification (modular, extendable)
# --------------------------------------------------------------------------- #
@dataclass
class Intent:
    name: str
    confidence: float = 0.0
    params: dict = field(default_factory=dict)


IntentHandler = Callable[[Intent, int], str]


KEYWORD_INTENTS: list[tuple[str, list[str]]] = [
    ("list_projects",   ["list projects", "all projects", "show projects", "my projects"]),
    ("count_projects",  ["how many projects", "number of projects", "project count"]),
    ("active_projects", ["active projects", "ongoing projects", "in progress"]),
    ("completed_projects", ["completed projects", "finished projects", "done projects"]),
    ("budget_summary",  ["total budget", "budget summary", "overall budget", "sum of budgets"]),
    ("project_details", ["details of", "info about", "tell me about project", "show project"]),
    ("estimate_materials", ["estimate for", "materials for", "how much cement", "how many bricks", "estimate materials"]),
    ("recent_estimations", ["recent estimations", "last estimation", "previous estimates"]),
    ("settings_info",   ["current rates", "material rates", "company settings"]),
]


def classify_intent(message: str) -> Intent:
    msg = message.lower().strip()

    # dimension estimate intent (e.g. "estimate 10x8x3 2 floors premium")
    dim_match = re.search(
        r"(\d+(?:\.\d+)?)\s*[x×by ]+\s*(\d+(?:\.\d+)?)\s*[x×by ]+\s*(\d+(?:\.\d+)?)",
        msg,
    )
    if dim_match and ("estimate" in msg or "material" in msg or "cost" in msg):
        floors_match = re.search(r"(\d+)\s*(?:floor|storey|story)", msg)
        quality = next(
            (q for q in ("economy", "standard", "premium", "luxury") if q in msg),
            "standard",
        )
        return Intent(
            "estimate_dimensions",
            confidence=0.95,
            params={
                "length": float(dim_match.group(1)),
                "width": float(dim_match.group(2)),
                "height": float(dim_match.group(3)),
                "floors": int(floors_match.group(1)) if floors_match else 1,
                "quality": quality.capitalize(),
            },
        )

    # named project detail
    name_match = re.search(r"(?:project|about|details of)\s+['\"]?([\w \-]{3,})['\"]?", msg)
    if name_match and any(k in msg for k in ("detail", "about", "info", "status", "budget")):
        return Intent("project_details", 0.7, {"name": name_match.group(1).strip()})

    for intent_name, keywords in KEYWORD_INTENTS:
        for kw in keywords:
            if kw in msg:
                return Intent(intent_name, 0.6)

    return Intent("general", 0.0)


# --------------------------------------------------------------------------- #
# Context builders (return a string that will be injected as system context)
# --------------------------------------------------------------------------- #
def _project_line(p: dict, currency: str) -> str:
    return (
        f"- #{p['id']} {p['name']} | client={p.get('client') or 'n/a'} | "
        f"type={p.get('building_type') or 'n/a'} | status={p.get('status')} | "
        f"floors={p.get('floors')} | area={p.get('area_sqft')} sqft | "
        f"budget={format_currency(p.get('budget'), currency)} | "
        f"progress={p.get('progress')}%"
    )


def _ctx_list_projects(_: Intent, user_id: int) -> str:
    s = get_settings(user_id)
    projects = list_projects(user_id)
    if not projects:
        return "DATABASE CONTEXT: There are currently no projects in the system."
    lines = [_project_line(p, s["currency"]) for p in projects[:50]]
    return "DATABASE CONTEXT — projects:\n" + "\n".join(lines)


def _ctx_count_projects(_: Intent, user_id: int) -> str:
    projects = list_projects(user_id)
    return f"DATABASE CONTEXT: total projects = {len(projects)}."


def _ctx_active_projects(_: Intent, user_id: int) -> str:
    s = get_settings(user_id)
    projects = [p for p in list_projects(user_id) if (p.get("status") or "").lower() == "active"]
    if not projects:
        return "DATABASE CONTEXT: no active projects."
    return "DATABASE CONTEXT — active projects:\n" + "\n".join(
        _project_line(p, s["currency"]) for p in projects
    )


def _ctx_completed_projects(_: Intent, user_id: int) -> str:
    s = get_settings(user_id)
    projects = [p for p in list_projects(user_id) if (p.get("status") or "").lower() == "completed"]
    if not projects:
        return "DATABASE CONTEXT: no completed projects."
    return "DATABASE CONTEXT — completed projects:\n" + "\n".join(
        _project_line(p, s["currency"]) for p in projects
    )


def _ctx_budget_summary(_: Intent, user_id: int) -> str:
    s = get_settings(user_id)
    projects = list_projects(user_id)
    total = sum(float(p.get("budget") or 0) for p in projects)
    by_status: dict[str, float] = {}
    for p in projects:
        by_status[p.get("status") or "Unknown"] = by_status.get(p.get("status") or "Unknown", 0) + float(p.get("budget") or 0)
    lines = [f"- {k}: {format_currency(v, s['currency'])}" for k, v in by_status.items()]
    return (
        f"DATABASE CONTEXT: total budget across {len(projects)} projects = "
        f"{format_currency(total, s['currency'])}.\nBreakdown by status:\n" + "\n".join(lines)
    )


def _ctx_project_details(intent: Intent, user_id: int) -> str:
    s = get_settings(user_id)
    name = (intent.params.get("name") or "").lower()
    projects = list_projects(user_id)
    match = None
    for p in projects:
        if name and name in (p.get("name") or "").lower():
            match = p
            break
    if not match:
        return "DATABASE CONTEXT: no project matched that name. Available projects: " + ", ".join(
            p["name"] for p in projects[:20]
        )
    return "DATABASE CONTEXT — project detail:\n" + _project_line(match, s["currency"]) + (
        f"\nnotes: {match.get('notes') or 'none'}\n"
        f"start: {match.get('start_date') or 'n/a'} | end: {match.get('end_date') or 'n/a'}"
    )


def _ctx_estimate_dimensions(intent: Intent, user_id: int) -> str:
    s = get_settings(user_id)
    p = intent.params
    q = estimate(p["length"], p["width"], p["height"], p["floors"], p["quality"])
    c = cost_breakdown(q, s)
    lines = [
        f"- {v['label']}: {v['quantity']:.2f} @ {format_currency(v['rate'], s['currency'])} "
        f"= {format_currency(v['cost'], s['currency'])}"
        for v in c["lines"].values()
    ]
    return (
        f"DATABASE CONTEXT — computed material estimate for "
        f"{p['length']}×{p['width']}×{p['height']} m, {p['floors']} floor(s), "
        f"{p['quality']} quality:\n"
        + "\n".join(lines)
        + f"\nSubtotal: {format_currency(c['subtotal'], s['currency'])}"
        + f" | Tax ({c['tax_percent']}%): {format_currency(c['tax_amount'], s['currency'])}"
        + f" | TOTAL: {format_currency(c['total'], s['currency'])}"
    )


def _ctx_recent_estimations(_: Intent, user_id: int) -> str:
    s = get_settings(user_id)
    rows = list_estimations(user_id)[:10]
    if not rows:
        return "DATABASE CONTEXT: no estimations logged yet."
    lines = [
        f"- {r['created_at']}: {r.get('length')}×{r.get('width')}×{r.get('height')} m, "
        f"{r.get('floors')} floors, {r.get('quality')} → "
        f"{format_currency(r.get('total_cost'), s['currency'])}"
        for r in rows
    ]
    return "DATABASE CONTEXT — recent estimations:\n" + "\n".join(lines)


def _ctx_settings_info(_: Intent, user_id: int) -> str:
    s = get_settings(user_id)
    keys = [
        "company_name", "currency", "tax_percent", "labor_cost_per_sqft",
        "rate_bricks_per_unit", "rate_cement_per_bag", "rate_sand_per_cum",
        "rate_aggregate_per_cum", "rate_steel_per_kg", "rate_concrete_per_cum",
    ]
    return "DATABASE CONTEXT — current settings:\n" + "\n".join(
        f"- {k}: {s.get(k)}" for k in keys
    )


INTENT_HANDLERS: dict[str, IntentHandler] = {
    "list_projects": _ctx_list_projects,
    "count_projects": _ctx_count_projects,
    "active_projects": _ctx_active_projects,
    "completed_projects": _ctx_completed_projects,
    "budget_summary": _ctx_budget_summary,
    "project_details": _ctx_project_details,
    "estimate_dimensions": _ctx_estimate_dimensions,
    "estimate_materials": _ctx_recent_estimations,
    "recent_estimations": _ctx_recent_estimations,
    "settings_info": _ctx_settings_info,
}


def build_context(intent: Intent, user_id: int) -> str | None:
    handler = INTENT_HANDLERS.get(intent.name)
    if not handler:
        return None
    try:
        return handler(intent, user_id)
    except Exception as e:  # pragma: no cover
        log.exception("Context handler failed: %s", e)
        return None


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #
def answer_with_context(user_msg: str, user_id: int, history: list[dict] | None = None) -> tuple[str, bool, Intent]:
    """Return (answer, used_context, intent).

    All database context is scoped to ``user_id`` so the model can never see
    another user's projects, estimations or settings.
    """
    intent = classify_intent(user_msg)
    context = build_context(intent, user_id)
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    if context:
        messages.append({"role": "system", "content": context})
    if history:
        # only keep the last 8 turns to control context length
        messages.extend(history[-8:])
    messages.append({"role": "user", "content": user_msg})
    answer = chat(messages)
    return answer, bool(context), intent
