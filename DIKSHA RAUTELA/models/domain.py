"""Domain models for the Construction Intelligence Hub.

All models are plain dataclasses with ``to_dict`` / ``from_dict`` so they can be
serialized to JSON today and mapped to PostgreSQL rows tomorrow without changes
to the service layer.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import Any


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


@dataclass
class Task:
    id: str = field(default_factory=lambda: _uid("task"))
    name: str = ""
    phase: str = ""
    start_date: str = ""
    end_date: str = ""
    progress: float = 0.0
    status: str = "Not Started"
    assignee: str = ""
    priority: str = "Medium"
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Task":
        return cls(**{k: d.get(k) for k in cls.__dataclass_fields__})


@dataclass
class Material:
    id: str = field(default_factory=lambda: _uid("mat"))
    name: str = ""
    category: str = ""
    quantity: float = 0.0
    unit: str = ""
    unit_cost: float = 0.0
    used: float = 0.0
    supplier: str = ""
    status: str = "Ordered"
    delivery_date: str = ""

    @property
    def total_cost(self) -> float:
        return self.quantity * self.unit_cost

    @property
    def utilization(self) -> float:
        return (self.used / self.quantity * 100) if self.quantity else 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Material":
        return cls(**{k: d.get(k) for k in cls.__dataclass_fields__})


@dataclass
class WorkforceMember:
    id: str = field(default_factory=lambda: _uid("wf"))
    name: str = ""
    role: str = ""
    crew: str = ""
    headcount: int = 1
    hourly_rate: float = 0.0
    hours_today: float = 0.0
    status: str = "On Site"
    trade: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "WorkforceMember":
        return cls(**{k: d.get(k) for k in cls.__dataclass_fields__})


@dataclass
class Equipment:
    id: str = field(default_factory=lambda: _uid("eq"))
    name: str = ""
    type: str = ""
    status: str = "Operational"
    operator: str = ""
    fuel_hours: float = 0.0
    last_service: str = ""
    next_service: str = ""
    daily_rate: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Equipment":
        return cls(**{k: d.get(k) for k in cls.__dataclass_fields__})


@dataclass
class SafetyIncident:
    id: str = field(default_factory=lambda: _uid("saf"))
    date: str = ""
    type: str = ""
    severity: str = "Low"
    description: str = ""
    reported_by: str = ""
    status: str = "Open"
    action_taken: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "SafetyIncident":
        return cls(**{k: d.get(k) for k in cls.__dataclass_fields__})


@dataclass
class SafetyChecklist:
    id: str = field(default_factory=lambda: _uid("chk"))
    item: str = ""
    completed: bool = False
    last_checked: str = ""
    responsible: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "SafetyChecklist":
        return cls(**{k: d.get(k) for k in cls.__dataclass_fields__})


@dataclass
class WeatherSnapshot:
    date: str = ""
    temp_c: float = 0.0
    condition: str = ""
    wind_kph: float = 0.0
    precipitation_mm: float = 0.0
    humidity: float = 0.0
    uv_index: float = 0.0
    work_impact: str = "Favorable"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "WeatherSnapshot":
        return cls(**{k: d.get(k) for k in cls.__dataclass_fields__})


@dataclass
class Document:
    id: str = field(default_factory=lambda: _uid("doc"))
    name: str = ""
    category: str = "General"
    uploaded_at: str = field(default_factory=_now_iso)
    file_type: str = ""
    size_bytes: int = 0
    summary: str = ""
    status: str = "Uploaded"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Document":
        return cls(**{k: d.get(k) for k in cls.__dataclass_fields__})


@dataclass
class HistoryEntry:
    id: str = field(default_factory=lambda: _uid("hist"))
    timestamp: str = field(default_factory=_now_iso)
    type: str = "activity"
    title: str = ""
    content: str = ""
    author: str = "System"
    file_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "HistoryEntry":
        return cls(**{k: d.get(k) for k in cls.__dataclass_fields__})


@dataclass
class ActivityEvent:
    id: str = field(default_factory=lambda: _uid("act"))
    timestamp: str = field(default_factory=_now_iso)
    project_id: str = ""
    project_name: str = ""
    event: str = ""
    category: str = "general"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ActivityEvent":
        return cls(**{k: d.get(k) for k in cls.__dataclass_fields__})


@dataclass
class Project:
    id: str = field(default_factory=lambda: _uid("proj"))
    name: str = ""
    code: str = ""
    type: str = "Commercial"
    status: str = "Planning"
    priority: str = "Medium"
    manager: str = ""
    client: str = ""
    location: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    start_date: str = ""
    end_date: str = ""
    budget: float = 0.0
    spent: float = 0.0
    progress: float = 0.0
    description: str = ""
    weather: WeatherSnapshot = field(default_factory=WeatherSnapshot)
    tasks: list[Task] = field(default_factory=list)
    materials: list[Material] = field(default_factory=list)
    workforce: list[WorkforceMember] = field(default_factory=list)
    equipment: list[Equipment] = field(default_factory=list)
    safety_incidents: list[SafetyIncident] = field(default_factory=list)
    safety_checklist: list[SafetyChecklist] = field(default_factory=list)
    documents: list[Document] = field(default_factory=list)
    history: list[HistoryEntry] = field(default_factory=list)
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)

    @property
    def budget_utilization(self) -> float:
        return (self.spent / self.budget * 100) if self.budget else 0.0

    @property
    def remaining_budget(self) -> float:
        return self.budget - self.spent

    @property
    def days_to_deadline(self) -> int | None:
        if not self.end_date:
            return None
        try:
            d = date.fromisoformat(self.end_date)
            return (d - date.today()).days
        except ValueError:
            return None

    @property
    def is_delayed(self) -> bool:
        if self.status == "Delayed":
            return True
        dtd = self.days_to_deadline
        return dtd is not None and dtd < 0 and self.status != "Completed"

    @property
    def health_score(self) -> float:
        score = 100.0
        if self.is_delayed:
            score -= 25
        if self.budget_utilization > 90:
            score -= 20
        elif self.budget_utilization > 75:
            score -= 10
        open_safety = sum(1 for s in self.safety_incidents if s.status == "Open")
        score -= open_safety * 8
        if self.progress < 30 and self.status == "Active":
            score -= 10
        return max(0.0, round(score, 1))

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Project":
        weather = WeatherSnapshot.from_dict(d.get("weather", {}))
        tasks = [Task.from_dict(t) for t in d.get("tasks", [])]
        materials = [Material.from_dict(m) for m in d.get("materials", [])]
        workforce = [WorkforceMember.from_dict(w) for w in d.get("workforce", [])]
        equipment = [Equipment.from_dict(e) for e in d.get("equipment", [])]
        safety_incidents = [SafetyIncident.from_dict(s) for s in d.get("safety_incidents", [])]
        safety_checklist = [SafetyChecklist.from_dict(c) for c in d.get("safety_checklist", [])]
        documents = [Document.from_dict(doc) for doc in d.get("documents", [])]
        history = [HistoryEntry.from_dict(h) for h in d.get("history", [])]
        return cls(
            id=d.get("id", ""),
            name=d.get("name", ""),
            code=d.get("code", ""),
            type=d.get("type", "Commercial"),
            status=d.get("status", "Planning"),
            priority=d.get("priority", "Medium"),
            manager=d.get("manager", ""),
            client=d.get("client", ""),
            location=d.get("location", ""),
            latitude=d.get("latitude", 0.0),
            longitude=d.get("longitude", 0.0),
            start_date=d.get("start_date", ""),
            end_date=d.get("end_date", ""),
            budget=d.get("budget", 0.0),
            spent=d.get("spent", 0.0),
            progress=d.get("progress", 0.0),
            description=d.get("description", ""),
            weather=weather,
            tasks=tasks,
            materials=materials,
            workforce=workforce,
            equipment=equipment,
            safety_incidents=safety_incidents,
            safety_checklist=safety_checklist,
            documents=documents,
            history=history,
            created_at=d.get("created_at", _now_iso()),
            updated_at=d.get("updated_at", _now_iso()),
        )
