"""Professional Welcome Landing Page for Construction Intelligence Hub."""
from __future__ import annotations

import streamlit as st
from config.settings import APP_NAME, APP_TAGLINE, APP_VERSION

# ── CSS injected once per render ──────────────────────────────────────────────
_WELCOME_CSS = """
<style>
/* ── Scoped welcome page animations & layout ──────────────────────────── */
@keyframes wFadeUp {
  from { opacity: 0; transform: translateY(18px); }
  to   { opacity: 1; transform: translateY(0);    }
}
@keyframes wPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(14, 124, 123, 0.35); }
  50%       { box-shadow: 0 0 0 10px rgba(14, 124, 123, 0);  }
}

/* Nav bar logo pill */
.wlc-logo-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.55rem 1rem 0.55rem 0.55rem;
  border-radius: 14px;
  border: 1px solid rgba(14, 124, 123, 0.25);
  animation: wFadeUp 0.4s ease both;
}
.wlc-logo-icon {
  width: 44px; height: 44px;
  background: linear-gradient(135deg, #1B3A5B, #0E7C7B);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.5rem;
  box-shadow: 0 4px 14px rgba(14, 124, 123, 0.35);
  animation: wPulse 3s ease infinite;
}
.wlc-logo-text h3  { margin: 0; font-weight: 800; font-size: 1.1rem; letter-spacing: -0.3px; }
.wlc-logo-text span { font-size: 0.72rem; opacity: 0.65; font-weight: 500; letter-spacing: 0.02em; }

/* Hero banner */
.wlc-hero {
  background: linear-gradient(135deg, #1B3A5B 0%,#0E7C7B 55%, #0D2640 100%);
  border-radius: 22px;
  padding: 3.2rem 2.8rem 3rem;
  box-shadow: 0 16px 48px rgba(15, 23, 42, 0.28);
  position: relative; overflow: hidden;
  margin-bottom: 0.5rem;
  animation: wFadeUp 0.45s ease both;
}
.wlc-hero::before {
  content: "";
  position: absolute; right: -80px; bottom: -80px;
  width: 320px; height: 320px; border-radius: 50%;
  background: rgba(255,255,255,0.04);
  pointer-events: none;
}
.wlc-hero::after {
  content: "";
  position: absolute; left: -40px; top: -40px;
  width: 200px; height: 200px; border-radius: 50%;
  background: rgba(14, 124, 123, 0.08);
  pointer-events: none;
}
.wlc-badge {
  display: inline-block;
  background: rgba(14, 124, 123, 0.32);
  border: 1px solid rgba(77, 208, 200, 0.38);
  border-radius: 30px;
  padding: 0.32rem 1rem;
  font-size: 0.72rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.09em;
  color: rgba(255,255,255,0.9);
  margin-bottom: 1.2rem;
}
.wlc-hero h1 {
  font-size: clamp(1.9rem, 4vw, 2.8rem);
  font-weight: 800; line-height: 1.18;
  margin: 0 0 1rem; color: #FFFFFF;
  letter-spacing: -0.7px;
}
.wlc-hero p {
  font-size: 1rem; color: rgba(255,255,255,0.82);
  line-height: 1.65; margin: 0;
  color: #ffffff;
  max-width: 680px; font-weight: 400;
}

/* Stats bar */
.wlc-stats {
  display: flex; gap: 0.5rem; margin-top: 2rem; flex-wrap: wrap;
}
.wlc-stat {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.18);
  border-radius: 10px;
  padding: 0.5rem 1rem;
  display: flex; flex-direction: column; align-items: center;
  min-width: 90px;
}
.wlc-stat-val { font-size: 1.25rem; font-weight: 800; color: #FFFFFF; }
.wlc-stat-lbl { font-size: 0.65rem; color: rgba(255,255,255,0.65); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.1rem; }

/* Feature cards */
.wlc-card {
  border-radius: 16px;
  padding: 1.4rem 1.3rem 1.2rem;
  height: 100%;
  transition: transform 0.22s ease, box-shadow 0.22s ease;
  animation: wFadeUp 0.5s ease both;
  position: relative; overflow: hidden;
}
.wlc-card:hover { transform: translateY(-5px); }

/* Gradient card variants */
.wlc-card-blue {
  background: linear-gradient(135deg, #1B3A5B 0%, #1d4e8f 100%);
  box-shadow: 0 6px 24px rgba(27, 58, 91, 0.3);
}
.wlc-card-blue:hover { box-shadow: 0 14px 36px rgba(27, 58, 91, 0.4); }

.wlc-card-teal {
  background: linear-gradient(135deg, #0E7C7B 0%, #0a5d5c 100%);
  box-shadow: 0 6px 24px rgba(14, 124, 123, 0.3);
}
.wlc-card-teal:hover { box-shadow: 0 14px 36px rgba(14, 124, 123, 0.4); }

.wlc-card-amber {
  background: linear-gradient(135deg, #b45309 0%, #92400e 100%);
  box-shadow: 0 6px 24px rgba(180, 83, 9, 0.3);
}
.wlc-card-amber:hover { box-shadow: 0 14px 36px rgba(180, 83, 9, 0.4); }

.wlc-card-slate {
  background: linear-gradient(135deg, #334155 0%, #1e293b 100%);
  box-shadow: 0 6px 24px rgba(51, 65, 85, 0.35);
}
.wlc-card-slate:hover { box-shadow: 0 14px 36px rgba(51, 65, 85, 0.45); }

.wlc-card-green {
  background: linear-gradient(135deg, #166534 0%, #14532d 100%);
  box-shadow: 0 6px 24px rgba(22, 101, 52, 0.3);
}
.wlc-card-green:hover { box-shadow: 0 14px 36px rgba(22, 101, 52, 0.4); }

.wlc-card-crimson {
  background: linear-gradient(135deg, #991b1b 0%, #7f1d1d 100%);
  box-shadow: 0 6px 24px rgba(153, 27, 27, 0.3);
}
.wlc-card-crimson:hover { box-shadow: 0 14px 36px rgba(153, 27, 27, 0.4); }

/* All text inside gradient cards must be white */
.wlc-card .wlc-card-icon  { font-size: 2rem; margin-bottom: 0.75rem; display: block;}
.wlc-card .wlc-card-title {
  font-size: 0.98rem; font-weight: 700;
  color: #FFFFFF !important; margin: 0 0 0.45rem;
  line-height: 1.3;
}
.wlc-card .wlc-card-desc  {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.80) !important;
  line-height: 1.55; margin: 0;
}
.wlc-card .wlc-card-tag {
  display: inline-block;
  margin-top: 0.9rem;
  background: rgba(255,255,255,0.15);
  border-radius: 20px;
  padding: 0.2rem 0.65rem;
  font-size: 0.68rem; font-weight: 600;
  color: rgba(255,255,255,0.9) !important;
  letter-spacing: 0.04em;
}

/* How it works steps */
.wlc-step {
  display: flex; align-items: flex-start; gap: 1rem;
  padding: 1rem 1.1rem;
  border-radius: 14px;
  border: 1px solid rgba(14, 124, 123, 0.2);
  background: rgba(14, 124, 123, 0.05);
  transition: border-color 0.2s ease, background 0.2s ease;
  animation: wFadeUp 0.5s ease both;
}
.wlc-step:hover {
  border-color: rgba(14, 124, 123, 0.45);
  background: rgba(14, 124, 123, 0.09);
}
.wlc-step-num {
  min-width: 38px; height: 38px;
  background: linear-gradient(135deg, #1B3A5B, #0E7C7B);
  border-radius: 10px; display: flex;
  align-items: center; justify-content: center;
  font-weight: 800; font-size: 0.9rem;
  color: #FFFFFF;
  box-shadow: 0 4px 12px rgba(14, 124, 123, 0.3);
}
.wlc-step-content h5 { margin: 0 0 0.2rem; font-size: 0.9rem; font-weight: 700; }
.wlc-step-content p  { margin: 0; font-size: 0.78rem; opacity: 0.7; line-height: 1.4; }

/* Footer */
.wlc-footer {
  text-align: center; padding: 1.5rem 0 0.5rem;
  font-size: 0.8rem; opacity: 0.6;
  border-top: 1px solid rgba(14, 124, 123, 0.2);
  margin-top: 1.5rem;
}
.wlc-footer strong { opacity: 0.85; }

/* Section headers */
.wlc-section-head { animation: wFadeUp 0.4s ease both; }
</style>
"""


