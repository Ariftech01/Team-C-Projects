"""AI Tool Center - focused construction workflows."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from repository import get_repository
from services import ai_chat
from utils.formatting import fmt_currency


AI_TOOLS = [
    ("Planning AI", "Next actions, schedule health, blockers, and PM priorities.", "Create a construction planning brief with next actions."),
    ("Cost & Budget AI", "Spend review, remaining budget, overrun pressure, and cost controls.", "Analyze cost and budget exposure."),
    ("Delay & Risk AI", "Delay signals, safety risks, weather risks, and recovery actions.", "Predict delay and risk exposure."),
    ("Report Generator", "Executive-ready daily or weekly report summary.", "Draft an executive report summary."),
    ("Safety & Quality AI", "Safety gaps, incident follow-up, checklist misses, and quality controls.", "Analyze safety and quality risks."),
]


def _estimate_materials(inputs: dict[str, str | float | int]) -> list[dict[str, str]]:
    """Create an indicative material take-off using India-focused planning rates."""
    area = float(inputs["area"])
    floors = int(inputs["floors"])
    foundation_factor = {"Isolated footing": 1.00, "Raft foundation": 1.18, "Pile foundation": 1.30}[inputs["foundation"]]
    structural_factor = {"RCC framed": 1.00, "Steel framed": 0.78, "Load-bearing masonry": 0.88}[inputs["structural"]]
    grade_factor = {"M20": 1.00, "M25": 1.05, "M30": 1.10}[inputs["concrete_grade"]]
    brick_factor = {"Clay brick": 1.00, "Fly ash brick": 0.96, "AAC block": 0.55}[inputs["brick_type"]]
    roof_factor = {"RCC slab": 1.00, "Metal sheet": 0.82, "Tile roof": 0.90}[inputs["roof_type"]]
    location_factor = {"Metro city": 1.15, "Tier 1 city": 1.08, "Tier 2 city": 1.00, "Rural / remote": 1.06}[inputs["location"]]
    quality_factor = {"Economy": 0.90, "Standard": 1.00, "Premium": 1.22}[inputs["quality"]]
    floor_factor = 1 + max(floors - 1, 0) * 0.04

    quantities = [
        ("Cement", area * 0.42 * structural_factor * grade_factor * quality_factor, "bags", 440),
        ("Steel reinforcement", area * 4.20 * structural_factor * floor_factor, "kg", 64),
        ("Sand", area * 1.80 * foundation_factor * floor_factor, "cu ft", 55),
        ("Aggregate", area * 2.50 * foundation_factor * floor_factor, "cu ft", 45),
        ("Bricks / blocks", area * 8.50 * brick_factor, "nos", 9),
        ("Ready-mix concrete", area * 0.033 * foundation_factor * structural_factor * roof_factor, "m³", 5800),
        ("Finishing materials", area, "sq ft", 190 * quality_factor),
    ]

    rows = []
    for material, quantity, unit, base_rate in quantities:
        rate = base_rate * location_factor
        total = quantity * rate
        rows.append(
            {
                "Material": material,
                "Quantity": f"{quantity:,.0f}",
                "Unit": unit,
                "Estimated Cost (₹)": f"₹{rate:,.0f}",
                "Total Cost (₹)": f"₹{total:,.0f}",
                "_total": total,
            }
        )
    return rows


def _render_material_estimator() -> None:
    st.subheader("Material Estimator")
    st.caption("Input-driven indicative material take-off using India-focused planning rates.")

    with st.form("material_estimator_form", border=True):
        first, second = st.columns(2)
        with first:
            project_type = st.selectbox("Project type", ["Residential", "Commercial", "Industrial", "Institutional"])
            area = st.number_input("Built-up area (sq ft)", min_value=100.0, value=2000.0, step=100.0)
            floors = st.number_input("Number of floors", min_value=1, max_value=100, value=2, step=1)
            foundation = st.selectbox("Foundation type", ["Isolated footing", "Raft foundation", "Pile foundation"])
            structural = st.selectbox("Structural system", ["RCC framed", "Steel framed", "Load-bearing masonry"])
        with second:
            concrete_grade = st.selectbox("Concrete grade", ["M20", "M25", "M30"])
            brick_type = st.selectbox("Brick / block type", ["Clay brick", "Fly ash brick", "AAC block"])
            roof_type = st.selectbox("Roof type", ["RCC slab", "Metal sheet", "Tile roof"])
            location = st.selectbox("Site location", ["Metro city", "Tier 1 city", "Tier 2 city", "Rural / remote"])
            quality = st.selectbox("Quality level", ["Economy", "Standard", "Premium"], index=1)

        submitted = st.form_submit_button("Estimate materials", type="primary", use_container_width=True)

    if submitted:
        st.session_state["material_estimate"] = _estimate_materials(
            {
                "project_type": project_type,
                "area": area,
                "floors": floors,
                "foundation": foundation,
                "structural": structural,
                "concrete_grade": concrete_grade,
                "brick_type": brick_type,
                "roof_type": roof_type,
                "location": location,
                "quality": quality,
            }
        )

    estimate = st.session_state.get("material_estimate")
    if not estimate:
        return

    total_cost = sum(row["_total"] for row in estimate)
    st.success("Indicative material estimate generated.")
    st.dataframe(
        [{key: value for key, value in row.items() if key != "_total"} for row in estimate],
        use_container_width=True,
        hide_index=True,
    )
    st.caption("Estimated Cost (₹) is the indicative rate per listed unit.")
    st.metric("Estimated material cost", f"₹{total_cost:,.0f}")
    st.caption("Planning estimate only. Validate quantities, specifications, freight, taxes, wastage, and local supplier quotations before procurement.")


def _render_boq_analyzer() -> None:
    """Itemized BOQ Quantity Takeoff & Cost Estimation with GST and contingency."""
    st.subheader("📋 Itemized BOQ Takeoff & Cost Analyzer")
    st.caption(
        "Generate a construction Bill of Quantities with itemized rates, 18% GST, and a contingency buffer. "
        "Based on Indian standard rates (CPWD / PWD schedule of rates)."
    )

    with st.form("boq_analyzer_form", border=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            project_title = st.text_input("Project Title", value="Construction Project", key="boq_proj_title")
            location = st.selectbox(
                "Location",
                ["Metro city (Delhi / Mumbai)", "Tier-1 city (Pune / Ahmedabad)",
                 "Tier-2 city (Jaipur / Nagpur)", "Remote / Rural"],
                key="boq_location",
            )
            project_type = st.selectbox(
                "Project Type",
                ["Residential", "Commercial", "Industrial", "Infrastructure"],
                key="boq_proj_type",
            )
        with col2:
            built_area = st.number_input("Built-up Area (sq ft)", min_value=100.0,
                                         value=5000.0, step=500.0, key="boq_area")
            floors = st.number_input("No. of Floors", min_value=1, max_value=80,
                                     value=5, key="boq_floors")
            concrete_grade = st.selectbox("Concrete Grade", ["M20", "M25", "M30", "M40"],
                                          key="boq_concrete")
        with col3:
            steel_type = st.selectbox("Steel Grade", ["Fe415", "Fe500", "Fe550D"],
                                      key="boq_steel")
            quality_spec = st.selectbox(
                "Specification Level",
                ["Economy", "Standard", "Premium", "Luxury"],
                index=1, key="boq_quality",
            )
            contingency_pct = st.slider("Contingency (%)", 5, 20, 10, key="boq_contingency")

        submitted = st.form_submit_button(
            "Generate BOQ Estimate", type="primary", use_container_width=True
        )

    if submitted:
        loc_factor = {
            "Metro city (Delhi / Mumbai)": 1.20,
            "Tier-1 city (Pune / Ahmedabad)": 1.08,
            "Tier-2 city (Jaipur / Nagpur)": 1.00,
            "Remote / Rural": 1.10,
        }[location]
        q_factor = {"Economy": 0.88, "Standard": 1.00, "Premium": 1.25, "Luxury": 1.55}[quality_spec]
        c_factor = {"M20": 1.00, "M25": 1.06, "M30": 1.13, "M40": 1.22}[concrete_grade]
        s_factor = {"Fe415": 0.95, "Fe500": 1.00, "Fe550D": 1.06}[steel_type]
        fl_factor = 1 + (int(floors) - 1) * 0.035
        area = float(built_area)

        # Item-wise BOQ (description, qty-multiplier, floor-factor, base-rate ₹/sqft)
        boq_items = [
            ("1.0", "Site Preparation & Earthwork",
             "Excavation, levelling, dewatering, compaction.",
             area * 0.20, fl_factor, 95 * loc_factor * q_factor),
            ("2.0", f"Foundation ({concrete_grade})",
             f"PCC + RCC {concrete_grade} raft/footing, waterproofing membrane.",
             area * 0.35, fl_factor, 320 * c_factor * loc_factor * q_factor),
            ("3.0", f"RCC Frame ({concrete_grade} / {steel_type})",
             f"Columns, beams, slabs — {concrete_grade} with {steel_type} TMT bars.",
             area, fl_factor, 420 * c_factor * s_factor * loc_factor * q_factor),
            ("4.0", "Masonry & Internal Walls",
             "Fly ash brick masonry, internal partitions, parapet.",
             area * 0.55, 1.00, 185 * loc_factor * q_factor),
            ("5.0", "Plastering & External Finish",
             "2-coat cement plaster internal (12mm); textured external (18mm).",
             area * 1.80, 1.00, 55 * loc_factor * q_factor),
            ("6.0", "Flooring & Tiling",
             "Vitrified tiles (600×600); ceramic tiles for wet areas.",
             area, 1.00, 165 * q_factor * loc_factor),
            ("7.0", "Doors, Windows & Glazing",
             "UPVC/aluminium frames; engineered wood/steel flush doors.",
             area * 0.10, 1.00, 750 * q_factor * loc_factor),
            ("8.0", "MEP — Electrical",
             "FRLS copper wiring, DB boards, earthing, ELCB, light points.",
             area, 1.00, 120 * q_factor * loc_factor),
            ("9.0", "MEP — Plumbing & Sanitation",
             "CPVC/UPVC supply, PVC drainage, EWC, WHB, CP fittings.",
             area, 1.00, 95 * q_factor * loc_factor),
            ("10.0", "False Ceiling & Partitions",
             "Gypsum board false ceiling, office partitions (where applicable).",
             area * 0.60, 1.00, 145 * q_factor * loc_factor),
            ("11.0", "Painting & Polishing",
             "Interior 2-coat emulsion; exterior weather-shield paint.",
             area * 2.00, 1.00, 45 * q_factor * loc_factor),
            ("12.0", "Site Overheads & Miscellaneous",
             "DG set, water tanker, safety barricading, site cleanup.",
             area, 1.00, 60 * loc_factor),
        ]

        rows, subtotal = [], 0.0
        for item_no, desc, detail, qty, ffactor, rate in boq_items:
            eff_qty = qty * ffactor
            amount = eff_qty * rate
            subtotal += amount
            rows.append({
                "Item": item_no,
                "Description": desc,
                "Qty (sq ft)": f"{eff_qty:,.0f}",
                "Rate (₹/sqft)": fmt_currency(rate),
                "Amount (₹)": fmt_currency(amount),
                "_amount": amount,
            })

        gst = subtotal * 0.18
        contingency = subtotal * (contingency_pct / 100)
        grand_total = subtotal + gst + contingency

        st.success(
            f"BOQ estimate generated for **{project_title}** "
            f"({built_area:,.0f} sq ft · {floors} floors)"
        )

        display = [{k: v for k, v in r.items() if k != "_amount"} for r in rows]
        st.dataframe(pd.DataFrame(display), use_container_width=True, hide_index=True)

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Construction Sub-Total", fmt_currency(subtotal))
        s2.metric("GST @ 18%", fmt_currency(gst))
        s3.metric(f"Contingency @ {contingency_pct}%", fmt_currency(contingency))
        s4.metric("Grand Total (₹)", fmt_currency(grand_total))

        per_sqft = grand_total / float(built_area) if built_area else 0
        st.info(
            f"📐 **Per sq ft cost estimate: ₹{per_sqft:,.0f}** │ "
            f"Spec: **{quality_spec}** │ Location: **{location}** │ "
            f"Concrete: **{concrete_grade}** / Steel: **{steel_type}**"
        )
        st.caption(
            "Indicative BOQ estimate based on CPWD/PWD schedule of rates. "
            "Validate with current market quotations, site surveys, statutory levies "
            "(Labour CESS, TDS), and architect / structural consultant fees before procurement."
        )

        # CSV download
        csv_rows = display + [
            {"Item": "", "Description": "Sub-Total", "Qty (sq ft)": "",
             "Rate (₹/sqft)": "", "Amount (₹)": fmt_currency(subtotal)},
            {"Item": "", "Description": "GST @ 18%", "Qty (sq ft)": "",
             "Rate (₹/sqft)": "", "Amount (₹)": fmt_currency(gst)},
            {"Item": "", "Description": f"Contingency @ {contingency_pct}%",
             "Qty (sq ft)": "", "Rate (₹/sqft)": "", "Amount (₹)": fmt_currency(contingency)},
            {"Item": "", "Description": "GRAND TOTAL", "Qty (sq ft)": "",
             "Rate (₹/sqft)": "", "Amount (₹)": fmt_currency(grand_total)},
        ]
        st.download_button(
            "⬇️ Download BOQ as CSV",
            data=pd.DataFrame(csv_rows).to_csv(index=False),
            file_name=f"BOQ_{project_title.replace(' ', '_')}.csv",
            mime="text/csv",
            use_container_width=True,
        )


def render_ai_actions() -> None:
    repo = get_repository()
    projects = repo.list_projects()

    st.title("AI Tool Center")
    st.caption("Focused construction workflows for planning, budget, materials, risk, reporting, and safety.")

    _render_boq_analyzer()
    st.divider()
    _render_material_estimator()
    st.divider()

    if not projects:
        st.info("Create a project to use the remaining AI workflows. The Material Estimator is available without a selected project.")
        return

    project_options = ["Portfolio-wide"] + [project.name for project in projects]
    selected = st.selectbox("AI Context", project_options, help="Choose portfolio-wide analysis or one project.")
    selected_project = next((project for project in projects if project.name == selected), None)
    context = {"page": "AI Actions", "project": selected_project} if selected_project else {"page": "AI Actions", "projects": projects}

    st.info("Flow: choose context, run a tool, review the result, then open a workspace if action is needed.")

    cols = st.columns(2)
    for index, (name, description, prompt) in enumerate(AI_TOOLS):
        with cols[index % 2]:
            with st.container(border=True):
                st.subheader(name)
                st.write(description)
                st.caption(f"Current context: {selected}")
                if st.button("Run Tool", key=f"ai_tool_{index}", use_container_width=True, type="primary"):
                    with st.spinner(f"Running {name}..."):
                        result = ai_chat(prompt, context=context)
                    st.session_state["last_ai_tool"] = {"name": name, "context": selected, "result": result}
                    st.success(f"{name} completed.")
                    st.write(result)

    last = st.session_state.get("last_ai_tool")
    if last:
        st.subheader("Latest AI Result")
        with st.container(border=True):
            st.write(f"**Tool:** {last['name']}")
            st.write(f"**Context:** {last['context']}")
            st.write(last["result"])
