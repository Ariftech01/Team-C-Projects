"""Report service - generates professional PDF reports and saves to history."""
from __future__ import annotations

import io
import os
import tempfile
from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from config.settings import APP_NAME, UPLOADS_DIR, THEME
from models.domain import Project, HistoryEntry, ActivityEvent
from repository import get_repository
from services.analytics_service import generate_insights
from services.weather_service import refresh_project_weather
from utils.formatting import fmt_currency


class ReportPDF(FPDF):
    def header(self) -> None:
        self.set_fill_color(*_hex_to_rgb(THEME.primary))
        self.rect(0, 0, self.w, 28, "F")
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 14)
        self.set_y(8)
        self.cell(0, 8, APP_NAME, ln=True, align="L")
        self.set_font("Helvetica", "", 9)
        self.set_y(16)
        self.cell(0, 6, f"Project Report - {datetime.now().strftime('%B %d, %Y at %H:%M')}", ln=True)
        self.set_text_color(*_hex_to_rgb(THEME.text))
        self.ln(6)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_text_color(*_hex_to_rgb(THEME.text_muted))
        self.set_font("Helvetica", "", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}} - {APP_NAME}", align="C")


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _section(pdf: ReportPDF, title: str) -> None:
    pdf.set_fill_color(*_hex_to_rgb(THEME.bg))
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*_hex_to_rgb(THEME.primary))
    pdf.cell(0, 8, title, ln=True, fill=True)
    pdf.set_text_color(*_hex_to_rgb(THEME.text))
    pdf.ln(2)


def _kv(pdf: ReportPDF, pairs: list[tuple[str, str]]) -> None:
    pdf.set_font("Helvetica", "", 9)
    for k, v in pairs:
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(60, 6, k, border=0)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 6, v, ln=True, border=0)
    pdf.ln(2)


