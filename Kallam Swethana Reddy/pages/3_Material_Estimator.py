"""Material Estimator — quantities, cost breakdown, export."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from database import init_db, get_settings, list_projects, log_estimation
from material_estimator import estimate, cost_breakdown, RATE_MAP, estimate_labor_cost
from report_generator import estimation_pdf, estimation_excel
from auth_ui import require_login, render_user_sidebar
from utils import (
    inject_css, render_sidebar_brand, page_header,
    QUALITY_LEVELS, format_currency, format_number,
)

st.set_page_config(page_title="Estimator • CIH", page_icon="🧮", layout="wide")
init_db()
inject_css()
user = require_login()
user_id = user["id"]
settings = get_settings(user_id)
render_sidebar_brand(settings.get("company_name"))
render_user_sidebar()
page_header("Material Estimator",
            "Engineering-grade quantity take-off and cost breakdown.", icon="🧮")

with st.form("estimator_form"):
    c1, c2, c3, c4, c5 = st.columns(5)
    length = c1.number_input("Length (m)", min_value=1.0, value=12.0, step=0.5)
    width = c2.number_input("Width (m)", min_value=1.0, value=9.0, step=0.5)
    height = c3.number_input("Floor height (m)", min_value=2.4, value=3.0, step=0.1)
    floors = c4.number_input("Floors", min_value=1, max_value=100, value=2, step=1)
    quality = c5.selectbox("Quality", QUALITY_LEVELS, index=1)
    submitted = st.form_submit_button("Calculate", use_container_width=True)

if not submitted and "last_estimate" not in st.session_state:
    st.info("Enter dimensions and click **Calculate** to generate an estimation.")
    st.stop()

if submitted:
    quantities = estimate(length, width, height, int(floors), quality)
    costs = cost_breakdown(quantities, settings)
    inputs = {"length": length, "width": width, "height": height,
              "floors": int(floors), "quality": quality}
    st.session_state["last_estimate"] = {
        "inputs": inputs, "quantities": quantities, "costs": costs,
    }

data = st.session_state["last_estimate"]
inputs, quantities, costs = data["inputs"], data["quantities"], data["costs"]
currency = settings["currency"]

# --- summary ---------------------------------------------------------------
labor = estimate_labor_cost(inputs["length"] * inputs["width"] * inputs["floors"] * 10.7639, settings)
grand_total = costs["total"] + labor
c1, c2, c3, c4 = st.columns(4)
c1.metric("Subtotal (materials)", format_currency(costs["subtotal"], currency))
c2.metric(f"Tax ({costs['tax_percent']}%)", format_currency(costs["tax_amount"], currency))
c3.metric("Estimated labor", format_currency(labor, currency))
c4.metric("Grand total", format_currency(grand_total, currency))

# --- table + chart ---------------------------------------------------------
rows = []
for key, meta in RATE_MAP.items():
    line = costs["lines"][key]
    rows.append({
        "Material": line["label"],
        "Quantity": format_number(line["quantity"]),
        "Rate": format_currency(line["rate"], currency),
        "Cost": format_currency(line["cost"], currency),
        "cost_val": line["cost"],
    })
df = pd.DataFrame(rows)
c_left, c_right = st.columns([1.2, 1])
with c_left:
    st.markdown("#### Material breakdown")
    st.dataframe(df.drop(columns=["cost_val"]), use_container_width=True, hide_index=True)
with c_right:
    st.markdown("#### Cost distribution")
    fig = px.pie(df, names="Material", values="cost_val", hole=0.5,
                 color_discrete_sequence=px.colors.sequential.Blues_r)
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

# --- save / export ---------------------------------------------------------
st.markdown("### Save & export")
projects = list_projects(user_id)
project_map = {0: "— none —"} | {p["id"]: f"#{p['id']} {p['name']}" for p in projects}
sel_pid = st.selectbox("Attach to project (optional)",
                       list(project_map.keys()),
                       format_func=lambda i: project_map[i])

col_s, col_p, col_x = st.columns(3)
with col_s:
    if st.button("💾 Save estimation", use_container_width=True):
        pid = sel_pid if sel_pid else None
        log_estimation(user_id, pid, inputs, quantities, costs, grand_total)
        st.success("Estimation saved to database.")

project_name = None
if sel_pid:
    project_name = next((p["name"] for p in projects if p["id"] == sel_pid), None)

pdf_bytes = estimation_pdf(inputs, quantities, costs,
                           company=settings["company_name"],
                           currency=currency, project_name=project_name)
xlsx_bytes = estimation_excel(inputs, quantities, costs, currency=currency)

with col_p:
    st.download_button("⬇️ Download PDF", pdf_bytes,
                       file_name="material_estimation.pdf",
                       mime="application/pdf", use_container_width=True)
with col_x:
    st.download_button("⬇️ Download Excel", xlsx_bytes,
                       file_name="material_estimation.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True)
