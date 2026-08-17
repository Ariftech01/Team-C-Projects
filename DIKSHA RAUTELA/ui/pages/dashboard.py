"""Dashboard — premium enterprise control room with repository-driven KPIs."""
from __future__ import annotations

import streamlit as st

from repository import get_repository
from services import portfolio_kpis, attention_projects, ai_chat
from utils.formatting import fmt_currency, fmt_pct, time_ago
from ui.i18n import tr


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────

def render_dashboard() -> None:
    repo = get_repository()
    projects = repo.list_projects()
    activity = repo.list_activity(limit=20)

    kpis = portfolio_kpis(projects)

    # ── 1. Compact header ────────────────────────────────────────────────────
    _render_header(kpis, projects)

    # ── 2. AI Portfolio Summary (near top, button-triggered) ─────────────────
    _render_ai_summary(projects)

    # ── 3. KPI Cards ─────────────────────────────────────────────────────────
    _render_kpis(kpis, projects)

    if not projects:
        st.info(tr("No project added yet. Go to the Projects tab to add your first project."))
        if st.button(tr("Go to Projects"), type="primary", key="dashboard_go_to_projects"):
            st.session_state["page"] = "Project Portfolio"
            st.session_state["show_new_project"] = True
            st.session_state["editing_project_id"] = None
            st.rerun()
        return

    # ── 4. PM Command Center ─────────────────────────────────────────────────
    _render_pm_command_center(projects)

    # ── 5. Projects Requiring Immediate Attention ────────────────────────────
    _render_attention_section(projects)

    # ── 6. Today's Activity (compact timeline) ───────────────────────────────
    _render_activity_timeline(activity)


# ─────────────────────────────────────────────────────────────────────────────
# Header — compact, professional
# ─────────────────────────────────────────────────────────────────────────────