def _card(icon: str, title: str, desc: str, tag: str, variant: str) -> str:
    """Return HTML for a single gradient feature card."""
    return f"""
    <div class="wlc-card wlc-card-{variant}">
      <span class="wlc-card-icon">{icon}</span>
      <p class="wlc-card-title">{title}</p>
      <p class="wlc-card-desc">{desc}</p>
      <span class="wlc-card-tag">{tag}</span>
    </div>
    """


def render_welcome() -> None:
    """Render high-impact enterprise landing page."""
    st.markdown(_WELCOME_CSS, unsafe_allow_html=True)

    # ── Navigation bar ─────────────────────────────────────────────────────────
    nav_l, nav_r = st.columns([3, 1])
    with nav_l:
        st.markdown(
            f"""
            <div class="wlc-logo-pill">
              <div class="wlc-logo-icon">🚧</div>
              <div class="wlc-logo-text">
                <h3>{APP_NAME}</h3>
                <span>{APP_TAGLINE}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with nav_r:
        st.markdown("<div style='padding-top:0.6rem'>", unsafe_allow_html=True)
        if st.button("Sign In →", key="wlc_top_signin", type="secondary", use_container_width=True):
            st.session_state["auth_view"] = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom:1.2rem'></div>", unsafe_allow_html=True)

    # ── Hero Banner ────────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="wlc-hero">
          <div class="wlc-badge">Enterprise Construction Management &amp; AI Intelligence</div>
          <h1>Next-Generation<br>Construction Intelligence Platform</h1>
          <p>
            Empowering Indian infrastructure and commercial project teams with
            real-time portfolio analytics, predictive risk modelling, automated
            BOQ document intelligence, and AI-driven site operations — all in
            one unified workspace.
          </p>
          <div class="wlc-stats">
            <div class="wlc-stat"><span class="wlc-stat-val">4+</span><span class="wlc-stat-lbl">Projects</span></div>
            <div class="wlc-stat"><span class="wlc-stat-val">₹ Cr</span><span class="wlc-stat-lbl">INR Budgets</span></div>
            <div class="wlc-stat"><span class="wlc-stat-val">AI</span><span class="wlc-stat-lbl">Copilot</span></div>
            <div class="wlc-stat"><span class="wlc-stat-val">BOQ</span><span class="wlc-stat-lbl">Takeoff</span></div>
            <div class="wlc-stat"><span class="wlc-stat-val">v{APP_VERSION}</span><span class="wlc-stat-lbl">Latest</span></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── CTA Buttons ────────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:1.1rem;margin-bottom:0.4rem'></div>", unsafe_allow_html=True)
    cta1, cta2, _ = st.columns([1.15, 1.45, 1.5])
    with cta1:
        if st.button(
            "🔐  Sign In to Workspace",
            key="wlc_hero_signin",
            use_container_width=True,
            type="primary",
        ):
            st.session_state["auth_view"] = "login"
            st.rerun()
    with cta2:
        if st.button(
            "🏢  Create Organisation Setup",
            key="wlc_hero_setup",
            use_container_width=True,
            type="secondary",
        ):
            st.session_state["auth_view"] = "setup"
            st.rerun()

    st.markdown("<div style='margin-bottom:2.8rem'></div>", unsafe_allow_html=True)

    # ── Feature Cards ──────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="wlc-section-head">
          <h3 style="margin:0 0 0.2rem;font-weight:800;letter-spacing:-0.3px">Enterprise Capabilities</h3>
          <p style="margin:0;opacity:0.6;font-size:0.87rem">Integrated intelligence across the entire construction lifecycle</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='margin-bottom:1.1rem'></div>", unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns(3)

    with fc1:
        st.markdown(
            _card(
                "🤖",
                "AI-Powered Construction Copilot",
                "Context-aware AI assistant trained on Indian construction standards, engineering codes, and real-time site data.",
                "AI Assistant",
                "blue",
            ),
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-bottom:0.9rem'></div>", unsafe_allow_html=True)
        st.markdown(
            _card(
                "🔮",
                "Predictive Risk Management",
                "Proactive safety, schedule delay, and cost overrun predictions before they impact the critical path.",
                "Risk Engine",
                "crimson",
            ),
            unsafe_allow_html=True,
        )

    with fc2:
        st.markdown(
            _card(
                "📊",
                "Portfolio Analytics & INR Budgeting",
                "Real-time budget tracking in ₹ Crore / Lakhs with 6 interactive Plotly charts and benchmarking.",
                "Analytics",
                "teal",
            ),
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-bottom:0.9rem'></div>", unsafe_allow_html=True)
        st.markdown(
            _card(
                "🧱",
                "Material & Resource Intelligence",
                "Automated quantity takeoff, equipment tracking, workforce planning, and material lead-time alerts.",
                "Resources",
                "green",
            ),
            unsafe_allow_html=True,
        )

    with fc3:
        st.markdown(
            _card(
                "📄",
                "Document Intelligence & BOQ Validation",
                "Upload BOQs, tenders, and drawings with automated verification, compliance checking, and extraction.",
                "Documents",
                "amber",
            ),
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-bottom:0.9rem'></div>", unsafe_allow_html=True)
        st.markdown(
            _card(
                "📑",
                "Executive PDF Reporting",
                "One-click corporate PDF reports with KPIs, safety metrics, and ₹ Crore budget summaries.",
                "Reports",
                "slate",
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-bottom:2.8rem'></div>", unsafe_allow_html=True)

    # ── How It Works ───────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="wlc-section-head">
          <h3 style="margin:0 0 0.2rem;font-weight:800;letter-spacing:-0.3px">How It Works</h3>
          <p style="margin:0;opacity:0.6;font-size:0.87rem">Up and running in minutes — no complex setup required</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='margin-bottom:0.9rem'></div>", unsafe_allow_html=True)

    step_c1, step_c2 = st.columns(2)
    steps = [
        ("01", "Create Your Organisation", "Set up your workspace with company details, admin credentials, and team roles in the one-time Setup Wizard."),
        ("02", "Add Your Projects", "Create projects with budgets, timelines, workforce, and milestones. Import site data from your existing BOQs."),
        ("03", "Monitor in Real-Time", "Track KPIs across the Portfolio dashboard with live health scores, weather impacts, and AI-generated insights."),
        ("04", "Act on AI Intelligence", "Use the AI Tool Center for planning briefs, risk assessments, BOQ takeoffs, and executive report generation."),
    ]
    for i, (num, title, desc) in enumerate(steps):
        col = step_c1 if i % 2 == 0 else step_c2
        with col:
            st.markdown(
                f"""
                <div class="wlc-step" style="margin-bottom:0.75rem">
                  <div class="wlc-step-num">{num}</div>
                  <div class="wlc-step-content">
                    <h5>{title}</h5>
                    <p>{desc}</p>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-bottom:2.5rem'></div>", unsafe_allow_html=True)

    # ── Final CTA strip ────────────────────────────────────────────────────────
    cta_strip_l, cta_strip_c, cta_strip_r = st.columns([1, 2, 1])
    with cta_strip_c:
        st.markdown(
            """
            <div style="text-align:center;margin-bottom:0.9rem">
              <p style="font-size:1.05rem;font-weight:700;margin:0 0 0.3rem;letter-spacing:-0.2px">
                Ready to transform your construction operations?
              </p>
              <p style="font-size:0.83rem;opacity:0.6;margin:0">
                Sign in to your existing workspace or create a new organisation account.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(
            "🚀  Get Started — Sign In",
            key="wlc_bottom_cta",
            use_container_width=True,
            type="primary",
        ):
            st.session_state["auth_view"] = "login"
            st.rerun()
        st.markdown("<div style='margin-bottom:0.4rem'></div>", unsafe_allow_html=True)
        if st.button(
            "🏢  New here? Create Organisation",
            key="wlc_bottom_setup",
            use_container_width=True,
            type="secondary",
        ):
            st.session_state["auth_view"] = "setup"
            st.rerun()

    # ── Footer ─────────────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="wlc-footer">
          {APP_NAME} &nbsp;v{APP_VERSION} &nbsp;•&nbsp;
          <strong>Designed &amp; Developed by Diksha Rautela</strong>
          &nbsp;•&nbsp; Enterprise Construction Intelligence
        </div>
        """,
        unsafe_allow_html=True,
    )
