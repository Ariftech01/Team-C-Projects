"""Project Portfolio - central hub for managing all projects."""
from __future__ import annotations

from datetime import date, datetime, timedelta

import streamlit as st

from config.settings import PROJECT_STATUSES, PROJECT_TYPES, PRIORITY_LEVELS
from models.domain import ActivityEvent, Project
from repository import JsonRepository, get_repository
from services.weather_service import refresh_project_weather
from utils.formatting import fmt_currency, fmt_pct, fmt_date, time_ago
from ui.components.theme import active_theme


def render_portfolio() -> None:
    repo = get_repository()
    projects = repo.list_projects()

    st.title("Project Portfolio")
    st.caption("Manage and monitor all construction projects")
    _show_portfolio_notice()

    col_search, col_status, col_sort, col_new = st.columns([2, 1.2, 1.2, 0.8])
    with col_search:
        search = st.text_input(
            "Search",
            placeholder="Project name, code, manager, location...",
            label_visibility="collapsed",
            key="portfolio_search",
        )
    with col_status:
        status_filter = st.selectbox(
            "Status",
            ["All"] + list(PROJECT_STATUSES),
            label_visibility="collapsed",
            key="portfolio_status_filter",
        )
    with col_sort:
        sort_by = st.selectbox(
            "Sort by",
            ["Name", "Progress", "Budget", "Health", "Deadline", "Recent"],
            label_visibility="collapsed",
            key="portfolio_sort_by",
        )
    with col_new:
        if st.button("New Project", use_container_width=True, type="primary"):
            st.session_state["show_new_project"] = True
            st.session_state["editing_project_id"] = None
            st.rerun()

    if st.session_state.get("show_new_project"):
        _render_project_editor(repo, mode="create")

    editing_project_id = st.session_state.get("editing_project_id")
    if editing_project_id:
        project = repo.get_project(editing_project_id)
        if project is None:
            st.session_state["editing_project_id"] = None
            st.error("The project selected for editing no longer exists.")
        else:
            _render_project_editor(repo, mode="edit", project=project)

    filtered = _sort_projects(
        _filter_projects(projects, status_filter=status_filter, search=search),
        sort_by,
    )

    _render_portfolio_operations(projects)
    st.subheader(f"{len(filtered)} Project{'s' if len(filtered) != 1 else ''}")
    if not filtered:
        st.info("No projects match your filters.")
        return

    cols = st.columns(2)
    for index, project in enumerate(filtered):
        with cols[index % 2]:
            _render_project_card(repo, project)