def _render_header(kpis: dict, projects: list) -> None:
    total_budget = sum(p.budget for p in projects)
    total_spent  = sum(p.spent  for p in projects)
    workers      = sum(w.headcount for p in projects for w in p.workforce)
    active_count = kpis["active_projects"]
    delayed      = kpis["delayed_projects"]
    health       = kpis["ai_health_score"]
    budget_pct   = kpis["budget_utilization"]

    # Chip variant per condition
    delayed_cls = "dash-chip-danger" if delayed > 0 else "dash-chip-accent"
    health_cls  = (
        "dash-chip-accent"  if health >= 80
        else "dash-chip-warn" if health >= 60
        else "dash-chip-danger"
    )
    budget_cls = (
        "dash-chip-accent"  if budget_pct < 75
        else "dash-chip-warn" if budget_pct < 90
        else "dash-chip-danger"
    )

    st.markdown(f"""
<div class="dash-header">
  <div class="dash-header-left">
    <h1 class="dash-header-title">Dashboard</h1>
    <p class="dash-header-sub">Monitor overall project health, portfolio performance, budgets, risks, and AI-driven insights across all active projects.</p>
    <!-- <div class="dash-header-chips">
      <span class="dash-chip">📁 {kpis['total_projects']} Projects</span>
      <span class="dash-chip dash-chip-accent">✅ {active_count} Active</span>
      <span class="dash-chip {delayed_cls}">⚠ {delayed} Delayed</span>
      <span class="dash-chip {health_cls}">◎ Health {health:.0f}/100</span>
      <span class="dash-chip {budget_cls}">◈ Budget {budget_pct:.1f}%</span>
      <span class="dash-chip">▲ {workers} Workers</span>
    </div> -->
  </div>
  <div class="dash-header-stats">
    <div class="dash-hstat">
      <span class="dash-hstat-val">{fmt_currency(total_budget)}</span>
      <span class="dash-hstat-lbl">Total Budget</span>
    </div>
    <div class="dash-hstat-divider"></div>
    <div class="dash-hstat">
      <span class="dash-hstat-val">{fmt_currency(total_spent)}</span>
      <span class="dash-hstat-lbl">Spent to Date</span>
    </div>
    <div class="dash-hstat-divider"></div>
    <div class="dash-hstat">
      <span class="dash-hstat-val">{fmt_pct(kpis['overall_progress'])}</span>
      <span class="dash-hstat-lbl">Avg Progress</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# AI Portfolio Summary (button-triggered, near top)
# ─────────────────────────────────────────────────────────────────────────────

def _render_ai_summary(projects: list) -> None:
    st.markdown("""
<div class="dash-section-hdr">
  <span class="dash-section-title">AI Portfolio Summary</span>
  <span class="dash-section-desc">Instant risk overview and recommendations powered by AI</span>
</div>""", unsafe_allow_html=True)

    shown = st.session_state.get("dash_ai_summary_shown", False)

    if not shown:
        col_btn, _ = st.columns([1, 3])
        with col_btn:
            if st.button("✦ Generate AI Summary", use_container_width=True, type="primary"):
                st.session_state["dash_ai_summary_shown"] = True
                st.rerun()
        return

    # Call existing ai_chat service — logic unchanged
    with st.spinner("Analysing portfolio…"):
        summary = ai_chat(
            "Give me a concise portfolio summary highlighting risks and priorities.",
            context={"page": "Dashboard", "projects": projects},
        )

    st.markdown("""
<div class="ai-panel-header">
  <span class="ai-panel-icon">🤖</span>
  <span class="ai-panel-title">AI Analysis</span>
  <span class="ai-panel-badge">AI Generated</span>
</div>""", unsafe_allow_html=True)

    with st.container(border=True):
        st.write(summary)

    col_r, _ = st.columns([1, 4])
    with col_r:
        if st.button("↩ Dismiss", use_container_width=True):
            st.session_state["dash_ai_summary_shown"] = False
            st.rerun()

    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# KPI Cards — rendered via st.columns + HTML, no global CSS override issue
# ─────────────────────────────────────────────────────────────────────────────

def _kpi_card(
    icon: str, label: str, value: str, sub: str,
    badge_text: str, badge_color: str,
    progress_pct: float | None = None,
) -> None:
    """Render a single KPI card using a mix of HTML + native Streamlit."""
    # Map logical color name → CSS inline values
    _BADGE = {
        "green":  ("rgba(46,125,50,0.12)",  "#2E7D32", "rgba(46,125,50,0.28)"),
        "orange": ("rgba(230,81,0,0.12)",   "#E65100", "rgba(230,81,0,0.28)"),
        "red":    ("rgba(198,40,40,0.12)",  "#C62828", "rgba(198,40,40,0.28)"),
        "blue":   ("rgba(14,124,123,0.12)", "#0E7C7B", "rgba(14,124,123,0.28)"),
        "grey":   ("rgba(100,116,139,0.10)","#64748B", "rgba(100,116,139,0.22)"),
    }
    bg, fg, border = _BADGE.get(badge_color, _BADGE["grey"])

    # Build progress bar HTML if needed
    prog_html = ""
    if progress_pct is not None:
        w = max(0, min(100, progress_pct))
        prog_html = f"""
<div style="background:rgba(100,116,139,0.15);border-radius:3px;height:4px;margin-top:0.65rem;overflow:hidden;">
  <div style="width:{w}%;height:100%;border-radius:3px;background:linear-gradient(90deg,#1B3A5B,#0E7C7B);"></div>
</div>"""

    card_html = f"""
<div class="kpi-card">
  <div class="kpi-card-top">
    <span class="kpi-card-icon">{icon}</span>
    <span class="kpi-badge" style="background:{bg};color:{fg};border:1px solid {border};">{badge_text}</span>
  </div>
  <p class="kpi-card-value">{value}</p>
  <p class="kpi-card-label">{label}</p>
  <p class="kpi-card-sub">{sub}</p>
  {prog_html}
</div>"""
    st.markdown(card_html, unsafe_allow_html=True)


def _render_kpis(kpis: dict, projects: list) -> None:
    total_budget = sum(p.budget for p in projects)
    total_spent  = sum(p.spent  for p in projects)
    workers      = sum(w.headcount for p in projects for w in p.workforce)
    materials    = sum(len(p.materials) for p in projects)
    budget_util  = kpis["budget_utilization"]
    overall_prog = kpis["overall_progress"]
    health       = kpis["ai_health_score"]
    delayed      = kpis["delayed_projects"]
    total        = kpis["total_projects"]
    active       = kpis["active_projects"]

    st.markdown("""
<div class="dash-section-hdr">
  <span class="dash-section-title">Key Performance Indicators</span>
  <span class="dash-section-desc">Live portfolio metrics across all active projects</span>
</div>""", unsafe_allow_html=True)

    # Compute badges
    bud_badge, bud_color = (
        ("On Track", "green") if budget_util < 75
        else ("Warning", "orange") if budget_util < 90
        else ("Critical", "red")
    )
    del_badge, del_color = (
        ("No Delays", "green") if delayed == 0
        else (f"{delayed} Delayed", "red")
    )
    hlth_badge, hlth_color = (
        ("Healthy", "green") if health >= 80
        else ("At Risk", "orange") if health >= 60
        else ("Critical", "red")
    )
    prog_badge, prog_color = (
        ("On Track", "green") if overall_prog >= 50
        else ("Early Stage", "grey")
    )

    # Delayed sub-text
    delayed_projects = [p for p in projects if p.is_delayed]
    if delayed_projects:
        worst = delayed_projects[0]
        dtd = worst.days_to_deadline
        delay_days = abs(dtd) if dtd is not None else 0
        delayed_sub = f"{worst.name} · {delay_days}d behind schedule"
    else:
        delayed_sub = "All projects on schedule"

    # Row 1
    row1 = st.columns(4)
    with row1[0]:
        _kpi_card("📁", "Total Projects", str(total),
                  f"{active} active · {total - active} other",
                  "Portfolio", "blue")
    with row1[1]:
        _kpi_card("◉", "Active Projects", str(active),
                  f"{fmt_pct(active / total * 100 if total else 0)} of portfolio",
                  "Live", "green")
    with row1[2]:
        _kpi_card("⚠", "Delayed Projects", str(delayed),
                  delayed_sub, del_badge, del_color)
    with row1[3]:
        _kpi_card("◎", "AI Health Score", f"{health:.0f}/100",
                  "Composite risk & progress index",
                  hlth_badge, hlth_color, progress_pct=health)

    st.markdown("<div style='height:0.55rem'></div>", unsafe_allow_html=True)

    # Row 2
    row2 = st.columns(4)
    with row2[0]:
        _kpi_card("◈", "Budget Utilization", fmt_pct(budget_util),
                  f"{fmt_currency(total_spent)} of {fmt_currency(total_budget)}",
                  bud_badge, bud_color, progress_pct=budget_util)
    with row2[1]:
        _kpi_card("▲", "Overall Progress", fmt_pct(overall_prog),
                  "Weighted average across all projects",
                  prog_badge, prog_color, progress_pct=overall_prog)
    with row2[2]:
        _kpi_card("▲", "Workforce", str(workers),
                  "Total workers across all sites",
                  "On Site", "blue")
    with row2[3]:
        _kpi_card("▣", "Material Lines", str(materials),
                  "Total material entries tracked",
                  "Tracked", "grey")

    st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PM Command Center
# ─────────────────────────────────────────────────────────────────────────────

_PM_ACTIONS: dict[str, tuple[str, str, str, str]] = {
    "budget":  ("#C62828", "⚑", "Budget Alert",   "Review cost exposure and commitments before next billing cycle"),
    "delayed": ("#ED6C02", "⏱", "Schedule Delay",  "Recover schedule — confirm critical path and mitigation plan"),
    "safety":  ("#C62828", "⛑", "Safety Issue",    "Close safety incident before next shift starts"),
    "weather": ("#F9A825", "☁", "Weather Impact",  "Adjust field plan to account for adverse weather conditions"),
}


def _render_pm_command_center(projects: list) -> None:
    threshold    = int(st.session_state.get("cost_alert_threshold", 85))
    over_budget  = [p for p in projects if p.budget_utilization >= threshold]
    delayed      = [p for p in projects if p.is_delayed]
    open_safety  = [p for p in projects if any(i.status == "Open" for i in p.safety_incidents)]
    weather_hold = [p for p in projects if p.weather.work_impact != "Favorable"]

    st.markdown("""
<div class="dash-section-hdr">
  <span class="dash-section-title">Project Manager Command Center</span>
  <span class="dash-section-desc">Real-time alerts and recommended actions requiring your attention today</span>
</div>""", unsafe_allow_html=True)

    # Summary stats row
    def _stat_color(lst: list, warn_color: str) -> str:
        return warn_color if lst else "inherit"

    stats_col = st.columns(4)
    with stats_col[0]:
        st.markdown(f"""
<div class="pm-stat">
  <span class="pm-stat-num" style="color:{_stat_color(over_budget,'#C62828')}">{len(over_budget)}</span>
  <span class="pm-stat-lbl">Budget Alerts &ge;{threshold}%</span>
</div>""", unsafe_allow_html=True)
    with stats_col[1]:
        st.markdown(f"""
<div class="pm-stat">
  <span class="pm-stat-num" style="color:{_stat_color(delayed,'#ED6C02')}">{len(delayed)}</span>
  <span class="pm-stat-lbl">Schedule Delays</span>
</div>""", unsafe_allow_html=True)
    with stats_col[2]:
        st.markdown(f"""
<div class="pm-stat">
  <span class="pm-stat-num" style="color:{_stat_color(open_safety,'#C62828')}">{len(open_safety)}</span>
  <span class="pm-stat-lbl">Safety Issues</span>
</div>""", unsafe_allow_html=True)
    with stats_col[3]:
        st.markdown(f"""
<div class="pm-stat">
  <span class="pm-stat-num" style="color:{_stat_color(weather_hold,'#F9A825')}">{len(weather_hold)}</span>
  <span class="pm-stat-lbl">Weather Impacts</span>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

    # Priority action cards
    priorities: list[tuple[str, str, str, str, str]] = []
    for p in over_budget[:2]:
        color, icon, kind, desc = _PM_ACTIONS["budget"]
        priorities.append((p.name, color, icon, kind, desc))
    for p in delayed[:2]:
        color, icon, kind, desc = _PM_ACTIONS["delayed"]
        priorities.append((p.name, color, icon, kind, desc))
    for p in open_safety[:2]:
        color, icon, kind, desc = _PM_ACTIONS["safety"]
        priorities.append((p.name, color, icon, kind, desc))
    for p in weather_hold[:2]:
        color, icon, kind, desc = _PM_ACTIONS["weather"]
        priorities.append((p.name, color, icon, kind, desc))

    if not priorities:
        st.success("✓ No high-priority PM actions based on current thresholds. Portfolio is healthy.")
        return

    st.markdown("""<p class="dash-subsection-lbl">Today's Priorities</p>""", unsafe_allow_html=True)

    # Render 2-column grid of action cards
    for i in range(0, len(priorities[:6]), 2):
        pair = priorities[i: i + 2]
        cols = st.columns(len(pair))
        for col, (proj_name, color, icon, kind, desc) in zip(cols, pair):
            with col:
                st.markdown(f"""
<div class="pm-action-card">
  <div class="pm-action-strip" style="background:{color};"></div>
  <div class="pm-action-content">
    <div class="pm-action-top">
      <span class="pm-action-kind-badge" style="color:{color};">{icon} {kind}</span>
    </div>
    <p class="pm-action-project">{proj_name}</p>
    <p class="pm-action-desc">{desc}</p>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.35rem'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Projects Requiring Immediate Attention
# ─────────────────────────────────────────────────────────────────────────────

def _render_attention_section(projects: list) -> None:
    st.markdown("""
<div class="dash-section-hdr">
  <span class="dash-section-title">Projects Requiring Immediate Attention</span>
  <span class="dash-section-desc">Projects with confirmed delays, low health scores, or open safety incidents</span>
</div>""", unsafe_allow_html=True)

    attention = [
        p for p in attention_projects(projects)
        if p.is_delayed
        or p.health_score < 75
        or any(i.status == "Open" for i in p.safety_incidents)
    ]

    if not attention:
        st.success("✓ All projects are within healthy thresholds. No immediate action required.")
        return

    for project in attention[:4]:
        _render_attention_card(project)

    st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)


def _render_attention_card(project) -> None:
    # Risk strip colour
    if project.is_delayed or project.health_score < 60:
        strip_color = "#C62828"
    elif project.health_score < 75:
        strip_color = "#ED6C02"
    else:
        strip_color = "#0E7C7B"

    # Progress
    prog = min(100, max(0, project.progress))

    # Tags — built as a list for the native columns below
    tag_pairs: list[tuple[str, str, str]] = []  # (label, fg, bg)
    if project.is_delayed:
        dtd = project.days_to_deadline
        days = abs(dtd) if dtd is not None else 0
        tag_pairs.append((f"⏱ {days}d Behind", "#C62828", "rgba(198,40,40,0.10)"))
    if project.health_score < 75:
        tag_pairs.append((f"◎ Health {project.health_score:.0f}/100", "#E65100", "rgba(230,81,0,0.10)"))
    open_safety = sum(1 for i in project.safety_incidents if i.status == "Open")
    if open_safety:
        tag_pairs.append((f"⛑ {open_safety} Safety Issue{'s' if open_safety > 1 else ''}", "#C62828", "rgba(198,40,40,0.10)"))
    bu = project.budget_utilization
    if bu >= 90:
        tag_pairs.append((f"◈ {bu:.0f}% Budget", "#C62828", "rgba(198,40,40,0.10)"))
    elif bu >= 75:
        tag_pairs.append((f"◈ {bu:.0f}% Budget", "#E65100", "rgba(230,81,0,0.10)"))
    else:
        tag_pairs.append((f"◈ {bu:.0f}% Budget", "#0E7C7B", "rgba(14,124,123,0.10)"))

    tags_html = "".join(
        f'<span style="background:{bg};color:{fg};border:1px solid {fg}33;'
        f'border-radius:10px;padding:0.15rem 0.6rem;font-size:0.7rem;font-weight:600;">{lbl}</span>'
        for lbl, fg, bg in tag_pairs
    )

    st.markdown(f"""
<div class="attn-card">
  <div class="attn-strip" style="background:{strip_color};"></div>
  <div class="attn-body">
    <div class="attn-row-top">
      <div>
        <p class="attn-name">{project.name}</p>
        <p class="attn-meta">{project.location or 'No location'} &nbsp;&middot;&nbsp; {project.manager or 'Unassigned'} &nbsp;&middot;&nbsp; Status: <strong>{project.status}</strong> &nbsp;&middot;&nbsp; Priority: <strong>{project.priority}</strong></p>
      </div>
    </div>
    <div class="attn-progress-wrap">
      <div class="attn-progress-labels">
        <span>Completion</span><span>{prog:.0f}%</span>
      </div>
      <div class="attn-progress-track">
        <div class="attn-progress-fill" style="width:{prog}%;"></div>
      </div>
    </div>
    <div class="attn-tags">{tags_html}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # Open Workspace button — session state preserved exactly
    col_btn, _ = st.columns([1, 4])
    with col_btn:
        if st.button("Open Workspace →", key=f"dashboard_open_{project.id}", type="primary",
                     use_container_width=True):
            st.session_state["current_project_id"] = project.id
            st.session_state["page"] = "Project Workspace"
            st.rerun()

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Today's Activity — Compact Timeline
# ─────────────────────────────────────────────────────────────────────────────

def _render_activity_timeline(activity: list) -> None:
    st.markdown("""
<div class="dash-section-hdr">
  <span class="dash-section-title">Today's Activity</span>
  <span class="dash-section-desc">Most recent project events across the portfolio</span>
</div>""", unsafe_allow_html=True)

    today_items = activity[:8]
    if not today_items:
        st.info("No recent activity.")
        return

    # Build each timeline item as native Streamlit inside a single HTML wrapper
    items_html = ""
    for item in today_items:
        items_html += (
            f'<div class="tl-item">'
            f'<div class="tl-dot"></div>'
            f'<div class="tl-body">'
            f'<span class="tl-event">{item.event}</span>'
            f'<span class="tl-meta">{item.project_name}</span>'
            f'</div>'
            f'<span class="tl-time">{time_ago(item.timestamp)}</span>'
            f'</div>'
        )

    st.markdown(f'<div class="tl-wrap">{items_html}</div>', unsafe_allow_html=True)

    older = activity[8:]
    if older:
        with st.expander("View Activity History", expanded=False):
            for item in older:
                st.write(f"**{item.event}**")
                st.caption(f"{item.project_name} | {time_ago(item.timestamp)}")
                st.divider()