def generate_report(project: Project) -> str:
    """Generate a PDF report, save to project history, log activity. Returns file path."""
    weather = refresh_project_weather(project)
    insights = generate_insights(project)

    pdf = ReportPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.alias_nb_pages()
    pdf.add_page()

    # Overview
    _section(pdf, "PROJECT OVERVIEW")
    _kv(pdf, [
        ("Project Name", project.name),
        ("Project Code", project.code),
        ("Type", project.type),
        ("Status", project.status),
        ("Priority", project.priority),
        ("Manager", project.manager),
        ("Client", project.client),
        ("Location", project.location),
        ("Start Date", project.start_date),
        ("End Date", project.end_date),
        ("Description", project.description[:120] + ("..." if len(project.description) > 120 else "")),
    ])

    # Progress
    _section(pdf, "PROGRESS & SCHEDULE")
    _kv(pdf, [
        ("Overall Progress", f"{project.progress}%"),
        ("Health Score", f"{project.health_score}/100"),
        ("Days to Deadline", str(project.days_to_deadline if project.days_to_deadline is not None else "N/A")),
        ("Delayed", "Yes" if project.is_delayed else "No"),
        ("Total Tasks", str(len(project.tasks))),
        ("Completed Tasks", str(sum(1 for t in project.tasks if t.status == "Completed"))),
        ("In Progress", str(sum(1 for t in project.tasks if t.status == "In Progress"))),
    ])
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(50, 6, "Task", border=1)
    pdf.cell(35, 6, "Phase", border=1)
    pdf.cell(30, 6, "Status", border=1)
    pdf.cell(25, 6, "Progress", border=1)
    pdf.cell(0, 6, "Assignee", border=1, ln=True)
    pdf.set_font("Helvetica", "", 8)
    for t in project.tasks:
        pdf.cell(50, 5, t.name[:30], border=1)
        pdf.cell(35, 5, t.phase[:20], border=1)
        pdf.cell(30, 5, t.status[:14], border=1)
        pdf.cell(25, 5, f"{t.progress}%", border=1)
        pdf.cell(0, 5, t.assignee[:20], border=1, ln=True)
    pdf.ln(3)

    # Budget
    _section(pdf, "BUDGET & COST")
    _kv(pdf, [
        ("Total Budget", fmt_currency(project.budget)),
        ("Spent", fmt_currency(project.spent)),
        ("Remaining", fmt_currency(project.remaining_budget)),
        ("Utilization", f"{project.budget_utilization:.1f}%"),
    ])
    mat_total = sum(m.total_cost for m in project.materials)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, f"Total material commitment: {fmt_currency(mat_total)}", ln=True)
    pdf.ln(3)

    # Materials
    _section(pdf, "MATERIALS")
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(55, 6, "Material", border=1)
    pdf.cell(25, 6, "Qty", border=1)
    pdf.cell(25, 6, "Unit Cost", border=1)
    pdf.cell(30, 6, "Used", border=1)
    pdf.cell(0, 6, "Status", border=1, ln=True)
    pdf.set_font("Helvetica", "", 8)
    for m in project.materials:
        pdf.cell(55, 5, m.name[:30], border=1)
        pdf.cell(25, 5, f"{m.quantity} {m.unit}", border=1)
        pdf.cell(25, 5, fmt_currency(m.unit_cost), border=1)
        pdf.cell(30, 5, f"{m.utilization:.0f}%", border=1)
        pdf.cell(0, 5, m.status[:18], border=1, ln=True)
    pdf.ln(3)

    # Workforce
    _section(pdf, "WORKFORCE")
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(55, 6, "Name", border=1)
    pdf.cell(35, 6, "Role", border=1)
    pdf.cell(25, 6, "Headcount", border=1)
    pdf.cell(25, 6, "Hours", border=1)
    pdf.cell(0, 6, "Status", border=1, ln=True)
    pdf.set_font("Helvetica", "", 8)
    for w in project.workforce:
        pdf.cell(55, 5, w.name[:30], border=1)
        pdf.cell(35, 5, w.role[:20], border=1)
        pdf.cell(25, 5, str(w.headcount), border=1)
        pdf.cell(25, 5, f"{w.hours_today}h", border=1)
        pdf.cell(0, 5, w.status[:14], border=1, ln=True)
    pdf.ln(3)

    # Equipment
    _section(pdf, "EQUIPMENT")
    pdf.set_font("Helvetica", "B", 8)
    pdf.cell(55, 6, "Name", border=1)
    pdf.cell(30, 6, "Type", border=1)
    pdf.cell(30, 6, "Status", border=1)
    pdf.cell(25, 6, "Hours", border=1)
    pdf.cell(0, 6, "Next Service", border=1, ln=True)
    pdf.set_font("Helvetica", "", 8)
    for e in project.equipment:
        pdf.cell(55, 5, e.name[:30], border=1)
        pdf.cell(30, 5, e.type[:18], border=1)
        pdf.cell(30, 5, e.status[:14], border=1)
        pdf.cell(25, 5, f"{e.fuel_hours}h", border=1)
        pdf.cell(0, 5, e.next_service[:12], border=1, ln=True)
    pdf.ln(3)

    # Safety
    _section(pdf, "SAFETY")
    open_inc = sum(1 for s in project.safety_incidents if s.status == "Open")
    _kv(pdf, [
        ("Total Incidents", str(len(project.safety_incidents))),
        ("Open Incidents", str(open_inc)),
        ("Checklist Items", str(len(project.safety_checklist))),
        ("Checklist Complete", f"{sum(1 for c in project.safety_checklist if c.completed)}/{len(project.safety_checklist)}" if project.safety_checklist else "0/0"),
    ])
    pdf.ln(2)

    # Weather
    _section(pdf, "WEATHER")
    _kv(pdf, [
        ("Condition", f"{weather.condition}, {weather.temp_c}C"),
        ("Wind", f"{weather.wind_kph} km/h"),
        ("Precipitation", f"{weather.precipitation_mm} mm"),
        ("Humidity", f"{weather.humidity}%"),
        ("Work Impact", weather.work_impact),
    ])
    pdf.ln(2)

    # Analytics / Insights
    _section(pdf, "AI INSIGHTS & RECOMMENDATIONS")
    pdf.set_font("Helvetica", "", 9)
    for ins in insights:
        pdf.multi_cell(0, 6, f"- {ins}")
    pdf.ln(3)

    # Save PDF
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in project.name)
    filename = f"report_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = UPLOADS_DIR / filename
    pdf.output(str(filepath))

    # Save to project history
    project.history.insert(0, HistoryEntry(
        type="report",
        title=f"Report generated - {datetime.now().strftime('%b %d, %Y %H:%M')}",
        content=f"Comprehensive project report covering progress, budget, materials, workforce, equipment, safety, weather, and AI insights.",
        author="AI Assistant",
        file_path=str(filepath),
    ))
    project.updated_at = datetime.now().isoformat(timespec="seconds")
    repo = get_repository()
    repo.save_project(project)

    # Log activity on dashboard
    repo.add_activity(ActivityEvent(
        project_id=project.id,
        project_name=project.name,
        event=f"Report generated and saved to history",
        category="report",
    ))

    return str(filepath)
