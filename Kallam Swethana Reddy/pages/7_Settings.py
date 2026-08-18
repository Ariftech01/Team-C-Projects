"""Settings — company info, material rates, labor, tax, currency."""
from __future__ import annotations

import streamlit as st

from database import init_db, get_settings, update_settings, reset_settings
from auth_ui import require_login, render_user_sidebar
from utils import inject_css, render_sidebar_brand, page_header

st.set_page_config(page_title="Settings • CIH", page_icon="⚙️", layout="wide")
init_db()
inject_css()
user = require_login()
user_id = user["id"]
settings = get_settings(user_id)
render_sidebar_brand(settings.get("company_name"))
render_user_sidebar()
page_header("Settings", "Your personal company details, material rates, labor cost, tax and currency.", icon="⚙️")
st.caption(f"These settings apply only to **{user['full_name']}**. Other users keep their own configuration.")

with st.form("settings_form"):
    st.markdown("### Company")
    c1, c2, c3 = st.columns(3)
    company_name = c1.text_input("Company name", value=settings["company_name"])
    currency = c2.selectbox(
        "Currency", ["INR", "USD", "EUR", "GBP", "AED"],
        index=["INR", "USD", "EUR", "GBP", "AED"].index(settings.get("currency", "INR")),
    )
    tax_percent = c3.number_input("Tax %", min_value=0.0, max_value=100.0,
                                  value=float(settings["tax_percent"]), step=0.5)

    st.markdown("### Labor")
    labor = st.number_input("Labor cost per sqft",
                            min_value=0.0, value=float(settings["labor_cost_per_sqft"]))

    st.markdown("### Material rates")
    m1, m2, m3 = st.columns(3)
    rate_bricks = m1.number_input("Bricks (per unit)", min_value=0.0,
                                   value=float(settings["rate_bricks_per_unit"]))
    rate_cement = m2.number_input("Cement (per 50 kg bag)", min_value=0.0,
                                   value=float(settings["rate_cement_per_bag"]))
    rate_sand = m3.number_input("Sand (per m³)", min_value=0.0,
                                 value=float(settings["rate_sand_per_cum"]))
    m4, m5, m6 = st.columns(3)
    rate_agg = m4.number_input("Aggregate (per m³)", min_value=0.0,
                                value=float(settings["rate_aggregate_per_cum"]))
    rate_steel = m5.number_input("Steel (per kg)", min_value=0.0,
                                  value=float(settings["rate_steel_per_kg"]))
    rate_concrete = m6.number_input("Concrete (per m³)", min_value=0.0,
                                     value=float(settings["rate_concrete_per_cum"]))
    m7, m8, m9 = st.columns(3)
    rate_mortar = m7.number_input("Mortar (per m³)", min_value=0.0,
                                   value=float(settings["rate_mortar_per_cum"]))
    rate_paint = m8.number_input("Paint (per sqft)", min_value=0.0,
                                  value=float(settings["rate_paint_per_sqft"]))
    rate_tiles = m9.number_input("Tiles (per sqft)", min_value=0.0,
                                  value=float(settings["rate_tiles_per_sqft"]))

    submitted = st.form_submit_button("Save settings", use_container_width=True)
    if submitted:
        update_settings({
            "company_name": company_name, "currency": currency,
            "tax_percent": tax_percent, "labor_cost_per_sqft": labor,
            "rate_bricks_per_unit": rate_bricks,
            "rate_cement_per_bag": rate_cement,
            "rate_sand_per_cum": rate_sand,
            "rate_aggregate_per_cum": rate_agg,
            "rate_steel_per_kg": rate_steel,
            "rate_concrete_per_cum": rate_concrete,
            "rate_mortar_per_cum": rate_mortar,
            "rate_paint_per_sqft": rate_paint,
            "rate_tiles_per_sqft": rate_tiles,
        }, user_id)
        st.success("Settings saved.")
        st.rerun()

st.markdown("---")
if st.button("Reset to defaults"):
    reset_settings(user_id)
    st.success("Your settings were reset to the platform defaults.")
    st.rerun()