def _render_portfolio_operations(projects: list[Project]) -> None:
    import plotly.graph_objects as go
    import pandas as pd

    theme = active_theme()

    threshold = int(st.session_state.get("cost_alert_threshold", 85))
    active = sum(1 for p in projects if p.status == "Active")
    delayed = sum(1 for p in projects if p.status == "Delayed")
    completed = sum(1 for p in projects if p.status == "Completed")
    budget_alerts = sum(1 for p in projects if p.budget_utilization >= threshold)
    high_risk = sum(1 for p in projects if p.health_score < 70 or p.is_delayed)
    total_budget = sum(p.budget for p in projects)

    cols = st.columns(6)
    cols[0].metric("Active", str(active))
    cols[1].metric("Delayed", str(delayed))
    cols[2].metric("Completed", str(completed))
    cols[3].metric("Budget Alerts", str(budget_alerts))
    cols[4].metric("High Risk", str(high_risk))
    cols[5].metric("Portfolio Budget", fmt_currency(total_budget))

    # ── Multi-project benchmarking comparison ─────────────────────────────────
    with st.expander("📊 Multi-Project Benchmarking & Comparison", expanded=False):
        if len(projects) < 2:
            st.info("Add at least 2 projects to use the benchmarking panel.")
            return

        project_names = [p.name for p in projects]
        selected_names = st.multiselect(
            "Select projects to compare (2+)",
            project_names,
            default=project_names[:min(4, len(project_names))],
            key="benchmark_selected",
        )
        selected = [p for p in projects if p.name in selected_names]
        if len(selected) < 2:
            st.warning("Select at least 2 projects to compare.")
            return

        # Comparison table
        comparison_data = []
        for p in selected:
            workers = sum(w.headcount for w in p.workforce)
            open_safety = sum(1 for i in p.safety_incidents if i.status == "Open")
            days_left = p.days_to_deadline if p.days_to_deadline is not None else "—"
            comparison_data.append({
                "Project": p.name[:28],
                "Location": p.location,
                "Status": p.status,
                "Progress %": f"{p.progress:.1f}%",
                "Health Score": f"{p.health_score:.0f}/100",
                "Budget (₹)": fmt_currency(p.budget),
                "Spent (₹)": fmt_currency(p.spent),
                "Budget Used": f"{p.budget_utilization:.1f}%",
                "Remaining (₹)": fmt_currency(p.remaining_budget),
                "Workers": workers,
                "Open Safety": open_safety,
                "Days Left": days_left,
            })

        st.markdown("**Comparison Matrix**")
        st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)

        c1, c2 = st.columns(2)
        names = [p.name[:20] for p in selected]

        with c1:
            fig = go.Figure(data=[
                go.Bar(name="Total Budget (₹ Cr)", x=names,
                       y=[round(p.budget / 1e7, 2) for p in selected],
                       marker_color=theme["primary"],
                       hovertemplate="%{x}<br>Budget: ₹%{y:.2f} Cr<extra></extra>"),
                go.Bar(name="Spent (₹ Cr)", x=names,
                       y=[round(p.spent / 1e7, 2) for p in selected],
                       marker_color=theme["accent"],
                       hovertemplate="%{x}<br>Spent: ₹%{y:.2f} Cr<extra></extra>"),
            ])
            fig.update_layout(
                barmode="group", title="Budget vs Spent (₹ Crore)",
                height=320, margin=dict(l=10, r=10, t=40, b=10),
                legend=dict(orientation="h", y=-0.3),
                font=dict(family="Inter", color=theme["text"]),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            )
            fig.update_yaxes(title_text="₹ Crore")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig2 = go.Figure(data=[
                go.Bar(name="Progress %", x=names,
                       y=[p.progress for p in selected], marker_color=theme["accent"]),
                go.Bar(name="Health Score", x=names,
                       y=[p.health_score for p in selected], marker_color=theme["primary_light"]),
            ])
            fig2.update_layout(
                barmode="group", title="Progress vs Health Score",
                height=320, margin=dict(l=10, r=10, t=40, b=10),
                legend=dict(orientation="h", y=-0.3),
                font=dict(family="Inter", color=theme["text"]),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            )
            fig2.update_yaxes(title_text="Score / Percentage")
            st.plotly_chart(fig2, use_container_width=True)



def _filter_projects(projects: list[Project], status_filter: str, search: str) -> list[Project]:
    filtered = projects
    if status_filter != "All":
        filtered = [project for project in filtered if project.status == status_filter]

    query = search.lower().strip()
    if query:
        filtered = [
            project for project in filtered
            if query in " ".join([
                project.name,
                project.code,
                project.manager,
                project.location,
                project.client,
                project.type,
            ]).lower()
        ]
    return filtered


def _sort_projects(projects: list[Project], sort_by: str) -> list[Project]:
    sort_map = {
        "Name": lambda project: project.name.lower(),
        "Progress": lambda project: -project.progress,
        "Budget": lambda project: -project.budget,
        "Health": lambda project: -project.health_score,
        "Deadline": lambda project: project.end_date or "9999",
        "Recent": lambda project: project.updated_at or project.created_at,
    }
    return sorted(projects, key=sort_map[sort_by], reverse=sort_by == "Recent")


