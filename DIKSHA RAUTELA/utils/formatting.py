"""Formatting and helper utilities for Indian Construction Intelligence Hub."""
from __future__ import annotations

from datetime import datetime, date


def fmt_currency(v: float) -> str:
    """Format currency in Indian Rupees (₹ Cr / ₹ L / ₹ formatted)."""
    if v is None:
        return "₹0"
    abs_v = abs(v)
    sign = "-" if v < 0 else ""
    if abs_v >= 10_000_000:
        cr_val = abs_v / 10_000_000
        return f"{sign}₹{cr_val:,.2f} Cr"
    if abs_v >= 100_000:
        l_val = abs_v / 100_000
        return f"{sign}₹{l_val:,.2f} L"
    return f"{sign}₹{v:,.0f}"


def fmt_currency2(v: float) -> str:
    """Format currency with two decimal places in INR."""
    return fmt_currency(v)


def fmt_pct(v: float) -> str:
    return f"{v:.1f}%"


def fmt_date(d: str) -> str:
    if not d:
        return "—"
    try:
        return date.fromisoformat(d).strftime("%b %d, %Y")
    except ValueError:
        return d


def fmt_datetime(d: str) -> str:
    if not d:
        return "—"
    try:
        return datetime.fromisoformat(d).strftime("%b %d, %H:%M")
    except ValueError:
        return d


def time_ago(d: str) -> str:
    if not d:
        return "—"
    try:
        dt = datetime.fromisoformat(d)
    except ValueError:
        return d
    delta = datetime.now() - dt
    secs = delta.total_seconds()
    if secs < 60:
        return "just now"
    if secs < 3600:
        return f"{int(secs // 60)}m ago"
    if secs < 86400:
        return f"{int(secs // 3600)}h ago"
    return f"{int(secs // 86400)}d ago"


def status_color(status: str) -> str:
    return {
        "Active": "#2E7D32",
        "Planning": "#0E7C7B",
        "On Hold": "#ED6C02",
        "Completed": "#1B3A5B",
        "Delayed": "#C62828",
    }.get(status, "#6B7280")


def priority_color(p: str) -> str:
    return {
        "Low": "#6B7280",
        "Medium": "#0E7C7B",
        "High": "#ED6C02",
        "Critical": "#C62828",
    }.get(p, "#6B7280")


def health_color(score: float) -> str:
    if score >= 80:
        return "#2E7D32"
    if score >= 60:
        return "#ED6C02"
    return "#C62828"
