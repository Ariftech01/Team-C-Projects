"""Seed the repository with realistic Indian construction demo data (North & West India)."""
from __future__ import annotations

from datetime import date, timedelta

from repository import get_repository
from models.domain import (
    Project, Task, Material, WorkforceMember, Equipment,
    SafetyIncident, SafetyChecklist, WeatherSnapshot,
    Document, HistoryEntry, ActivityEvent,
)


def _d(offset: int) -> str:
    return (date.today() + timedelta(days=offset)).isoformat()


def _weather(cond: str, t: float, wind: float, rain: float, impact: str) -> WeatherSnapshot:
    return WeatherSnapshot(
        date=date.today().isoformat(), temp_c=t, condition=cond,
        wind_kph=wind, precipitation_mm=rain, humidity=65, uv_index=7.0,
        work_impact=impact,
    )


def _project_delhi_metro() -> Project:
    return Project(
        id="proj_delhi_metro",
        name="Delhi Metro Line-10 Extension Corridor",
        code="DMRC-PH4-2025",
        type="Infrastructure",
        status="Active",
        priority="High",
        manager="Rajesh Sharma",
        client="Delhi Metro Rail Corporation (DMRC)",
        location="Delhi NCR",
        latitude=28.6139,
        longitude=77.2090,
        start_date=_d(-120),
        end_date=_d(180),
        budget=24_500_000_000,  # ₹2,450 Cr
        spent=14_200_000_000,   # ₹1,420 Cr
        progress=58.0,
        description="23.6 km elevated & underground rapid transit corridor with 16 stations and multi-modal integration.",
        weather=_weather("Hazy / Clear", 32, 10, 0.0, "Favorable"),
        tasks=[
            Task(name="Geotechnical survey & utility diversion", phase="Pre-construction", start_date=_d(-120), end_date=_d(-95), progress=100, status="Completed", assignee="L&T Infrastructure", priority="High"),
            Task(name="Pier foundation & pile cap construction", phase="Foundation", start_date=_d(-95), end_date=_d(-70), progress=100, status="Completed", assignee="Piling Crew A", priority="High"),
            Task(name="U-Girder casting & launching L1-L10", phase="Structure", start_date=_d(-70), end_date=_d(-20), progress=100, status="Completed", assignee="Erection Team B", priority="High"),
            Task(name="Station structural framing & concourse", phase="Structure", start_date=_d(-20), end_date=_d(40), progress=68, status="In Progress", assignee="Station Crew C", priority="High"),
            Task(name="Track laying & ballastless bed", phase="Trackwork", start_date=_d(-10), end_date=_d(80), progress=35, status="In Progress", assignee="Track Wing", priority="Medium"),
            Task(name="OHE traction electrification", phase="MEP", start_date=_d(20), end_date=_d(120), progress=0, status="Not Started", assignee="Siemens India", priority="High"),
        ],
        materials=[
            Material(name="M60 High-strength concrete", category="Concrete", quantity=45000, unit="m³", unit_cost=6500, used=28000, supplier="UltraTech Concrete", status="Delivered", delivery_date=_d(-40)),
            Material(name="Fe550D TMT Reinforcement Steel", category="Steel", quantity=12500, unit="tons", unit_cost=62000, used=8200, supplier="Tata Steel Ltd.", status="Partially Delivered", delivery_date=_d(-15)),
            Material(name="PSC Segmental Girders", category="Precast", quantity=420, unit="ea", unit_cost=850000, used=290, supplier="L&T Casting Yard Noida", status="Partially Delivered", delivery_date=_d(-5)),
            Material(name="Head Hardened Rails (60E1)", category="Track", quantity=3200, unit="tons", unit_cost=88000, used=1100, supplier="JSW Steel", status="Ordered", delivery_date=_d(15)),
        ],
        workforce=[
            WorkforceMember(name="Rajesh Sharma", role="Project Director", crew="Management", headcount=1, hourly_rate=450, hours_today=9, status="On Site", trade="Management"),
            WorkforceMember(name="L&T Structural Riggers", role="Structural", crew="B", headcount=42, hourly_rate=180, hours_today=8, status="On Site", trade="Ironworker"),
            WorkforceMember(name="Siemens Track Electricals", role="MEP", crew="C", headcount=18, hourly_rate=220, hours_today=8, status="On Site", trade="Electrician"),
        ],
        equipment=[
            Equipment(name="Heavy Launching Gantry LG-01", type="Gantry Crane", status="Operational", operator="S. Kumar", fuel_hours=1420, last_service=_d(-20), next_service=_d(10), daily_rate=45000),
            Equipment(name="Tunnel Boring Machine TBM-2", type="TBM", status="Operational", operator="V. Singh", fuel_hours=2150, last_service=_d(-10), next_service=_d(15), daily_rate=180000),
            Equipment(name="Rigid Hydraulic Piling Rig", type="Piling", status="Operational", operator="R. Yadav", fuel_hours=880, last_service=_d(-12), next_service=_d(18), daily_rate=32000),
        ],
        safety_incidents=[
            SafetyIncident(date=_d(-25), type="Near Miss", severity="Low", description="Gantry movement clearance warning at Station 4", reported_by="R. Sharma", status="Resolved", action_taken="Safety barricades reinforced, extra spotter deployed"),
        ],
        safety_checklist=[
            SafetyChecklist(item="Daily site toolbox talk & briefing", completed=True, last_checked=_d(0), responsible="Safety Manager"),
            SafetyChecklist(item="High-elevation fall protection harness audit", completed=True, last_checked=_d(0), responsible="Safety Officer"),
            SafetyChecklist(item="TBM ventilation & gas monitor check", completed=True, last_checked=_d(0), responsible="Shift In-Charge"),
        ],
        documents=[
            Document(name="DMRC_PH4_DPR_Final.pdf", category="Engineering", file_type="pdf", size_bytes=8_500_000, summary="Detailed Project Report, alignment drawings, EIA compliance."),
            Document(name="Geotechnical_Borelog_Report.pdf", category="Geotech", file_type="pdf", size_bytes=4_200_000, summary="Delhi silt & rock strata analysis across 16 stations."),
        ],
        history=[
            HistoryEntry(type="activity", title="Project initialized", content="Delhi Metro Line-10 Extension registered in hub.", author="System"),
            HistoryEntry(type="milestone", title="U-Girder milestone", content="100th U-Girder successfully launched.", author="R. Sharma"),
        ],
    )


