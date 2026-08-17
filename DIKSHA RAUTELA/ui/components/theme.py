"""Global CSS theme and base styling injected into Streamlit."""
from __future__ import annotations

import streamlit as st


LIGHT = {
    "primary":       "#1B3A5B",
    "primary_light": "#2E5A87",
    "accent":        "#0E7C7B",
    "bg":            "#F0F4F8",
    "surface":       "#FFFFFF",
    "surface_alt":   "#E8EFF6",
    "surface_2":     "#F7FAFC",
    "text":          "#17202C",
    "muted":         "#5F6B7A",
    "border":        "#C8D8E8",
    "sidebar_bg":    "#0D1926",
    "sidebar_text":  "#C8D8E8",
    "sidebar_muted": "#7A8FA0",
    "sidebar_active":"#FFFFFF",
    "sidebar_hover": "#1A2E40",
    "sidebar_accent":"#0E7C7B",
}

DARK = {
    "primary":       "#7DB7F0",
    "primary_light": "#A5CCF4",
    "accent":        "#4DD0C8",
    "bg":            "#0F1720",
    "surface":       "#17212D",
    "surface_alt":   "#1F2C3A",
    "surface_2":     "#19232F",
    "text":          "#E8EEF5",
    "muted":         "#A9B7C7",
    "border":        "#3A4A5D",
    "sidebar_bg":    "#0B1118",
    "sidebar_text":  "#C8D8E8",
    "sidebar_muted": "#6A7E90",
    "sidebar_active":"#FFFFFF",
    "sidebar_hover": "#1A2D3F",
    "sidebar_accent":"#4DD0C8",
}


def active_theme() -> dict[str, str]:
    return DARK if st.session_state.get("theme_mode", "Light") == "Dark" else LIGHT


