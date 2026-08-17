"""Repository pattern — JSON-backed storage with a PostgreSQL-ready interface.

The ``Repository`` protocol defines the contract. ``JsonRepository`` implements
it against a single JSON file. Swapping in a ``PostgresRepository`` later only
requires implementing the same methods — the service and UI layers stay
unchanged.
"""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any, Iterable, Protocol

from config.settings import DB_PATH
from models.domain import Project, ActivityEvent


class Repository(Protocol):
    def list_projects(self) -> list[Project]: ...
    def get_project(self, project_id: str) -> Project | None: ...
    def save_project(self, project: Project) -> Project: ...
    def delete_project(self, project_id: str) -> bool: ...
    def list_activity(self, limit: int = 50) -> list[ActivityEvent]: ...
    def add_activity(self, event: ActivityEvent) -> ActivityEvent: ...


class JsonRepository:
    """Single-file JSON store. Thread-safe via a process lock."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = Path(path or DB_PATH)
        self._lock = threading.Lock()
        self._ensure()

    def _ensure(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._write({"projects": [], "activity": []})

    def _read(self) -> dict[str, Any]:
        with self._lock:
            if not self._path.exists():
                return {"projects": [], "activity": []}
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return {"projects": [], "activity": []}
            return data if isinstance(data, dict) else {"projects": [], "activity": []}

    def _write(self, data: dict[str, Any]) -> None:
        with self._lock:
            temp_path = self._path.with_suffix(".tmp")
            temp_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
            os.replace(temp_path, self._path)

    # ---- Projects ----
    def list_projects(self) -> list[Project]:
        raw_projects = self._read().get("projects", [])
        return [Project.from_dict(p) for p in raw_projects if isinstance(p, dict)]

    def get_project(self, project_id: str) -> Project | None:
        for p in self.list_projects():
            if p.id == project_id:
                return p
        return None

    def save_project(self, project: Project) -> Project:
        data = self._read()
        projects = data.setdefault("projects", [])
        idx = next((i for i, p in enumerate(projects) if p.get("id") == project.id), None)
        if idx is None:
            projects.append(project.to_dict())
        else:
            projects[idx] = project.to_dict()
        self._write(data)
        return project

    def delete_project(self, project_id: str) -> bool:
        data = self._read()
        projects = data.get("projects", [])
        new = [p for p in projects if p["id"] != project_id]
        if len(new) == len(projects):
            return False
        data["projects"] = new
        self._write(data)
        return True

    # ---- Activity feed ----
    def list_activity(self, limit: int = 50) -> list[ActivityEvent]:
        acts = self._read().get("activity", [])
        acts = sorted(acts, key=lambda a: a.get("timestamp", ""), reverse=True)
        return [ActivityEvent.from_dict(a) for a in acts[:limit]]

    def add_activity(self, event: ActivityEvent) -> ActivityEvent:
        data = self._read()
        data.setdefault("activity", []).append(event.to_dict())
        self._write(data)
        return event


_repo: JsonRepository | None = None


def get_repository() -> JsonRepository:
    global _repo
    if _repo is None:
        _repo = JsonRepository()
    return _repo