def _project_mumbai_coastal() -> Project:
    return Project(
        id="proj_mumbai_coastal",
        name="Mumbai Coastal Road & Trans-Harbor Link",
        code="MCR-2025-08",
        type="Infrastructure",
        status="Delayed",
        priority="Critical",
        manager="Vikramaditya Patil",
        client="Municipal Corp. of Greater Mumbai (MCGM)",
        location="Mumbai, MH",
        latitude=18.9750,
        longitude=72.8258,
        start_date=_d(-210),
        end_date=_d(60),
        budget=18_500_000_000,  # ₹1,850 Cr
        spent=16_800_000_000,   # ₹1,680 Cr
        progress=79.0,
        description="8-lane freeway & sea bridge connecting Nariman Point to Bandra-Worli Sea Link with underground twin tunnels.",
        weather=_weather("Monsoon Rain / Wind", 29, 32, 45.0, "Unfavorable"),
        tasks=[
            Task(name="Seawall reclamation & armouring", phase="Marine", start_date=_d(-210), end_date=_d(-150), progress=100, status="Completed", assignee="Hindustan Construction", priority="High"),
            Task(name="Subsea twin tunnel excavation", phase="Tunnelling", start_date=_d(-150), end_date=_d(-40), progress=100, status="Completed", assignee="L&T Geo", priority="Critical"),
            Task(name="Prestressed sea bridge deck pouring", phase="Deck", start_date=_d(-50), end_date=_d(20), progress=75, status="In Progress", assignee="Shapoorji Pallonji", priority="Critical"),
            Task(name="Promenade, landscaping & lighting", phase="Finishes", start_date=_d(0), end_date=_d(50), progress=20, status="In Progress", assignee="Urban Infra", priority="Medium"),
        ],
        materials=[
            Material(name="Marine-grade C50 Concrete", category="Concrete", quantity=52000, unit="m³", unit_cost=7200, used=41000, supplier="RMC Readymix India", status="Delivered", delivery_date=_d(-30)),
            Material(name="High tensile prestressing strand", category="Steel", quantity=4800, unit="tons", unit_cost=78000, used=3900, supplier="Usha Martin", status="Delivered", delivery_date=_d(-20)),
            Material(name="Anti-corrosive marine paint", category="Coatings", quantity=35000, unit="L", unit_cost=450, used=18000, supplier="Asian Paints PPG", status="Partially Delivered", delivery_date=_d(-5)),
        ],
        workforce=[
            WorkforceMember(name="Vikramaditya Patil", role="Chief Project Manager", crew="Management", headcount=1, hourly_rate=500, hours_today=10, status="On Site", trade="Management"),
            WorkforceMember(name="Shapoorji Marine Crew", role="Deck", crew="3", headcount=36, hourly_rate=190, hours_today=4, status="Weather Hold", trade="Concrete"),
        ],
        equipment=[
            Equipment(name="Floating Crane Barge FC-02", type="Marine Crane", status="Maintenance", operator="Capt. N. Rao", fuel_hours=1890, last_service=_d(-5), next_service=_d(25), daily_rate=120000),
            Equipment(name="High Capacity Concrete Pump", type="Pump", status="Operational", operator="M. Kulkarni", fuel_hours=920, last_service=_d(-15), next_service=_d(15), daily_rate=28000),
        ],
        safety_incidents=[
            SafetyIncident(date=_d(-12), type="Weather Hold", severity="Medium", description="High tide & heavy swell paused barge operations", reported_by="V. Patil", status="Resolved", action_taken="Barge moored safely, weather watch active"),
        ],
        safety_checklist=[
            SafetyChecklist(item="Marine lifejacket & safety harness audit", completed=True, last_checked=_d(0), responsible="Safety Officer"),
            SafetyChecklist(item="Sea swell & monsoon wind speed monitoring", completed=True, last_checked=_d(0), responsible="Site Engineer"),
        ],
        documents=[
            Document(name="MCGM_Coastal_Approval.pdf", category="Permits", file_type="pdf", size_bytes=6_200_000, summary="CRZ clearance & MCGM environmental approval document."),
        ],
        history=[
            HistoryEntry(type="activity", title="Project logged", content="Mumbai Coastal Road added to portfolio.", author="System"),
            HistoryEntry(type="alert", title="Monsoon delay", content="Sea bridge deck pouring paused due to high swell.", author="System"),
        ],
    )