def inject_css() -> None:
    t = active_theme()
    is_dark = st.session_state.get("theme_mode", "Light") == "Dark"
    btn_text = "#0D1926" if is_dark else "#FFFFFF"

    css = f"""
<style>
:root {{
  --cih-primary: {t["primary"]};
  --cih-primary-light: {t["primary_light"]};
  --cih-accent: {t["accent"]};
  --cih-bg: {t["bg"]};
  --cih-surface: {t["surface"]};
  --cih-surface-alt: {t["surface_alt"]};
  --cih-text: {t["text"]};
  --cih-muted: {t["muted"]};
  --cih-border: {t["border"]};
}}
/* ══════════════════════════════════════════════════════════════════════
   FONTS
══════════════════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  -webkit-font-smoothing: antialiased;
}}

/* ══════════════════════════════════════════════════════════════════════
   APP BACKGROUND
══════════════════════════════════════════════════════════════════════ */
.stApp {{
  background: {t["bg"]};
  color: {t["text"]};
}}

/* Global text colour — covers most Streamlit containers */
.stApp p, .stApp span, .stApp label, .stApp li, .stApp small,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stWidgetLabel"] p {{
  color: {t["text"]} !important;
}}

[data-testid="stCaptionContainer"] p,
[data-testid="stCaptionContainer"] span {{
  color: {t["muted"]} !important;
}}

/* Streamlit Header & Control Bar */
header[data-testid="stHeader"] {{
  background: transparent !important;
  z-index: 99 !important;
}}
header[data-testid="stHeader"] * {{
  color: {t["text"]} !important;
}}

/* Main content padding */
.main .block-container {{
  padding-top: 2rem;
  padding-bottom: 3rem;
  max-width: 1400px;
}}

/* ══════════════════════════════════════════════════════════════════════
   BORDERED CONTAINERS (global)
══════════════════════════════════════════════════════════════════════ */
div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stBorderedContainer"] {{
  background: {t["surface"]} !important;
  border: 1px solid {t["border"]} !important;
  border-radius: 12px !important;
  box-shadow: 0 1px 6px rgba(0,0,0,0.08) !important;
  transition: box-shadow 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
}}
div[data-testid="stVerticalBlockBorderWrapper"]:hover,
div[data-testid="stBorderedContainer"]:hover {{
  border-color: {t["primary_light"]} !important;
  box-shadow: 0 6px 24px rgba(0,0,0,0.13) !important;
  transform: translateY(-1px);
}}

/* ══════════════════════════════════════════════════════════════════════
   METRICS
══════════════════════════════════════════════════════════════════════ */
div[data-testid="stMetric"] {{
  background: linear-gradient(135deg, {t["surface"]}, {t["surface_alt"]});
  border: 1px solid {t["border"]};
  border-radius: 10px;
  padding: 0.85rem 1rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
}}
div[data-testid="stMetric"] * {{
  color: {t["text"]} !important;
}}

/* ══════════════════════════════════════════════════════════════════════
   FORM INPUTS
══════════════════════════════════════════════════════════════════════ */
.stTextInput input, .stNumberInput input, .stDateInput input,
.stTextArea textarea, div[data-baseweb="select"] > div {{
  background: {t["surface"]} !important;
  color: {t["text"]} !important;
  border-color: {t["border"]} !important;
  border-radius: 8px !important;
}}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {{
  color: {t["muted"]} !important;
  opacity: 1 !important;
}}

/* ══════════════════════════════════════════════════════════════════════
   DROPDOWNS / POPOVERS
══════════════════════════════════════════════════════════════════════ */
[data-baseweb="popover"], [data-baseweb="popover"] *,
[role="listbox"], [role="listbox"] *, [role="option"], [role="option"] * {{
  background-color: {t["surface"]} !important;
  color: {t["text"]} !important;
}}

/* ══════════════════════════════════════════════════════════════════════
   ALERTS
══════════════════════════════════════════════════════════════════════ */
div[data-testid="stAlert"] {{
  background: {t["surface_alt"]} !important;
  border: 1px solid {t["border"]} !important;
  border-radius: 10px !important;
}}
div[data-testid="stAlert"] * {{
  color: {t["text"]} !important;
}}

/* ══════════════════════════════════════════════════════════════════════
   TABS
══════════════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab"],
.stTabs [data-baseweb="tab"] * {{
  color: {t["text"]} !important;
}}
.stTabs [aria-selected="true"],
.stTabs [aria-selected="true"] * {{
  background: linear-gradient(135deg, {t["primary"]}, {t["accent"]}) !important;
  color: {btn_text} !important;
}}

/* ══════════════════════════════════════════════════════════════════════
   BUTTONS (global)
══════════════════════════════════════════════════════════════════════ */
.stButton > button {{
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.85rem;
  border: 1px solid {t["border"]};
  background: {t["surface"]};
  color: {t["text"]};
  transition: all 0.15s ease;
  letter-spacing: 0.01em;
}}
.stButton > button:hover {{
  background: linear-gradient(135deg, {t["primary"]}, {t["accent"]});
  border-color: {t["primary"]};
  color: #FFFFFF;
  box-shadow: 0 4px 12px rgba(0,0,0,0.18);
  transform: translateY(-1px);
}}
.stButton > button * {{ color: inherit !important; }}

/* ══════════════════════════════════════════════════════════════════════
   PROGRESS BARS
══════════════════════════════════════════════════════════════════════ */
.stProgress > div > div {{
  background: linear-gradient(90deg, {t["primary"]}, {t["accent"]});
  border-radius: 4px;
}}

/* ══════════════════════════════════════════════════════════════════════
   ─────────────────────────────────────────────
   SIDEBAR — PREMIUM ENTERPRISE NAVIGATION
   ─────────────────────────────────────────────
══════════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {{
  background: {t["sidebar_bg"]} !important;
  border-right: 1px solid rgba(255,255,255,0.06) !important;
}}
section[data-testid="stSidebar"] > div {{
  background: transparent !important;
  padding: 0 !important;
}}

/* Make everything in sidebar inherit correct colours */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
  color: {t["sidebar_text"]} !important;
}}

/* ── Brand block ── */
.sb-brand {{
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 1.25rem 1rem 0.75rem;
}}
.sb-brand-icon {{
  font-size: 1.5rem;
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, {t["primary"]}, {t["accent"]});
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}}
.sb-brand-text {{
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}}
.sb-brand-name {{
  font-size: 1rem !important;
  font-weight: 800 !important;
  color: #FFFFFF !important;
  letter-spacing: -0.3px;
}}
.sb-brand-tag {{
  font-size: 0.65rem !important;
  color: {t["sidebar_muted"]} !important;
  font-weight: 500;
  letter-spacing: 0.02em;
}}

/* ── Divider ── */
.sb-divider {{
  height: 1px;
  background: rgba(255,255,255,0.06);
  margin: 0.25rem 0.75rem;
}}

/* ── Nav container ── */
.sb-nav {{
  padding: 0.4rem 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}}

/* ── Nav items (HTML visual layer) ── */
.sb-nav-item {{
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.55rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s ease;
  position: relative;
  margin-bottom: -2.4rem;  /* overlap the Streamlit button below */
  # /*pointer-events: none;     let the button handle clicks */
  pointer-events: auto;
}}
.sb-nav-item:hover {{
  # background: {t["sidebar_hover"]};
  background: {t["sidebar_hover"]} !important;
    transform: translateX(3px);
    transition: all 0.18s ease;
}}
.sb-nav-active {{
  background: linear-gradient(135deg, rgba(14,124,123,0.25), rgba(27,58,91,0.35)) !important;
  border: 1px solid rgba(14,124,123,0.30);
}}
.sb-nav-icon {{
  font-size: 0.9rem;
  width: 20px;
  text-align: center;
  color: {t["sidebar_muted"]};
  flex-shrink: 0;
}}
.sb-nav-active .sb-nav-icon {{
  color: {t["sidebar_accent"]};
}}
.sb-nav-label {{
  font-size: 0.84rem !important;
  font-weight: 500;
  # color: {t["sidebar_text"]} !important;
  flex: 1;
}}
.sb-nav-active .sb-nav-label {{
  font-weight: 700;
  color: {t["sidebar_active"]} !important;
}}
.sb-nav-dot {{
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: {t["sidebar_accent"]};
  flex-shrink: 0;
}}

/* ── Hide the raw Streamlit sidebar buttons (replaced by HTML overlay) ── */
section[data-testid="stSidebar"] .stButton > button {{
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: transparent !important;
  padding: 0.55rem 0.75rem !important;
  border-radius: 8px !important;
  width: 100% !important;
  text-align: left !important;
  font-size: 0.84rem !important;
  font-weight: 500 !important;
  cursor: pointer !important;
  transition: background 0.15s ease !important;
  position: relative !important;
  z-index: 10 !important;
  margin-bottom: 0.15rem !important;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
  background: {t["sidebar_hover"]} !important;
  box-shadow: none !important;
  transform: none !important;
  color: transparent !important;
}}

/* Sidebar navigation buttons stay invisible */
section[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] .stButton > button:hover,
section[data-testid="stSidebar"] .stButton > button:focus,
section[data-testid="stSidebar"] .stButton > button:active {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: transparent !important;
    transform: none !important;
}}

/* Invisible click layer over custom navigation */
# section[data-testid="stSidebar"] .stButton {{
#     position: absolute;
#     width: 100%;
#     margin-top: -55px;
#     z-index: 10;
# }}

# section[data-testid="stSidebar"] .stButton button {{
#     width: 100%;
#     height: 55px;
#     opacity: 0;
#     cursor: pointer;
# }}

/* ── Bottom spacer to push controls down ── */
.sb-spacer {{
  flex: 1;
  min-height: 1rem;
}}

/* ── Control labels ── */
.sb-ctrl-lbl {{
  font-size: 0.68rem !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
  color: {t["sidebar_muted"]} !important;
  margin: 0.75rem 0.75rem 0.25rem !important;
  padding: 0 !important;
}}

/* ── Sidebar selectboxes ── */
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
  background: rgba(255,255,255,0.07) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: 8px !important;
  color: {t["sidebar_text"]} !important;
  font-size: 0.82rem !important;
}}
section[data-testid="stSidebar"] div[data-baseweb="select"] span {{
  color: {t["sidebar_text"]} !important;
}}

/* ── Version footer ── */
.sb-version {{
  font-size: 0.65rem !important;
  color: {t["sidebar_muted"]} !important;
  text-align: center !important;
  padding: 0.5rem 1rem 0.75rem !important;
  margin: 0 !important;
}}

/* ══════════════════════════════════════════════════════════════════════
   ─────────────────────────────────────────────
   DASHBOARD — HEADER
   ─────────────────────────────────────────────
══════════════════════════════════════════════════════════════════════ */
.dash-header {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1.1rem 1.5rem;
  # background: linear-gradient(135deg, {t["primary"]} 0%, #0D4060 55%, {t["accent"]} 100%);
  border-radius: 14px;
  border: 1px solid black
  margin-bottom: 1.25rem;
  position: relative;
  overflow: hidden;
  # box-shadow: 0 4px 20px rgba(0,0,0,0.18);
}}
.dash-header::before {{
  content: '';
  position: absolute;
  top: -50px; right: -50px;
  width: 180px; height: 180px;
  border-radius: 50%;
  background: rgba(255,255,255,0.05);
  pointer-events: none;
}}
.dash-header-left {{ flex: 1; min-width: 260px; }}
.dash-header-title {{
  font-size: 1.45rem !important;
  font-weight: 800 !important;
  color: {t["text"]} !important;
  margin: 0 0 0.2rem 0 !important;
  letter-spacing: -0.4px;
  line-height: 1.1;
}}
.dash-header-sub {{
  font-size: 0.8rem !important;
  color: {t["muted"]} !important;
  margin: 0 0 0.9rem 0 !important;
  font-weight: 400;
  line-height: 1.4;
  max-width: 560px;
}}
.dash-header-chips {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}}
.dash-chip {{
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.20);
  color: #FFFFFF !important;
  border-radius: 20px;
  padding: 0.2rem 0.7rem;
  font-size: 0.73rem;
  font-weight: 500;
  white-space: nowrap;
}}
.dash-chip-accent  {{ background: rgba(77,208,200,0.22); border-color: rgba(77,208,200,0.40); }}
.dash-chip-warn    {{ background: rgba(237,108,2,0.28);  border-color: rgba(237,108,2,0.50);  }}
.dash-chip-danger  {{ background: rgba(198,40,40,0.28);  border-color: rgba(198,40,40,0.50);  }}

/* Header right stats panel */
.dash-header-stats {{
  display: flex;
  align-items: center;
  background: rgba(255,255,255,0.10);
  border: 1px solid rgba(255,255,255,0.16);
  border-radius: 12px;
  padding: 0.5rem 0;
  backdrop-filter: blur(8px);
  flex-shrink: 0;
}}
.dash-hstat {{
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.35rem 1rem;
}}
.dash-hstat-val {{
  font-size: 0.95rem !important;
  font-weight: 700 !important;
  color: #FFFFFF !important;
  white-space: nowrap;
}}
.dash-hstat-lbl {{
  font-size: 0.6rem !important;
  color: {t["muted"]} !important;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  white-space: nowrap;
}}
.dash-hstat-divider {{
  width: 1px;
  background: rgba(255,255,255,0.16);
  align-self: stretch;
}}

/* ══════════════════════════════════════════════════════════════════════
   SECTION HEADERS
══════════════════════════════════════════════════════════════════════ */
.dash-section-hdr {{
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
  margin: 0.9rem 0 0.55rem;
  border-bottom: 1px solid {t["border"]};
  padding-bottom: 0.45rem;
}}
.dash-section-title {{
  font-size: 0.88rem !important;
  font-weight: 700 !important;
  color: {t["text"]} !important;
  letter-spacing: -0.1px;
}}
.dash-section-desc {{
  font-size: 0.75rem !important;
  color: {t["muted"]} !important;
  font-weight: 400;
}}
.dash-subsection-lbl {{
  font-size: 0.68rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.07em !important;
  color: {t["muted"]} !important;
  margin: 0.1rem 0 0.4rem !important;
}}

/* ══════════════════════════════════════════════════════════════════════
   KPI CARDS
══════════════════════════════════════════════════════════════════════ */
.kpi-card {{
  background: {t["surface"]};
  border: 1px solid {t["border"]};
  border-radius: 12px;
  padding: 1rem 1.1rem 0.85rem;
  box-shadow: 0 1px 6px rgba(0,0,0,0.07);
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
  min-height: 130px;
  display: flex;
  flex-direction: column;
}}
.kpi-card:hover {{
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  border-color: {t["primary_light"]};
}}
.kpi-card-top {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.55rem;
}}
.kpi-card-icon {{
  font-size: 1.1rem;
  color: {t["muted"]};
}}
/* Badge — inline styled from Python, no class needed */
.kpi-badge {{
  display: inline-block;
  border-radius: 10px;
  padding: 0.15rem 0.55rem;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  white-space: nowrap;
}}
.kpi-card-value {{
  font-size: 1.7rem !important;
  font-weight: 800 !important;
  color: {t["text"]} !important;
  margin: 0 0 0.1rem 0 !important;
  line-height: 1;
  letter-spacing: -1px;
}}
.kpi-card-label {{
  font-size: 0.7rem !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.07em !important;
  color: {t["muted"]} !important;
  margin: 0 0 0.2rem 0 !important;
}}
.kpi-card-sub {{
  font-size: 0.72rem !important;
  color: {t["muted"]} !important;
  margin: 0 !important;
  flex: 1;
  line-height: 1.35;
}}

/* ══════════════════════════════════════════════════════════════════════
   AI SUMMARY PANEL
══════════════════════════════════════════════════════════════════════ */
.ai-panel-header {{
  display: flex;
  align-items: center;
  gap: 0.55rem;
  padding: 0.5rem 0 0.65rem;
}}
.ai-panel-icon {{ font-size: 1.1rem; }}
.ai-panel-title {{
  font-size: 0.9rem !important;
  font-weight: 700 !important;
  color: {t["text"]} !important;
  flex: 1;
}}
.ai-panel-badge {{
  background: linear-gradient(135deg, {t["primary"]}, {t["accent"]});
  color: #fff !important;
  border-radius: 6px;
  padding: 0.15rem 0.5rem;
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}}

/* ══════════════════════════════════════════════════════════════════════
   PM COMMAND CENTER
══════════════════════════════════════════════════════════════════════ */
.pm-stat {{
  background: {t["surface"]};
  border: 1px solid {t["border"]};
  border-radius: 10px;
  padding: 0.7rem 0.9rem;
  text-align: center;
}}
.pm-stat-num {{
  font-size: 1.5rem !important;
  font-weight: 800 !important;
  display: block;
  line-height: 1;
  margin-bottom: 0.2rem;
}}
.pm-stat-lbl {{
  font-size: 0.65rem !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.06em !important;
  color: {t["muted"]} !important;
}}
.pm-action-card {{
  background: {t["surface"]};
  border: 1px solid {t["border"]};
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  height: 100%;
}}
.pm-action-card:hover {{
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.10);
}}
.pm-action-strip {{
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 4px;
  border-radius: 12px 0 0 12px;
}}
.pm-action-content {{
  padding: 0.8rem 0.9rem 0.8rem 1.1rem;
}}
.pm-action-top {{ margin-bottom: 0.35rem; }}
.pm-action-kind-badge {{
  font-size: 0.7rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.03em;
}}
.pm-action-project {{
  font-size: 0.88rem !important;
  font-weight: 700 !important;
  color: {t["text"]} !important;
  margin: 0 0 0.2rem 0 !important;
}}
.pm-action-desc {{
  font-size: 0.74rem !important;
  color: {t["muted"]} !important;
  margin: 0 !important;
  line-height: 1.4;
}}

/* ══════════════════════════════════════════════════════════════════════
   ATTENTION PROJECT CARDS
══════════════════════════════════════════════════════════════════════ */
.attn-card {{
  background: {t["surface"]};
  border: 1px solid {t["border"]};
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  box-shadow: 0 1px 5px rgba(0,0,0,0.07);
}}
.attn-card:hover {{
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.11);
}}
.attn-strip {{
  width: 5px;
  flex-shrink: 0;
}}
.attn-body {{
  flex: 1;
  padding: 1rem 1.1rem;
}}
.attn-row-top {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}}
.attn-name {{
  font-size: 0.95rem !important;
  font-weight: 700 !important;
  color: {t["text"]} !important;
  margin: 0 0 0.18rem 0 !important;
}}
.attn-meta {{
  font-size: 0.72rem !important;
  color: {t["muted"]} !important;
  margin: 0 !important;
  line-height: 1.4;
}}
.attn-progress-wrap {{ margin: 0.65rem 0 0.5rem; }}
.attn-progress-labels {{
  display: flex;
  justify-content: space-between;
  font-size: 0.68rem !important;
  color: {t["muted"]} !important;
  margin-bottom: 0.28rem;
}}
.attn-progress-track {{
  background: {t["surface_alt"]};
  border-radius: 3px;
  height: 5px;
  overflow: hidden;
}}
.attn-progress-fill {{
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, {t["primary"]}, {t["accent"]});
}}
.attn-tags {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  margin-top: 0.45rem;
}}

/* ══════════════════════════════════════════════════════════════════════
   ACTIVITY TIMELINE
══════════════════════════════════════════════════════════════════════ */
.tl-wrap {{
  background: {t["surface"]};
  border: 1px solid {t["border"]};
  border-radius: 12px;
  padding: 0.25rem 1rem;
}}
.tl-item {{
  display: flex;
  align-items: flex-start;
  gap: 0.7rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid {t["border"]};
}}
.tl-item:last-child {{ border-bottom: none; }}
.tl-dot {{
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: {t["accent"]};
  margin-top: 0.38rem;
  flex-shrink: 0;
  box-shadow: 0 0 0 3px rgba(14,124,123,0.15);
}}
.tl-body {{ flex: 1; min-width: 0; }}
.tl-event {{
  font-size: 0.8rem !important;
  font-weight: 600 !important;
  color: {t["text"]} !important;
  margin: 0 0 0.08rem 0 !important;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}}
.tl-meta {{
  font-size: 0.68rem !important;
  color: {t["muted"]} !important;
  margin: 0 !important;
}}
.tl-time {{
  font-size: 0.65rem !important;
  color: {t["muted"]} !important;
  white-space: nowrap;
  margin-top: 0.22rem;
  flex-shrink: 0;
}}

/* ══════════════════════════════════════════════════════════════════════
   MICRO-ANIMATIONS & PREMIUM POLISH
══════════════════════════════════════════════════════════════════════ */

/* Fade-in on load */
@keyframes fadeSlideUp {{
  from {{ opacity: 0; transform: translateY(12px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}

/* KPI metric tiles — hover elevation */
div[data-testid="stMetric"] {{
  animation: fadeSlideUp 0.28s ease both;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}}
div[data-testid="stMetric"]:hover {{
  transform: translateY(-3px) scale(1.015);
  box-shadow: 0 8px 28px rgba(14, 124, 123, 0.18) !important;
}}

/* Bordered card glow on hover */
div[data-testid="stVerticalBlockBorderWrapper"]:hover,
div[data-testid="stBorderedContainer"]:hover {{
  box-shadow: 0 10px 32px rgba(14, 124, 123, 0.15) !important;
  transition: box-shadow 0.2s ease;
}}

/* Buttons — smooth lift */
.stButton > button {{
  transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1) !important;
}}
.stButton > button:hover {{
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(14, 124, 123, 0.25) !important;
}}
.stButton > button:active {{
  transform: translateY(0) !important;
}}

/* Primary button — gradient sweep */
.stButton > button[kind="primary"] {{
  background: linear-gradient(135deg, {t["primary"]}, {t["accent"]}) !important;
  color: #FFFFFF !important;
  border: none !important;
}}
.stButton > button[kind="primary"]:hover {{
  background: linear-gradient(135deg, {t["accent"]}, {t["primary"]}) !important;
}}

/* Tab transitions */
.stTabs [data-baseweb="tab"] {{
  transition: background 0.2s ease, color 0.2s ease !important;
}}

/* Progress bar animated fill */
div[data-testid="stProgress"] > div > div {{
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}}

/* Sidebar nav item slide */
.sb-nav-item {{
  transition: background 0.15s ease, transform 0.15s ease !important;
}}
.sb-nav-item:hover {{
  transform: translateX(4px) !important;
}}

/* Expander smooth transition */
[data-testid="stExpander"] {{
  transition: all 0.2s ease;
}}

/* Plotly chart hover glow */
[data-testid="stPlotlyChart"] {{
  border-radius: 12px;
  overflow: hidden;
  transition: box-shadow 0.18s ease;
}}
[data-testid="stPlotlyChart"]:hover {{
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}}

/* Glassmorphism card helper class */
.glass-card {{
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 16px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}}
.glass-card:hover {{
  box-shadow: 0 16px 48px rgba(14,124,123,0.2);
  transform: translateY(-2px);
}}

/* Scrollbar styling */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{
  background: {t["border"]};
  border-radius: 3px;
}}
::-webkit-scrollbar-thumb:hover {{ background: {t["primary_light"]}; }}

/* Input focus ring */
.stTextInput input:focus,
.stTextArea textarea:focus {{
  border-color: {t["accent"]} !important;
  box-shadow: 0 0 0 3px rgba(14, 124, 123, 0.15) !important;
  outline: none !important;
}}

/* Alert / info box polish */
div[data-testid="stAlert"] {{
  border-radius: 10px !important;
  transition: box-shadow 0.18s ease;
}}
div[data-testid="stAlert"]:hover {{
  box-shadow: 0 4px 16px rgba(0,0,0,0.1) !important;
}}


/* Responsive layout for light and dark themes */
@media (max-width: 768px) {{
  .main .block-container {{ padding: 1rem 0.8rem 5rem; }}
  .dash-header {{ padding: 1rem; }}
  .dash-header-left {{ min-width: 0; }}
  .dash-header-stats {{ width: 100%; justify-content: space-around; overflow-x: auto; }}
  .dash-hstat {{ padding: 0.35rem 0.55rem; }}
  .dash-section-hdr {{ align-items: flex-start; flex-direction: column; gap: 0.15rem; }}
  div[data-testid="stHorizontalBlock"] {{ flex-wrap: wrap; gap: 0.65rem; }}
  div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {{ min-width: calc(50% - 0.4rem); flex: 1 1 calc(50% - 0.4rem); }}
}}
@media (max-width: 480px) {{
  div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {{ min-width: 100%; flex-basis: 100%; }}
  .dash-hstat-val {{ font-size: 0.8rem !important; }}
  .kpi-card {{ min-height: 112px; }}
}}</style>
"""
    st.markdown(css, unsafe_allow_html=True)
