"""Analytics service — computes charts and insights from project data."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from models.domain import Project


def phase_progress(project: Project) -> dict[str, dict[str, float]]:
    """Return {phase: {progress, task_count}}."""
    phases: dict[str, list[float]] = {}
    for t in project.tasks:
        phases.setdefault(t.phase, []).append(t.progress)
    return {
        phase: {
            "progress": sum(v) / len(v) if v else 0,
            "task_count": len(v),
        }
        for phase, v in phases.items()
    }


def budget_breakdown(project: Project) -> dict[str, float]:
    """Material cost by category + labor estimate."""
    cats: dict[str, float] = {}
    for m in project.materials:
        cats[m.category] = cats.get(m.category, 0) + m.total_cost
    labor = sum(w.hourly_rate * w.hours_today * w.headcount for w in project.workforce)
    if labor:
        cats["Labor (today)"] = labor
    cats["Other / Overhead"] = max(0, project.spent - sum(cats.values()))
    return cats


def spend_trend(project: Project, days: int = 30) -> list[dict[str, Any]]:
    """Synthesize a cumulative spend trend over the project timeline."""
    if not project.start_date:
        return []
    try:
        start = date.fromisoformat(project.start_date)
    except ValueError:
        return []
    total_days = max(1, (date.today() - start).days)
    daily_rate = project.spent / total_days if total_days else 0
    trend = []
    cumulative = 0.0
    for i in range(min(days, total_days)):
        d = start + timedelta(days=i)
        # add slight variance
        cumulative += daily_rate * (0.85 + ((i * 7) % 10) / 20)
        trend.append({"date": d.isoformat(), "spend": round(cumulative, 2)})
    return trend


def progress_trend(project: Project, weeks: int = 12) -> list[dict[str, Any]]:
    """Synthesize weekly progress trend up to current progress."""
    trend = []
    for i in range(weeks):
        frac = (i + 1) / weeks
        trend.append({
            "week": f"W{i+1}",
            "progress": round(min(project.progress, project.progress * frac + (i % 3)), 1),
        })
    return trend


def workforce_distribution(project: Project) -> dict[str, int]:
    dist: dict[str, int] = {}
    for w in project.workforce:
        dist[w.trade or w.role] = dist.get(w.trade or w.role, 0) + w.headcount
    return dist


def material_utilization(project: Project) -> list[dict[str, Any]]:
    return [
        {"name": m.name, "utilization": round(m.utilization, 1), "remaining": round(m.quantity - m.used, 1)}
        for m in project.materials
    ]


def safety_summary(project: Project) -> dict[str, Any]:
    incidents = project.safety_incidents
    return {
        "total": len(incidents),
        "open": sum(1 for s in incidents if s.status == "Open"),
        "resolved": sum(1 for s in incidents if s.status == "Resolved"),
        "by_severity": {
            s: sum(1 for i in incidents if i.severity == s) for s in ("Low", "Medium", "High")
        },
        "checklist_completion": (
            sum(1 for c in project.safety_checklist if c.completed) / len(project.safety_checklist) * 100
            if project.safety_checklist else 0
        ),
    }


def portfolio_kpis(projects: list[Project]) -> dict[str, Any]:
    total = len(projects)
    active = sum(1 for p in projects if p.status == "Active")
    delayed = sum(1 for p in projects if p.is_delayed)
    total_budget = sum(p.budget for p in projects)
    total_spent = sum(p.spent for p in projects)
    budget_util = (total_spent / total_budget * 100) if total_budget else 0
    avg_progress = sum(p.progress for p in projects) / total if total else 0
    avg_health = sum(p.health_score for p in projects) / total if total else 0
    return {
        "total_projects": total,
        "active_projects": active,
        "delayed_projects": delayed,
        "budget_utilization": round(budget_util, 1),
        "overall_progress": round(avg_progress, 1),
        "ai_health_score": round(avg_health, 1),
    }


def attention_projects(projects: list[Project]) -> list[Project]:
    """Projects requiring immediate attention."""
    def severity(p: Project) -> int:
        score = 0
        if p.is_delayed:
            score += 3
        if p.health_score < 60:
            score += 2
        if p.budget_utilization > 90:
            score += 1
        if any(s.status == "Open" for s in p.safety_incidents):
            score += 1
        if any(e.status == "Down" for e in p.equipment):
            score += 1
        return score
    return sorted(projects, key=severity, reverse=True)[:5]


def generate_insights(project: Project) -> list[str]:
    """AI-style insights without needing the LLM."""
    insights = []
    if project.is_delayed:
        insights.append(f"Project is delayed by {abs(project.days_to_deadline or 0)} days. Re-baseline critical path immediately.")
    if project.budget_utilization > 90:
        insights.append(f"Budget at {project.budget_utilization:.0f}% — risk of overrun. Review change orders.")
    open_safety = sum(1 for s in project.safety_incidents if s.status == "Open")
    if open_safety:
        insights.append(f"{open_safety} open safety incident(s). Schedule resolution before next shift.")
    down_eq = [e for e in project.equipment if e.status == "Down"]
    if down_eq:
        insights.append(f"{len(down_eq)} equipment unit(s) down — arrange emergency service.")
    low_mat = [m for m in project.materials if m.utilization > 80 and m.status != "Delivered"]
    if low_mat:
        names = ", ".join(m.name for m in low_mat)
        insights.append(f"Reorder soon: {names}.")
    if project.weather.work_impact == "Unfavorable":
        insights.append(f"Weather unfavorable ({project.weather.condition}) — adjust outdoor work plan.")
    if not insights:
        insights.append("All metrics within healthy range. Maintain current pace.")
    return insights