def _project_gurugram_cyber() -> Project:
    return Project(
        id="proj_gurugram_cyber",
        name="Gurugram Cyber City Commercial Tower B",
        code="GCC-2025-12",
        type="Commercial",
        status="Active",
        priority="Medium",
        manager="Ananya Sengupta",
        client="DLF Cyber City Developers Ltd.",
        location="Gurugram, HR",
        latitude=28.4595,
        longitude=77.0266,
        start_date=_d(-45),
        end_date=_d(240),
        budget=3_800_000_000,   # ₹380 Cr
        spent=950_000_000,      # ₹95 Cr
        progress=25.0,
        description="28-story LEED Platinum commercial IT tower with double-glazed curtain wall & automated HVAC.",
        weather=_weather("Clear", 30, 8, 0.0, "Favorable"),
        tasks=[
            Task(name="Basement diaphragm wall & excavation", phase="Foundation", start_date=_d(-45), end_date=_d(-15), progress=100, status="Completed", assignee="Ahluwalia Contracts", priority="High"),
            Task(name="Raft foundation pouring", phase="Foundation", start_date=_d(-15), end_date=_d(15), progress=85, status="In Progress", assignee="Ahluwalia Contracts", priority="High"),
            Task(name="Superstructure L1-L10 framing", phase="Structure", start_date=_d(15), end_date=_d(90), progress=0, status="Not Started", assignee="Tata Projects", priority="High"),
        ],
        materials=[
            Material(name="Self-compacting concrete M50", category="Concrete", quantity=18000, unit="m³", unit_cost=5800, used=14000, supplier="ACC Concrete", status="Delivered", delivery_date=_d(-10)),
            Material(name="Double-glazed facade panels", category="Glazing", quantity=12000, unit="m²", unit_cost=14500, used=0, supplier="Saint-Gobain India", status="Ordered", delivery_date=_d(45)),
        ],
        workforce=[
            WorkforceMember(name="Ananya Sengupta", role="Senior Project Manager", crew="Management", headcount=1, hourly_rate=420, hours_today=8, status="On Site", trade="Management"),
        ],
        equipment=[
            Equipment(name="Tower Crane TC-01", type="Crane", status="Operational", operator="P. Das", fuel_hours=310, last_service=_d(-8), next_service=_d(22), daily_rate=35000),
        ],
        safety_incidents=[],
        safety_checklist=[
            SafetyChecklist(item="Deep excavation shoring inspection", completed=True, last_checked=_d(0), responsible="A. Sengupta"),
        ],
        documents=[
            Document(name="DLF_TowerB_Architectural.pdf", category="Drawings", file_type="pdf", size_bytes=12_400_000, summary="Complete 28-story floor plans & elevation drawings."),
        ],
        history=[
            HistoryEntry(type="activity", title="Project registered", content="Gurugram Cyber City Tower B initialized.", author="System"),
        ],
    )


