import ollama
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import re
import base64

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Construction Intelligence Hub",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# GLOBAL STYLES
# force a light theme regardless of the visitor's OS/browser theme
# ============================================================
st.html("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root{
    --bg:#F4F5F9;
    --card:#FFFFFF;
    --ink:#14213D;
    --muted:#6B7280;
    --orange:#FF7A29;
    --orange-light:#FFF1E6;
    --green:#16A34A;
    --green-bg:#DCFCE7;
    --red:#DC2626;
    --red-bg:#FEE2E2;
    --amber:#B45309;
    --amber-bg:#FEF3C7;
    --blue:#2563EB;
    --blue-bg:#DBEAFE;
    --border:#ECEDF2;
}
/* Re-declare Streamlit's own theme variables so every native widget
   (buttons, inputs, uploaders, selects) follows OUR light palette no
   matter what theme/dark-mode the visitor's system is set to. */
:root, [data-theme="light"], [data-theme="dark"], .stApp{
    --primary-color:#FF7A29 !important;
    --background-color:#F4F5F9 !important;
    --secondary-background-color:#FFFFFF !important;
    --text-color:#14213D !important;
}
html, body, [class*="css"]{
    font-family:'Inter', sans-serif;
}
.stApp{
    background:var(--bg) !important;
    color:var(--ink) !important;
}
#MainMenu, footer, header{visibility:hidden;}
.block-container{
    padding-top:1.5rem;
    padding-bottom:5rem;
    max-width:1250px;
}

