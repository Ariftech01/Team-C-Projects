"""Shared utility helpers for Construction Intelligence Hub."""
from __future__ import annotations

import logging
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

import streamlit as st

APP_ROOT = Path(__file__).resolve().parent
ASSETS_DIR = APP_ROOT / "assets"

# ---------- logging ---------------------------------------------------------
_logger: logging.Logger | None = None


def get_logger() -> logging.Logger:
    global _logger
    if _logger is None:
        logging.basicConfig(
            level=os.environ.get("CIH_LOG_LEVEL", "INFO"),
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        _logger = logging.getLogger("cih")
    return _logger


# ---------- css / branding --------------------------------------------------
def inject_css() -> None:
    css_path = ASSETS_DIR / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def render_sidebar_brand(company_name: str = "Construction Intelligence Hub") -> None:
    st.sidebar.markdown(
        f"""
        <div class="cih-brand">
          <div class="cih-brand-logo">CI</div>
          <div>
            <div class="cih-brand-title">{company_name}</div>
            <div class="cih-brand-sub">AI Construction Platform</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = "", icon: str = "🏗️") -> None:
    st.markdown(
        f"""
        <div class="cih-page-header">
          <div>
            <div class="cih-page-title">{icon}&nbsp; {title}</div>
            <div class="cih-page-sub">{subtitle}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------- formatting -----------------------------------------------------
def format_currency(value: float | int | None, currency: str = "INR") -> str:
    if value is None:
        return "-"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value)
    symbols = {"INR": "₹", "USD": "$", "EUR": "€", "GBP": "£", "AED": "د.إ"}
    sym = symbols.get(currency.upper(), currency + " ")
    if abs(v) >= 1_00_00_000:
        return f"{sym}{v/1_00_00_000:,.2f} Cr"
    if abs(v) >= 1_00_000:
        return f"{sym}{v/1_00_000:,.2f} L"
    return f"{sym}{v:,.2f}"


def format_number(value: float | int | None, decimals: int = 2) -> str:
    if value is None:
        return "-"
    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value in (None, "", "None"):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value in (None, "", "None"):
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def parse_date(value: Any) -> date | None:
    if not value:
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(str(value), fmt).date()
        except ValueError:
            continue
    return None


# ---------- KPI helpers ----------------------------------------------------
def compute_kpis(projects: Iterable[dict]) -> dict:
    projects = list(projects)
    total = len(projects)
    active = sum(1 for p in projects if (p.get("status") or "").lower() == "active")
    completed = sum(1 for p in projects if (p.get("status") or "").lower() == "completed")
    planning = sum(1 for p in projects if (p.get("status") or "").lower() == "planning")
    on_hold = sum(1 for p in projects if (p.get("status") or "").lower() == "on hold")
    total_budget = sum(safe_float(p.get("budget")) for p in projects)
    total_area = sum(safe_float(p.get("area_sqft")) for p in projects)
    return {
        "total": total,
        "active": active,
        "completed": completed,
        "planning": planning,
        "on_hold": on_hold,
        "total_budget": total_budget,
        "total_area": total_area,
    }


def kpi_card(label: str, value: str, hint: str = "", variant: str = "") -> str:
    variant_cls = f" {variant}" if variant else ""
    return (
        f'<div class="cih-kpi{variant_cls}">'
        f'<div class="cih-kpi-label">{label}</div>'
        f'<div class="cih-kpi-value">{value}</div>'
        f'<div class="cih-kpi-hint">{hint}</div>'
        f"</div>"
    )


def render_kpi_grid(cards: list[str]) -> None:
    st.markdown(
        '<div class="cih-kpi-grid">' + "".join(cards) + "</div>",
        unsafe_allow_html=True,
    )


def status_pill(status: str) -> str:
    cls = (status or "planning").lower().replace(" ", "-")
    return f'<span class="cih-pill {cls}">{status}</span>'


STATUS_OPTIONS = ["Planning", "Active", "On Hold", "Completed", "Cancelled"]
BUILDING_TYPES = [
    "Residential",
    "Commercial",
    "Industrial",
    "Institutional",
    "Infrastructure",
    "Mixed-Use",
]
QUALITY_LEVELS = ["Economy", "Standard", "Premium", "Luxury"]