def _render_project_card(repo: JsonRepository, project: Project) -> None:
    workers = sum(worker.headcount for worker in project.workforce)
    recent = project.history[0] if project.history else None
    recent_text = f"{recent.title} - {time_ago(recent.timestamp)}" if recent else "No recent project activity"
    weather = project.weather

    with st.container(border=True):
        top_left, top_right = st.columns([2.2, 1])
        with top_left:
            st.markdown(f"#### {project.name}")
            st.caption(f"{project.code or 'No code'} | {project.type} | {project.location or 'No location'}")
        with top_right:
            st.write(f"Status: **{project.status}**")
            st.write(f"Priority: **{project.priority}**")

        st.progress(project.progress / 100)

        metric_a, metric_b, metric_c = st.columns(3)
        metric_a.metric("Progress", f"{project.progress:.0f}%")
        metric_b.metric("Budget Used", fmt_pct(project.budget_utilization))
        metric_c.metric("Risk", f"{project.health_score:.0f}/100")

        st.write(f"**Budget:** {fmt_currency(project.spent)} / {fmt_currency(project.budget)}")
        st.write(f"**Manager:** {project.manager or 'Unassigned'}")
        st.write(f"**Workers:** {workers}")
        st.write(f"**Deadline:** {fmt_date(project.end_date)}")
        st.write(f"**Weather:** {weather.condition} | {weather.temp_c}C | {weather.work_impact}")
        st.caption(f"Recent: {recent_text}")

        open_col, edit_col, archive_col, delete_col = st.columns(4)
        with open_col:
            if st.button("Open", key=f"open_{project.id}", use_container_width=True):
                st.session_state["current_project_id"] = project.id
                st.session_state["page"] = "Project Workspace"
                st.rerun()
        with edit_col:
            if st.button("Edit", key=f"edit_{project.id}", use_container_width=True):
                st.session_state["editing_project_id"] = project.id
                st.session_state["show_new_project"] = False
                st.rerun()
        with archive_col:
            if st.button(
                "Archive",
                key=f"archive_{project.id}",
                use_container_width=True,
                disabled=project.status == "Archived",
            ):
                _archive_project(repo, project)
                _set_portfolio_notice(f"Archived '{project.name}'.")
                st.rerun()
        with delete_col:
            if st.button(
                "Delete",
                key=f"delete_{project.id}",
                use_container_width=True,
                disabled=project.status != "Completed",
                help="Only completed projects can be deleted.",
            ):
                _delete_completed_project(repo, project)
                st.rerun()