/* ---------- SIDEBAR ---------- */
section[data-testid="stSidebar"]{
    background:#14213D !important;
    border-right:1px solid #1E2A4A;
    /* redefine the theme vars again, scoped to the sidebar, so any
       descendant using var(--text-color) etc. picks up WHITE here
       instead of the dark navy used by the rest of the app */
    --text-color:#FFFFFF !important;
    --background-color:#14213D !important;
    --secondary-background-color:#1B2747 !important;
}
section[data-testid="stSidebar"] .block-container{
    padding-top:1.6rem;
}
section[data-testid="stSidebar"] *{
    color:#F4F6FB !important;
    opacity:1 !important;
    -webkit-text-fill-color:#F4F6FB !important;
}
.brand{
    display:flex;
    align-items:center;
    gap:10px;
    padding:0 0 18px 4px;
    border-bottom:1px solid #2A3760;
    margin-bottom:14px;
}
.brand-icon{
    font-size:26px;
}
.brand-title{
    font-size:17px;
    font-weight:800;
    line-height:1.1;
    color:#fff !important;
}
.brand-sub{
    font-size:11px;
    color:#8B95B8 !important;
    font-weight:500;
}
.side-user{
    display:flex;
    align-items:center;
    gap:10px;
    background:#1B2747;
    border-radius:12px;
    padding:10px 12px;
    margin-top:10px;
}
.side-avatar{
    width:34px;height:34px;border-radius:50%;
    background:linear-gradient(135deg,#FF7A29,#FFB067);
    display:flex;align-items:center;justify-content:center;
    font-weight:700;color:#fff;font-size:14px;
}
.side-user-name{font-size:13px;font-weight:700;color:#fff !important;}
.side-user-role{font-size:11px;color:#8B95B8 !important;}

div[data-testid="stSidebar"] div.stButton > button,
div[data-testid="stSidebar"] div.stButton > button *{
    background:transparent !important;
    border:1px solid transparent !important;
    color:#F4F6FB !important;
    -webkit-text-fill-color:#F4F6FB !important;
    opacity:1 !important;
    text-align:left;
    justify-content:flex-start;
    width:100%;
    padding:10px 14px;
    border-radius:10px;
    font-weight:600;
    font-size:14.5px;
    margin-bottom:4px;
    transition:all .15s ease;
}
div[data-testid="stSidebar"] div.stButton > button p{
    color:#F4F6FB !important;
    -webkit-text-fill-color:#F4F6FB !important;
    font-weight:600 !important;
}
div[data-testid="stSidebar"] div.stButton > button:hover,
div[data-testid="stSidebar"] div.stButton > button:hover *{
    background:#1E2A4A !important;
    border:1px solid #2A3760 !important;
    color:#FFFFFF !important;
    -webkit-text-fill-color:#FFFFFF !important;
}
div[data-testid="stSidebar"] div.stButton > button:focus{
    box-shadow:none !important;
}
.nav-active > button,
.nav-active > button *{
    background:linear-gradient(135deg,#FF7A29,#FF9354) !important;
    color:#fff !important;
    box-shadow:0 4px 12px rgba(255,122,41,.35);
}

/* ---------- CARDS ---------- */
.hero-title{
    font-size:34px;
    font-weight:800;
    color:var(--ink);
    margin-bottom:0;
}
.hero-date{
    color:var(--muted);
    font-size:14px;
    margin-top:2px;
    margin-bottom:20px;
}
.card{
    background:var(--card);
    border-radius:16px;
    padding:20px 22px;
    box-shadow:0 1px 3px rgba(20,33,61,.06);
    border:1px solid var(--border);
    height:100%;
}
.card-accent{
    border-left:4px solid var(--orange);
}
.metric-label{
    color:var(--muted);
    font-size:13.5px;
    font-weight:600;
    margin-bottom:6px;
}
.metric-value{
    color:var(--ink);
    font-size:32px;
    font-weight:800;
    line-height:1.1;
}
.badge{
    display:inline-block;
    padding:3px 10px;
    border-radius:20px;
    font-size:11.5px;
    font-weight:700;
    margin-top:8px;
}
.badge-green{background:var(--green-bg);color:var(--green);}
.badge-red{background:var(--red-bg);color:var(--red);}
.badge-amber{background:var(--amber-bg);color:var(--amber);}
.badge-blue{background:var(--blue-bg);color:var(--blue);}

.section-title{
    font-size:19px;
    font-weight:800;
    color:var(--ink);
    margin:26px 0 12px 0;
    display:flex;
    align-items:center;
    gap:8px;
}
.alert-box{
    border-radius:12px;
    padding:14px 18px;
    font-weight:600;
    font-size:14.5px;
    margin-bottom:10px;
    border:1px solid transparent;
}
.alert-high{background:var(--red-bg);color:#991B1B;border-color:#FCA5A5;}
.alert-med{background:var(--amber-bg);color:#92400E;border-color:#FCD34D;}
.alert-low{background:var(--blue-bg);color:#1E3A8A;border-color:#93C5FD;}

.qa-btn{
    background:var(--card);
    border:1px solid var(--border);
    border-radius:14px;
    padding:16px;
    text-align:center;
    font-weight:700;
    color:var(--ink);
    box-shadow:0 1px 3px rgba(20,33,61,.05);
}

.weather-temp{font-size:36px;font-weight:800;color:var(--ink);}
.divider-line{height:1px;background:var(--border);margin:6px 0 14px 0;}

/* project pill selector */
.proj-card{
    background:var(--card);
    border:1px solid var(--border);
    border-radius:14px;
    padding:16px 18px;
    box-shadow:0 1px 3px rgba(20,33,61,.05);
}
.proj-status{
    display:inline-block;
    padding:3px 10px;
    border-radius:20px;
    font-size:11px;
    font-weight:700;
}

/* progress bar custom */
.progress-outer{
    background:#EEF0F5;
    border-radius:10px;
    height:12px;
    width:100%;
    overflow:hidden;
}
.progress-inner{
    background:linear-gradient(90deg,#FF7A29,#FFB067);
    height:100%;
    border-radius:10px;
}

/* chat bubbles */
.chat-user{
    background:linear-gradient(135deg,#FF7A29,#FF9354);
    color:#fff;
    padding:10px 16px;
    border-radius:16px 16px 4px 16px;
    max-width:75%;
    margin-left:auto;
    margin-bottom:10px;
    font-size:14.5px;
    font-weight:500;
}
.chat-bot{
    background:#fff;
    color:var(--ink);
    padding:10px 16px;
    border-radius:16px 16px 16px 4px;
    max-width:75%;
    margin-right:auto;
    margin-bottom:10px;
    font-size:14.5px;
    border:1px solid var(--border);
    font-weight:500;
}

/* floating action button + side chat panel (targets st.container(key=...) classes) */
.st-key-fab_wrap{
    position:fixed;
    bottom:28px;
    right:32px;
    z-index:9999;
    width:60px;
}
.st-key-fab_wrap div[data-testid="stButton"] > button{
    width:60px !important;
    height:60px !important;
    border-radius:50% !important;
    background:linear-gradient(135deg,#FF7A29,#FF9354) !important;
    color:#fff !important;
    -webkit-text-fill-color:#fff !important;
    font-size:24px !important;
    box-shadow:0 8px 24px rgba(255,122,41,.45);
    border:3px solid #fff !important;
    animation:pulse 2.5s infinite;
    padding:0 !important;
    margin:0 !important;
}
.st-key-fab_wrap div[data-testid="stButton"] > button:hover{transform:scale(1.08);}
@keyframes pulse{
    0%{box-shadow:0 8px 24px rgba(255,122,41,.45);}
    50%{box-shadow:0 8px 30px rgba(255,122,41,.75);}
    100%{box-shadow:0 8px 24px rgba(255,122,41,.45);}
}
.st-key-chat_panel{
    position:fixed;
    top:0;
    right:0;
    height:100vh;
    width:400px;
    max-width:92vw;
    background:#FFFFFF !important;
    box-shadow:-8px 0 32px rgba(20,33,61,.22);
    z-index:9998;
    padding:18px 18px 10px 18px;
    overflow-y:auto;
    border-left:1px solid var(--border);
}
.st-key-chat_panel *{ color:var(--ink) !important; }
.st-key-chat_close button{
    background:#F4F5F9 !important;
    color:var(--ink) !important;
    border:1px solid var(--border) !important;
    border-radius:8px !important;
    padding:2px 10px !important;
    font-weight:700 !important;
}

h1,h2,h3,h4{color:var(--ink) !important;}
.stTabs [data-baseweb="tab-list"]{gap:4px;}
.stTabs [data-baseweb="tab"]{
    background:var(--card);
    border-radius:10px 10px 0 0;
    padding:8px 18px;
    font-weight:600;
}
div[data-testid="stFileUploader"]{
    background:var(--card);
    border-radius:14px;
    padding:10px;
    border:1px dashed #D8DCE8;
}
div[data-baseweb="select"]{border-radius:10px;}

/* ---------- FORCE LIGHT SURFACES EVERYWHERE (fixes dark-mode clashes) ---------- */
.stApp, .main, .block-container, div[data-testid="stAppViewContainer"]{
    background:var(--bg) !important;
    color:var(--ink) !important;
}
/* Main content */
.stMarkdown,
.stMarkdown *,
.stChatMessage,
.stChatMessage *,
.stChatMessage p,
.stChatMessage li,
.stChatMessage ul,
.stChatMessage ol,
.stChatMessage strong,
.stChatMessage em{
    color:#14213D !important;
}
div[data-testid="stMarkdownContainer"] p{ color:var(--ink) !important; }
.stMarkdown ul li{
    color:#14213D !important;
}

.stMarkdown ol li{
    color:#14213D !important;
}
[data-testid="stChatMessageContent"]{
    color:#14213D !important;
}

[data-testid="stChatMessageContent"] *{
    color:#14213D !important;
}
/* Buttons anywhere OUTSIDE the sidebar (quick actions, project cards,
   run-estimation, browse-files, etc.) — several selector variants are
   used together since Streamlit's internal testids vary by version. */
div[data-testid="stAppViewContainer"] div.stButton > button,
div[data-testid="stMain"] div.stButton > button,
section.main div.stButton > button,
.main div.stButton > button{
    background:#FFFFFF !important;
    color:var(--ink) !important;
    -webkit-text-fill-color:var(--ink) !important;
    opacity:1 !important;
    border:1px solid var(--border) !important;
    border-radius:12px !important;
    padding:14px 12px !important;
    font-weight:700 !important;
    font-size:14.5px !important;
    box-shadow:0 1px 3px rgba(20,33,61,.06);
    white-space:pre-line;
    line-height:1.5;
    transition:all .15s ease;
}
div[data-testid="stAppViewContainer"] div.stButton > button *,
div[data-testid="stMain"] div.stButton > button *,
section.main div.stButton > button *,
.main div.stButton > button *{
    color:inherit !important;
    -webkit-text-fill-color:inherit !important;
    font-weight:700 !important;
}
div[data-testid="stAppViewContainer"] div.stButton > button:hover,
div[data-testid="stMain"] div.stButton > button:hover{
    border:1px solid var(--orange) !important;
    background:var(--orange-light) !important;
    color:var(--orange) !important;
}
div[data-testid="stAppViewContainer"] div.stButton > button:hover *,
div[data-testid="stMain"] div.stButton > button:hover *{
    color:var(--orange) !important;
    -webkit-text-fill-color:var(--orange) !important;
}
div[data-testid="stAppViewContainer"] div.stButton > button:focus:not(:active),
div[data-testid="stMain"] div.stButton > button:focus:not(:active){
    color:var(--ink) !important;
    border:1px solid var(--orange) !important;
}
/* the sidebar's own (more specific) button rules defined above always
   win over these general ones, so the sidebar keeps its dark styling */

/* primary CTA buttons (Run AI Estimation / Run Safety Scan) */
div[data-testid="stAppViewContainer"] div.stButton > button[kind="primary"],
div[data-testid="stMain"] div.stButton > button[kind="primary"]{
    background:linear-gradient(135deg,#FF7A29,#FF9354) !important;
    color:#fff !important;
    -webkit-text-fill-color:#fff !important;
    border:none !important;
}
div[data-testid="stAppViewContainer"] div.stButton > button[kind="primary"] *,
div[data-testid="stMain"] div.stButton > button[kind="primary"] *{
    color:#fff !important;
    -webkit-text-fill-color:#fff !important;
}

/* Native widgets: selects, sliders, inputs, checkboxes, uploaders, tables */
div[data-baseweb="select"] > div{
    background:#FFFFFF !important;
    color:var(--ink) !important;
    border-color:var(--border) !important;
}
div[data-baseweb="select"] *{ color:var(--ink) !important; }
div[data-baseweb="popover"] li{ color:var(--ink) !important; background:#FFFFFF !important; }
input, textarea{
    background:#FFFFFF !important;
    color:var(--ink) !important;
}
div[data-testid="stNumberInput"] input, div[data-testid="stTextInput"] input{
    background:#FFFFFF !important;
    color:var(--ink) !important;
    border-radius:10px !important;
}
div[data-testid="stFileUploaderDropzone"]{
    background:#FAFBFD !important;
    color:var(--muted) !important;
}
div[data-testid="stFileUploaderDropzone"] *{ color:var(--muted) !important; }
div[data-testid="stFileUploaderDropzoneInstructions"] span{ color:var(--ink) !important; }
/* the small "Browse files" button inside the uploader */
div[data-testid="stFileUploaderDropzone"] button{
    background:#FFFFFF !important;
    border:1px solid var(--border) !important;
    border-radius:8px !important;
}
div[data-testid="stFileUploaderDropzone"] button,
div[data-testid="stFileUploaderDropzone"] button *{
    color:var(--ink) !important;
    -webkit-text-fill-color:var(--ink) !important;
    opacity:1 !important;
    font-weight:700 !important;
}
[data-testid="stCheckbox"] label, [data-testid="stRadio"] label{ color:var(--ink) !important; }
[data-testid="stSlider"] label{ color:var(--ink) !important; }
[data-baseweb="tag"]{ background:var(--orange) !important; color:#fff !important; }
div[data-testid="stDataFrame"]{ background:#FFFFFF !important; border-radius:10px; }
[data-testid="stMetricValue"], [data-testid="stMetricLabel"]{ color:var(--ink) !important; }
.stTabs [data-baseweb="tab"] p{ color:var(--ink) !important; }
.stTabs [aria-selected="true"]{ background:var(--orange-light) !important; }
.stTabs [aria-selected="true"] p{ color:var(--orange) !important; }
[data-testid="stChatInput"] textarea{ background:#FFFFFF !important; color:var(--ink) !important; }
[data-testid="stExpander"]{ background:#FFFFFF !important; border-radius:12px; border:1px solid var(--border); }
</style>
""")

# ============================================================
# MOCK DATA
# ============================================================
PROJECTS = {
    "Tower A — Residential Complex": {
        "type": "Residential Tower",
        "location": "Sector 12, Site North",
        "progress": 64,
        "status": "On Track",
        "workers": {"on_site": 22, "total": 25},
        "budget_used": 58,
        "start": "2026-01-12",
        "end": "2026-11-30",
        "materials": {
            "Cement (bags)": {"required": 4200, "in_stock": 120, "unit": "bags"},
            "Steel (tons)": {"required": 180, "in_stock": 64, "unit": "tons"},
            "Bricks (nos)": {"required": 320000, "in_stock": 96000, "unit": "nos"},
            "Sand (cu.m)": {"required": 900, "in_stock": 410, "unit": "cu.m"},
        },
        "equipment": [
            {"name": "Tower Crane TC-1", "status": "Active", "hours": 812},
            {"name": "Concrete Mixer M-3", "status": "Active", "hours": 420},
            {"name": "Excavator EX-2", "status": "Idle", "hours": 210},
            {"name": "Scaffolding Set A", "status": "Active", "hours": "-"},
        ],
        "timeline": [
            {"phase": "Foundation", "start": "2026-01-12", "end": "2026-03-01", "status": "Done"},
            {"phase": "Structure (Floors 1-10)", "start": "2026-03-02", "end": "2026-06-15", "status": "Done"},
            {"phase": "Roof Slab & Floors 11-18", "start": "2026-06-16", "end": "2026-08-20", "status": "In Progress"},
            {"phase": "MEP & Finishing", "start": "2026-08-21", "end": "2026-10-30", "status": "Pending"},
            {"phase": "Handover", "start": "2026-10-31", "end": "2026-11-30", "status": "Pending"},
        ],
        "docs": ["Structural_Drawings_RevC.pdf", "Site_Survey_Report.pdf", "Safety_Permit_Aug2026.pdf"],
    },
    "Zone B — Commercial Plaza": {
        "type": "Commercial Complex",
        "location": "Sector 8, Site East",
        "progress": 38,
        "status": "Needs Attention",
        "workers": {"on_site": 18, "total": 20},
        "budget_used": 41,
        "start": "2026-03-01",
        "end": "2027-01-15",
        "materials": {
            "Cement (bags)": {"required": 3100, "in_stock": 640, "unit": "bags"},
            "Steel (tons)": {"required": 140, "in_stock": 88, "unit": "tons"},
            "Glass Panels (nos)": {"required": 850, "in_stock": 210, "unit": "nos"},
            "Sand (cu.m)": {"required": 700, "in_stock": 300, "unit": "cu.m"},
        },
        "equipment": [
            {"name": "Concrete Pump CP-1", "status": "Active", "hours": 260},
            {"name": "Tower Crane TC-2", "status": "Active", "hours": 305},
            {"name": "Boom Lift BL-1", "status": "Maintenance", "hours": 150},
        ],
        "timeline": [
            {"phase": "Foundation", "start": "2026-03-01", "end": "2026-04-20", "status": "Done"},
            {"phase": "Steel Frame Erection", "start": "2026-04-21", "end": "2026-07-10", "status": "In Progress"},
            {"phase": "Concrete Pour Zone B", "start": "2026-08-05", "end": "2026-08-05", "status": "Today"},
            {"phase": "Facade & Glazing", "start": "2026-09-01", "end": "2026-11-15", "status": "Pending"},
            {"phase": "Interior Fit-out", "start": "2026-11-16", "end": "2027-01-15", "status": "Pending"},
        ],
        "docs": ["Zone_B_Structural_Plan.pdf", "Glazing_Spec_Sheet.pdf"],
    },
    "Metro Line Extension — Phase 2": {
        "type": "Metro / Infrastructure",
        "location": "Corridor 4, Underground Section",
        "progress": 22,
        "status": "On Track",
        "workers": {"on_site": 7, "total": 7},
        "budget_used": 19,
        "start": "2026-05-01",
        "end": "2028-02-28",
        "materials": {
            "Concrete (cu.m)": {"required": 52000, "in_stock": 9800, "unit": "cu.m"},
            "Steel (tons)": {"required": 6200, "in_stock": 1450, "unit": "tons"},
            "Tunnel Segments (nos)": {"required": 1800, "in_stock": 260, "unit": "nos"},
        },
        "equipment": [
            {"name": "TBM Unit-1 (Tunnel Boring)", "status": "Active", "hours": 1900},
            {"name": "Segment Erector SE-1", "status": "Active", "hours": 900},
            {"name": "Ventilation Rig VR-1", "status": "Active", "hours": 1500},
        ],
        "timeline": [
            {"phase": "Site Prep & Shaft", "start": "2026-05-01", "end": "2026-07-15", "status": "Done"},
            {"phase": "Tunnel Boring Section 1", "start": "2026-07-16", "end": "2026-12-01", "status": "In Progress"},
            {"phase": "Tunnel Boring Section 2", "start": "2026-12-02", "end": "2027-05-01", "status": "Pending"},
            {"phase": "Track & Systems", "start": "2027-05-02", "end": "2027-11-01", "status": "Pending"},
            {"phase": "Testing & Commissioning", "start": "2027-11-02", "end": "2028-02-28", "status": "Pending"},
        ],
        "docs": ["Tunnel_Alignment_Drawings.pdf", "Geotech_Survey.pdf"],
    },
}

ALERTS = [
    {"level": "high", "text": "⚠️ Cement stock low at Tower A — 120 bags left (reorder level: 150)"},
    {"level": "med", "text": "⚠️ Rain expected tomorrow afternoon — plan concrete pours before noon"},
    {"level": "high", "text": "⚠️ Worker entered restricted zone near crane at 10:42 AM — Tower A"},
]

# ============================================================
# LOCAL AI (Ollama + llama3.2:1b)
# ============================================================
OLLAMA_MODEL = "llama3.2:1b"

SYSTEM_PROMPT_BASE = """You are ConstructAI, the AI assistant embedded in the Construction Intelligence Hub app used by site managers, engineers and contractors.

Your expertise: material estimation, BOQ analysis, safety analysis, construction planning, project monitoring, cost estimation, IS codes, and site documentation.

Rules:
1. Never invent precise engineering values you were not given — state assumptions clearly.
2. Use metric units.
3. Be concise and practical — 3 to 5 sentences unless the user asks for more detail.
4. If project data is supplied below, base your answer on it first before general knowledge.
5. You ONLY discuss construction, civil engineering, project management, materials, cost estimation, safety, and related site-management topics (plus basic greetings/small talk). If a request falls outside that scope, politely decline and redirect the user back to construction topics — do not answer it.
"""

def build_project_context():
    """Turn the mock PROJECTS/ALERTS data into a short text block the LLM can read."""
    lines = []
    for name, p in PROJECTS.items():
        mats = ", ".join(f"{m} {d['in_stock']}/{d['required']} {d['unit']}" for m, d in p["materials"].items())
        lines.append(
            f"- {name}: {p['progress']}% complete, status {p['status']}, "
            f"workers {p['workers']['on_site']}/{p['workers']['total']} on site, "
            f"budget used {p['budget_used']}%. Materials — {mats}."
        )
    alerts_txt = " | ".join(a["text"].replace("⚠️ ", "") for a in ALERTS)
    return (
        "CURRENT PROJECT DATA:\n" + "\n".join(lines) +
        f"\n\nACTIVE ALERTS: {alerts_txt}" +
        "\n\nWEATHER: Sunny, 31°C, 58% humidity, rain expected tomorrow afternoon."
    )

def query_llm(user_prompt, extra_system=""):
    """
    Calls the local Ollama server running llama3.2:1b.
    Returns (answer_text, error_message) — exactly one of the two is not None.
    Never raises: if Ollama isn't running or the model isn't pulled, this
    returns (None, "<error>") so callers can fall back gracefully.
    """
    try:
        system = SYSTEM_PROMPT_BASE + "\n\n" + build_project_context()
        if extra_system:
            system += "\n\n" + extra_system
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response["message"]["content"].strip(), None
    except Exception as e:
        return None, str(e)

# ============================================================
# GUARDRAIL — restrict the assistant to construction-related topics
# ============================================================
# Tier 1: a fast, cheap keyword allow-list. Catches the large majority of
# real questions instantly, without spending a model call on the obvious case.
CONSTRUCTION_KEYWORDS = [
    "construct", "civil", "cement", "concrete", "steel", "brick", "sand", "aggregate",
    "scaffold", "crane", "excavat", "foundation", "structur", "blueprint", "site",
    "project", "material", "budget", "cost", "estimat", "procure", "contractor",
    "engineer", "architect", "safety", "ppe", "hazard", "violation", "worker",
    "labor", "labour", "timeline", "schedule", "milestone", "permit", "inspection",
    "survey", "plan", "drawing", "tunnel", "bridge", "road", "highway", "metro",
    "building", "floor", "apartment", "house", "residential", "commercial",
    "plumbing", "electrical", "hvac", "wiring", "is code", "boq", "rebar",
    "formwork", "curing", "mortar", "plaster", "tile", "roof", "slab", "beam",
    "column", "pile", "girder", "insulation", "waterproof", "demolition",
    "renovation", "renovat", "subcontractor", "vendor", "supplier", "equipment",
    "machinery", "bulldozer", "excavator", "workforce", "shift", "invoice",
    "quotation", "tender", "warranty", "defect", "handover", "occupancy",
    "zoning", "tower", "crew", "helmet", "vest", "harness", "masonry",
    "hello", "hi", "hey", "thanks", "thank you",
    # Common short follow-ups within an ongoing chat — these have no
    # construction vocabulary of their own, and the LLM classifier proved
    # unreliable at recognizing them as continuations even with recent
    # chat history included in its prompt (small models are inconsistent
    # at that kind of contextual reasoning). Allowing them outright is low
    # risk: query_llm() always answers grounded in the ConstructAI persona
    # and mock project data anyway, so even a bare "give me a report" gets
    # a construction-relevant answer, never a genuinely off-topic one.
    "report", "deadline", "summary", "summarize", "explain", "detail",
    "elaborate", "update", "status", "overview", "insight", "analysis",
    "analyze", "clarify", "more info", "tell me more",
]

def _keyword_hits_construction(text):
    t = text.lower()
    return any(kw in t for kw in CONSTRUCTION_KEYWORDS)

def is_construction_related(query):
    """
    Two-tier guardrail. Returns (allowed: bool, reason: str) — reason is
    purely for debugging/transparency, never shown to the end user directly.

    Tier 1 (keyword allow-list) handles the obvious majority instantly.
    Tier 2 (LLM classifier) handles anything ambiguous that doesn't match
    a keyword. The classifier is given the last few turns of conversation
    as context — a short follow-up like "give me a report" or "explain
    more" has no construction keywords of its own and looks unrelated in
    isolation, but is obviously a continuation of an on-topic conversation
    once the preceding turns are visible. Classifying each message with no
    memory of what came before was causing exactly that kind of false
    rejection.

    If the classifier itself is unreachable or returns something
    unparseable, this fails OPEN (allows the message through) rather than
    silently blocking a possibly-legitimate question — the main query_llm()
    call right after this will hit the same connectivity problem anyway and
    fall back through its own error handling.
    """
    if _keyword_hits_construction(query):
        return True, "keyword-match"

    history = st.session_state.get("chat_history", [])
    recent = history[-6:]
    context_lines = [f'{"User" if m["role"] == "user" else "Assistant"}: {m["text"]}' for m in recent]
    context_block = ("Recent conversation so far:\n" + "\n".join(context_lines) + "\n\n") if context_lines else ""

    classifier_prompt = (
        "You are a lenient topic classifier for a construction-industry assistant. "
        "Reply with exactly one word — YES or NO — and nothing else.\n\n"
        f"{context_block}"
        "Is the NEW message on-topic for a construction assistant? Answer YES if it is "
        "about construction, civil engineering, building/site management, materials, "
        "cost estimation, safety, a construction project, simple greetings/small talk, "
        "OR if it's a short follow-up request (like 'give me a report', 'summarize that', "
        "'explain more', 'what about the other one') that makes sense as a continuation "
        "of the conversation above. Answer NO only if the new message is clearly about "
        "something with no construction connection at all (e.g. recipes, sports scores, "
        "general trivia unrelated to the conversation).\n\n"
        f"New message: \"{query}\""
    )
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": classifier_prompt}],
        )
        verdict = response["message"]["content"].strip().upper()
        if verdict.startswith("YES"):
            return True, "llm-classifier-yes"
        if verdict.startswith("NO"):
            return False, "llm-classifier-no"
        return True, "unclear-classifier-fail-open"
    except Exception:
        return True, "classifier-unreachable-fail-open"


GUARDRAIL_REFUSAL = (
    "🛡️ I'm ConstructAI — I'm built to help with construction, safety, materials, "
    "cost estimation, and project planning questions only. That looks outside my "
    "scope, so I can't help with it here. Try asking me about your projects, "
    "materials, safety, or cost estimates instead."
)

def guardrail_refusal_upload(caption_or_excerpt):
    """Refusal message for an uploaded file/photo that the guardrail rejected,
    including what the model actually saw/read so the rejection is transparent
    rather than a black box."""
    snippet = (caption_or_excerpt or "").strip().replace("\n", " ")
    if len(snippet) > 220:
        snippet = snippet[:220].rsplit(" ", 1)[0] + "…"
    return (
        "🛡️ This doesn't look like construction-related content, so I won't run a "
        "construction analysis on it. I'm built to analyze construction site photos, "
        "plans, blueprints, and project documents only.\n\n"
        f"*What I actually saw/read: \"{snippet}\"*"
    )

def log_guardrail(label, allowed, reason):
    st.session_state.setdefault("guardrail_log", []).append({"msg": label, "allowed": allowed, "reason": reason})

def check_llm_status():
    """Lightweight one-time check (cached in session_state) of whether
    Ollama is reachable and the model is pulled — used for the sidebar badge."""
    if "llm_status" in st.session_state:
        return st.session_state.llm_status
    try:
        resp = ollama.list()
        try:
            names = [m["model"] for m in resp["models"]]
        except (TypeError, KeyError):
            names = [getattr(m, "model", "") for m in getattr(resp, "models", [])]
        status = "online" if any(OLLAMA_MODEL.split(":")[0] in n for n in names) else "model_missing"
    except Exception:
        status = "offline"
    st.session_state.llm_status = status
    return status

# ---- Vision model (for real photo/plan analysis) ----
VISION_MODEL = "moondream"  # small (~1.7GB) CPU-friendly vision model — swap here if you pull a different one

def _vision_chat(messages):
    """One raw attempt at ollama.chat() for the vision model."""
    response = ollama.chat(model=VISION_MODEL, messages=messages)
    return response["message"]["content"].strip()

def query_vision_llm(image_bytes, user_prompt, extra_system=""):
    """
    Sends an actual image to a local vision model via Ollama.
    Returns (answer_text, error_message) — same contract as query_llm().
    This is what makes Safety Analysis and image-plan analysis "real" —
    query_llm() alone can never see an image, only text.

    Vision models pulled through Ollama vary in what message shape they'll
    accept (some reject a separate "system" message; some want base64 text
    instead of raw bytes). To be robust across models/ollama versions this
    tries a couple of shapes instead of assuming one.
    """
    guidance = "Only describe what is actually visible in the image — never invent details."
    if extra_system:
        guidance += " " + extra_system
    b64_image = base64.b64encode(image_bytes).decode("utf-8")

    attempts = [
        # 1) no system role, base64 string image — most broadly compatible
        [{"role": "user", "content": f"{guidance}\n\n{user_prompt}", "images": [b64_image]}],
        # 2) with a system role, base64 string image
        [
            {"role": "system", "content": guidance},
            {"role": "user", "content": user_prompt, "images": [b64_image]},
        ],
        # 3) no system role, raw bytes image (older/newer client variants)
        [{"role": "user", "content": f"{guidance}\n\n{user_prompt}", "images": [image_bytes]}],
    ]
    last_err = None
    for messages in attempts:
        try:
            text = _vision_chat(messages)
            if text:
                return text, None
        except Exception as e:
            last_err = str(e)
    return None, last_err or "Vision model returned an empty response."

def classify_description(description, extra_note=""):
    """
    Shared content guardrail for uploads (images and PDFs). Takes text that
    has ALREADY been produced by a vision or text model — a photo
    description, a plan reading, extracted PDF text — and asks llama3.2:1b
    (which follows instructions far more reliably than a small vision model
    like moondream) whether it plausibly relates to construction.

    IMPORTANT: this makes a RAW ollama.chat() call, deliberately bypassing
    query_llm(). query_llm() always injects the full ConstructAI persona
    system prompt plus the mock project data (Tower A, cement stock,
    workers, etc.) — appropriate for answering questions, but disastrous
    for a neutral classifier, since it primes the model with pages of
    construction context immediately before asking it to judge unrelated
    content. That contamination was the actual cause of a real bug: a
    plain code-editor screenshot got waved through as "construction
    content" because the model had just been told, in the same call, that
    it's a construction expert looking at Tower A's data. Removing that
    priming and keeping this call minimal and neutral fixes it.

    Returns (allowed: bool, reason: str).
    - A clean YES is allowed; a clean NO is blocked.
    - Anything that doesn't parse as a clean YES/NO fails CLOSED (blocked).
      An earlier version failed open here, on the theory that a working
      classifier rarely returns something unparseable — but combined with
      the contamination bug above, "fail open on anything unclear" plus "a
      contaminated model that leans YES" meant almost nothing was actually
      being blocked. Failing closed here is the safety margin while the
      classifier itself is a small, imperfect model.
    """
    classify_prompt = (
        "The following text is a factual description of an uploaded image or "
        "document, produced by a separate AI model:\n\n"
        f"\"{description}\"\n\n"
        "Decide whether this description genuinely indicates construction-related "
        "content. Answer YES only if it clearly describes one of: a construction "
        "site or building/civil-engineering work in progress, construction "
        "machinery or equipment, construction materials (cement, steel, bricks, "
        "scaffolding, rebar), a building/architectural floor plan, blueprint, or "
        "technical construction drawing, or people wearing PPE/hard hats/hi-vis "
        "vests doing site work.\n\n"
        "Answer NO for anything else, including (but not limited to): computer, "
        "phone, or TV screens, code, software, apps, or websites; ordinary indoor "
        "office/home scenes with no site context; documents unrelated to "
        "construction (resumes, recipes, articles); food; pets or animals; people "
        "or portraits with no site/work context; nature or wildlife; vehicles with "
        "no construction connection. When genuinely unsure, answer NO."
        + (f"\n\n{extra_note}" if extra_note else "")
        + "\n\nReply with exactly one word: YES or NO."
    )
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": classify_prompt}],
        )
        result = response["message"]["content"].strip()
    except Exception:
        return True, "content-guardrail-classifier-unreachable-fail-open"
    if not result:
        return True, "content-guardrail-classifier-unreachable-fail-open"
    verdict = result.strip().upper()
    if verdict.startswith("YES"):
        return True, "content-guardrail-yes"
    if verdict.startswith("NO"):
        return False, "content-guardrail-no"
    return False, "content-guardrail-unclear-fail-closed"




def extract_pdf_text(file_bytes, max_chars=6000):
    """Best-effort text extraction from an uploaded PDF, for feeding to the text model.
    Returns None if extraction fails or the PDF has no extractable text (e.g. scanned images)."""
    try:
        from pypdf import PdfReader
        import io
        reader = PdfReader(io.BytesIO(file_bytes))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        text = text.strip()
        return text[:max_chars] if text else None
    except Exception:
        return None

def check_vision_status():
    """Same idea as check_llm_status() but for the vision model used by
    Safety Analysis / image-plan analysis in Doc Analyzer."""
    if "vision_status" in st.session_state:
        return st.session_state.vision_status
    try:
        resp = ollama.list()
        try:
            names = [m["model"] for m in resp["models"]]
        except (TypeError, KeyError):
            names = [getattr(m, "model", "") for m in getattr(resp, "models", [])]
        status = "online" if any(VISION_MODEL in n for n in names) else "model_missing"
    except Exception:
        status = "offline"
    st.session_state.vision_status = status
    return status

def bot_reply_fallback(msg):
    """Rule-based backup used only if the local LLM can't be reached."""
    msg_l = msg.lower()
    if "cement" in msg_l or "material" in msg_l or "stock" in msg_l:
        return ("Tower A has 120 bags of cement in stock against a requirement of 4200 bags "
                "(reorder level 150). I recommend placing an order today to avoid delays on the roof slab work.")
    if "safety" in msg_l or "violation" in msg_l:
        return ("Current overall safety score is 92/100. One violation was flagged this morning at 10:42 AM — "
                "a worker entered the restricted zone near the Tower A crane. Supervisor has been notified.")
    if "worker" in msg_l or "workforce" in msg_l or "labour" in msg_l or "labor" in msg_l:
        return "47 out of 52 registered workers are on site today across all 3 active projects."
    if "progress" in msg_l or "status" in msg_l:
        lines = [f"- {name}: {p['progress']}% complete ({p['status']})" for name, p in PROJECTS.items()]
        return "Here's the current progress across projects:\n" + "\n".join(lines)
    if "weather" in msg_l or "rain" in msg_l:
        return "It's sunny, 31°C right now with 58% humidity. Rain is expected tomorrow afternoon — plan concrete pours before noon."
    if "cost" in msg_l or "budget" in msg_l:
        return "Budget utilization: Tower A 58%, Zone B 41%, Metro Line Phase 2 19%. Use the Doc Analyzer page for new cost estimates."
    if "hello" in msg_l or "hi" in msg_l:
        return "Hello! I can help with material stock, safety alerts, workforce numbers, project progress, and cost estimates. What would you like to know?"
    return ("I can help with material stock, safety alerts, workforce, project progress, weather, and budgets. "
            "Try asking: 'How much cement is left at Tower A?' or 'What's the safety score today?'")

def bot_reply(msg):
    """Main chat entry point: gates every message through the guardrail first,
    then tries the local llama3.2:1b model, and only falls back to the
    rule-based answers if Ollama is unreachable."""
    allowed, reason = is_construction_related(msg)
    log_guardrail(msg, allowed, reason)
    if not allowed:
        return GUARDRAIL_REFUSAL

    text, err = query_llm(msg)
    if text:
        return text
    return (bot_reply_fallback(msg) +
            "\n\n*(Local AI model unreachable — showing a quick fallback answer. "
            "Run `ollama serve` and make sure `llama3.2:1b` is pulled to enable full AI responses.)*")

# ============================================================
# SESSION STATE
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "bot", "text": "Hi Site Manager 👋 I'm your AI assistant. Ask me about material stock, safety, or project progress."}
    ]
if "selected_project" not in st.session_state:
    st.session_state.selected_project = list(PROJECTS.keys())[0]
if "show_chat" not in st.session_state:
    st.session_state.show_chat = False

# ============================================================
# SIDEBAR NAV
# ============================================================
with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div class="brand-icon">🏗️</div>
        <div>
            <div class="brand-title">Construction<br>Intelligence Hub</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    nav_items = [
        ("Dashboard", "📊  Dashboard"),
        ("Project Monitoring", "🏢  Project Monitoring"),
        ("Doc Analyzer", "📄  Doc Analyzer"),
        ("Material Estimator", "🧮  Material Estimator"),
        ("Safety Analysis", "🦺  Safety Analysis"),
        ("AI Assistant", "🤖  AI Assistant"),
    ]
    for key, label in nav_items:
        active = st.session_state.page == key
        wrapper_class = "nav-active" if active else ""
        st.markdown(f'<div class="{wrapper_class}">', unsafe_allow_html=True)
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.page = key
            st.session_state.show_chat = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="margin-top:22px;"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="side-user">
        <div class="side-avatar">SM</div>
        <div>
            <div class="side-user-name">Site Manager</div>
            <div class="side-user-role">Field Operations</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _status_map = {
        "online": ("🟢", "connected"),
        "model_missing": ("🟡", "not pulled"),
        "offline": ("🔴", "unreachable"),
    }
    _llm_dot, _llm_label = _status_map.get(check_llm_status(), ("⚪", "unknown"))
    _vis_dot, _vis_label = _status_map.get(check_vision_status(), ("⚪", "unknown"))
    st.markdown(f"""
    <div style="margin-top:10px;padding:8px 12px;background:#1B2747;border-radius:10px;
                font-size:11.5px;color:#C6CCE3;line-height:1.9;">
        <div>{_llm_dot} Text — llama3.2:1b {_llm_label}</div>
        <div>{_vis_dot} Vision — {VISION_MODEL} {_vis_label}</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# FLOATING AI BOT — opens a docked chat panel on the right,
# without leaving the current page
# ============================================================
if st.session_state.page != "AI Assistant":
    fab_wrap = st.container(key="fab_wrap")
    with fab_wrap:
        if st.button("💬", key="fab_btn", help="Ask AI Assistant"):
            st.session_state.show_chat = not st.session_state.show_chat
            st.rerun()

    if st.session_state.show_chat:
        panel = st.container(key="chat_panel")
        with panel:
            hc1, hc2 = st.columns([4, 1])
            hc1.markdown('<div style="font-weight:800;font-size:16px;padding-top:4px;">🤖 AI Assistant</div>', unsafe_allow_html=True)
            with hc2:
                close_wrap = st.container(key="chat_close")
                with close_wrap:
                    if st.button("✕", key="chat_close_btn"):
                        st.session_state.show_chat = False
                        st.rerun()
            st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)

            for m in st.session_state.chat_history[-12:]:
                if m["role"] == "user":
                    st.markdown(f'<div class="chat-user">{m["text"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-bot">🤖 {m["text"]}</div>', unsafe_allow_html=True)

            mini_col1, mini_col2 = st.columns([4, 1])
            with mini_col1:
                mini_input = st.text_input("Ask me anything...", key="mini_chat_input", label_visibility="collapsed", placeholder="Ask me anything...")
            with mini_col2:
                send_clicked = st.button("➤", key="mini_chat_send")
            if send_clicked and mini_input.strip():
                st.session_state.chat_history.append({"role": "user", "text": mini_input.strip()})
                st.session_state.chat_history.append({"role": "bot", "text": bot_reply(mini_input.strip())})
                st.rerun()

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def status_badge(status):
    m = {
        "On Track": "badge-green",
        "Needs Attention": "badge-amber",
        "Delayed": "badge-red",
        "Done": "badge-green",
        "In Progress": "badge-blue",
        "Pending": "badge-amber",
        "Today": "badge-red",
        "Active": "badge-green",
        "Idle": "badge-amber",
        "Maintenance": "badge-red",
    }
    return m.get(status, "badge-blue")

def render_metric_card(label, value, badge_text=None, badge_class="badge-green", accent=True):
    accent_class = "card-accent" if accent else ""
    badge_html = f'<span class="badge {badge_class}">{badge_text}</span>' if badge_text else ""
    st.markdown(f"""
    <div class="card {accent_class}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {badge_html}
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# PAGE: DASHBOARD
# ============================================================
def page_dashboard():
    now = datetime.now()
    hour = now.hour
    greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 18 else "Good evening")

    st.markdown(f'<div class="hero-title">{greeting}, Site Manager 👋</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-date">{now.strftime("%A, %B %d, %Y")}</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([1, 2.2])
    with c1:
        st.markdown("""
        <div class="card">
            <div class="weather-temp">☀️ 31°C</div>
            <div style="font-weight:700;margin-top:6px;">Sunny</div>
            <div style="color:var(--muted);font-size:13px;margin-top:4px;">Wind 12 km/h · Humidity 58% · Rain tomorrow PM</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        active_count = len(PROJECTS)
        st.markdown(f"""
        <div class="card">
            <div style="font-weight:800;font-size:16px;margin-bottom:6px;">Today's site summary</div>
            <div style="color:var(--ink);font-size:14.5px;line-height:1.5;">
            Roof slab work continuing on Tower A. Concrete pour planned for Zone B at 2 PM.
            One safety violation flagged this morning. Cement stock needs reorder across {active_count} active projects.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height:18px;"></div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    total_workers = sum(p["workers"]["on_site"] for p in PROJECTS.values())
    total_capacity = sum(p["workers"]["total"] for p in PROJECTS.values())
    avg_safety = 92
    low_materials = sum(
        1 for p in PROJECTS.values() for m in p["materials"].values()
        if m["in_stock"] < m["required"] * 0.15
    )
    with m1:
        render_metric_card("Active projects", len(PROJECTS), "▲ 1 new this month", "badge-green")
    with m2:
        render_metric_card("Workers on site", f"{total_workers} / {total_capacity}", "On schedule", "badge-blue")
    with m3:
        render_metric_card("Safety score", f"{avg_safety} / 100", "▲ +2 this week", "badge-green")
    with m4:
        render_metric_card("Material status", f"{low_materials} low", "Cement ⚠️", "badge-red")

    st.markdown('<div class="section-title">🤖 AI Alerts</div>', unsafe_allow_html=True)
    for a in ALERTS:
        cls = "alert-high" if a["level"] == "high" else ("alert-med" if a["level"] == "med" else "alert-low")
        st.markdown(f'<div class="alert-box {cls}">{a["text"]}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">⚡ Quick actions</div>', unsafe_allow_html=True)
    q1, q2, q3, q4, q5 = st.columns(5)
    actions = [
        ("🏢", "View Projects", "Project Monitoring"),
        ("📄", "Analyze Plan", "Doc Analyzer"),
        ("🧮", "Estimate Materials", "Material Estimator"),
        ("🦺", "Check Safety", "Safety Analysis"),
        ("🤖", "Ask AI", "AI Assistant"),
    ]
    for col, (icon, label, target) in zip([q1, q2, q3, q4, q5], actions):
        with col:
            if st.button(f"{icon}\n\n{label}", key=f"qa_{target}", use_container_width=True):
                st.session_state.page = target
                st.rerun()

    st.markdown('<div class="section-title">📈 Project progress overview</div>', unsafe_allow_html=True)
    df = pd.DataFrame([
        {"Project": k.split("—")[0].strip(), "Progress": v["progress"], "Status": v["status"]}
        for k, v in PROJECTS.items()
    ])
    fig = px.bar(df, x="Progress", y="Project", orientation="h", color="Status",
                 color_discrete_map={"On Track": "#16A34A", "Needs Attention": "#F59E0B", "Delayed": "#DC2626"},
                 text="Progress")
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        height=280, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(range=[0, 110], showgrid=False),
        font=dict(family="Inter", color="#14213D"),
        showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)

    if st.button("🧠 Generate AI Insights", use_container_width=True):
        total_workers_ = sum(p["workers"]["on_site"] for p in PROJECTS.values())
        avg_progress = round(sum(p["progress"] for p in PROJECTS.values()) / len(PROJECTS))
        insight_prompt = (
            f"Portfolio snapshot — {len(PROJECTS)} active projects, {total_workers_} workers on site today, "
            f"average progress {avg_progress}%, safety score 92/100.\n\n"
            "Give a short executive summary for the site manager: overall health, the top 1-2 risks, "
            "any likely delays, and one concrete recommendation for today."
        )
        with st.spinner("🤖 Analyzing with llama3.2:1b..."):
            insight, err = query_llm(insight_prompt)
        if insight:
            st.markdown(f'<div class="card card-accent">{insight}</div>', unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="alert-box alert-med">🤖 AI insight unavailable — local model unreachable. '
                'Run <code>ollama serve</code> and make sure <code>llama3.2:1b</code> is pulled.</div>',
                unsafe_allow_html=True,
            )

# ============================================================
# PAGE: PROJECT MONITORING
# ============================================================
def page_projects():
    st.markdown('<div class="hero-title">Project Monitoring</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-date">Deep-dive into every active project</div>', unsafe_allow_html=True)

    cols = st.columns(len(PROJECTS))
    for col, name in zip(cols, PROJECTS.keys()):
        p = PROJECTS[name]
        with col:
            selected = st.session_state.selected_project == name
            border = "3px solid #FF7A29" if selected else "1px solid var(--border)"
            st.markdown(f"""
            <div class="proj-card" style="border:{border};margin-bottom:8px;">
                <div style="font-weight:800;font-size:14.5px;color:var(--ink);">{name}</div>
                <div style="color:var(--muted);font-size:12.5px;margin:4px 0 8px 0;">{p['type']} · {p['location']}</div>
                <div class="progress-outer"><div class="progress-inner" style="width:{p['progress']}%;"></div></div>
                <div style="display:flex;justify-content:space-between;margin-top:8px;">
                    <span style="font-size:12.5px;font-weight:700;">{p['progress']}% complete</span>
                    <span class="proj-status {status_badge(p['status'])}">{p['status']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View details", key=f"sel_{name}", use_container_width=True):
                st.session_state.selected_project = name
                st.rerun()

    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
    p = PROJECTS[st.session_state.selected_project]
    st.markdown(f'<div class="section-title">🏢 {st.session_state.selected_project}</div>', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_metric_card("Progress", f"{p['progress']}%", p['status'], status_badge(p['status']))
    with k2:
        render_metric_card("Workers on site", f"{p['workers']['on_site']} / {p['workers']['total']}", "Present today", "badge-blue")
    with k3:
        render_metric_card("Budget utilized", f"{p['budget_used']}%", None)
    with k4:
        days_left = (datetime.strptime(p['end'], "%Y-%m-%d") - datetime.now()).days
        render_metric_card("Est. days remaining", max(days_left, 0), f"Ends {p['end']}", "badge-amber")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📦 Materials", "🔧 Equipment", "📅 Timeline", "📁 Documents", "👷 Workforce"])

    with tab1:
        rows = []
        for mat, d in p["materials"].items():
            pct = round(d["in_stock"] / d["required"] * 100, 1) if d["required"] else 0
            rows.append({"Material": mat, "Required": d["required"], "In Stock": d["in_stock"],
                         "Stock %": pct, "Status": "🔴 Reorder" if pct < 25 else ("🟡 Low" if pct < 50 else "🟢 OK")})
        mat_df = pd.DataFrame(rows)
        c1, c2 = st.columns([1.3, 1])
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Required", x=mat_df["Material"], y=mat_df["Required"], marker_color="#FFE0C2"))
            fig.add_trace(go.Bar(name="In Stock", x=mat_df["Material"], y=mat_df["In Stock"], marker_color="#FF7A29"))
            fig.update_layout(barmode="group", plot_bgcolor="white", paper_bgcolor="white",
                               height=320, margin=dict(l=10, r=10, t=30, b=10),
                               font=dict(family="Inter", color="#14213D"),
                               legend=dict(orientation="h", y=1.1))
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.dataframe(mat_df, use_container_width=True, hide_index=True, height=320)
        low = mat_df[mat_df["Stock %"] < 25]
        if not low.empty:
            for _, r in low.iterrows():
                st.markdown(f'<div class="alert-box alert-high">⚠️ {r["Material"]} critically low — only {r["Stock %"]}% of required stock available. Reorder recommended.</div>', unsafe_allow_html=True)

    with tab2:
        eq_df = pd.DataFrame(p["equipment"])
        for _, row in eq_df.iterrows():
            c1, c2, c3 = st.columns([2.5, 1, 1])
            c1.markdown(f"**{row['name']}**")
            c2.markdown(f'<span class="badge {status_badge(row["status"])}">{row["status"]}</span>', unsafe_allow_html=True)
            c3.markdown(f"Runtime: {row['hours']} hrs" if row['hours'] != "-" else "Runtime: —")
            st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)

    with tab3:
        tdf = pd.DataFrame(p["timeline"])
        tdf["start"] = pd.to_datetime(tdf["start"])
        tdf["end"] = pd.to_datetime(tdf["end"]) + pd.Timedelta(days=1)
        color_map = {"Done": "#16A34A", "In Progress": "#FF7A29", "Pending": "#D1D5DB", "Today": "#DC2626"}
        fig = px.timeline(tdf, x_start="start", x_end="end", y="phase", color="status",
                           color_discrete_map=color_map)
        fig.update_yaxes(autorange="reversed", title="")
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=320,
                           margin=dict(l=10, r=10, t=20, b=10),
                           font=dict(family="Inter", color="#14213D"),
                           legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig, use_container_width=True)
        for item in p["timeline"]:
            st.markdown(f'<span class="badge {status_badge(item["status"])}">{item["status"]}</span>&nbsp;&nbsp;**{item["phase"]}** &nbsp;·&nbsp; {item["start"]} → {item["end"]}', unsafe_allow_html=True)

    with tab4:
        st.markdown("**Existing documents**")
        for d in p["docs"]:
            st.markdown(f"📄 {d}")
        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload a document for this project", type=["pdf", "png", "jpg", "jpeg", "docx", "xlsx"], key=f"upload_{st.session_state.selected_project}")
        if uploaded:
            st.success(f"✅ '{uploaded.name}' uploaded and linked to {st.session_state.selected_project}.")

    with tab5:
        c1, c2 = st.columns(2)
        with c1:
            fig = go.Figure(go.Pie(
                labels=["On site", "Absent"],
                values=[p['workers']['on_site'], p['workers']['total'] - p['workers']['on_site']],
                hole=.6, marker_colors=["#FF7A29", "#EEF0F5"]
            ))
            fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), showlegend=True,
                               font=dict(family="Inter", color="#14213D"),
                               annotations=[dict(text=f"{p['workers']['on_site']}/{p['workers']['total']}", x=0.5, y=0.5, font_size=18, showarrow=False)])
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            trades = ["Masons", "Electricians", "Welders", "Helpers", "Supervisors"]
            counts = np.random.RandomState(hash(st.session_state.selected_project) % 1000).randint(2, 10, size=len(trades))
            fig2 = px.bar(x=trades, y=counts, color_discrete_sequence=["#FF7A29"])
            fig2.update_layout(height=280, plot_bgcolor="white", paper_bgcolor="white",
                                margin=dict(l=10, r=10, t=10, b=10), xaxis_title="", yaxis_title="Workers",
                                font=dict(family="Inter", color="#14213D"))
            st.plotly_chart(fig2, use_container_width=True)

# ============================================================
# PAGE: DOC ANALYZER
# ============================================================
def page_doc_analyzer():
    st.markdown('<div class="hero-title">Doc Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-date">Upload a plan, blueprint, or PDF — the AI reads the actual file, nothing else</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1.3])
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Upload a document**")
        plan_file = st.file_uploader("Drop a site plan, blueprint image, or PDF", type=["pdf", "png", "jpg", "jpeg"], key="plan_upload")
        if plan_file and plan_file.type.startswith("image"):
            st.image(plan_file, use_container_width=True, caption="Uploaded plan preview")
        elif plan_file:
            st.success(f"✅ {plan_file.name} received.")

        st.markdown(
            '<div style="font-size:12px;color:var(--muted);margin-top:8px;">'
            f'Images are analyzed by the local vision model ({VISION_MODEL}). '
            'PDFs have their text extracted and analyzed by llama3.2:1b — scanned/image-only PDFs with no '
            'selectable text can\'t be read this way yet.</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)
        run = st.button("🔍 Analyze Document", use_container_width=True, disabled=(plan_file is None))
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        if not plan_file:
            st.markdown("""
            <div class="card" style="text-align:center;padding:60px 20px;">
                <div style="font-size:44px;">📐</div>
                <div style="font-weight:700;color:var(--muted);margin-top:10px;">Upload a plan or PDF and click<br>"Analyze Document" to see the AI's read of it</div>
            </div>
            """, unsafe_allow_html=True)
        elif run:
            if plan_file.type.startswith("image"):
                vis_prompt = (
                    "Describe this image factually and specifically: what type of structure or "
                    "document it is if identifiable, any visible dimensions, labels, room/floor "
                    "layout, people, equipment, or notable features. If text or numbers are "
                    "visible, quote them. If something is unclear, say so — do not guess or "
                    "invent details."
                )
                with st.spinner(f"🤖 Reading the image with {VISION_MODEL}..."):
                    result, err = query_vision_llm(plan_file.getvalue(), vis_prompt)

                if not result:
                    st.markdown(
                        f'<div class="alert-box alert-med">🤖 Vision analysis unavailable. '
                        f'Run <code>ollama pull {VISION_MODEL}</code> and make sure <code>ollama serve</code> is running.</div>',
                        unsafe_allow_html=True,
                    )
                    if err:
                        with st.expander("Show technical error (for debugging)"):
                            st.code(err)
                else:
                    with st.spinner("🛡️ Checking the content is construction-related..."):
                        img_allowed, img_reason = classify_description(result)
                    log_guardrail("[Doc Analyzer image] pre-analysis classification", img_allowed, img_reason)

                    if not img_allowed:
                        st.markdown(
                            f'<div class="alert-box alert-med">{guardrail_refusal_upload(result)}</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown('<div class="section-title">🤖 What the AI actually sees in this image</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="card">{result}</div>', unsafe_allow_html=True)
            else:  # PDF
                pdf_text = extract_pdf_text(plan_file.getvalue())
                if not pdf_text:
                    st.markdown(
                        '<div class="alert-box alert-med">⚠️ No selectable text could be extracted from this PDF '
                        '(it may be a scanned image). Try uploading it as a PNG/JPG instead so the vision model can read it.</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    allowed, reason = classify_description(pdf_text[:1500])
                    log_guardrail(f"[Doc Analyzer PDF] {pdf_text[:80]}", allowed, reason)
                    if not allowed:
                        st.markdown(f'<div class="alert-box alert-med">{guardrail_refusal_upload(pdf_text[:300])}</div>', unsafe_allow_html=True)
                        with st.expander("View extracted text that was checked"):
                            st.text(pdf_text)
                    else:
                        doc_prompt = (
                            f"Here is the extracted text of an uploaded construction document:\n\n{pdf_text}\n\n"
                            "Based ONLY on the text above, provide:\n"
                            "1. Summary (2-3 sentences)\n"
                            "2. Important dates mentioned\n"
                            "3. Materials or quantities mentioned\n"
                            "4. Risks or red flags\n"
                            "5. Anything important that seems missing\n"
                            "If the text doesn't contain information for a section, say 'Not mentioned in the document.'"
                        )
                        with st.spinner("🤖 Reading the document with llama3.2:1b..."):
                            result, err = query_llm(doc_prompt, extra_system="Analyze only the supplied document text — do not use the mock project data for this task.")
                        if result:
                            st.markdown('<div class="section-title">🤖 What the AI found in this document</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="card">{result}</div>', unsafe_allow_html=True)
                            with st.expander("View extracted text used for this analysis"):
                                st.text(pdf_text)
                        else:
                            st.markdown(
                                '<div class="alert-box alert-med">🤖 Analysis unavailable — local model unreachable. '
                                'Run <code>ollama serve</code> and make sure <code>llama3.2:1b</code> is pulled.</div>',
                                unsafe_allow_html=True,
                            )
        else:
            st.markdown("""
            <div class="card" style="text-align:center;padding:60px 20px;">
                <div style="font-size:44px;">🔍</div>
                <div style="font-weight:700;color:var(--muted);margin-top:10px;">Click "Analyze Document" to run the AI on your upload</div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# PAGE: MATERIAL ESTIMATOR
# ============================================================
def page_material_estimator():
    st.markdown('<div class="hero-title">Material Estimator</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-date">Enter project specs for a formula-based material & cost estimate, with an AI planning insight</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1.3])
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Project details**")
        proj_type = st.selectbox("Project type", ["House / Residential", "Apartment Building", "Metro / Rail Line", "Bridge", "Road / Highway"])

        if proj_type in ["House / Residential", "Apartment Building"]:
            area = st.number_input("Built-up area (sq. ft)", min_value=100, max_value=200000, value=2000, step=100)
            floors = st.number_input("Number of floors", min_value=1, max_value=60, value=2)
            quality = st.select_slider("Finish quality", options=["Basic", "Standard", "Premium", "Luxury"], value="Standard")
        elif proj_type == "Metro / Rail Line":
            length_km = st.number_input("Line length (km)", min_value=0.5, max_value=100.0, value=5.0, step=0.5)
            underground = st.checkbox("Underground section", value=True)
        elif proj_type == "Bridge":
            span_m = st.number_input("Span length (meters)", min_value=10, max_value=5000, value=200, step=10)
            lanes = st.number_input("Number of lanes", min_value=1, max_value=12, value=4)
        else:
            length_km = st.number_input("Road length (km)", min_value=0.5, max_value=200.0, value=10.0, step=0.5)
            lanes = st.number_input("Number of lanes", min_value=1, max_value=8, value=4)

        st.markdown('<div style="height:6px;"></div>', unsafe_allow_html=True)
        run = st.button("🔮 Run AI Estimation", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        if not run:
            st.markdown("""
            <div class="card" style="text-align:center;padding:60px 20px;">
                <div style="font-size:44px;">🧮</div>
                <div style="font-weight:700;color:var(--muted);margin-top:10px;">Fill in the details and click<br>"Run AI Estimation" to see predictions</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            quality_mult = {"Basic": 0.85, "Standard": 1.0, "Premium": 1.35, "Luxury": 1.8}
            if proj_type in ["House / Residential", "Apartment Building"]:
                qm = quality_mult[quality]
                cement = round(area * floors * 0.4 * qm)
                steel = round(area * floors * 0.004 * qm, 1)
                bricks = round(area * floors * 8 * qm)
                sand = round(area * floors * 0.18 * qm)
                cost_per_sqft = 1650 * qm
                total_cost = round(area * floors * cost_per_sqft)
                duration_months = round(2 + (area * floors) / 3500, 1)
                materials = {
                    "Cement": (cement, "bags"), "Steel": (steel, "tons"),
                    "Bricks": (bricks, "nos"), "Sand": (sand, "cu.m"),
                }
                spec_line = f"{proj_type}, {area} sq.ft built-up area, {floors} floors, {quality} finish quality."
            elif proj_type == "Metro / Rail Line":
                mult = 1.6 if underground else 1.0
                concrete = round(length_km * 3500 * mult)
                steel = round(length_km * 450 * mult)
                segments = round(length_km * 320 * mult) if underground else 0
                total_cost = round(length_km * (450 if underground else 180) * 10000000)
                duration_months = round(length_km * (7 if underground else 4), 1)
                materials = {
                    "Concrete": (concrete, "cu.m"), "Steel": (steel, "tons"),
                }
                if underground:
                    materials["Tunnel segments"] = (segments, "nos")
                spec_line = f"{proj_type}, {length_km} km, {'underground' if underground else 'elevated/at-grade'}."
            elif proj_type == "Bridge":
                concrete = round(span_m * lanes * 4.2)
                steel = round(span_m * lanes * 0.9, 1)
                total_cost = round(span_m * lanes * 850000)
                duration_months = round(6 + span_m / 120, 1)
                materials = {"Concrete": (concrete, "cu.m"), "Steel": (steel, "tons")}
                spec_line = f"{proj_type}, {span_m}m span, {lanes} lanes."
            else:
                asphalt = round(length_km * lanes * 480)
                aggregate = round(length_km * lanes * 950)
                total_cost = round(length_km * lanes * 12000000)
                duration_months = round(1 + length_km / 3, 1)
                materials = {"Asphalt": (asphalt, "tons"), "Aggregate base": (aggregate, "tons")}
                spec_line = f"{proj_type}, {length_km} km, {lanes} lanes."

            st.markdown(f"""
            <div class="card card-accent">
                <div class="metric-label">Estimated total cost</div>
                <div class="metric-value">₹ {total_cost:,}</div>
                <span class="badge badge-blue">Est. duration: {duration_months} months</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
            mcols = st.columns(len(materials))
            for col, (name, (qty, unit)) in zip(mcols, materials.items()):
                with col:
                    render_metric_card(name, f"{qty:,}", unit, "badge-green", accent=False)

            mat_df = pd.DataFrame([{"Material": k, "Quantity": v[0], "Unit": v[1]} for k, v in materials.items()])
            fig = px.bar(mat_df, x="Material", y="Quantity", color_discrete_sequence=["#FF7A29"], text="Quantity")
            fig.update_traces(texttemplate='%{text:,}', textposition='outside')
            fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", height=300,
                               margin=dict(l=10, r=10, t=30, b=10), font=dict(family="Inter", color="#14213D"))
            st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="alert-box alert-low">ℹ️ These are formula-based approximate values for early planning. Confirm with a certified structural engineer / QS before procurement.</div>', unsafe_allow_html=True)

            # ---- AI-written insight, grounded ONLY in the numbers just computed ----
            st.markdown('<div class="section-title">🤖 AI planning insight</div>', unsafe_allow_html=True)
            mats_str = ", ".join(f"{k}: {v[0]:,} {v[1]}" for k, v in materials.items())
            insight_prompt = (
                f"Project spec: {spec_line}\n"
                f"Computed estimate — Total cost: ₹{total_cost:,}, Duration: {duration_months} months.\n"
                f"Materials: {mats_str}\n\n"
                "In 3-4 sentences, give a practical planning insight: call out the biggest cost/schedule risk, "
                "one procurement tip, and one assumption the site manager should double-check."
            )
            with st.spinner("🤖 Generating insight with llama3.2:1b..."):
                insight, err = query_llm(insight_prompt, extra_system="Focus only on this one estimate — it is unrelated to any uploaded document.")
            if insight:
                st.markdown(f'<div class="card">{insight}</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div class="alert-box alert-med">🤖 AI insight unavailable — local model unreachable. '
                    'Run <code>ollama serve</code> and make sure <code>llama3.2:1b</code> is pulled.</div>',
                    unsafe_allow_html=True,
                )

# ============================================================
# PAGE: SAFETY ANALYSIS
# ============================================================
def page_safety():
    st.markdown('<div class="hero-title">Safety Analysis</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-date">Upload a site photo — analyzed for real by the local vision model ({VISION_MODEL})</div>', unsafe_allow_html=True)

    left, right = st.columns([1, 1.2])
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        img_file = st.file_uploader("Upload site image", type=["png", "jpg", "jpeg"], key="safety_upload")
        if img_file:
            st.image(img_file, use_container_width=True, caption="Uploaded site photo")
            scan = st.button("🔍 Run Safety Scan", use_container_width=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:40px 10px;color:var(--muted);">
                <div style="font-size:40px;">📷</div>
                Upload a photo from the site to check for safety violations
            </div>
            """, unsafe_allow_html=True)
            scan = False
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        if img_file and scan:
            # Single vision call — moondream just DESCRIBES what it sees (its
            # strength). The prompt is neutral about what the photo IS, since
            # this same description now also drives the guardrail decision
            # right after — presuming it's a construction site here would
            # bias the description regardless of what's actually in frame.
            describe_prompt = (
                "Describe this photo factually and specifically: the setting, any "
                "people and what they are wearing on their heads and bodies (hard "
                "hats? hi-vis vests? nothing?), objects, tools, machinery, or "
                "structures visible, how close anyone is to machinery, edges, "
                "height, or scaffolding, and anything else notable."
            )
            with st.spinner(f"🤖 Looking at the photo with {VISION_MODEL}..."):
                description, verr = query_vision_llm(img_file.getvalue(), describe_prompt)

            if not description:
                st.markdown(
                    f'<div class="alert-box alert-med">🤖 Vision analysis unavailable. '
                    f'Run <code>ollama pull {VISION_MODEL}</code> and make sure <code>ollama serve</code> is running, '
                    f'then check the sidebar status badge.</div>',
                    unsafe_allow_html=True,
                )
                if verr:
                    with st.expander("Show technical error (for debugging)"):
                        st.code(verr)
            else:
                with st.spinner("🛡️ Checking the photo is construction-related..."):
                    img_allowed, img_reason = classify_description(description)
                log_guardrail("[Safety Analysis] pre-analysis classification", img_allowed, img_reason)

                if not img_allowed:
                    st.markdown(
                        f'<div class="alert-box alert-med">{guardrail_refusal_upload(description)}</div>',
                        unsafe_allow_html=True,
                    )
                else:
                    # Stage 2 — llama3.2:1b turns that description into a score
                    # and structured findings (its strength: following instructions).
                    reasoning_prompt = (
                        f"A vision model just examined a construction site photo and described it as follows:\n\n"
                        f"\"{description}\"\n\n"
                        "Based ONLY on this description, reply in exactly this format:\n"
                        "SAFETY SCORE: <a number from 0 to 100, where 100 is fully compliant>\n"
                        "Then a bullet list of each violation implied by the description, with severity "
                        "(High/Medium/Low). If the description mentions no issues, write 'No violations observed.' "
                        "instead of a list. Do not invent anything not implied by the description."
                    )
                    with st.spinner("🤖 Scoring with llama3.2:1b..."):
                        result, err = query_llm(
                            reasoning_prompt,
                            extra_system="This task is about the photo description just given — ignore the mock project data for this one.",
                        )

                    if not result:
                        st.markdown(
                            '<div class="alert-box alert-med">🤖 The vision model described the photo, but scoring it '
                            'with llama3.2:1b failed. Run <code>ollama serve</code> and make sure <code>llama3.2:1b</code> is pulled.</div>',
                            unsafe_allow_html=True,
                        )
                        if err:
                            with st.expander("Show technical error (for debugging)"):
                                st.code(err)
                        st.markdown('<div class="section-title">🔎 Raw vision description</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="card">{description}</div>', unsafe_allow_html=True)
                    else:
                        score_match = re.search(r"SAFETY\s*SCORE\s*:\s*(\d{1,3})", result, re.IGNORECASE)
                        safety_score = min(100, int(score_match.group(1))) if score_match else None
                        narrative = result
                        if score_match:
                            narrative = (result[:score_match.start()] + result[score_match.end():]).strip()
                            narrative = narrative.lstrip(":\n ").strip()
                        if not narrative:
                            narrative = result  # never show a blank card

                        if safety_score is not None:
                            st.markdown(f"""
                            <div class="card card-accent">
                                <div class="metric-label">AI Safety Score</div>
                                <div class="metric-value">{safety_score} / 100</div>
                                <span class="badge {'badge-green' if safety_score>=85 else ('badge-amber' if safety_score>=70 else 'badge-red')}">
                                {'Good' if safety_score>=85 else ('Caution' if safety_score>=70 else 'Immediate action needed')}
                                </span>
                            </div>
                            """, unsafe_allow_html=True)

                        st.markdown('<div class="section-title">🔎 AI findings (from the actual photo)</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="card">{narrative}</div>', unsafe_allow_html=True)

                        with st.expander("What the vision model actually saw"):
                            st.markdown(description)
        else:
            st.markdown("""
            <div class="card" style="text-align:center;padding:70px 20px;">
                <div style="font-size:44px;">🦺</div>
                <div style="font-weight:700;color:var(--muted);margin-top:10px;">Upload an image and run the scan<br>to see real AI safety analysis here</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📋 Recent safety log</div>', unsafe_allow_html=True)
    log = pd.DataFrame([
        {"Time": "10:42 AM", "Project": "Tower A", "Issue": "Worker entered restricted zone near crane", "Severity": "High"},
        {"Time": "09:15 AM", "Project": "Zone B", "Issue": "Missing hi-vis vest — steel yard", "Severity": "Medium"},
        {"Time": "Yesterday", "Project": "Metro Line Ph.2", "Issue": "Routine PPE check passed", "Severity": "Low"},
    ])
    st.dataframe(log, use_container_width=True, hide_index=True)

# ============================================================
# PAGE: AI ASSISTANT
# ============================================================
def page_assistant():
    st.markdown('<div class="hero-title">AI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-date">Ask anything about your projects, materials, safety, or workforce — powered by local llama3.2:1b</div>', unsafe_allow_html=True)

    suggestions = [
        "📦 Cement stock at Tower A?", "🦺 Today's safety score?",
        "👷 Workers on site?", "📈 Project progress?",
        "🛡️ Test guardrail (off-topic)",
    ]
    scols = st.columns(5)
    for col, s in zip(scols, suggestions):
        with col:
            if st.button(s, use_container_width=True, key=f"sug_{s}"):
                sent = "What's a good recipe for pasta?" if "guardrail" in s else s
                st.session_state.chat_history.append({"role": "user", "text": sent})
                with st.spinner("🤖 Thinking..."):
                    reply = bot_reply(sent)
                st.session_state.chat_history.append({"role": "bot", "text": reply})
                st.rerun()

    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            avatar_role = "user" if msg["role"] == "user" else "assistant"
            with st.chat_message(avatar_role):
                st.markdown(msg["text"])

        user_input = st.chat_input("Ask anything about your projects...")
        if user_input:
            with st.chat_message("user"):
                st.markdown(user_input)
            st.session_state.chat_history.append({"role": "user", "text": user_input})

            with st.chat_message("assistant"):
                with st.spinner("🤖 Thinking..."):
                    answer = bot_reply(user_input)
                st.markdown(answer)
            st.session_state.chat_history.append({"role": "bot", "text": answer})
            st.rerun()

    guardrail_log = st.session_state.get("guardrail_log", [])
    if guardrail_log:
        with st.expander(f"🛡️ Guardrail activity log ({len(guardrail_log)} message(s) checked)"):
            for entry in reversed(guardrail_log[-15:]):
                icon = "✅" if entry["allowed"] else "🚫"
                st.markdown(f"{icon} `{entry['reason']}` — \"{entry['msg'][:80]}\"")

# ============================================================
# ROUTER
# ============================================================
PAGES = {
    "Dashboard": page_dashboard,
    "Project Monitoring": page_projects,
    "Doc Analyzer": page_doc_analyzer,
    "Material Estimator": page_material_estimator,
    "Safety Analysis": page_safety,
    "AI Assistant": page_assistant,
}
PAGES[st.session_state.page]()