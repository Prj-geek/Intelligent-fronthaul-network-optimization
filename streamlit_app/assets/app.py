import streamlit as st
import pandas as pd
import os
import base64
from pathlib import Path

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Fronthaul Network Optimization",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": "Intelligent Fronthaul Network Optimization — Topology & Capacity Estimation"
    }
)

# =====================================================
# PATH SETUP
# =====================================================
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")

# =====================================================
# HELPER — encode local image to base64 for embedding
# =====================================================
def img_to_base64(path: str) -> str | None:
    p = Path(path)
    if p.exists():
        return base64.b64encode(p.read_bytes()).decode()
    return None

# =====================================================
# GLOBAL CSS — dark industrial telecom theme
# =====================================================
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700&family=Share+Tech+Mono&family=Inter:wght@300;400;500;600&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background: #0a0e14 !important;
    color: #c8d6e5 !important;
    font-family: 'Inter', sans-serif !important;
    min-height: 100vh;
}

/* ── Hide default Streamlit chrome ── */
.stApp > header { display: none !important; }
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }
.reportview-container .main .block-container { padding-top: 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0e14; }
::-webkit-scrollbar-thumb { background: #2a3545; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3a4f6e; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   HERO SECTION
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.hero-wrap {
    position: relative;
    width: 100%;
    padding: 56px 40px 44px;
    overflow: hidden;
    background: linear-gradient(135deg, #0d1420 0%, #111c2c 50%, #0a0e14 100%);
    border-bottom: 1px solid #1e2d45;
}
/* animated grid lines */
.hero-wrap::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(56,189,248,.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(56,189,248,.06) 1px, transparent 1px);
    background-size: 48px 48px;
    animation: gridDrift 25s linear infinite;
    pointer-events: none;
}
@keyframes gridDrift {
    0%   { background-position: 0 0; }
    100% { background-position: 48px 48px; }
}
/* accent glow blobs */
.hero-wrap::after {
    content: '';
    position: absolute;
    top: -60px; right: -80px;
    width: 420px; height: 420px;
    background: radial-gradient(circle, rgba(56,189,248,.12) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero-glow-left {
    position: absolute;
    bottom: -80px; left: -60px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(34,197,94,.08) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero-content { position: relative; z-index: 1; text-align: center; display: flex; flex-direction: column; align-items: center; }
.hero-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(56,189,248,.1);
    border: 1px solid rgba(56,189,248,.25);
    border-radius: 20px;
    padding: 5px 14px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #38bdf8;
    letter-spacing: 1.4px;
    text-transform: uppercase;
    margin-bottom: 18px;
}
.hero-badge .dot {
    width: 7px; height: 7px;
    background: #22c55e;
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(34,197,94,.5); }
    50%      { opacity: .7; box-shadow: 0 0 8px 3px rgba(34,197,94,.3); }
}
.hero-title {
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(26px, 3.8vw, 42px);
    font-weight: 700;
    color: #f0f4f8;
    line-height: 1.15;
    letter-spacing: -0.5px;
}
.hero-title span { color: #38bdf8; }
.hero-sub {
    margin-top: 14px;
    font-size: 15px;
    font-weight: 300;
    color: #6b7f99;
    max-width: 620px;
    line-height: 1.6;
    text-align: center;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   KPI METRIC CARDS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.kpi-row {
    display: flex; gap: 16px;
    padding: 24px 40px 0;
    flex-wrap: wrap;
    justify-content: center;
}
.kpi-card {
    flex: 1 1 180px; max-width: 260px;
    background: linear-gradient(145deg, #111c2c, #0d1520);
    border: 1px solid #1e2d45;
    border-radius: 14px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
    transition: border-color .3s, transform .2s;
}
.kpi-card:hover {
    border-color: #38bdf8;
    transform: translateY(-2px);
}
.kpi-card .kpi-accent {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.kpi-card:nth-child(1) .kpi-accent { background: linear-gradient(90deg, #38bdf8, #0ea5e9); }
.kpi-card:nth-child(2) .kpi-accent { background: linear-gradient(90deg, #22c55e, #16a34a); }
.kpi-card:nth-child(3) .kpi-accent { background: linear-gradient(90deg, #a78bfa, #7c3aed); }
.kpi-card:nth-child(4) .kpi-accent { background: linear-gradient(90deg, #fb923c, #ea580c); }

.kpi-label {
    font-size: 10.5px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #5a6e8a;
    margin-bottom: 10px;
}
.kpi-value {
    font-family: 'Orbitron', sans-serif;
    font-size: 26px;
    font-weight: 700;
    color: #f0f4f8;
    line-height: 1;
}
.kpi-unit {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #5a6e8a;
    margin-left: 4px;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   STREAMLIT TAB OVERRIDE
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.stTabs [data-baseid="tabs"] {
    background: #0a0e14 !important;
}
.stTabs [role="tablist"] {
    gap: 0 !important;
    border-bottom: 1px solid #1e2d45 !important;
    padding: 0 !important;
    background: transparent !important;
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
}
.stTabs [role="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #5a6e8a !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 10px 0 !important;
    border: none !important;
    background: transparent !important;
    transition: color .25s, background .25s !important;
    flex: 1 !important;
    max-width: 180px !important;
    text-align: center !important;
}
.stTabs [role="tab"]:hover {
    color: #c8d6e5 !important;
    background: rgba(56,189,248,.06) !important;
}
.stTabs [role="tab"][aria-selected="true"] {
    color: #38bdf8 !important;
    background: rgba(56,189,248,.08) !important;
    border-bottom: 2px solid #38bdf8 !important;
}
.stTabs [role="tabpanel"] {
    background: #0a0e14 !important;
    padding: 28px 24px !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   SECTION PANELS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.panel {
    background: linear-gradient(145deg, #111c2c, #0d1520);
    border: 1px solid #1e2d45;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 20px;
    position: relative;
}
.panel-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 13px;
    font-weight: 600;
    color: #38bdf8;
    text-transform: uppercase;
    letter-spacing: 1.6px;
    margin-bottom: 6px;
    display: flex; align-items: center; gap: 10px;
}
.panel-title .icon { font-size: 16px; }
.panel-desc {
    font-size: 13px;
    color: #5a6e8a;
    line-height: 1.6;
    margin-bottom: 18px;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   PIPELINE STEPPER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.pipeline {
    display: flex;
    flex-wrap: wrap;
    gap: 0;
    margin-top: 8px;
}
.step {
    flex: 1 1 160px;
    position: relative;
    display: flex; flex-direction: column; align-items: flex-start;
    padding: 0 16px 0 0;
}
.step:not(:last-child)::after {
    content: '→';
    position: absolute;
    right: -4px; top: 14px;
    color: #2a3545;
    font-size: 18px;
    font-weight: 300;
}
.step-num {
    width: 30px; height: 30px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Orbitron', sans-serif;
    font-size: 11px;
    font-weight: 700;
    margin-bottom: 10px;
}
.step-num.active { background: #38bdf8; color: #0a0e14; box-shadow: 0 0 12px rgba(56,189,248,.4); }
.step-num.done   { background: #22c55e; color: #0a0e14; }
.step-num.idle   { background: #1e2d45; color: #5a6e8a; }
.step-text {
    font-size: 12px;
    color: #8899b0;
    line-height: 1.45;
    max-width: 140px;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   OBJECTIVE CARDS (Overview)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.obj-row { display: flex; gap: 14px; flex-wrap: wrap; }
.obj-card {
    flex: 1 1 200px;
    background: #0d1520;
    border: 1px solid #1e2d45;
    border-radius: 12px;
    padding: 18px 20px;
    display: flex; gap: 14px; align-items: flex-start;
    transition: border-color .3s;
}
.obj-card:hover { border-color: #2a4a6e; }
.obj-icon {
    width: 36px; height: 36px; min-width: 36px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px;
}
.obj-icon.blue  { background: rgba(56,189,248,.15); }
.obj-icon.green { background: rgba(34,197,94,.15); }
.obj-icon.purple{ background: rgba(167,139,250,.15); }
.obj-card-title { font-size: 13px; font-weight: 600; color: #c8d6e5; margin-bottom: 4px; }
.obj-card-desc  { font-size: 11.5px; color: #5a6e8a; line-height: 1.5; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   INSIGHT BANNER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.insight-banner {
    background: linear-gradient(135deg, rgba(56,189,248,.08), rgba(167,139,250,.06));
    border: 1px solid rgba(56,189,248,.2);
    border-radius: 12px;
    padding: 18px 22px;
    display: flex; gap: 14px; align-items: flex-start;
    margin-top: 16px;
}
.insight-banner .bulb { font-size: 22px; }
.insight-banner p { font-size: 13px; color: #8899b0; line-height: 1.6; }
.insight-banner strong { color: #38bdf8; font-weight: 500; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   DATAFRAME OVERRIDE
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.stDataFrame {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid #1e2d45 !important;
}
.stDataFrame table {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 12.5px !important;
}
.stDataFrame thead th {
    background: #111c2c !important;
    color: #38bdf8 !important;
    font-size: 10.5px !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    border-bottom: 1px solid #1e2d45 !important;
    padding: 10px 14px !important;
}
.stDataFrame tbody tr { border-bottom: 1px solid #141e2e !important; }
.stDataFrame tbody tr:hover { background: rgba(56,189,248,.04) !important; }
.stDataFrame tbody td {
    color: #c8d6e5 !important;
    padding: 9px 14px !important;
    background: #0d1520 !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   IMAGE CONTAINER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.img-frame {
    border: 1px solid #1e2d45;
    border-radius: 12px;
    overflow: hidden;
    background: #0d1520;
    padding: 12px;
    max-width: 65%;
    margin: 0 auto;
}
.img-frame img { border-radius: 8px; width: 100%; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   RADIO / SELECTBOX OVERRIDES
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.stRadio > div { flex-direction: row !important; gap: 12px !important; }
.stRadio label, .stSelectbox label {
    color: #8899b0 !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}
.stRadio [class*="radioLabel"] {
    color: #c8d6e5 !important;
    font-size: 13px !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TAG PILL (buffer info)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.tag {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(56,189,248,.1);
    border: 1px solid rgba(56,189,248,.2);
    border-radius: 6px;
    padding: 4px 10px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #38bdf8;
    margin-right: 6px;
}
.tag.green { background: rgba(34,197,94,.1); border-color: rgba(34,197,94,.2); color: #22c55e; }
.tag.amber { background: rgba(251,146,60,.1); border-color: rgba(251,146,60,.2); color: #fb923c; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   LINK SELECTOR BUTTONS (Traffic Viz)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.link-btn-row { display: flex; gap: 10px; margin-bottom: 20px; }
.link-btn {
    flex: 1;
    background: #0d1520;
    border: 1px solid #1e2d45;
    border-radius: 10px;
    padding: 12px 16px;
    text-align: center;
    cursor: pointer;
    transition: all .25s;
    text-decoration: none;
}
.link-btn:hover { border-color: #38bdf8; background: rgba(56,189,248,.06); }
.link-btn.active { border-color: #38bdf8; background: rgba(56,189,248,.1); }
.link-btn-label { font-family: 'Orbitron', sans-serif; font-size: 12px; color: #c8d6e5; font-weight: 600; }
.link-btn-sub { font-size: 10px; color: #5a6e8a; margin-top: 3px; font-family: 'Share Tech Mono', monospace; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   WARNING CARD
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.warn-card {
    background: rgba(251,146,60,.08);
    border: 1px solid rgba(251,146,60,.25);
    border-radius: 10px;
    padding: 16px 20px;
    display: flex; gap: 12px; align-items: flex-start;
}
.warn-card p { font-size: 13px; color: #c8d6e5; line-height: 1.5; }
.warn-card strong { color: #fb923c; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TEAM NAME (hero)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.team-name-wrap {
    margin-top: 22px;
    display: flex; align-items: center; justify-content: center; gap: 10px;
}
.team-name-label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #3a4f6e;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
}
.team-name {
    font-family: 'Share Tech Mono', monospace;
    font-size: 15px;
    color: #38bdf8;
    background: rgba(56,189,248,.08);
    border: 1px solid rgba(56,189,248,.22);
    border-radius: 8px;
    padding: 6px 16px;
    letter-spacing: 0.5px;
}
.team-name .bracket { color: #3a4f6e; }

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   TEAM MEMBER CARDS
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.team-row {
    display: flex; gap: 16px; flex-wrap: wrap;
    justify-content: center;
}
.team-card {
    flex: 1 1 180px; max-width: 220px;
    background: #0d1520;
    border: 1px solid #1e2d45;
    border-radius: 14px;
    padding: 24px 18px 20px;
    text-align: center;
    transition: border-color .3s, transform .2s;
    position: relative;
    overflow: hidden;
}
.team-card:hover {
    border-color: #38bdf8;
    transform: translateY(-3px);
}
.team-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.team-card:nth-child(1)::before { background: linear-gradient(90deg, #38bdf8, #0ea5e9); }
.team-card:nth-child(2)::before { background: linear-gradient(90deg, #22c55e, #16a34a); }
.team-card:nth-child(3)::before { background: linear-gradient(90deg, #a78bfa, #7c3aed); }
.team-card:nth-child(4)::before { background: linear-gradient(90deg, #fb923c, #ea580c); }

.team-avatar {
    width: 82px; height: 82px;
    border-radius: 50%;
    margin: 0 auto 14px;
    overflow: hidden;
    border: 3px solid #1e2d45;
    background: #111c2c;
    display: flex; align-items: center; justify-content: center;
}
.team-avatar img {
    width: 100%; height: 100%;
    object-fit: cover;
}
.team-avatar .avatar-placeholder {
    font-family: 'Orbitron', sans-serif;
    font-size: 26px;
    font-weight: 700;
    color: #2a3545;
}
.team-name-card {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 600;
    color: #f0f4f8;
    margin-bottom: 4px;
}
.team-role {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10.5px;
    color: #5a6e8a;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   FOOTER
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
.app-footer {
    margin-top: 40px;
    padding: 22px 40px;
    border-top: 1px solid #1e2d45;
    display: flex; justify-content: space-between; align-items: center;
}
.app-footer .logo { font-family: 'Orbitron', sans-serif; font-size: 11px; color: #2a3545; letter-spacing: 2px; text-transform: uppercase; }
.app-footer .meta { font-size: 11px; color: #3a4f6e; font-family: 'Share Tech Mono', monospace; }
</style>
""", unsafe_allow_html=True)


# =====================================================
# HERO SECTION
# =====================================================
st.markdown("""
<div class="hero-wrap">
  <div class="hero-glow-left"></div>
  <div class="hero-content">
    <div class="hero-badge"><span class="dot"></span>Live Dashboard — Fronthaul Analysis</div>
    <h1 class="hero-title">Intelligent Fronthaul <span>Network Optimization</span></h1>
    <p class="hero-sub">
      Correlation-driven topology identification and per-link capacity estimation
      built on historical traffic logs — designed to keep packet loss under 1%.
    </p>
    <div class="team-name-wrap">
      <span class="team-name-label">Presented by</span>
      <span class="team-name"><span class="bracket">&lt;</span>npm install regrets<span class="bracket"> /&gt;</span></span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# =====================================================
# KPI METRIC CARDS  (read from CSVs where possible)
# =====================================================

# -- try to pull real numbers from capacity CSVs --
n_cells, n_links, max_cap, pkt_loss_pct = "—", "—", "—", "≤ 1%"
try:
    _map = pd.read_csv(os.path.join(OUTPUT_DIR, "member3", "cell_to_link_mapping.csv"))
    n_cells = str(len(_map))
    n_links = str(_map.iloc[:, 1].nunique()) if _map.shape[1] > 1 else "—"
except Exception:
    pass
try:
    _cap = pd.read_csv(os.path.join(OUTPUT_DIR, "capacity", "required_capacity_with_buffer.csv"))
    # pick the largest numeric value in any column that looks like capacity (Mbps)
    numeric_cols = _cap.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        max_val = _cap[numeric_cols].max().max()
        max_cap = f"{max_val:.1f}"
except Exception:
    pass

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-accent"></div>
    <div class="kpi-label">Total Cells</div>
    <div class="kpi-value">{n_cells}<span class="kpi-unit">cells</span></div>
  </div>
  <div class="kpi-card">
    <div class="kpi-accent"></div>
    <div class="kpi-label">Fronthaul Links</div>
    <div class="kpi-value">{n_links}<span class="kpi-unit">links</span></div>
  </div>
  <div class="kpi-card">
    <div class="kpi-accent"></div>
    <div class="kpi-label">Max Link Capacity</div>
    <div class="kpi-value">{max_cap}<span class="kpi-unit">Mbps</span></div>
  </div>
  <div class="kpi-card">
    <div class="kpi-accent"></div>
    <div class="kpi-label">Packet-Loss Target</div>
    <div class="kpi-value">{pkt_loss_pct}<span class="kpi-unit">slots</span></div>
  </div>
</div>
""", unsafe_allow_html=True)


# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "⬡  Overview",
    "🔗  Topology",
    "📊  Capacity",
    "📈  Traffic",
    "⚡  Snapshot"
])


# =====================================================
# TAB 1 — OVERVIEW
# =====================================================
with tab1:

    # --- team intro ---
    # ┌─────────────────────────────────────────────────────────────────┐
    # │  HOW TO CHANGE NAMES                                            │
    # │    Just edit the first string in each tuple below.              │
    # │    Example: ("Rahul Mehta", "Data Engineer", "")                │
    # │                                                                 │
    # │  HOW TO ADD PHOTOS                                              │
    # │    1. Place your photo files (JPG/PNG) in a folder called       │
    # │       'assets/' in the SAME directory as this app.py            │
    # │           project/                                               │
    # │             ├── app.py          ← this file                     │
    # │             └── assets/                                         │
    # │                   ├── photo1.jpg                                │
    # │                   ├── photo2.jpg                                │
    # │                   ├── photo3.jpg                                │
    # │                   └── photo4.jpg                                │
    # │    2. Set the third string to "assets/photo1.jpg" etc.          │
    # │    3. Photos are auto-cropped into the circular avatar.         │
    # │    Leave the path as "" to show the letter-initial fallback.    │
    # └─────────────────────────────────────────────────────────────────┘
    TEAM = [
        ("Rashi Goyal",  "Signal Processing & Correlation Analysis Lead",     "assets/photo1.jpeg"),   # ← ("Real Name", "Role", "assets/photo1.jpg")
        ("Priyanshu Raj",  "Capacity Estimation, Visualization & Frontend Lead",      "assets/photo2.jpeg"),   # ← ("Real Name", "Role", "assets/photo2.jpg")
        ("Shadman Nishat",  "Topology Inference & Traffic Modeling Lead",    "assets/photo3.jpeg"),   # ← ("Real Name", "Role", "assets/photo3.jpg")
        ("Harshit Badera",  "Data Engineering & Preprocessing Lead", "assets/photo4.jpeg"),   # ← ("Real Name", "Role", "assets/photo4.jpg")
    ]

    _APP_DIR = os.path.dirname(os.path.abspath(__file__))   # folder containing app.py

    avatar_cards_html = ""
    for name, role, photo in TEAM:
        initials = "".join(w[0].upper() for w in name.split())[:2]
        if photo:
            full_photo_path = os.path.join(_APP_DIR, photo)   # resolve relative to app.py
            b64 = img_to_base64(full_photo_path)
            inner = f'<img src="data:image/png;base64,{b64}" />' if b64 else f'<span class="avatar-placeholder">{initials}</span>'
        else:
            inner = f'<span class="avatar-placeholder">{initials}</span>'
        avatar_cards_html += f"""
        <div class="team-card">
          <div class="team-avatar">{inner}</div>
          <div class="team-name-card">{name}</div>
          <div class="team-role">{role}</div>
        </div>"""

    st.markdown(f"""
    <div class="panel">
      <div class="panel-title" style="justify-content:center; margin-bottom:18px;"><span class="icon">👥</span> Our Team</div>
      <div class="team-row">{avatar_cards_html}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- objective cards ---
    st.markdown("""
    <div class="panel">
      <div class="panel-title"><span class="icon">◈</span> Problem Objectives</div>
      <div class="obj-row">
        <div class="obj-card">
          <div class="obj-icon blue">🔍</div>
          <div>
            <div class="obj-card-title">Topology Discovery</div>
            <div class="obj-card-desc">Identify which cells share the same physical fronthaul Ethernet links using correlated loss patterns.</div>
          </div>
        </div>
        <div class="obj-card">
          <div class="obj-icon green">⚡</div>
          <div>
            <div class="obj-card-title">Capacity Estimation</div>
            <div class="obj-card-desc">Compute the minimum required link capacity per fronthaul segment to sustain expected traffic load.</div>
          </div>
        </div>
        <div class="obj-card">
          <div class="obj-icon purple">🎯</div>
          <div>
            <div class="obj-card-title">Loss Constraint</div>
            <div class="obj-card-desc">Guarantee packet loss stays at or below 1% of all traffic slots across every estimated link.</div>
          </div>
        </div>
      </div>

      <div class="insight-banner">
        <span class="bulb">💡</span>
        <p><strong>Core Insight:</strong> Cells that share a fronthaul link experience <strong>simultaneous packet loss</strong> during congestion events. By measuring the Pearson correlation of per-slot loss indicators, we can reliably cluster cells into groups — each group maps to one physical link.</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # --- pipeline stepper ---
    st.markdown("""
    <div class="panel">
      <div class="panel-title"><span class="icon">⟳</span> Solution Pipeline</div>
      <div class="pipeline">
        <div class="step">
          <div class="step-num done">1</div>
          <div class="step-text"><strong style="color:#c8d6e5">Preprocess</strong><br>Clean throughput &amp; packet-loss time-series</div>
        </div>
        <div class="step">
          <div class="step-num done">2</div>
          <div class="step-text"><strong style="color:#c8d6e5">Correlate</strong><br>Compute pairwise loss correlation matrix</div>
        </div>
        <div class="step">
          <div class="step-num done">3</div>
          <div class="step-text"><strong style="color:#c8d6e5">Cluster</strong><br>Threshold-based grouping into links</div>
        </div>
        <div class="step">
          <div class="step-num done">4</div>
          <div class="step-text"><strong style="color:#c8d6e5">Aggregate</strong><br>Sum per-slot traffic across each group</div>
        </div>
        <div class="step">
          <div class="step-num done">5</div>
          <div class="step-text"><strong style="color:#c8d6e5">Estimate</strong><br>Capacity with &amp; without buffer margin</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# TAB 2 — TOPOLOGY IDENTIFICATION
# =====================================================
with tab2:

    # --- heatmap ---
    heatmap_path = os.path.join(OUTPUT_DIR, "member3", "correlation_heatmap.png")
    st.markdown("""
    <div class="panel">
      <div class="panel-title"><span class="icon">◈</span> Correlation Heatmap</div>
      <div class="panel-desc">Each cell in the matrix shows the Pearson correlation of packet-loss indicators between two cells. Bright clusters reveal shared fronthaul links.</div>
    </div>
    """, unsafe_allow_html=True)

    hm_b64 = img_to_base64(heatmap_path)
    if hm_b64:
        st.markdown(f'<div class="img-frame"><img src="data:image/png;base64,{hm_b64}" /></div>', unsafe_allow_html=True)
    else:
        st.image(heatmap_path, use_container_width=True)

    st.markdown("""
    <div class="insight-banner" style="margin-top:18px; margin-bottom:8px;">
      <span class="bulb">📖</span>
      <p>
        <strong>How to read this heatmap:</strong> Each row and column represents one base-station cell.
        The colour intensity at position (i, j) is the Pearson correlation coefficient of the per-slot packet-loss
        binary signals of cell <em>i</em> and cell <em>j</em>. A value close to <strong>1.0</strong> (bright) means the two cells
        lose packets at almost exactly the same time slots — the strongest evidence that they share a single
        physical Ethernet fronthaul link. Cells that correlate weakly (dark) are served by independent links.
        The algorithm applies a fixed threshold (typically &ge; 0.8) to partition the matrix into discrete groups,
        each group mapping to one fronthaul segment.
      </p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown("""
        <div class="panel" style="margin-bottom:0">
          <div class="panel-title"><span class="icon">📋</span> Cell → Link Mapping</div>
          <div class="panel-desc">Each cell is assigned to exactly one fronthaul link.</div>
        </div>
        """, unsafe_allow_html=True)
        try:
            df_map = pd.read_csv(os.path.join(OUTPUT_DIR, "member3", "cell_to_link_mapping.csv"))
            st.dataframe(df_map, use_container_width=True, hide_index=True)
        except FileNotFoundError:
            st.warning("cell_to_link_mapping.csv not found.")

    with col2:
        st.markdown("""
        <div class="panel" style="margin-bottom:0">
          <div class="panel-title"><span class="icon">🔗</span> Group-wise Link Topology</div>
          <div class="panel-desc">Summary of which cells belong to each discovered link group.</div>
        </div>
        """, unsafe_allow_html=True)
        try:
            df_group = pd.read_csv(os.path.join(OUTPUT_DIR, "member3", "link_groupwise_table.csv"))
            st.dataframe(df_group, use_container_width=True, hide_index=True)
        except FileNotFoundError:
            st.warning("link_groupwise_table.csv not found.")


# =====================================================
# TAB 3 — CAPACITY ESTIMATION
# =====================================================
with tab3:

    st.markdown("""
    <div class="panel">
      <div class="panel-title"><span class="icon">◈</span> Required Link Capacity</div>
      <div class="panel-desc">Toggle between buffered and unbuffered estimation modes. Buffer adds a 4-symbol (143 μs) margin to absorb short bursts.</div>
    </div>
    """, unsafe_allow_html=True)

    # interactive toggle
    col_mode1, col_mode2, _ = st.columns([1, 1, 2])
    with col_mode1:
        no_buf = st.button("⚡  Without Buffer", use_container_width=True,
                           key="btn_no_buf",
                           help="Direct capacity — no buffering margin")
    with col_mode2:
        with_buf = st.button("🛡️  With Buffer", use_container_width=True,
                             key="btn_with_buf",
                             help="Adds 4-symbol buffer (143 μs)")

    # keep state via session
    if "cap_mode" not in st.session_state:
        st.session_state["cap_mode"] = "no_buffer"
    if no_buf:
        st.session_state["cap_mode"] = "no_buffer"
    if with_buf:
        st.session_state["cap_mode"] = "with_buffer"

    if st.session_state["cap_mode"] == "with_buffer":
        cap_file = "required_capacity_with_buffer.csv"
        st.markdown("""
        <div style="margin:12px 0 20px">
          <span class="tag green">✓ Buffer Enabled</span>
          <span class="tag">4 symbols · 143 μs</span>
          <span class="tag green">Packet loss ≤ 1%</span>
        </div>""", unsafe_allow_html=True)
    else:
        cap_file = "required_capacity_no_buffer.csv"
        st.markdown("""
        <div style="margin:12px 0 20px">
          <span class="tag amber">⚠ No Buffer</span>
          <span class="tag">Direct estimation</span>
          <span class="tag green">Packet loss ≤ 1%</span>
        </div>""", unsafe_allow_html=True)

    try:
        df_cap = pd.read_csv(os.path.join(OUTPUT_DIR, "capacity", cap_file))
        st.dataframe(df_cap, use_container_width=True, hide_index=True)

        # quick download
        st.download_button(
            label="⬇  Export CSV",
            data=df_cap.to_csv(index=False),
            file_name=cap_file,
            mime="text/csv"
        )
    except FileNotFoundError:
        st.warning(f"{cap_file} not found in output/capacity/.")

    st.markdown("""
    <div class="insight-banner" style="margin-top:22px;">
      <span class="bulb">📖</span>
      <p>
        <strong>How capacity is estimated:</strong> For every identified fronthaul link, we sum the per-slot throughput
        of all cells belonging to that link across the full 60-second observation window. The required capacity is then
        set to the smallest value that keeps the number of slots where the aggregate traffic exceeds the link capacity
        at or below <strong>1 %</strong> of total slots — this is the packet-loss constraint. When the <strong>buffer mode</strong> is enabled,
        an additional 4-symbol (143 &mu;s) look-ahead window is added so that short bursts can be absorbed without
        immediate packet drops, resulting in a lower (more realistic) capacity requirement for the same loss target.
      </p>
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# TAB 4 — TRAFFIC VISUALIZATION
# =====================================================
with tab4:

    st.markdown("""
    <div class="panel">
      <div class="panel-title"><span class="icon">◈</span> Per-Slot Aggregated Traffic</div>
      <div class="panel-desc">60-second traffic profile for the selected fronthaul link, with the estimated required capacity shown as an overlay threshold.</div>
    </div>
    """, unsafe_allow_html=True)

    # -- interactive link selector --
    links = ["Link 1", "Link 2", "Link 3"]
    if "sel_link" not in st.session_state:
        st.session_state["sel_link"] = "Link 1"

    cols_link = st.columns(len(links))
    for i, lnk in enumerate(links):
        active_cls = "active" if st.session_state["sel_link"] == lnk else ""
        # use a real Streamlit button styled via class hack
        clicked = cols_link[i].button(
            f"Link {i+1}",
            use_container_width=True,
            key=f"link_btn_{i}",
            help=f"View traffic for {lnk}"
        )
        if clicked:
            st.session_state["sel_link"] = lnk

    selected_link = st.session_state["sel_link"]
    fig_path = os.path.join(OUTPUT_DIR, "figures", f"figure3_{selected_link.replace(' ', '_')}.png")

    fig_b64 = img_to_base64(fig_path)
    if fig_b64:
        st.markdown(f'<div class="img-frame"><img src="data:image/png;base64,{fig_b64}" /></div>', unsafe_allow_html=True)
    elif os.path.exists(fig_path):
        st.image(fig_path, use_container_width=True)
    else:
        st.markdown(f"""
        <div class="warn-card">
          <span style="font-size:22px">⚠️</span>
          <p><strong>Figure not found</strong> — <code>figure3_{selected_link.replace(' ', '_')}.png</code> is missing from the output/figures/ directory.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:14px; display:flex; gap:16px; align-items:center">
      <span class="tag">Selected: {selected_link}</span>
      <span style="font-size:11px; color:#3a4f6e; font-family:'Share Tech Mono',monospace">60s window · capacity overlay included</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="insight-banner" style="margin-top:20px;">
      <span class="bulb">📖</span>
      <p>
        <strong>How to read this plot:</strong> The <strong>blue trace</strong> is the aggregate per-slot throughput for all cells assigned to
        the selected fronthaul link, sampled every 143 &mu;s (one OFDM symbol period) over a 60-second window.
        The <strong>horizontal red line</strong> marks the estimated required link capacity — any slot where the blue trace
        exceeds this line results in a packet drop. The algorithm guarantees that no more than <strong>1 %</strong> of all slots
        breach this threshold. Switching between links lets you compare traffic profiles and verify that the capacity
        estimates are appropriate for each segment independently.
      </p>
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# TAB 5 — TRAFFIC SNAPSHOT
# =====================================================
with tab5:

    st.markdown("""
    <div class="panel">
      <div class="panel-title"><span class="icon">◈</span> Correlated Traffic-Loss Snapshot</div>
      <div class="panel-desc">A short time-window zoom showing how cells on the same link experience synchronized packet loss during congestion bursts.</div>
    </div>
    """, unsafe_allow_html=True)

    snapshot_path = os.path.join(OUTPUT_DIR, "member3", "traffic_snapshot.png")
    snap_b64 = img_to_base64(snapshot_path)

    if snap_b64:
        st.markdown(f'<div class="img-frame"><img src="data:image/png;base64,{snap_b64}" /></div>', unsafe_allow_html=True)
    elif os.path.exists(snapshot_path):
        st.image(snapshot_path, use_container_width=True)
    else:
        st.markdown("""
        <div class="warn-card">
          <span style="font-size:22px">⚠️</span>
          <p><strong>Snapshot not generated</strong> — run <code>src/member3_traffic_snapshot.py</code> to produce the traffic_snapshot.png asset.</p>
        </div>""", unsafe_allow_html=True)

    # correlation context card
    st.markdown("""
    <div class="insight-banner" style="margin-top:20px">
      <span class="bulb">📖</span>
      <p>
        <strong>How to read this snapshot:</strong> The horizontal axis is time (a short sub-window of the full 60-second log,
        zoomed in to make individual symbol slots visible). Each row is one cell. A <strong>coloured mark</strong> at a given
        slot means that cell experienced a packet drop in that slot. Notice how cells that belong to the
        <strong>same fronthaul link</strong> always drop packets in the <em>exact same columns</em> — their loss events are perfectly
        aligned. This synchronisation is the statistical signature the algorithm exploits: it would be
        extraordinarily unlikely for independent links to produce identical drop patterns by chance.
        Cells on <em>different</em> links show no such alignment, confirming the topology inference is correct.
      </p>
    </div>
    """, unsafe_allow_html=True)


# =====================================================
# FOOTER
# =====================================================
st.markdown("""
<div class="app-footer">
  <div class="logo">◈ Fronthaul Optimizer</div>
  <div class="meta" style="font-family:'Share Tech Mono',monospace; color:#2a3a56;">&lt;npm install regrets /&gt; &nbsp;·&nbsp; Correlation · Clustering · Capacity Estimation — v1.0</div>
</div>
""", unsafe_allow_html=True)