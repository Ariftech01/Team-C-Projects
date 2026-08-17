#Application configuration and constants.

#postpones evaluation of type hints.
from __future__ import annotations 

import os #interact with the os
from dataclasses import dataclass #, field
from pathlib import Path

APP_NAME = "Construction Intelligence Hub"
APP_TAGLINE = "AI-Powered Construction Project Management"
APP_VERSION = "1.0.0"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "db.json" #stores data in a JSON file

# AI / Ollama settings
#Use environment variable if available otherwise use localhost
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
AI_TIMEOUT_SECONDS = 30
AI_FALLBACK_ENABLED = True

# Theme tokens — enterprise neutral/blue palette (no purple)
#creates boilerplate methods automatically
@dataclass(frozen=True)
class Theme:
    primary: str = "#1B3A5B"
    primary_light: str = "#2E5A87"
    accent: str = "#0E7C7B"
    success: str = "#2E7D32"
    warning: str = "#ED6C02"
    error: str = "#C62828"
    bg: str = "#F4F6F9"
    surface: str = "#FFFFFF"
    text: str = "#1A1D23"
    text_muted: str = "#6B7280"
    border: str = "#E2E8F0"
    sidebar_bg: str = "#101923"
    sidebar_text: str = "#CBD5E1"

THEME = Theme()

# dropdown for filtering projects
PROJECT_STATUSES = ("Planning", "Active", "On Hold", "Completed", "Delayed", "Archived")
PROJECT_TYPES = (
    "Residential",
    "Commercial",
    "Infrastructure",
    "Industrial",
    "Renovation",
    "Mixed-Use",
)
PRIORITY_LEVELS = ("Low", "Medium", "High", "Critical")

KPI_TILES = (
    "total_projects",
    "active_projects",
    "delayed_projects",
    "budget_utilization",
    "overall_progress",
    "ai_health_score",
)