def _render_project_editor(repo: JsonRepository, mode: str, project: Project | None = None) -> None:
    is_edit = mode == "edit" and project is not None
    title = "Edit Project" if is_edit else "Create New Project"
    key_prefix = f"{mode}_{project.id if project else 'new'}"

    with st.container(border=True):
        st.subheader(title)
        st.caption("Fill the required project basics first. Budget, dates, status, and progress drive dashboard KPIs.")
        left, right = st.columns(2)
        with left:
            name = st.text_input(
                "Project Name *",
                value=project.name if is_edit else "",
                placeholder="Example: Riverside Tower Complex",
                help="Required. This is the main name shown on cards and reports.",
                key=f"{key_prefix}_name",
            )
            code = st.text_input(
                "Project Code",
                value=project.code if is_edit else "",
                placeholder="Example: RT-2026-01",
                help="Optional internal tracking code.",
                key=f"{key_prefix}_code",
            )
            ptype = st.selectbox(
                "Type",
                list(PROJECT_TYPES),
                index=_option_index(PROJECT_TYPES, project.type if is_edit else "Commercial"),
                help="Used for portfolio grouping and analytics.",
                key=f"{key_prefix}_type",
            )
            manager = st.text_input(
                "Project Manager",
                value=project.manager if is_edit else "",
                placeholder="Example: David Chen",
                key=f"{key_prefix}_manager",
            )
            client = st.text_input(
                "Client",
                value=project.client if is_edit else "",
                placeholder="Example: Meridian Development Group",
                key=f"{key_prefix}_client",
            )
        with right:
            location = st.text_input(
                "Location",
                value=project.location if is_edit else "",
                placeholder="Example: Austin, TX",
                help="Used by the weather impact service.",
                key=f"{key_prefix}_location",
            )
            status = st.selectbox(
                "Status",
                list(PROJECT_STATUSES),
                index=_option_index(PROJECT_STATUSES, project.status if is_edit else "Active"),
                help="Archived projects remain searchable but are hidden when a specific status filter is used.",
                key=f"{key_prefix}_status",
            )
            priority = st.selectbox(
                "Priority",
                list(PRIORITY_LEVELS),
                index=_option_index(PRIORITY_LEVELS, project.priority if is_edit else "Medium"),
                help="Critical and high priorities are surfaced in attention views.",
                key=f"{key_prefix}_priority",
            )
            start_date = st.date_input(
                "Start Date",
                value=_date_value(project.start_date if is_edit else "", date.today()),
                key=f"{key_prefix}_start",
            )
            end_date = st.date_input(
                "End Date",
                value=_date_value(project.end_date if is_edit else "", date.today() + timedelta(days=180)),
                key=f"{key_prefix}_end",
            )

        budget_col, spent_col = st.columns(2)
        with budget_col:
            budget = st.number_input(
                "Budget ($)",
                min_value=0.0,
                value=float(project.budget if is_edit else 1_000_000.0),
                step=100_000.0,
                help="Total approved project budget.",
                key=f"{key_prefix}_budget",
            )
        with spent_col:
            spent = st.number_input(
                "Spent ($)",
                min_value=0.0,
                value=float(project.spent if is_edit else 0.0),
                step=50_000.0,
                help="Current committed or actual spend.",
                key=f"{key_prefix}_spent",
            )

        progress = st.slider(
            "Progress (%)",
            0,
            100,
            int(project.progress if is_edit else 0),
            key=f"{key_prefix}_progress",
        )
        description = st.text_area(
            "Description",
            value=project.description if is_edit else "",
            placeholder="Briefly describe the scope, site, and key objectives.",
            key=f"{key_prefix}_description",
        )

        save_col, cancel_col = st.columns([1, 1])
        with save_col:
            save_clicked = st.button(
                "Save Project" if is_edit else "Create Project",
                type="primary",
                key=f"{key_prefix}_save",
            )
        with cancel_col:
            cancel_clicked = st.button("Cancel", key=f"{key_prefix}_cancel")

    if save_clicked:
        if not name.strip():
            st.error("Project name is required.")
            return

        target = project if is_edit else Project()
        target.name = name.strip()
        target.code = code.strip()
        target.type = ptype
        target.status = status
        target.priority = priority
        target.manager = manager.strip()
        target.client = client.strip()
        target.location = location.strip()
        target.start_date = start_date.isoformat()
        target.end_date = end_date.isoformat()
        target.budget = budget
        target.spent = spent
        target.progress = float(progress)
        target.description = description
        target.updated_at = datetime.now().isoformat(timespec="seconds")
        if not is_edit:
            target.weather = refresh_project_weather(target)

        repo.save_project(target)
        _record_activity(repo, target, "Project updated" if is_edit else "Project created", "planning")
        st.session_state["show_new_project"] = False
        st.session_state["editing_project_id"] = None
        _set_portfolio_notice(f"Project '{target.name}' {'updated' if is_edit else 'created'} successfully.")
        st.rerun()

    if cancel_clicked:
        st.session_state["show_new_project"] = False
        st.session_state["editing_project_id"] = None
        st.rerun()


def _archive_project(repo: JsonRepository, project: Project) -> None:
    project.status = "Archived"
    project.updated_at = datetime.now().isoformat(timespec="seconds")
    repo.save_project(project)
    _record_activity(repo, project, "Project archived", "planning")


def _delete_completed_project(repo: JsonRepository, project: Project) -> None:
    if project.status != "Completed":
        st.error("Only completed projects can be deleted.")
        return
    deleted = repo.delete_project(project.id)
    if deleted:
        _record_activity(repo, project, "Completed project deleted", "planning")
        if st.session_state.get("current_project_id") == project.id:
            st.session_state["current_project_id"] = None
        _set_portfolio_notice(f"Deleted completed project '{project.name}'.")
    else:
        st.error("Project could not be deleted because it was not found.")


def _set_portfolio_notice(message: str) -> None:
    st.session_state["portfolio_notice"] = message


def _show_portfolio_notice() -> None:
    notice = st.session_state.pop("portfolio_notice", "")
    if notice:
        st.success(notice)


def _record_activity(repo: JsonRepository, project: Project, event: str, category: str) -> None:
    repo.add_activity(ActivityEvent(
        project_id=project.id,
        project_name=project.name,
        event=event,
        category=category,
    ))


def _option_index(options: tuple[str, ...], value: str) -> int:
    return list(options).index(value) if value in options else 0


def _date_value(raw: str, fallback: date) -> date:
    try:
        return date.fromisoformat(raw)
    except (TypeError, ValueError):
        return fallback