def _project_gift_city() -> Project:
    return Project(
        id="proj_gift_city",
        name="GIFT City Smart Logistics & Data Center Hub",
        code="GIFT-2025-03",
        type="Industrial",
        status="Planning",
        priority="Medium",
        manager="Harshvardhan Shah",
        client="GIFT SEZ Development Corp.",
        location="Gandhinagar / Ahmedabad, GJ",
        latitude=23.1600,
        longitude=72.6800,
        start_date=_d(15),
        end_date=_d(270),
        budget=2_400_000_000,   # ₹240 Cr
        spent=80_000_000,       # ₹8 Cr
        progress=5.0,
        description="Next-gen automated warehouse & Tier-IV data center facility inside India's premier IFSC tech city.",
        weather=_weather("Sunny / Warm", 34, 12, 0.0, "Favorable"),
        tasks=[
            Task(name="Environmental clearance & GPCB approval", phase="Pre-construction", start_date=_d(-30), end_date=_d(10), progress=70, status="In Progress", assignee="H. Shah", priority="High"),
            Task(name="Boundary wall & site grading", phase="Site", start_date=_d(10), end_date=_d(40), progress=0, status="Not Started", assignee="Local Infra", priority="Medium"),
        ],
        materials=[
            Material(name="Structural steel trusses", category="Steel", quantity=2200, unit="tons", unit_cost=64000, used=0, supplier="JSW Steel", status="Quoted", delivery_date=""),
        ],
        workforce=[
            WorkforceMember(name="Harshvardhan Shah", role="Lead PM", crew="Management", headcount=1, hourly_rate=400, hours_today=6, status="Off Site", trade="Management"),
        ],
        equipment=[],
        safety_incidents=[],
        safety_checklist=[
            SafetyChecklist(item="Environmental compliance & dust control plan", completed=True, last_checked=_d(-2), responsible="H. Shah"),
        ],
        documents=[
            Document(name="GIFT_City_Masterplan.pdf", category="Planning", file_type="pdf", size_bytes=5_100_000, summary="SEZ layout, power grid redundancy, optical fiber topology."),
        ],
        history=[
            HistoryEntry(type="activity", title="Project planned", content="GIFT City Hub entered planning phase.", author="System"),
        ],
    )


def seed_if_empty() -> None:
    repo = get_repository()
    if repo.list_projects():
        return
    projects = [_project_delhi_metro(), _project_mumbai_coastal(), _project_gurugram_cyber(), _project_gift_city()]
    for p in projects:
        repo.save_project(p)
    
    repo.add_activity(ActivityEvent(project_id="proj_delhi_metro", project_name="Delhi Metro Line-10 Extension Corridor", event="Station structural framing reached 68% completion", category="progress"))
    repo.add_activity(ActivityEvent(project_id="proj_mumbai_coastal", project_name="Mumbai Coastal Road & Trans-Harbor Link", event="Monsoon rain alert — sea bridge deck pouring paused", category="weather"))
    repo.add_activity(ActivityEvent(project_id="proj_gurugram_cyber", project_name="Gurugram Cyber City Commercial Tower B", event="Raft foundation pouring 85% complete", category="progress"))
    repo.add_activity(ActivityEvent(project_id="proj_gift_city", project_name="GIFT City Smart Logistics & Data Center Hub", event="Environmental clearance 70% complete", category="planning"))
