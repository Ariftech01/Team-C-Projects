"""Weather service.

Uses a local heuristic to generate plausible weather snapshots for each
project location. The interface is designed so a live API (OpenWeather,
Open-Meteo) can be dropped in later without touching the UI.
"""
from __future__ import annotations

import random

from models.domain import Project, WeatherSnapshot


# Rough climate baselines by region keyword -> (temp_c baseline, humidity, rain_prone)
_CLIMATE_HINTS = {
    "austin": (28, 55, 0.15),
    "phoenix": (38, 25, 0.02),
    "portland": (12, 70, 0.5),
    "columbus": (18, 60, 0.25),
    "chicago": (15, 60, 0.3),
    "denver": (20, 40, 0.15),
    "miami": (30, 75, 0.4),
    "seattle": (14, 72, 0.55),
}

_CONDITIONS = ["Sunny", "Partly Cloudy", "Cloudy", "Overcast", "Light Rain", "Heavy Rain", "Windy", "Fog"]
_IMPACT_MAP = {
    "Sunny": "Favorable",
    "Partly Cloudy": "Favorable",
    "Cloudy": "Favorable",
    "Overcast": "Favorable",
    "Light Rain": "Caution",
    "Heavy Rain": "Unfavorable",
    "Windy": "Caution",
    "Fog": "Caution",
}


def _classify_impact(w: WeatherSnapshot) -> str:
    if w.precipitation_mm > 10 or w.wind_kph > 35:
        return "Unfavorable"
    if w.precipitation_mm > 2 or w.wind_kph > 25 or w.temp_c > 37 or w.temp_c < -2:
        return "Caution"
    return "Favorable"


def fetch_weather(project: Project) -> WeatherSnapshot:
    """Return a weather snapshot for the project's location.

    Deterministic-ish based on location keyword + slight randomness so the
    UI feels alive. Swap this for a real API call later.
    """
    loc = (project.location or "").lower()
    base_temp, base_hum, rain_prone = (20, 60, 0.2)
    for key, val in _CLIMATE_HINTS.items():
        if key in loc:
            base_temp, base_hum, rain_prone = val
            break

    rng = random.Random(hash(project.id) & 0xFFFFFFFF)
    raining = rng.random() < rain_prone
    condition = rng.choice(["Heavy Rain", "Light Rain"]) if raining else rng.choice(
        ["Sunny", "Partly Cloudy", "Cloudy", "Overcast", "Windy"]
    )
    temp = round(base_temp + rng.uniform(-4, 4), 1)
    wind = round(rng.uniform(5, 40 if "wind" in condition.lower() else 22), 1)
    precip = round(rng.uniform(8, 28) if condition == "Heavy Rain" else (rng.uniform(0.5, 5) if condition == "Light Rain" else 0.0), 1)
    humidity = round(base_hum + rng.uniform(-10, 10))
    uv = round(rng.uniform(2, 9), 1)

    snap = WeatherSnapshot(
        date=__import__("datetime").date.today().isoformat(),
        temp_c=temp,
        condition=condition,
        wind_kph=wind,
        precipitation_mm=precip,
        humidity=max(10, min(100, humidity)),
        uv_index=uv,
        work_impact=_IMPACT_MAP.get(condition, "Favorable"),
    )
    snap.work_impact = _classify_impact(snap)
    return snap


def refresh_project_weather(project: Project) -> WeatherSnapshot:
    return fetch_weather(project)
