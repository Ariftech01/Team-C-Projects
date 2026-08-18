"""Engineering material estimation and costing.

The formulas follow standard civil-engineering thumb rules for RCC-framed
buildings with brick masonry walls. Quantities scale by floor count and are
adjusted by a quality multiplier that reflects specification grade.
"""
from __future__ import annotations

from typing import TypedDict

# ---- constants (per m3 of masonry / concrete) -----------------------------
BRICKS_PER_CUM_MASONRY = 500          # standard modular brick count / m3
MORTAR_RATIO_IN_MASONRY = 0.30        # 30 % of wall volume is mortar
CEMENT_BAGS_PER_CUM_MORTAR = 7.5      # 1:6 cement:sand mortar
SAND_PER_CUM_MORTAR = 1.10            # m3 sand per m3 wet mortar (bulking)

CEMENT_BAGS_PER_CUM_CONCRETE = 8.0    # M20 mix, 1:1.5:3
SAND_PER_CUM_CONCRETE = 0.45          # m3
AGG_PER_CUM_CONCRETE = 0.90           # m3
STEEL_KG_PER_CUM_CONCRETE = 80.0      # typical RCC reinforcement

WALL_THICKNESS_M = 0.23               # 9-inch brick wall
SLAB_THICKNESS_M = 0.15               # 150 mm RCC slab
COLUMN_CONCRETE_FRACTION = 0.03       # 3 % of built-up volume for columns/beams

# Wall-to-floor ratio: linear wall length per m2 of floor area (typical layout)
WALL_LINEAR_M_PER_SQM = 0.55

QUALITY_MULTIPLIER = {
    "Economy": 0.90,
    "Standard": 1.00,
    "Premium": 1.15,
    "Luxury": 1.35,
}

SQFT_PER_SQM = 10.7639


class Quantities(TypedDict):
    bricks: float
    cement_bags: float
    sand_cum: float
    aggregate_cum: float
    steel_kg: float
    concrete_cum: float
    mortar_cum: float
    paint_sqft: float
    tiles_sqft: float


def estimate(
    length_m: float,
    width_m: float,
    height_m: float,
    floors: int,
    quality: str = "Standard",
) -> Quantities:
    """Return material quantities for a rectangular building footprint.

    Args:
        length_m, width_m: plan dimensions in meters.
        height_m: floor-to-floor height in meters.
        floors: number of floors.
        quality: one of Economy / Standard / Premium / Luxury.
    """
    length_m = max(float(length_m), 0.0)
    width_m = max(float(width_m), 0.0)
    height_m = max(float(height_m), 0.0)
    floors = max(int(floors), 1)
    qm = QUALITY_MULTIPLIER.get(quality, 1.0)

    footprint_sqm = length_m * width_m
    built_up_sqm = footprint_sqm * floors

    # ---- masonry -----------------------------------------------------------
    wall_length_m = WALL_LINEAR_M_PER_SQM * built_up_sqm
    wall_volume_cum = wall_length_m * height_m * WALL_THICKNESS_M
    mortar_cum = wall_volume_cum * MORTAR_RATIO_IN_MASONRY
    masonry_volume_cum = wall_volume_cum - mortar_cum
    bricks = masonry_volume_cum * BRICKS_PER_CUM_MASONRY

    # ---- concrete (slab + columns/beams) ----------------------------------
    slab_volume = footprint_sqm * SLAB_THICKNESS_M * floors
    frame_volume = built_up_sqm * height_m * COLUMN_CONCRETE_FRACTION
    concrete_cum = slab_volume + frame_volume

    # ---- cement / sand / aggregate ----------------------------------------
    cement_bags = (
        mortar_cum * CEMENT_BAGS_PER_CUM_MORTAR
        + concrete_cum * CEMENT_BAGS_PER_CUM_CONCRETE
    )
    sand_cum = (
        mortar_cum * SAND_PER_CUM_MORTAR
        + concrete_cum * SAND_PER_CUM_CONCRETE
    )
    aggregate_cum = concrete_cum * AGG_PER_CUM_CONCRETE
    steel_kg = concrete_cum * STEEL_KG_PER_CUM_CONCRETE

    # ---- finishes ----------------------------------------------------------
    wall_face_sqm = wall_length_m * height_m * 2  # both sides
    paint_sqft = wall_face_sqm * SQFT_PER_SQM
    tiles_sqft = built_up_sqm * SQFT_PER_SQM  # floor tiling

    result: Quantities = {
        "bricks": round(bricks * qm, 0),
        "cement_bags": round(cement_bags * qm, 1),
        "sand_cum": round(sand_cum * qm, 2),
        "aggregate_cum": round(aggregate_cum * qm, 2),
        "steel_kg": round(steel_kg * qm, 1),
        "concrete_cum": round(concrete_cum * qm, 2),
        "mortar_cum": round(mortar_cum * qm, 2),
        "paint_sqft": round(paint_sqft * qm, 1),
        "tiles_sqft": round(tiles_sqft * qm, 1),
    }
    return result


RATE_MAP = {
    "bricks": ("rate_bricks_per_unit", "Bricks (nos)"),
    "cement_bags": ("rate_cement_per_bag", "Cement (50 kg bags)"),
    "sand_cum": ("rate_sand_per_cum", "Sand (m³)"),
    "aggregate_cum": ("rate_aggregate_per_cum", "Aggregate (m³)"),
    "steel_kg": ("rate_steel_per_kg", "Steel (kg)"),
    "concrete_cum": ("rate_concrete_per_cum", "Ready-mix concrete (m³)"),
    "mortar_cum": ("rate_mortar_per_cum", "Mortar (m³)"),
    "paint_sqft": ("rate_paint_per_sqft", "Paint (sqft)"),
    "tiles_sqft": ("rate_tiles_per_sqft", "Tiles (sqft)"),
}


def cost_breakdown(quantities: dict, settings: dict) -> dict:
    """Return per-material cost and grand total using settings rates."""
    lines: dict[str, dict] = {}
    subtotal = 0.0
    for key, (rate_key, label) in RATE_MAP.items():
        qty = float(quantities.get(key, 0) or 0)
        rate = float(settings.get(rate_key, 0) or 0)
        cost = qty * rate
        subtotal += cost
        lines[key] = {"label": label, "quantity": qty, "rate": rate, "cost": round(cost, 2)}
    tax_pct = float(settings.get("tax_percent", 0) or 0)
    tax_amount = subtotal * tax_pct / 100.0
    total = subtotal + tax_amount
    return {
        "lines": lines,
        "subtotal": round(subtotal, 2),
        "tax_percent": tax_pct,
        "tax_amount": round(tax_amount, 2),
        "total": round(total, 2),
    }


def estimate_labor_cost(area_sqft: float, settings: dict) -> float:
    return round(float(area_sqft) * float(settings.get("labor_cost_per_sqft", 0) or 0), 2)
