from __future__ import annotations


# streamlit_app.py
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple
import statistics
import math


import streamlit as st
import pandas as pd
import plotly.express as px
import pathlib
from html import escape as html_escape
import plotly.graph_objects as go
import numpy as np

# Configure the page before any other Streamlit UI/state commands. Keep
# the sidebar expanded initially; users can still collapse/reopen it normally.
st.set_page_config(
    page_title="PETAL",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_TITLE = "PETAL - Participatory Evaluation Tool for Analysis from an early Lifestage"
APP_TAGLINE = "Participatory sustainability assessment for early-stage innovation"
APP_ROOT = pathlib.Path(__file__).resolve().parent

# Brand colors sampled from the supplied, original PETAL logo.
# They also encode the three dimensions in the petal figures.
PALETTE = {
    "ink": "#2C2726", "charcoal": "#2C2726", "green": "#24BB7A",
    "orange": "#F28500", "red": "#D6463C", "green_dark": "#13784F",
    "paper": "#FAFAF8", "white": "#FFFFFF", "muted": "#6E6C68",
    "line": "#E9E8E3", "sidebar": "#FFFFFF", "quiet": "#F4F4F0",
    "environmental": "#24BB7A", "social": "#D6463C", "economic": "#F28500",
    "good": "#24BB7A", "bad": "#D6463C", "mixed": "#F28500", "na": "#B7B8B3",
}
PLOT_FONT = "Inter, ui-sans-serif, system-ui, Segoe UI, sans-serif"
DIMENSION_COLORS = {k: PALETTE[k.lower()] for k in ("Environmental", "Social", "Economic")}
LOGO_MARK = APP_ROOT / "assets" / "petal_logo.svg"


def mark_data() -> str:
    """The supplied PETAL mark, prepared as a transparent sidebar/hero asset."""
    if not LOGO_MARK.exists():
        return ""
    import base64
    return "data:image/png;base64," + base64.b64encode(LOGO_MARK.read_bytes()).decode("ascii")


def inject_theme() -> None:
    """Style the native, keyboard-accessible Streamlit controls."""
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
      :root { --ink:#2C2726; --green:#24BB7A; --deep-green:#13784F;
          --orange:#F28500; --red:#D6463C; --paper:#FAFAF8; --muted:#6E6C68;
          --line:#E9E8E3; --quiet:#F4F4F0; --card:#FFFFFF; }
      html, body, [data-testid="stAppViewContainer"] {
          background:var(--paper); color:var(--ink); font-family:'DM Sans',system-ui,sans-serif;
      }
      [data-testid="stHeader"] {background:rgba(250,250,248,.92); border-bottom:1px solid rgba(233,232,227,.45);}
      [data-testid="stSidebar"] {background:#fff; border-right:1px solid var(--line);}
      [data-testid="stSidebar"] [data-testid="stSidebarContent"] {padding-top:1.4rem; padding-left:1rem; padding-right:1rem;}
      footer {display:none;}
      .block-container {max-width:1280px; padding:1.8rem 2.4rem 4rem;}
      h1,h2,h3,h4,h5 {font-family:'DM Sans',system-ui,sans-serif; color:var(--ink); letter-spacing:-.035em;}
      h1 {font-weight:800;}
      h2,h3 {font-weight:750;}
      [data-testid="stCaptionContainer"] {color:var(--muted);}
      [data-testid="stMetric"] {background:#fff; border:1px solid var(--line);
          border-radius:16px; padding:.95rem 1.1rem;}
      [data-testid="stMetricValue"] {color:var(--ink);}
      [data-testid="stMetricLabel"] {color:var(--muted);}
      [data-testid="stVerticalBlockBorderWrapper"] > div {
          border-radius:16px!important; border-color:var(--line)!important; background:#fff;
      }
      [data-testid="stExpander"] {border:1px solid var(--line);border-radius:14px;
          overflow:hidden;background:#fff;}
      [data-testid="stExpander"] summary {font-weight:650;}
      div.stButton button, div.stDownloadButton button {border-radius:12px;
          font-weight:700; min-height:2.65rem; transition:all .16s ease;}
      div.stButton button[kind="primary"],div.stDownloadButton button[kind="primary"] {
          background:var(--green);color:#142C20;border-color:var(--green);}
      div.stButton button[kind="primary"]:hover, div.stDownloadButton button[kind="primary"]:hover {
          background:#1AD384;border-color:#1AD384;color:#142C20;}
      div.stButton button:not([kind="primary"]):hover,div.stDownloadButton button:not([kind="primary"]):hover {
          border-color:var(--green);color:var(--deep-green);}
      div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div,
      div[data-baseweb="select"] > div {border-radius:12px;}
      div[data-baseweb="tab-list"] {gap:.5rem; border-bottom:1px solid var(--line);}
      button[data-baseweb="tab"] {font-weight:700;}
      [data-testid="stProgressBar"] [role="progressbar"] > div {background:var(--deep-green);}
      hr {border-color:var(--line);}
      .petal-lockup {display:flex;gap:.8rem;align-items:center;padding:.15rem .05rem 1.3rem;}
      .petal-lockup img {height:56px;width:46px;object-fit:contain;}
      .petal-lockup strong {font-family:Georgia,'Times New Roman',serif;font-size:1.84rem;
          letter-spacing:-.055em;color:var(--ink);line-height:1.08;}
      .petal-lockup small {display:block;font-size:.66rem;letter-spacing:.13em;
          font-weight:800;color:var(--muted);margin-top:.32rem;}
      .petal-side-project {border:1px solid var(--line);border-radius:16px;
          padding:1rem 1rem;margin:.1rem 0 1.25rem;background:#FAFAF8;}
      .petal-side-project small {display:block;font-size:.67rem;letter-spacing:.1em;
          color:var(--muted);font-weight:800;margin-bottom:.3rem;}
      .petal-side-project strong {display:block;font-size:.95rem;font-weight:800;
          overflow-wrap:anywhere;line-height:1.4;color:#203A31;}
      .petal-side-project span {font-size:.8rem;color:var(--muted);}
      .petal-nav-heading {font-size:.67rem;letter-spacing:.13em;font-weight:800;
          color:#918E8A;margin:.75rem 0 .28rem .55rem;}
      [data-testid="stSidebar"] [class*="st-key-petal_nav_"] button {
          border:0!important; background:transparent!important; color:#5A5652!important;
          padding:.72rem .85rem!important; border-radius:12px!important; justify-content:flex-start!important;
          width:100%;font-size:.94rem; font-weight:650; box-shadow:none!important;
      }
      [data-testid="stSidebar"] [class*="st-key-petal_nav_"] button:hover {
          background:#F3F8F4!important;color:var(--ink)!important;
      }
      [data-testid="stSidebar"] [class*="st-key-petal_nav_active_"] button {
          color:var(--deep-green)!important; background:#E8F8EF!important; font-weight:800!important;
          box-shadow:inset 3px 0 0 var(--green)!important;
      }
      .petal-tiny-progress {height:5px;background:#EDEDE9;border-radius:99px;overflow:hidden;margin:.45rem .5rem 1rem;}
      .petal-tiny-progress div {height:100%;background:var(--green);border-radius:99px;}
      .petal-page-intro {margin:.08rem 0 1.45rem;display:flex;justify-content:space-between;
          gap:1rem;align-items:flex-end;}
      .petal-kicker {color:var(--deep-green);font-size:.72rem;letter-spacing:.12em;font-weight:800;}
      .petal-page-intro h1 {font-size:clamp(1.95rem,3.2vw,2.7rem);margin:.25rem 0 .36rem;line-height:1.16;}
      .petal-page-intro p {font-size:1rem;color:var(--muted);margin:0;line-height:1.6;max-width:760px;}
      .petal-page-index {font-size:.82rem;font-weight:750;color:#99958F;white-space:nowrap;padding-bottom:.3rem;}
      .petal-workspace {display:flex;flex-wrap:wrap;align-items:center;gap:.55rem;
          padding:.15rem 0 .55rem;color:#8A8680;font-size:.76rem;}
      .petal-workspace strong {color:var(--ink);font-size:.81rem;}
      .petal-project-tag {border:1px solid var(--line);background:white;border-radius:99px;
          padding:.22rem .68rem;font-size:.72rem;font-weight:750;color:var(--deep-green);}
      .petal-projectstrip {display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap;
          border:1px solid var(--line); border-radius:16px; background:#fff; padding:.85rem 1rem; margin:0 0 1.35rem;}
      .petal-projectstrip .petal-small {color:var(--muted); font-size:.92rem;}
      .petal-stagechip {border-radius:999px; background:#F3F8F4; color:var(--deep-green);
          padding:.32rem .75rem; font-size:.76rem; font-weight:750; border:1px solid #E0F1E6;}
      .petal-home-hero {border:1px solid var(--line);background:linear-gradient(120deg,#fff 0%,#fff 52%,#F3F8F3 100%);
          border-radius:26px;display:grid;grid-template-columns:1.55fr .75fr;gap:1.6rem;
          align-items:center;padding:clamp(1.7rem,4vw,3.15rem);margin:.25rem 0 1.7rem;overflow:hidden;}
      .petal-home-hero .kicker {font-size:.73rem;font-weight:800;letter-spacing:.12em;color:var(--deep-green);}
      .petal-home-hero h1 {font-size:clamp(2rem,4.4vw,3.55rem);letter-spacing:-.055em;
          margin:.65rem 0 .8rem;line-height:1.12;max-width:710px;}
      .petal-home-hero p {font-size:1rem;line-height:1.68;max-width:580px;color:var(--muted);margin:0;}
      .petal-hero-mark {height:240px;width:205px;max-width:100%;object-fit:contain;
          margin:auto;filter:drop-shadow(0 17px 28px rgba(40,40,40,.055));}
      .petal-flow {display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:.6rem;
          margin:1rem 0 1.65rem;}
      .petal-flow-step {background:#fff;border:1px solid var(--line);border-radius:14px;
          padding:.9rem .85rem;min-height:90px;}
      .petal-flow-dot {display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:.42rem;
          background:var(--green);}
      .petal-flow-step strong {font-size:.85rem;color:var(--ink);}
      .petal-flow-step p {font-size:.77rem;color:var(--muted);margin:.42rem 0 0;line-height:1.5;}
      .petal-dimension-head {display:flex;gap:.65rem;align-items:center;margin:.9rem 0 .8rem;}
      .petal-dimension-dot {width:10px;height:10px;border-radius:99px;flex-shrink:0;}
      .petal-dimension-head strong {font-size:1rem;color:var(--ink);}
      .petal-scale-strip {display:flex;gap:.55rem;align-items:center;flex-wrap:wrap;
          font-size:.75rem;color:var(--muted);margin:.5rem 0 1rem;}
      .petal-scale-strip span {padding:.34rem .58rem;border-radius:9px;background:#fff;border:1px solid var(--line);}
      .petal-hint {color:var(--muted);font-size:.82rem;}
      .petal-footer-note {padding:1.2rem 0 0;border-top:1px solid var(--line);
          color:#8D8B86;font-size:.77rem;}
      .petal-score-guide {display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:.55rem;margin:.55rem 0 1rem;}
      .petal-score-guide .item {background:#fff;border:1px solid var(--line);border-radius:14px;padding:.75rem .65rem;min-height:86px;}
      .petal-score-guide .num {display:inline-flex;align-items:center;justify-content:center;width:1.9rem;height:1.9rem;
          border-radius:999px;font-weight:800;font-size:.9rem;margin-bottom:.5rem;color:#fff;}
      .petal-score-guide .lab {display:block;font-size:.8rem;font-weight:700;color:var(--ink);line-height:1.35;}
      .petal-score-guide .sub {display:block;font-size:.73rem;color:var(--muted);line-height:1.4;margin-top:.18rem;}
      .petal-score-guide .i1 .num {background:#D6463C;}
      .petal-score-guide .i2 .num {background:#E97A2E;}
      .petal-score-guide .i3 .num {background:#8E8C87;}
      .petal-score-guide .i4 .num {background:#56B975;}
      .petal-score-guide .i5 .num {background:#24BB7A;}
      .petal-assumption-box {border:1px solid var(--line);border-radius:16px;background:#fff;padding:1rem 1rem .85rem;margin:1rem 0 1.1rem;}
      .petal-assumption-box h4 {margin:.1rem 0 .25rem;font-size:1rem;}
      .petal-assumption-box p {margin:0;color:var(--muted);font-size:.84rem;line-height:1.55;}

      @media (min-width: 980px) {
          [data-testid="stSidebar"] {min-width:330px!important; max-width:330px!important;}
          [data-testid="collapsedControl"] {display:none;}
      }
      @media (max-width:980px) {
          .block-container {padding:1.3rem 1rem 3rem;}
          .petal-home-hero {grid-template-columns:1fr;padding:1.7rem;}
          .petal-hero-mark {height:120px;width:100px;}
          .petal-flow {grid-template-columns:repeat(2,minmax(0,1fr));}
      }
    </style>""", unsafe_allow_html=True)


def brand_markup() -> str:
    img = f'<img src="{mark_data()}" alt="PETAL three-petal logo" />' if mark_data() else '<span>✿</span>'
    return (f'<div class="petal-lockup">{img}'
            '<div><strong>PETAL</strong><small>ASSESSMENT WORKSPACE</small></div></div>')


def render_step_header(number: int, title: str, description: str) -> None:
    section = ("DEFINE" if number <= 2 else "ASSESS" if number <= 4 else "EXPLORE")
    st.markdown(
        f'<div class="petal-page-intro"><div><div class="petal-kicker">{section}</div>'
        f'<h1>{html_escape(title)}</h1><p>{html_escape(description)}</p></div>'
        f'<span class="petal-page-index">{number:02d} / 05</span></div>',
        unsafe_allow_html=True,
    )


def style_plot(fig, height=None):
    """White charts with logo-derived accents and consistent publication export."""
    fig.update_layout(
        template="plotly_white", font=dict(family=PLOT_FONT,color=PALETTE["ink"],size=13),
        paper_bgcolor="#FFFFFF",plot_bgcolor="#FFFFFF",
        margin=dict(l=24,r=30,t=55,b=40),
        **({"height":height} if height is not None else {}),
    )
    return fig


# -------------------------------
# Data & configuration
# -------------------------------

WORKFLOW_STEPS = [
    "Readiness & team",
    "Scope & lifecycle",
    "Choose factors",
    "Assess stages",
    "Insights & export",
]
WORKFLOW_ICONS = [
    ":material/groups:", ":material/account_tree:", ":material/tune:",
    ":material/fact_check:", ":material/insights:",
]


def _set_workflow_step(index: int) -> None:
    """Single source of truth for navigation, from buttons or page transitions."""
    st.session_state.step_idx = max(0,min(int(index),len(WORKFLOW_STEPS)-1))


def _move_workflow_step(offset: int) -> None:
    _set_workflow_step(st.session_state.get("step_idx",0)+offset)


def render_sidebar_navigation() -> None:
    index = int(st.session_state.get("step_idx",0))
    for category, indexes in (("DEFINE",(0,1)),("ASSESS",(2,3)),("EXPLORE",(4,))):
        st.markdown(f'<div class="petal-nav-heading">{category}</div>',unsafe_allow_html=True)
        for pos in indexes:
            active = "active" if pos == index else "idle"
            with st.container(key=f"petal_nav_{active}_{pos}"):
                st.button(WORKFLOW_STEPS[pos],key=f"petal_nav_button_{pos}",
                          icon=WORKFLOW_ICONS[pos],use_container_width=True,
                          on_click=_set_workflow_step,args=(pos,))
    # Position in the workflow, not a completion percentage.
    width = (index+1)*100/len(WORKFLOW_STEPS)
    st.markdown(f'<div class="petal-tiny-progress" aria-label="Current workflow page">'
                f'<div style="width:{width:.0f}%"></div></div>',unsafe_allow_html=True)

TRL_TABLE = [
    {"level": 1, "actors": ["Technology developers", "External scientific experts"],
     "definition": "Basic principles observed"},
    {"level": 2, "actors": ["Technology developers", "External scientific experts"],
     "definition": "Technology concept formulated"},
    {"level": 3, "actors": ["Technology developers", "External scientific experts"],
     "definition": "Experimental proof of concept"},
    {"level": 4, "actors": ["Technology developers", "External scientific experts", "Industry representatives"],
     "definition": "Technology validated in lab"},
    {"level": 5, "actors": ["Technology developers", "External scientific experts", "Industry representatives", "Government agency representatives"],
     "definition": "Technology validated in relevant environment (industrially relevant environment in the case of key enabling technologies)"},
    {"level": 6, "actors": ["N/A"],
     "definition": "Technology demonstrated in relevant environment (industrially relevant environment in the case of key enabling technologies)"},
    {"level": 7, "actors": ["N/A"],
     "definition": "System prototype demonstration in operational environment"},
    {"level": 8, "actors": ["N/A"],
     "definition": "System complete and qualified"},
    {"level": 9, "actors": ["N/A"],
     "definition": "Actual system proven in operational environment (competitive manufacturing in the case of key enabling technologies; or in space)"},
]

ENVIRONMENTAL_FACTORS = [
    {"name": "Climate change", "unit": "kg CO2 eq", "explanation": "Modification of climate affecting global ecosystem.", "selected": True},
    {"name": "Particulate matters", "unit": "disease incidence", "explanation": "PM effects on human health.", "selected": False},
    {"name": "Water use", "unit": "m3 world eq", "explanation": "Consumption & depletion, scarcity-adjusted.", "selected": False},
    {"name": "Resource use, fossils", "unit": "MJ", "explanation": "Depletion of non-renewable energy resources.", "selected": True},
    {"name": "Land Use", "unit": "point", "explanation": "Impact on land degradation & biodiversity.", "selected": True},
    {"name": "Resource use, minerals and metals", "unit": "kg Sb eq", "explanation": "Depletion of mineral resources.", "selected": False},
    {"name": "Ozone depletion", "unit": "kg CFC-11 eq", "explanation": "Impoverishment of protective ozone layer.", "selected": False},
    {"name": "Acidification", "unit": "mol H+ eq", "explanation": "Atmospheric chemicals redeposited in ecosystems.", "selected": False},
    {"name": "Ionizing radiation, effect on human health", "unit": "kBq U235 eq", "explanation": "Effects of radioactivity.", "selected": False},
    {"name": "Photochemical ozone formation, effect on human health", "unit": "kg NMVOC eq", "explanation": "Air quality deterioration (smog).", "selected": False},
    {"name": "Eutrophication, terrestrial", "unit": "mol N eq", "explanation": "Excess enrichment leading to imbalance.", "selected": False},
    {"name": "Eutrophication, marine", "unit": "kg N eq", "explanation": "Excess nutrients leading to dead zones.", "selected": False},
    {"name": "Eutrophication, freshwater", "unit": "kg P eq", "explanation": "Excess nutrients in rivers & lakes.", "selected": False},
]

SOCIAL_FACTORS = [
    {"name": "Health and safety (workers)", "unit": "", "explanation": "Worker health & safety across supply chain.", "selected": True},
    {"name": "Equal opportunities (workers)", "unit": "", "explanation": "Non-discrimination & inclusion.", "selected": False},
    {"name": "Smallholders including farmers (workers)", "unit": "", "explanation": "Impacts on smallholders.", "selected": False},
    {"name": "Access to material resources (local community)", "unit": "", "explanation": "Shared resource access & rights.", "selected": False},
    {"name": "Delocalization and migration (local community)", "unit": "", "explanation": "Community displacement risks.", "selected": False},
    {"name": "Safe and healthy living conditions (local community)", "unit": "", "explanation": "Ambient environmental & safety conditions.", "selected": False},
    {"name": "Respect of indigenous rights (local community)", "unit": "", "explanation": "FPIC & cultural heritage.", "selected": False},
    {"name": "Local employment (local community)", "unit": "", "explanation": "Quality job opportunities locally.", "selected": False},
    {"name": "Public commitment to sustainability issues (society)", "unit": "", "explanation": "Transparency & responsible conduct.", "selected": True},
    {"name": "Contribution to economic development (society)", "unit": "", "explanation": "Shared prosperity enablement.", "selected": False},
    {"name": "Prevention and mitigation of conflicts (society)", "unit": "", "explanation": "Conflict sensitivity & mitigation.", "selected": False},
    {"name": "Technology development (society)", "unit": "", "explanation": "Innovation spillovers & capacity.", "selected": False},
    {"name": "Ethical treatment of animals (society)", "unit": "", "explanation": "Animal welfare standards.", "selected": False},
    {"name": "Poverty alleviation (society)", "unit": "", "explanation": "Inclusive growth & poverty reduction.", "selected": False},
    {"name": "Health and safety (consumers)", "unit": "", "explanation": "Consumer health & safety.", "selected": False},
    {"name": "End of life responsibility (consumers)", "unit": "", "explanation": "Design for circularity & EPR.", "selected": True},
    {"name": "Health issues for children as consumers (children)", "unit": "", "explanation": "Child-specific health risks.", "selected": False},
]

ECONOMIC_FACTORS = [
    {"name": "Complexity of production process", "unit": "", "explanation": "How complex is manufacturing?", "selected": True},
    {"name": "Raw material cost", "unit": "", "explanation": "Cost of feedstocks & inputs.", "selected": True},
    {"name": "Market size", "unit": "", "explanation": "Addressable market potential.", "selected": False},
    {"name": "Cost of final product", "unit": "", "explanation": "Unit economics and price point.", "selected": True},
    {"name": "Scalability of production process", "unit": "", "explanation": "Ease of scale-up to volume.", "selected": False},
    {"name": "Raw material availability", "unit": "", "explanation": "Supply security & constraints.", "selected": False},
    {"name": "Chance on subsidies", "unit": "", "explanation": "Public funding & incentives likelihood.", "selected": False},
]

INTERPRETATION = [
    {"label":"Measurably Worse", "upper":1, "explanation":"Leads to a measurable worsening"},
    {"label":"Possibly Worse", "upper":2, "explanation":"Might lead to a measurable worsening"},
    {"label":"Equal", "upper":3, "explanation":"No measurable change"},
    {"label":"Possibly Better", "upper":4, "explanation":"Might lead to a measurable improvement"},
    {"label":"Measurably Better", "upper":5, "explanation":"Leads to a measurable improvement"},
]


# --- Factor metadata for Step 3 (EF3.1) ---
ENV_FACTOR_META = {
    "Acidification": {
        "indicator": "Accumulated Exceedance (AE)", "category": "ACIDIFICATION",
        "method": "EF3.1", "version": "2017-01.04.000",
        "uuid": "b5c611c6-def3-11e6-bf01-fe55135034f3",
        "explanation": "Atmospheric chemicals redeposited in ecosystems.",
    },
    "Climate change": {
        "indicator": "Radiative forcing as GWP100", "category": "CLIMATE_CHANGE",
        "method": "EF3.1", "version": "2022-01.00.000",
        "uuid": "6209b35f-9447-40b5-b68c-a1099e3674a0",
        "explanation": "Modification of climate affecting global ecosystem.",
    },
    "Ecotoxicity, freshwater": {
        "indicator": "CTUe", "category": "AQUATIC_ECO_TOXICITY",
        "method": "EF3.1", "version": "2022-01.00.000",
        "uuid": "05316e7a-b254-4bea-9cf0-6bf33eb5c630",
        "explanation": "Toxic effects on freshwater organisms.",
    },
    "Eutrophication, marine": {
        "indicator": "Fraction of N to marine", "category": "AQUATIC_EUTROPHICATION",
        "method": "EF3.1", "version": "2017-02.00.010",
        "uuid": "b5c619fa-def3-11e6-bf01-fe55135034f3",
        "explanation": "Excess nutrients leading to dead zones.",
    },
    "Eutrophication, freshwater": {
        "indicator": "Fraction of P to freshwater", "category": "AQUATIC_EUTROPHICATION",
        "method": "EF3.1", "version": "2017-01.00.010",
        "uuid": "b53ec18f-7377-4ad3-86eb-cc3f4f276b2b",
        "explanation": "Excess nutrients in rivers & lakes.", 
    },
    "Eutrophication, terrestrial": {
        "indicator": "Accumulated Exceedance (AE)", "category": "TERRESTRIAL_EUTROPHICATION",
        "method": "EF3.1", "version": "2017-01.02.009",
        "uuid": "b5c614d2-def3-11e6-bf01-fe55135034f3",
        "explanation": "Excess enrichment leading to imbalance.",
    },
    "Ionizing radiation, effect on human health": {
        "indicator": "Human exposure efficiency rel. U235", "category": "IONIZING_RADIATION",
        "method": "EF3.1", "version": "2017-01.00.011",
        "uuid": "b5c632be-def3-11e6-bf01-fe55135034f3",
        "explanation": "Effects of radioactivity.",
    },
    "Land Use": {
        "indicator": "Soil quality index", "category": "LAND_USE",
        "method": "EF3.1", "version": "2017-01.00.010",
        "uuid": "b2ad6890-c78d-11e6-9d9d-cec0c932ce01",
        "explanation": "Impact on land degradation & biodiversity.",
    },
    "Ozone depletion": {
        "indicator": "ODP", "category": "OZONE_DEPLETION",
        "method": "EF3.1", "version": "2017-02.00.012 (until 2040)",
        "uuid": "b5c629d6-def3-11e6-bf01-fe55135034f3",
        "explanation": "Impoverishment of protective ozone layer.",
    },
    "Particulate matters": {
        "indicator": "Impact on human health", "category": "RESPIRATORY_INORGANICS",
        "method": "EF3.1", "version": "2017-02.00.011",
        "uuid": "b5c602c6-def3-11e6-bf01-fe55135034f3",
        "explanation": "PM effects on human health.", 
    },
    "Photochemical ozone formation, effect on human health": {
        "indicator": "Tropospheric ozone conc. increase", "category": "PHOTOCHEMICAL_OZONE_CREATION",
        "method": "EF3.1", "version": "2017-02.01.000",
        "uuid": "b5c610fe-def3-11e6-bf01-fe55135034f3",
        "explanation": "Air quality deterioration (smog).",
    },
    "Resource use, fossils": {
        "indicator": "ADP-fossil", "category": "ABIOTIC_RESOURCE_DEPLETION",
        "method": "EF3.1", "version": "2017-01.00.010",
        "uuid": "b2ad6110-c78d-11e6-9d9d-cec0c932ce01",
        "explanation": "Depletion of non-renewable energy resources.",
    },
    "Resource use, minerals and metals": {
        "indicator": "ADP ultimate reserve", "category": "ABIOTIC_RESOURCE_DEPLETION",
        "method": "EF3.1", "version": "2017-01.00.010",
        "uuid": "b2ad6494-c78d-11e6-9d9d-cec0c932ce01",
        "explanation": "Depletion of mineral resources.",
    },
    "Water use": {
        "indicator": "Deprivation-weighted water consumption", "category": "OTHER",
        "method": "EF3.1", "version": "2017-03.00.014",
        "uuid": "b2ad66ce-c78d-11e6-9d9d-cec0c932ce01",
        "explanation": "Consumption & depletion, scarcity-adjusted.",
    },
}

# Social & Economic text used in fold-outs
SOCIAL_FACTOR_META = {
    "Health and safety (workers)": "Ensures safe working conditions; avoids long-term health risks (OSH).",
    "Equal opportunities (workers)": "Fair access to employment, advancement, benefits.",
    "Smallholders including farmers (workers)": "Fair integration and economic benefit of small-scale producers.",
    "Access to material resources (local community)": "Effect on access to land, water, essential resources.",
    "Delocalization and migration (local community)": "Risk of displacement/forced migration due to operations.",
    "Safe and healthy living conditions (local community)": "Air, water, noise, safety around sites.",
    "Respect of indigenous rights (local community)": "FPIC, land rights, cultural heritage.",
    "Local employment (local community)": "Creation of fair, stable local jobs and suppliers.",
    "Public commitment to sustainability issues (society)": "Transparency, responsible communication & initiatives.",
    "Contribution to economic development (society)": "Broader growth and infrastructure benefits.",
    "Prevention and mitigation of conflicts (society)": "Conflict sensitivity and mitigation.",
    "Technology development (society)": "Innovation spillovers, capacity building.",
    "Ethical treatment of animals (society)": "Animal welfare in sourcing/testing.",
    "Poverty alleviation (society)": "Contribution to reducing poverty.",
    "Health and safety (consumers)": "Product safety for end users, compliance.",
    "End of life responsibility (consumers)": "Design for circularity; take-back support.",
    "Health issues for children as consumers (children)": "Child-specific exposure risks.",
}

ECON_FACTOR_META = {
    "Complexity of production process": "Technical/operational difficulty; impacts cost and scale.",
    "Raw material cost": "Current prices and stability of inputs.",
    "Market size": "Total addressable demand and growth potential.",
    "Cost of final product": "Price vs. cost; affordability; competitiveness.",
    "Scalability of production process": "Ease of ramping volume without heavy capex.",
    "Raw material availability": "Abundance, geography, supply risk.",
    "Chance on subsidies": "Likelihood of public funding/incentives.",
}

SCORE_COLORS = {k: PALETTE[k] for k in ("good", "bad", "mixed", "na")}

# -------------------------------
# High-resolution chart export
# -------------------------------
def plot_export_config(
    filename: str,
    width: int = 1800,
    height: int = 1400,
    *,
    image_format: str = "png",
    scale: int = 2,
) -> dict:
    """Configure Plotly's client-side image export (camera toolbar icon).

    For publication petal plots we export from a *smaller layout* (1100 x 920)
    at scale 4, producing 4400 x 3680 PNG pixels if the browser permits.
    This preserves larger text relative to figure size when inserted into a
    document. Unlike changing figure fonts, it does not alter the screen view.
    SVG is a vector option; it stays sharp at any publication size.
    """
    if image_format not in ("png", "svg"):
        raise ValueError("image_format must be 'png' or 'svg'")
    return {
        "displayModeBar": True,
        "displaylogo": False,
        "toImageButtonOptions": {
            "format": image_format,
            "filename": filename,
            "width": width,
            "height": height,
            "scale": scale if image_format == "png" else 1,
        },
    }

# -------------------------------
# Data model
# -------------------------------
@dataclass
class FactorScore:
    score: Optional[float] = None
    note: str = ""
    to_research: bool = False
    unknown: bool = False

@dataclass
class Project:
    name: str
    description: str = ""
    trl: int = 4
    scoping_notes: str = ""
    stakeholder_notes: str = ""
    lifecycle_stages: List[str] = field(default_factory=list)  # start empty; you manage via UI
    lifecycle_changed: Dict[str, bool] = field(default_factory=dict)
    selected_factors: Dict[str, List[str]] = field(default_factory=dict)  # keys: Environmental/Social/Economic
    grid: Dict[str, Dict[str, FactorScore]] = field(default_factory=dict)  # stage -> factor -> FactorScore
    core_function: str = ""
    functional_unit: str = ""
    tradeoff_notes: str = ""
    scenario_scores: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    assumptions: List[str] = field(default_factory=list)
    unknown_factors: List[str] = field(default_factory=list)

    # --- restore this! ---
    def ensure_grid(self, all_factors: List[str]) -> None:
        """Make sure every (stage, factor) exists in the grid with a FactorScore."""
        for stage in self.lifecycle_stages:
            stage_map = self.grid.setdefault(stage, {})
            # keep only relevant factors for this stage (optional: clean stale)
            for f in all_factors:
                if f not in stage_map:
                    stage_map[f] = FactorScore()
            # optionally drop factors no longer selected:
            for f in list(stage_map.keys()):
                if f not in all_factors:
                    del stage_map[f]

    def assessment_stages(self) -> List[str]:
        """Match the stages shown in Step 4, excluding stale/archived grid rows.

        If no stages are marked 'Will change?', Step 4 scores all current
        lifecycle stages; the result calculations use the same fallback.
        """
        changed = [stage for stage in self.lifecycle_stages
                   if self.lifecycle_changed.get(stage, False)]
        return changed if changed else list(self.lifecycle_stages)

    def assessment_grid(self) -> Dict[str, Dict[str, FactorScore]]:
        """Only active stages and the nine currently selected factors."""
        selected = set(sum((self.selected_factors.get(cat, [])
                            for cat in ("Environmental", "Social", "Economic")), []))
        return {
            stage: {factor: fs for factor, fs in self.grid.get(stage, {}).items()
                    if factor in selected}
            for stage in self.assessment_stages()
        }

    def average_by_stage(self) -> Dict[str, float]:
        out: Dict[str, float] = {}
        for stage, facs in self.assessment_grid().items():
            vals = [fs.score for fs in facs.values()
                    if getattr(fs, "score", None) is not None]
            out[stage] = statistics.mean(vals) if vals else float("nan")
        return out

    def average_by_factor(self) -> Dict[str, float]:
        acc: Dict[str, List[float]] = {}
        for facs in self.assessment_grid().values():
            for factor, fs in facs.items():
                if getattr(fs, "score", None) is not None:
                    acc.setdefault(factor, []).append(fs.score)
        return {factor: statistics.mean(vals) for factor, vals in acc.items()}

    def overall_score(self) -> Optional[float]:
        avs = self.average_by_stage()
        vals = [v for v in avs.values() if isinstance(v, (int, float)) and not math.isnan(v)]
        return round(statistics.mean(vals), 2) if vals else None

    # keep this to fix imports
    def coerce_grid(self) -> None:
        """Turn nested dicts (from JSON) back into FactorScore instances."""
        for stage, fdict in self.grid.items():
            for fname, fs in list(fdict.items()):
                if isinstance(fs, dict):
                    self.grid[stage][fname] = FactorScore(**fs)

# -------------------------------
# Helpers
# -------------------------------

# --- Landing page renderer ---
import plotly.express as px
import pandas as pd
import random
import re

def hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def _new_project_name(base="New PETAL Project"):
    # create a unique default project name if the user clicks the CTA
    existing = set(st.session_state.get("projects", {}).keys())
    if base not in existing:
        return base
    i = 2
    while f"{base} {i}" in existing:
        i += 1
    return f"{base} {i}"

def _design_paradox_fig():
    x = list(range(0, 101, 5))
    df = pd.DataFrame({
        "Development progress (%)": x,
        "Knowledge about impacts": [1 + 99 * (t / 100) ** 1.6 for t in x],
        "Design freedom": [100 - 90 * (t / 100) ** .7 for t in x],
    })
    fig = px.line(
        df, x="Development progress (%)", y=["Knowledge about impacts", "Design freedom"],
        color_discrete_map={"Knowledge about impacts": PALETTE["green"], "Design freedom": PALETTE["red"]},
    )
    fig.add_vrect(x0=0, x1=25, fillcolor="#EAF8F0", opacity=.65, line_width=0,
                  annotation_text="Early leverage", annotation_position="top left")
    fig.update_traces(line=dict(width=3))
    fig.update_layout(legend_title_text="", legend=dict(orientation="h", y=-.27, x=0),
                      yaxis_title="Relative level", title=None)
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="#ECF1ED", zeroline=False)
    return style_plot(fig, height=370)


def import_project_json(uploaded) -> Project:
    """Read a full project export, including old projects with optional fields."""
    data = json.load(uploaded)
    if not isinstance(data, dict) or not isinstance(data.get("name"), str):
        raise ValueError("This is not a PETAL project file. Use the full project JSON export.")
    # Preserve compatibility with earlier full project JSON exports.
    from dataclasses import fields
    valid_fields = {item.name for item in fields(Project)}
    proj = Project(**{key: value for key, value in data.items() if key in valid_fields})
    proj.coerce_grid()
    return proj


def render_landing():
    visual = (f'<img class="petal-hero-mark" src="{mark_data()}" alt="PETAL flower mark">'
              if mark_data() else '<span style="font-size:7rem;color:#24BB7A">✿</span>')
    st.markdown(f"""
      <div class="petal-home-hero">
        <div><span class="kicker">PETAL / EARLY-STAGE SUSTAINABILITY</span>
          <h1>Make better sustainability choices while change is still possible.</h1>
          <p>PETAL helps teams scope an early-stage technology, select the most relevant sustainability factors,
          record what is known, and discuss trade-offs before a full assessment is feasible.</p>
        </div><div>{visual}</div>
      </div>""",unsafe_allow_html=True)

    new_col, resume_col = st.columns(2,gap="large")
    with new_col:
        with st.container(border=True):
            st.markdown("### Start a new assessment")
            with st.form("create_project"):
                name = st.text_input("Project name",value="New PETAL Project")
                description = st.text_input("Short description",placeholder="What are you developing?")
                submitted = st.form_submit_button("Create assessment",type="primary",
                                                  use_container_width=True)
            if submitted:
                clean = (name or "").strip() or "New PETAL Project"
                unique = _new_project_name(clean)
                st.session_state.projects[unique] = Project(name=unique,description=description.strip())
                st.session_state.active_project = unique
                _set_workflow_step(0)
                st.rerun()
            st.caption("Create a new PETAL workspace for a technology, product or material under development.")
    with resume_col:
        with st.container(border=True):
            st.markdown("### Open an existing assessment")
            uploaded = st.file_uploader("Import a saved project",type=["json"],
                                        help="Select a full PETAL project JSON, not a results-only file.")
            if uploaded is not None and st.button("Import project",type="primary",use_container_width=True):
                try:
                    project = import_project_json(uploaded)
                    project.name = _new_project_name(project.name)
                    st.session_state.projects[project.name] = project
                    st.session_state.active_project = project.name
                    _set_workflow_step(0)
                    st.rerun()
                except (TypeError,ValueError,KeyError,json.JSONDecodeError) as exc:
                    st.error(f"Could not open project: {exc}")
            existing = list(st.session_state.projects)
            if existing:
                selected = st.selectbox("Open a project from this session",existing)
                if st.button("Open selected project",use_container_width=True):
                    st.session_state.active_project = selected
                    _set_workflow_step(0)
                    st.rerun()
            else:
                st.caption("Saved project files can be reopened here.")

    info_left, info_right = st.columns([1.35, 1], gap="large")
    with info_left:
        st.markdown("#### What this helps you do")
        st.markdown("""
- **Bring in the right people early** based on technology readiness.
- **Define the reference product and functional unit** before the discussion becomes too detailed.
- **Select the three most relevant factors** in each sustainability dimension.
- **Score transparently** across lifecycle stages and explain the reasoning behind each score.
- **Surface trade-offs and hotspots** while uncertainty is still high and design freedom remains.
""")

        st.markdown("#### Interpreting PETAL")
        st.markdown("""
- PETAL supports **qualitative, participatory assessment** for early-stage technologies.
- A score of **3 means equal to the reference**; lower scores indicate worse expected performance and higher scores indicate better expected performance.
- **Unknown** and **to research** flags are part of the method and should be discussed, not hidden.
- Findings are **indicative rather than conclusive** and should guide decisions, not replace detailed LCA or S-LCA work.
""")
    with info_right:
        st.markdown("#### Sustainable design paradox")
        st.caption("We know most about impacts when it is hardest to change the design. PETAL is built for that earlier moment.")
        st.plotly_chart(_design_paradox_fig(), use_container_width=True,
                        config=plot_export_config("PETAL_design_paradox", 1600, 1050))
        with st.container(border=True):
            st.markdown("#### Scope and limits")
            st.markdown("""
- Best suited to **TRL 1–5**.
- Intended for **qualitative scoping and structured discussion**.
- Not a substitute for a **full LCA, S-LCA or TEA**.
""")

    st.markdown("#### How the workflow works")
    st.markdown('<div class="petal-flow">' + ''.join(
        f'<div class="petal-flow-step"><span class="petal-flow-dot"></span>'
        f'<strong>{title}</strong><p>{subtitle}</p></div>'
        for title,subtitle in [
            ("Readiness & team","Identify TRL and the people who should be involved."),
            ("Scope & lifecycle","Define the reference, functional unit and lifecycle stages."),
            ("Choose factors","Select the three key environmental, social and economic factors."),
            ("Assess stages","Score each selected factor and record what is uncertain."),
            ("Insights & export","Review patterns, discuss scenarios and export the results."),
        ]) + '</div>',unsafe_allow_html=True)

    more_left, more_right = st.columns([1.15, .85], gap="large")
    with more_left:
        with st.container(border=True):
            st.markdown("#### Assessment principles")
            st.markdown("""
- Keep the lifecycle **lean and focused**.
- Choose factors that the group can meaningfully discuss.
- Use notes and assumptions to make the reasoning visible.
- Treat trade-offs as the main output of the exercise.
""")
    with more_right:
        with st.container(border=True):
            st.markdown("#### Example project")
            st.markdown("Use the recyclable wind turbine blades example to explore the workflow before running your own workshop.")
            example = APP_ROOT / "assets" / "recyclable_windmill_blades.json"
            if example.exists():
                st.download_button("Download example project",example.read_bytes(),
                                   file_name=example.name,mime="application/json",
                                   use_container_width=True)
            else:
                st.caption("Add the example JSON in the assets folder to enable the download.")


def bottom_nav(total_steps=len(WORKFLOW_STEPS)):
    """Two predictable actions: previous page and the specifically named next page."""
    idx = int(st.session_state.get("step_idx",0))
    st.divider()
    left,center,right = st.columns([1.4,2.5,1.7],vertical_alignment="center")
    with left:
        if idx > 0:
            st.button("←  " + WORKFLOW_STEPS[idx-1],on_click=_move_workflow_step,
                      args=(-1,),use_container_width=True)
    with center:
        st.markdown('<span class="petal-hint">Changes stay in this session. Export to save.</span>',
                    unsafe_allow_html=True)
    with right:
        if idx < total_steps-1:
            st.button(WORKFLOW_STEPS[idx+1] + "  →",type="primary",on_click=_move_workflow_step,
                      args=(1,),use_container_width=True)


def factor_breakdown_plot(stage_name: str, breakdown: Dict[str, FactorScore]):
    # dict -> DataFrame
    df = pd.DataFrame(
        {"Factor": list(breakdown.keys()),
         "Average score": [float(breakdown[f].score) for f in breakdown.keys()]}
    )
    plot_df = to_plot_df(df, "Factor", "Average score").rename(columns={"Factor": "Category"})
    title = f"Factor breakdown — {stage_name}"
    return horizontal_delta_bar(plot_df, title)

def factor_names(factors):
    return [f["name"] for f in factors]

def score_band_color(score: float) -> str:
    """Qualitative display bands: red <2.5; orange 2.5-3.5; green >3.5."""
    if score is None or (isinstance(score, float) and math.isnan(score)):
        return SCORE_COLORS["na"]

    if score > 3.5:
        return SCORE_COLORS["good"]
    if score < 2.5:
        return SCORE_COLORS["bad"]

    return SCORE_COLORS["mixed"]



def to_plot_df(df: pd.DataFrame, cat_col: str, val_col: str) -> pd.DataFrame:
    out = df.copy()
    out["Score"] = out[val_col].astype(float)
    out["Delta"] = out["Score"] - 3.0
    out["Color"] = out["Score"].apply(score_band_color)
    # label shown at bar end (original score, not delta)
    out["Label"] = out["Score"].round(1)
    return out

def horizontal_delta_bar(plot_df: pd.DataFrame, title: str):
    sorted_df = plot_df.dropna(subset=["Score"]).sort_values("Delta", ascending=True)
    fig = go.Figure()
    if not sorted_df.empty:
        fig.add_trace(go.Bar(
            x=sorted_df["Delta"], y=sorted_df["Category"], orientation="h",
            marker=dict(color=sorted_df["Color"], line=dict(width=0)),
            text=[f"{value:.1f}" for value in sorted_df["Score"]],
            textposition="outside", cliponaxis=False,
            customdata=sorted_df[["Score"]].values,
            hovertemplate="<b>%{y}</b><br>Qualitative mean: %{customdata[0]:.2f}<extra></extra>",
        ))
    fig.add_vline(x=0, line_dash="dash", line_color=PALETTE["charcoal"], opacity=.9)
    fig.update_xaxes(range=[-2.3, 2.3], tickmode="array", tickvals=[-2,-1,0,1,2],
                     ticktext=["1", "2", "3 · Equal", "4", "5"],
                     gridcolor="#F1F0ED", zeroline=False,
                     title="Compared with the reference product (3 = equal)")
    fig.update_yaxes(title="", autorange="reversed", showgrid=False)
    fig.update_layout(title=dict(text=title, font=dict(size=17)), showlegend=False,
                      bargap=.38, margin=dict(l=20, r=42, t=58, b=60))
    return style_plot(fig, height=max(330, len(sorted_df)*46+160))

def get_selected_factors(factors, override_selected: Optional[List[str]] = None) -> List[str]:
    if override_selected is not None:
        return override_selected
    return [f["name"] for f in factors if f.get("selected")]

def interp_label(value: float) -> str:
    for row in INTERPRETATION:
        if value <= row["upper"] + 1e-9:
            return row["label"]
    return "n/a"

def download_json_button(obj, filename, label):
    st.download_button(
        label=label,
        data=json.dumps(obj, indent=2),
        file_name=filename,
        mime="application/json"
    )

def assumptions_sidebar_block(project):
    st.session_state.setdefault("assumption_input", "")

    def save_assumption():
        value = (st.session_state.get("assumption_input") or "").strip()
        if value:
            project.assumptions.append(value)
            st.session_state["assumption_input"] = ""

    with st.expander(f"Assumptions  ·  {len(project.assumptions)}", expanded=False):
        st.caption("Record assumptions that the group is using to make judgments.")
        if project.assumptions:
            for i, value in enumerate(project.assumptions, 1):
                st.markdown(f"{i}. {value}")
        st.text_input("Add assumption (press Enter)", key="assumption_input",
                      on_change=save_assumption, placeholder="e.g. Grid mix remains constant")
        if project.assumptions:
            if st.button("Undo last assumption", use_container_width=True):
                project.assumptions.pop()
                st.rerun()

def render_score_guide():
    st.markdown(
        """<div class=\"petal-score-guide\">
            <div class=\"item i1\"><span class=\"num\">1</span><span class=\"lab\">Measurably worse</span><span class=\"sub\">Clear evidence of worse performance than the reference.</span></div>
            <div class=\"item i2\"><span class=\"num\">2</span><span class=\"lab\">Possibly worse</span><span class=\"sub\">Likely worse, but with limited evidence or confidence.</span></div>
            <div class=\"item i3\"><span class=\"num\">3</span><span class=\"lab\">Equal</span><span class=\"sub\">Roughly comparable to the reference product.</span></div>
            <div class=\"item i4\"><span class=\"num\">4</span><span class=\"lab\">Possibly better</span><span class=\"sub\">Likely better, but evidence is still incomplete.</span></div>
            <div class=\"item i5\"><span class=\"num\">5</span><span class=\"lab\">Measurably better</span><span class=\"sub\">Clear evidence of better performance than the reference.</span></div>
        </div>""",
        unsafe_allow_html=True,
    )


def assumptions_editor(project, context_key: str, title: str = "Assumptions"):
    st.markdown(
        f"""<div class=\"petal-assumption-box\"><h4>{html_escape(title)}</h4>
        <p>Record assumptions that are shaping the scoring. Add them while discussing the current stage if helpful.</p></div>""",
        unsafe_allow_html=True,
    )
    input_key = f"{project.name}_{context_key}_assumption_input"
    button_key = f"{project.name}_{context_key}_assumption_add"
    cols = st.columns([4.5, 1.1], vertical_alignment="bottom")
    with cols[0]:
        new_assumption = st.text_input(
            "Add assumption",
            key=input_key,
            placeholder="e.g. Maintenance frequency remains similar to the reference product",
            label_visibility="collapsed",
        )
    with cols[1]:
        if st.button("Add", key=button_key, use_container_width=True):
            value = (new_assumption or "").strip()
            if value:
                project.assumptions.append(value)
                st.session_state[input_key] = ""
                st.rerun()
    if project.assumptions:
        for idx, value in enumerate(project.assumptions, 1):
            st.markdown(f"- {idx}. {html_escape(value)}")
        if st.button("Undo last assumption", key=f"{project.name}_{context_key}_undo_assumption"):
            project.assumptions.pop()
            st.rerun()
    else:
        st.caption("No assumptions recorded yet.")


def collect_to_research(project):
    out = {}

    for stage, fdict in project.assessment_grid().items():
        pending = [
            (factor, fs.note)
            for factor, fs in fdict.items()
            if getattr(fs, "to_research", False)
        ]

        if pending:
            out[stage] = pending

    return out

def collect_unknown_factors(project):
    out = {}

    for stage, fdict in project.assessment_grid().items():
        unknown = [
            (factor, fs.note)
            for factor, fs in fdict.items()
            if getattr(fs, "unknown", False)
        ]

        if unknown:
            out[stage] = unknown

    return out

def category_means(project, avg_factor: dict) -> dict:
    out = {}
    for cat in ("Environmental", "Social", "Economic"):
        factors = project.selected_factors.get(cat, [])
        vals = [avg_factor[f] for f in factors if f in avg_factor and not math.isnan(avg_factor[f])]
        out[cat] = (sum(vals) / len(vals)) if vals else float("nan")
    return out

def _petal_polygon(score: Optional[float], center: int) -> tuple:
    """A petal with a common radius scale (score 3 = reference ring)."""
    if score is None or not math.isfinite(float(score)):
        return [], []
    extent = max(0.0, min(1.0, (float(score) - 1) / 4))
    width = 40
    angles = np.linspace(center - width, center + width, 121)
    bump = (np.cos(np.deg2rad((angles - center) * (90 / width))) + 1) / 2
    radii = extent * (0.15 + 0.85 * bump)
    theta_closed = np.concatenate([angles, angles[::-1]])
    r_closed = np.concatenate([radii, np.zeros_like(radii)])
    return theta_closed.tolist(), r_closed.tolist()


def _score_to_radius(score: Optional[float]) -> float:
    if score is None or (isinstance(score, float) and math.isnan(score)):
        return 0.0
    return max(0.0, min(1.0, (float(score) - 1) / 4))


def _petal_base() -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[0.5] * 361,
        theta=list(range(0, 361)),
        mode="lines",
        line=dict(width=1.5, dash="dot", color="rgba(44,39,38,0.45)"),
        hoverinfo="skip",
        showlegend=False,
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="white",
            radialaxis=dict(
                range=[0, 1],
                tickmode="array",
                tickvals=[0.0, 0.5, 1.0],
                ticktext=["", "", ""],
                ticks="",
                gridcolor="#EEEDE8",
                gridwidth=1,
                showline=False,
                angle=90,
            ),
            angularaxis=dict(
                tickmode="array",
                tickvals=[90, 210, 330],
                ticktext=["Environmental", "Social", "Economic"],
                tickfont=dict(size=16, color=PALETTE["ink"], family=PLOT_FONT),
                rotation=90,
                direction="clockwise",
                showgrid=False,
                showline=False,
            ),
        ),
        annotations=[
            dict(text="1", x=0.5, y=0.50, xref="paper", yref="paper", showarrow=False,
                 font=dict(size=13, color=PALETTE["ink"], family=PLOT_FONT)),
            dict(text="3", x=0.5, y=0.735, xref="paper", yref="paper", showarrow=False,
                 font=dict(size=13, color=PALETTE["ink"], family=PLOT_FONT)),
            dict(text="5", x=0.5, y=0.94, xref="paper", yref="paper", showarrow=False,
                 font=dict(size=13, color=PALETTE["ink"], family=PLOT_FONT)),
        ],
        showlegend=False,
        margin=dict(t=55, r=50, b=95, l=50),
    )
    return fig


def seed_flower_petal_chart(category_avg: dict, title: str = ""):
    """Logo-colored petals with a clear reference ring and tip markers."""
    fig = _petal_base()
    for cat, center in (("Environmental", 90), ("Social", 210), ("Economic", 330)):
        score = category_avg.get(cat, float("nan"))
        theta, r = _petal_polygon(score, center)
        if not theta:
            continue
        fill = hex_to_rgba(DIMENSION_COLORS[cat], 0.58)
        hover = f"<b>{cat}</b><br>Indicative mean: {score:.2f}<extra></extra>"
        fig.add_trace(go.Scatterpolar(
            r=r,
            theta=theta,
            mode="lines",
            line=dict(width=0),
            fill="toself",
            fillcolor=fill,
            hovertemplate=hover,
            showlegend=False,
        ))
        fig.add_trace(go.Scatterpolar(
            r=[_score_to_radius(score)],
            theta=[center],
            mode="markers",
            marker=dict(size=11, color="#6B7280", line=dict(width=0)),
            hovertemplate=hover,
            showlegend=False,
        ))
    if title:
        fig.update_layout(title=dict(text=title, font=dict(size=18)))
    else:
        fig.update_layout(title=dict(text=""))
    return style_plot(fig, height=470)


def seed_flower_overlay(baseline_cat_avg: dict, scenario_cat_avg: dict,
                        title="Current vs scenario", color_by="baseline"):
    """Current = stronger petal with grey marker, scenario = lighter underlay."""
    fig = _petal_base()
    cats = ("Environmental", "Social", "Economic")
    centers = {"Environmental": 90, "Social": 210, "Economic": 330}

    for cat in cats:
        center = centers[cat]
        color = DIMENSION_COLORS[cat]
        scenario_score = scenario_cat_avg.get(cat, float("nan"))
        theta, r = _petal_polygon(scenario_score, center)
        if theta:
            fig.add_trace(go.Scatterpolar(
                r=r, theta=theta, mode="lines", line=dict(width=0), fill="toself",
                fillcolor=hex_to_rgba(color, 0.28),
                hovertemplate=f"<b>{cat}</b><br>Scenario: {scenario_score:.2f}<extra></extra>",
                showlegend=False,
            ))

    for cat in cats:
        center = centers[cat]
        color = DIMENSION_COLORS[cat]
        baseline_score = baseline_cat_avg.get(cat, float("nan"))
        theta, r = _petal_polygon(baseline_score, center)
        if theta:
            fig.add_trace(go.Scatterpolar(
                r=r, theta=theta, mode="lines", line=dict(width=0), fill="toself",
                fillcolor=hex_to_rgba(color, 0.56),
                hovertemplate=f"<b>{cat}</b><br>Current: {baseline_score:.2f}<extra></extra>",
                showlegend=False,
            ))
            fig.add_trace(go.Scatterpolar(
                r=[_score_to_radius(baseline_score)], theta=[center], mode="markers",
                marker=dict(size=11, color="#6B7280", line=dict(width=0)),
                hovertemplate=f"<b>{cat}</b><br>Current: {baseline_score:.2f}<extra></extra>",
                showlegend=False,
            ))

    if title:
        fig.update_layout(title=dict(text=title, font=dict(size=18)))
    else:
        fig.update_layout(title=dict(text=""))
    return style_plot(fig, height=465)


def overlay_delta_bars(baseline_plot_df: pd.DataFrame, scenario_plot_df: pd.DataFrame, title: str):
    # assumes both have columns: Category, Delta, Score
    b = baseline_plot_df.copy().set_index("Category")
    s = scenario_plot_df.copy().set_index("Category")
    cats = list(b.index.union(s.index))

    fig = go.Figure()

    # scenario first (underlay)
    fig.add_trace(go.Bar(
        x=[s.loc[c, "Delta"] if c in s.index else 0 for c in cats],
        y=cats,
        orientation="h",
        opacity=0.52,
        marker_color=PALETTE["green"],
        name="Scenario",
    ))

    # baseline on top (overlay)
    fig.add_trace(go.Bar(
        x=[b.loc[c, "Delta"] if c in b.index else 0 for c in cats],
        y=cats,
        orientation="h",
        opacity=0.88,
        marker_color=PALETTE["charcoal"],
        name="Baseline",
    ))

    fig.add_vline(x=0, line_dash="dash", line_color="#77716D")
    fig.update_layout(
        barmode="overlay",
        title=title,
        margin=dict(t=30, r=10, b=20, l=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(range=[-2.3, 2.3])
    fig.update_yaxes(title="", autorange="reversed")
    fig.update_xaxes(gridcolor="#F1F0ED")
    return style_plot(fig, height=max(340, len(cats)*46 + 150))

# -------------------------------
# State init
# -------------------------------
if "projects" not in st.session_state:
    st.session_state.projects: Dict[str,Project] = {}
if "active_project" not in st.session_state:
    st.session_state.active_project: Optional[str] = None
if "step_idx" not in st.session_state:
    st.session_state.step_idx = 0

inject_theme()
with st.sidebar:
    st.markdown(brand_markup(),unsafe_allow_html=True)
    current_key = st.session_state.get("active_project")
    current = st.session_state.projects.get(current_key) if current_key else None
    if current is not None:
        st.markdown(f'<div class="petal-side-project"><small>ACTIVE PROJECT</small>'
                    f'<strong>{html_escape(current.name)}</strong>'
                    f'<span>TRL {current.trl} · {len(current.lifecycle_stages)} stages</span>'
                    '</div>',unsafe_allow_html=True)
        render_sidebar_navigation()
        st.divider()
        assumptions_sidebar_block(current)
        download_json_button(asdict(current),
                             f"{current.name.replace(' ','_')}.json","Download project JSON")
        if st.button("All projects",icon=":material/arrow_back:",use_container_width=True):
            st.session_state.active_project = None
            st.rerun()
    else:
        st.markdown('<p class="petal-hint">Participatory sustainability assessment</p>',
                    unsafe_allow_html=True)

if st.session_state.active_project is None:
    render_landing()
    st.stop()

project: Project = st.session_state.projects[st.session_state.active_project]
step = int(st.session_state.step_idx)
st.markdown(f'<div class="petal-workspace"><strong>{html_escape(project.name)}</strong>'
            f'<span class="petal-project-tag">TRL {project.trl}</span></div>',
            unsafe_allow_html=True)


def scoping_is_done(p: Project) -> bool:
    return bool(getattr(p, "functional_unit", "").strip()) and len(p.lifecycle_stages) > 0

st.session_state.scoping_done = scoping_is_done(project)
st.markdown(
    f'<div class="petal-projectstrip">'
    f'<span><strong>{html_escape(project.name)}</strong> '
    f'<span class="petal-small">· {html_escape(project.description[:110]) if project.description else "Qualitative sustainability assessment"}</span></span>'
    f'<span class="petal-stagechip">TRL {project.trl} · 3 dimensions</span></div>',
    unsafe_allow_html=True,
)

# -------------------------------
# Step 1: TRL
# -------------------------------
if step == 0:
    render_step_header(1, "Readiness & team", "Identify the people who can assess the technology.")
    left, right = st.columns([1.1, .9], gap="large")
    with left:
        with st.container(border=True):
            st.markdown("#### Select technology readiness")
            project.trl = st.select_slider("Technology Readiness Level (TRL)",
                                           options=[r["level"] for r in TRL_TABLE], value=project.trl)
            row = next(r for r in TRL_TABLE if r["level"] == project.trl)
            st.metric("Current TRL", project.trl)
            st.caption(row["definition"])
    with right:
        with st.container(border=True):
            st.markdown("#### Who to involve")
            if row["actors"] == ["N/A"]:
                st.write("The original PETAL actor guidance primarily covers TRLs 1–5.")
            else:
                for actor in row["actors"]:
                    st.markdown(f"✓  {actor}")
    project.stakeholder_notes = st.text_area(
        "Notes on stakeholders and initial assumptions", value=project.stakeholder_notes,
        key=f"{project.name}_trl_notes", height=125,
        placeholder="Which disciplines, users or external experts should be represented?",
    )
    bottom_nav()

# -------------------------------
# Step 2: Scoping & lifecycle
# -------------------------------

elif step == 1:
    render_step_header(2,"Scope & lifecycle","Define what is compared, then map the relevant lifecycle stages.")

    st.markdown("### Reference")
    left,right=st.columns([1.1,1],gap="large")
    with left:
        project.core_function=st.text_area("Reference product",value=project.core_function,
            key=f"{project.name}_core_function",height=95,
            placeholder="What existing product or technology is the reference?")
    with right:
        project.functional_unit=st.text_area("Functional unit",value=project.functional_unit,
            key=f"{project.name}_functional_unit",height=95,
            placeholder="What equivalent service is being compared?",
            help="Include service duration or lifetime where it is relevant.")

    st.markdown("### Lifecycle map")
    st.caption("Edit stages below. Mark the stages expected to change; up to seven in total.")
    CODE_TO_LABEL = {
        "A0": "A0 - Pre-construction (design & non-physical activities) [UK]",
        "A1": "A1 - Raw Material Supply",
        "A2": "A2 - Transport to Manufacturer",
        "A3": "A3 - Manufacturing",
        "A4": "A4 - Transport to Site",
        "A5": "A5 - Installation on Site",
        "B1": "B1 - Use/Application",
        "B2": "B2 - Maintenance",
        "B3": "B3 - Repair",
        "B4": "B4 - Replacement",
        "B5": "B5 - Refurbishment",
        "B6": "B6 - Operational Energy Use",
        "B7": "B7 - Operational Water Use",
        "B8": "B8 - Operational Transport (NS3720/PAS2080/EN-17472)",
        "B9": "B9 - User Utilisation (PAS2080)",
        "C1": "C1 - Deconstruction/Demolition",
        "C2": "C2 - Transport to Waste Processing",
        "C3": "C3 - Waste Processing for Reuse/Recovery/Recycling",
        "C4": "C4 - Disposal",
        "D":  "D - Reuse/Recovery/Recycling Potentials (beyond boundary)",
    }

    import uuid
    editor_owner=f"{project.name}_stage_editor_owner"
    rows_key=f"{project.name}_stage_editor_rows"
    if st.session_state.get(editor_owner) != project.name:
        initial=project.lifecycle_stages or [CODE_TO_LABEL[c] for c in ("A1","A3","B1","C3")]
        st.session_state[rows_key]=[
            {"_id":str(uuid.uuid4()),"Order":i+1,"Stage":stage,
             "Will change?":bool(project.lifecycle_changed.get(stage,False))}
            for i,stage in enumerate(initial)
        ]
        st.session_state[editor_owner]=project.name
    old_rows=st.session_state[rows_key]
    version_key=f"{project.name}_stage_editor_version"
    st.session_state.setdefault(version_key,0)
    frame=pd.DataFrame(old_rows,columns=["_id","Order","Stage","Will change?"])
    edited=st.data_editor(frame,hide_index=True,use_container_width=True,
        num_rows="dynamic",key=f"{project.name}_lifecycle_table_{st.session_state[version_key]}",
        column_order=["Order","Stage","Will change?"],
        column_config={
            "Order":st.column_config.NumberColumn("Order",width="small",min_value=1,max_value=7,step=1),
            "Stage":st.column_config.TextColumn("Lifecycle stage",width="large",required=True),
            "Will change?":st.column_config.CheckboxColumn("Will change?",width="small",default=False),
        })
    pending=[]
    previous_by_id={r["_id"]:r["Stage"] for r in old_rows if r.get("_id")}
    for i,row in edited.iterrows():
        stage=str(row.get("Stage") or "").strip()
        if not stage or stage.lower()=="nan":
            continue
        raw_id=row.get("_id")
        stable_id=raw_id if isinstance(raw_id,str) and raw_id else str(uuid.uuid4())
        raw_order=row.get("Order")
        order=int(raw_order) if pd.notna(raw_order) else i+1
        pending.append({"_id":stable_id,"Order":order,"Stage":stage,
                        "Will change?":bool(row.get("Will change?",False)) if pd.notna(row.get("Will change?",False)) else False})
    pending.sort(key=lambda x:x["Order"])
    names=[r["Stage"] for r in pending]
    if len(names)>7:
        st.warning("Maximum seven stages. Remove a row to continue.")
    elif len(set(names)) != len(names):
        st.warning("Stage names must be unique.")
    else:
        # Stable row IDs distinguish renames from deleted/reordered rows.
        for row in pending:
            old=previous_by_id.get(row["_id"])
            new_name=row["Stage"]
            if old and old != new_name:
                if old in project.grid and new_name not in project.grid:
                    project.grid[new_name]=project.grid.pop(old)
                if old in project.scenario_scores and new_name not in project.scenario_scores:
                    project.scenario_scores[new_name]=project.scenario_scores.pop(old)
        project.lifecycle_stages=names
        project.lifecycle_changed={r["Stage"]:r["Will change?"] for r in pending}
        st.session_state[rows_key]=pending

    st.caption(f"{len(project.lifecycle_stages)} / 7 stages · " +
               f"{sum(project.lifecycle_changed.values())} marked to change")

    # Optional standard stage library; custom stages can also be typed in the table.
    with st.expander("Add a standard lifecycle stage"):
        available=[label for label in CODE_TO_LABEL.values()
                   if label not in project.lifecycle_stages]
        if available:
            stage_to_add=st.selectbox("Lifecycle module",available,
                                     key=f"{project.name}_library_stage")
            if st.button("Add selected stage",disabled=len(project.lifecycle_stages)>=7,
                         use_container_width=True):
                current=st.session_state[rows_key]
                if stage_to_add not in [r["Stage"] for r in current]:
                    current.append({"_id":str(uuid.uuid4()),"Order":len(current)+1,
                                    "Stage":stage_to_add,"Will change?":False})
                    project.lifecycle_stages=[r["Stage"] for r in current]
                    project.lifecycle_changed.setdefault(stage_to_add,False)
                    st.session_state[version_key]+=1
                    st.rerun()
        else:
            st.caption("All standard stages are already selected.")

    with st.expander("Scope notes & resources"):
        project.scoping_notes=st.text_area("Scope boundaries, assumptions, sources",
            value=project.scoping_notes,height=110,key=f"{project.name}_scoping_notes")
        guidance=APP_ROOT / "assets" / "scopingexercise.pdf"
        if guidance.exists():
            st.download_button("Download scoping guide",guidance.read_bytes(),
                file_name="scopingexercise.pdf",mime="application/pdf")
    st.session_state.scoping_done=scoping_is_done(project)
    if not st.session_state.scoping_done:
        st.warning("Add a functional unit and at least one lifecycle stage.")
    bottom_nav()

elif step == 2:
    render_step_header(3, "Choose factors", "Select three relevant factors in each sustainability dimension.")

# Require scoping completion
    if not st.session_state.get("scoping_done"):
        st.warning("Complete the functional unit and lifecycle in Scope before choosing factors.")
        if st.button("Go to Scope & lifecycle",on_click=_set_workflow_step,args=(1,)):
            pass
        st.stop()

    # Helpful fold-outs with factor meanings
    with st.expander("🔎 Factor definitions (Environmental/Social/Economic)"):
        tab_env, tab_soc, tab_eco = st.tabs(["Environmental (EF3.1)", "Social", "Economic"])

        with tab_env:
            for name in sorted(ENV_FACTOR_META.keys()):
                meta = ENV_FACTOR_META[name]
                with st.expander(name, expanded=False):
                    st.markdown(
                        f"**Indicator:** {meta['indicator']}  \n"
                        f"**Category:** {meta['category']}  \n"
                        f"**Method:** {meta['method']} ({meta['version']})  \n"
                        f"**UUID:** `{meta['uuid']}` \n"
                        f"**Explanation:** {meta['explanation']} \n"
                    )

        with tab_soc:
            for name in sorted(SOCIAL_FACTOR_META.keys()):
                with st.expander(name, expanded=False):
                    st.markdown(SOCIAL_FACTOR_META[name])

        with tab_eco:
            for name in sorted(ECON_FACTOR_META.keys()):
                with st.expander(name, expanded=False):
                    st.markdown(ECON_FACTOR_META[name])


    def pick3(label, factors_list, keyprefix, current_selection):
        options = factor_names(factors_list)
        default = (current_selection if current_selection is not None
                   else [f["name"] for f in factors_list if f["selected"]])
        chosen = st.multiselect(f"{label} factors", options=options, default=default,
                                key=f"{project.name}_{keyprefix}", max_selections=3,
                                help="Choose the three factors most relevant to this assessment.")
        st.caption(f"{len(chosen)} of 3 selected")
        return chosen

    tab_env, tab_soc, tab_eco = st.tabs(["Environmental", "Social", "Economic"])
    with tab_env:
        env_sel = pick3("Environmental", ENVIRONMENTAL_FACTORS, "ENV_SEL",
                        project.selected_factors.get("Environmental"))
    with tab_soc:
        soc_sel = pick3("Social", SOCIAL_FACTORS, "SOC_SEL",
                        project.selected_factors.get("Social"))
    with tab_eco:
        eco_sel = pick3("Economic", ECONOMIC_FACTORS, "ECO_SEL",
                        project.selected_factors.get("Economic"))

    project.selected_factors["Environmental"] = env_sel
    project.selected_factors["Social"] = soc_sel
    project.selected_factors["Economic"] = eco_sel


    # Ensure grid has all combinations
    all9 = env_sel + soc_sel + eco_sel
    project.ensure_grid(all9)
    bottom_nav()

# -------------------------------
# Step 4: Scoring grid
# -------------------------------
elif step == 3:
    render_step_header(4,"Assess stages","Score one lifecycle stage at a time and explicitly flag missing knowledge.")
    all9 = sum((project.selected_factors.get(cat,[])
                for cat in ("Environmental","Social","Economic")),[])
    if any(len(project.selected_factors.get(cat,[])) != 3
           for cat in ("Environmental","Social","Economic")):
        st.warning("Choose three factors per dimension before assessing stages.")
        st.button("Go to Choose factors",on_click=_set_workflow_step,args=(2,))
        st.stop()
    project.ensure_grid(all9)
    stages = project.assessment_stages()
    if not stages:
        st.warning("Choose lifecycle stages in Scope before assessing.")
        st.button("Go to Scope & lifecycle",on_click=_set_workflow_step,args=(1,))
        st.stop()

    n_scored = sum(project.grid.get(stg,{}).get(f,FactorScore()).score is not None
                   for stg in stages for f in all9)
    total = len(stages) * len(all9)
    progress_left,progress_right = st.columns([4,1],vertical_alignment="center")
    with progress_left:
        st.progress(n_scored/total if total else 0)
    with progress_right:
        st.caption(f"{n_scored} / {total} scored")

    stage_key = f"{project.name}_active_stage"
    if st.session_state.get(stage_key) not in stages:
        st.session_state[stage_key] = stages[0]

    def change_stage(direction):
        index=stages.index(st.session_state[stage_key])
        index=max(0,min(len(stages)-1,index+direction))
        st.session_state[stage_key]=stages[index]

    previous,choice,next_stage = st.columns([.65,5,.65],vertical_alignment="bottom")
    with previous:
        st.button("←",key="previous_lifecycle_stage",on_click=change_stage,
                  args=(-1,),disabled=st.session_state[stage_key]==stages[0],
                  help="Previous stage",use_container_width=True)
    with choice:
        stage = st.selectbox("Lifecycle stage",stages,key=stage_key)
    with next_stage:
        st.button("→",key="next_lifecycle_stage",on_click=change_stage,
                  args=(1,),disabled=st.session_state[stage_key]==stages[-1],
                  help="Next stage",use_container_width=True)

    stage_records = [project.grid[stage][f] for f in all9]
    stage_scored = sum(fs.score is not None for fs in stage_records)
    stage_flagged = sum(fs.unknown or fs.to_research for fs in stage_records)
    st.caption(f"{stage_scored} of 9 factors scored  ·  {stage_flagged} flagged for follow-up" +
               ("  ·  This stage is expected to change" if project.lifecycle_changed.get(stage,False) else ""))
    st.markdown("#### Scoring scale")
    render_score_guide()
    assumptions_editor(project, context_key="scoring", title="Working assumptions")

    tab_env,tab_soc,tab_econ = st.tabs(["Environmental","Social","Economic"])
    factor_definitions = {
        cat:{item["name"]:item["explanation"] for item in source}
        for cat,source in (("Environmental",ENVIRONMENTAL_FACTORS),
                           ("Social",SOCIAL_FACTORS),("Economic",ECONOMIC_FACTORS))
    }
    for cat,tab in zip(("Environmental","Social","Economic"),
                       (tab_env,tab_soc,tab_econ)):
        with tab:
            st.markdown(
                f'<div class="petal-dimension-head"><span class="petal-dimension-dot" '
                f'style="background:{DIMENSION_COLORS[cat]}"></span>'
                f'<strong>{cat}</strong></div>',unsafe_allow_html=True)
            cols=st.columns(3,gap="medium")
            for i,fname in enumerate(project.selected_factors[cat]):
                fs=project.grid.setdefault(stage,{}).setdefault(fname,FactorScore())
                with cols[i]:
                    with st.container(border=True):
                        st.markdown(f"**{fname}**")
                        st.caption(factor_definitions[cat].get(fname,""))
                        current=("To research" if fs.to_research else
                                 "I don't know" if fs.unknown else
                                 "Scored" if fs.score is not None else "Not assessed")
                        key=f"{project.name}_{stage}_{fname}"
                        status=st.selectbox("Status",["Not assessed","Scored","I don't know","To research"],
                                            index=["Not assessed","Scored","I don't know","To research"].index(current),
                                            key=f"{key}_status")
                        score=st.slider("Score",min_value=1,max_value=5,
                                        value=int(fs.score) if fs.score is not None else 3,
                                        disabled=status != "Scored",key=f"{key}_score")
                        if status=="Scored":
                            fs.score=float(score);fs.unknown=False;fs.to_research=False
                        elif status=="I don't know":
                            fs.score=None;fs.unknown=True;fs.to_research=False
                        elif status=="To research":
                            fs.score=None;fs.unknown=False;fs.to_research=True
                        else:
                            fs.score=None;fs.unknown=False;fs.to_research=False
                        fs.note=st.text_area("Reason or evidence",value=fs.note,
                                             key=f"{key}_note",height=90,
                                             placeholder="Why this score? Add evidence, assumptions or a source if useful.")
    bottom_nav()

elif step == 4:
    render_step_header(5,"Insights & export","Explore patterns, uncertainty and alternative design choices.")
    all9=sum((project.selected_factors.get(cat,[])
              for cat in ("Environmental","Social","Economic")),[])
    if any(len(project.selected_factors.get(cat,[])) != 3
           for cat in ("Environmental","Social","Economic")):
        st.warning("Choose three factors in each dimension before viewing insights.")
        st.button("Go to Choose factors",on_click=_set_workflow_step,args=(2,))
        st.stop()
    project.ensure_grid(all9)
    grid=project.assessment_grid()
    avg_stage=project.average_by_stage()
    avg_factor=project.average_by_factor()
    overall=project.overall_score()
    cat_avg=category_means(project,avg_factor)
    valid_stages={key:value for key,value in avg_stage.items() if math.isfinite(value)}
    total_cells=sum(len(factors) for factors in grid.values())
    scored_cells=sum(fs.score is not None for factors in grid.values() for fs in factors.values())
    gap_cells=total_cells-scored_cells
    flagged_cells=sum((fs.unknown or fs.to_research) and fs.score is None
                      for factors in grid.values() for fs in factors.values())
    to_research=collect_to_research(project)
    unknown_factors=collect_unknown_factors(project)
    flagged_stages=set(to_research)|set(unknown_factors)
    stage_count=len(project.assessment_stages())
    flagged_count=len(flagged_stages)
    flagged_pct=100*flagged_count/stage_count if stage_count else 0

    # Result pages are separate workspaces, not one enormous scrolling document.
    overview_tab,gaps_tab,scenario_tab,export_tab=st.tabs(
        ["Overview","Knowledge gaps","Scenarios","Export"])

    with overview_tab:
        a,b,c=st.columns(3)
        a.metric("Stages assessed",stage_count)
        b.metric("Comparisons scored",f"{scored_cells} / {total_cells}")
        c.metric("Explicit knowledge gaps",flagged_cells)

        left,right=st.columns([1.25,1],gap="large")
        with left:
            with st.container(border=True):
                st.plotly_chart(seed_flower_petal_chart(cat_avg),use_container_width=True,
                    config=plot_export_config("PETAL_petal",1100,920,image_format=(
                        "svg" if st.session_state.get("petal_download_svg",False) else "png"),scale=4))
        with right:
            st.markdown("#### Sustainability dimensions")
            for category in ("Environmental","Social","Economic"):
                value=cat_avg.get(category,float("nan"))
                display=f"{value:.1f} / 5" if math.isfinite(value) else "Not assessed"
                st.markdown(
                    f'<div class="petal-dimension-head"><span class="petal-dimension-dot" '
                    f'style="background:{DIMENSION_COLORS[category]}"></span><strong>{category}</strong>'
                    f'<span style="margin-left:auto;font-size:.85rem;color:#6E6C68">{display}</span></div>',
                    unsafe_allow_html=True)
            st.caption("Each petal represents one sustainability dimension. The dotted ring marks score 3: equal to the reference product.")
            if valid_stages:
                worst=min(valid_stages,key=valid_stages.get)
                st.markdown("**Stage to examine**")
                st.write(worst)
            if gap_cells:
                st.caption(f"{gap_cells} comparisons are unscored. Patterns may change as evidence improves.")
            else:
                st.caption("All selected comparisons have a score." if total_cells else "No scores yet.")
            st.caption("Means summarise ordinal judgments; findings are indicative, not conclusive.")

        view_factor,view_stage=st.tabs(["By factor","By lifecycle stage"])
        stage_df=pd.DataFrame([{"Lifecycle stage":k,"Average score":round(v,2) if math.isfinite(v) else None}
                               for k,v in avg_stage.items()],columns=["Lifecycle stage","Average score"])
        factor_df=pd.DataFrame([{"Factor":k,"Average score":round(v,2)} for k,v in avg_factor.items()],
                               columns=["Factor","Average score"])
        with view_factor:
            data=to_plot_df(factor_df,"Factor","Average score").rename(columns={"Factor":"Category"})
            st.plotly_chart(horizontal_delta_bar(data,"Qualitative comparison by factor"),
                use_container_width=True,config=plot_export_config("PETAL_factors"))
            with st.expander("Data table"):
                st.dataframe(factor_df,use_container_width=True,hide_index=True)
        with view_stage:
            data=to_plot_df(stage_df,"Lifecycle stage","Average score").rename(
                columns={"Lifecycle stage":"Category"})
            st.plotly_chart(horizontal_delta_bar(data,"Qualitative comparison by stage"),
                use_container_width=True,config=plot_export_config("PETAL_stages"))
            with st.expander("Data table"):
                st.dataframe(stage_df,use_container_width=True,hide_index=True)
        if valid_stages:
            with st.expander("Examine a lifecycle stage"):
                stage_detail=st.selectbox("Stage",list(valid_stages),key=f"{project.name}_detail_stage")
                details=pd.DataFrame([{
                    "Dimension":next((cat for cat in ("Environmental","Social","Economic")
                                      if fname in project.selected_factors.get(cat,[])),""),
                    "Factor":fname,"Score":fs.score,"Note":fs.note,
                } for fname,fs in grid.get(stage_detail,{}).items()])
                st.dataframe(details,use_container_width=True,hide_index=True)

    with gaps_tab:
        st.markdown("### Knowledge gaps")
        st.markdown(
            f'<div style="border:1px solid #E9E8E3;border-radius:16px;background:#fff;padding:1.2rem 1.3rem">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap">'
            f'<strong>Stages with explicit flags</strong><span>{flagged_count} of {stage_count} · {flagged_pct:.0f}%</span></div>'
            f'<div style="height:10px;border-radius:99px;background:#F0F0EC;overflow:hidden;margin-top:1rem">'
            f'<div style="width:{flagged_pct:.2f}%;height:100%;background:#F28500"></div></div>'
            '</div>',unsafe_allow_html=True)
        st.caption("Presence of knowledge-gap flags, not severity or statistical uncertainty. Unscored factors are excluded from averages.")
        flagged_rows=[]
        for stage,factors in grid.items():
            for factor,fs in factors.items():
                if fs.to_research or fs.unknown:
                    flagged_rows.append({"Stage":stage,"Factor":factor,
                                         "Status":"To research" if fs.to_research else "I don't know",
                                         "Note":fs.note})
        if flagged_rows:
            st.dataframe(pd.DataFrame(flagged_rows),use_container_width=True,hide_index=True)
        else:
            st.caption("No explicit knowledge gaps flagged.")
        uncategorised=gap_cells-flagged_cells
        if uncategorised>0:
            st.caption(f"{uncategorised} additional comparisons are not assessed and have no explicit flag.")
        if project.assumptions:
            with st.expander(f"Assumptions · {len(project.assumptions)}"):
                for note in project.assumptions:
                    st.markdown(f"- {html_escape(note)}")

    with scenario_tab:
        st.markdown("### Compare an alternative")
        if not valid_stages:
            st.info("Score at least one comparison in Assess stages to create a scenario.")
        else:
            stage_choice=st.selectbox("Lifecycle stage",list(valid_stages),
                    key=f"{project.name}_scenario_stage_choice")
            stage_scen=dict(project.scenario_scores.get(stage_choice,{}))
            active_baseline=grid[stage_choice]

            reset_a,reset_b,_=st.columns([1.4,1.4,3])
            with reset_a:
                if st.button("Reset this stage",use_container_width=True):
                    project.scenario_scores.pop(stage_choice,None)
                    for key in list(st.session_state):
                        if key.startswith(f"{project.name}_scenario_{stage_choice}_"):
                            del st.session_state[key]
                    st.rerun()
            with reset_b:
                if st.button("Reset all scenarios",use_container_width=True):
                    project.scenario_scores={}
                    for key in list(st.session_state):
                        if key.startswith(f"{project.name}_scenario_") and key != f"{project.name}_scenario_stage_choice":
                            del st.session_state[key]
                    st.rerun()

            dimension_columns=st.columns(3,gap="medium")
            for column,cat in zip(dimension_columns,("Environmental","Social","Economic")):
                with column:
                    st.markdown(f'<div class="petal-dimension-head">'
                        f'<span class="petal-dimension-dot" style="background:{DIMENSION_COLORS[cat]}"></span>'
                        f'<strong>{cat}</strong></div>',unsafe_allow_html=True)
                    for factor in project.selected_factors.get(cat,[]):
                        fs=active_baseline.get(factor)
                        if fs is None or fs.score is None:
                            continue
                        new_score=st.slider(factor,1,5,
                            int(stage_scen.get(factor,fs.score)),
                            key=f"{project.name}_scenario_{stage_choice}_{factor}",
                            help=f"Original: {fs.score:.0f}")
                        if float(new_score) != float(fs.score):
                            stage_scen[factor]=float(new_score)
                        else:
                            stage_scen.pop(factor,None)
            if stage_scen:
                project.scenario_scores[stage_choice]=stage_scen
            else:
                project.scenario_scores.pop(stage_choice,None)
            st.caption("Changing a scenario does not overwrite the original assessment.")

            scen_stage_avgs={}
            scen_factor_values={}
            for stg,records in grid.items():
                values=[]
                overrides=project.scenario_scores.get(stg,{})
                for factor,fs in records.items():
                    value=overrides.get(factor,fs.score)
                    # Do not fabricate a value for an unknown/unassessed factor.
                    if fs.score is None or value is None:
                        continue
                    number=float(value)
                    values.append(number)
                    scen_factor_values.setdefault(factor,[]).append(number)
                scen_stage_avgs[stg]=statistics.mean(values) if values else float("nan")
            scen_factor_avgs={factor:statistics.mean(values)
                              for factor,values in scen_factor_values.items()}
            scenario_cat=category_means(project,scen_factor_avgs)
            changed=any(
                fs.score is not None and abs(float(project.scenario_scores.get(stg,{}).get(f,fs.score))
                                             -float(fs.score))>1e-9
                for stg,fac in grid.items() for f,fs in fac.items()
            )
            if not changed:
                st.caption("The scenario currently matches the original assessment.")

            comparison_left,comparison_right=st.columns([1.15,1],gap="large")
            with comparison_left:
                with st.container(border=True):
                    st.plotly_chart(seed_flower_overlay(cat_avg,scenario_cat),
                        use_container_width=True,config=plot_export_config("PETAL_scenario_petal",
                        1100,920,image_format="svg" if st.session_state.get("petal_download_svg",False) else "png",scale=4))
                    st.caption("Outline = original · Translucent fill = scenario")
            with comparison_right:
                st.markdown("#### Dimension comparison")
                comparison=pd.DataFrame([{
                    "Dimension":cat,
                    "Original":round(cat_avg[cat],2) if math.isfinite(cat_avg[cat]) else None,
                    "Scenario":round(scenario_cat[cat],2) if math.isfinite(scenario_cat[cat]) else None,
                } for cat in ("Environmental","Social","Economic")])
                st.dataframe(comparison,use_container_width=True,hide_index=True)
                st.caption("The scenario carries changes across all stages you edit.")
            with st.expander("Detailed comparison"):
                baseline_stage=pd.DataFrame([{"Category":k,"Score":v} for k,v in avg_stage.items()])
                scenario_stage=pd.DataFrame([{"Category":k,"Score":v} for k,v in scen_stage_avgs.items()])
                if not baseline_stage.empty:
                    bar1=overlay_delta_bars(
                        to_plot_df(baseline_stage,"Category","Score"),
                        to_plot_df(scenario_stage,"Category","Score"),
                        "By lifecycle stage")
                    st.plotly_chart(bar1,use_container_width=True,
                        config=plot_export_config("PETAL_scenario_stages"))
                baseline_factor=pd.DataFrame([{"Category":k,"Score":v} for k,v in avg_factor.items()])
                scenario_factor=pd.DataFrame([{"Category":k,"Score":v} for k,v in scen_factor_avgs.items()])
                if not baseline_factor.empty:
                    bar2=overlay_delta_bars(
                        to_plot_df(baseline_factor,"Category","Score"),
                        to_plot_df(scenario_factor,"Category","Score"),
                        "By factor")
                    st.plotly_chart(bar2,use_container_width=True,
                        config=plot_export_config("PETAL_scenario_factors"))
            project.tradeoff_notes=st.text_area("Trade-off notes",value=project.tradeoff_notes,
                key=f"{project.name}_tradeoff_notes",height=110,
                placeholder="Which trade-offs matter for the next design decision?")

    with export_tab:
        st.markdown("### Save & share")
        st.caption("Project JSON is re-importable. Results JSON and Markdown are reports.")
        data={
            "project":project.name,"description":project.description,"trl":project.trl,
            "functional_unit":project.functional_unit,"core_function":project.core_function,
            "stakeholder_notes":project.stakeholder_notes,"scoping_notes":project.scoping_notes,
            "assumptions":project.assumptions,"lifecycle_stages":project.assessment_stages(),
            "lifecycle_changed":{k:project.lifecycle_changed.get(k,False)
                                 for k in project.assessment_stages()},
            "selected_factors":project.selected_factors,
            "grid":{stage:{factor:asdict(fs) for factor,fs in records.items()}
                    for stage,records in grid.items()},
            "to_research":to_research,"unknown_factors":unknown_factors,
            "coverage":{"assessed_cells":total_cells,"scored_cells":scored_cells,
                        "unscored_cells":gap_cells,"explicitly_flagged_cells":flagged_cells,
                        "assessed_stages":stage_count,"stages_with_flags":flagged_count,
                        "share_stages_with_flags_pct":round(flagged_pct,1)},
            "averages":{"by_stage":avg_stage,"by_factor":avg_factor,"overall":overall},
            "tradeoff_notes":project.tradeoff_notes,
            "scenario_scores":{stage:{f:v for f,v in fac.items() if f in grid.get(stage,{})}
                               for stage,fac in project.scenario_scores.items() if stage in grid},
        }
        def safe_json(value):
            if isinstance(value,float) and not math.isfinite(value):
                return None
            if isinstance(value,dict):
                return {str(k):safe_json(v) for k,v in value.items()}
            if isinstance(value,list):
                return [safe_json(v) for v in value]
            return value
        report=[f"# {project.name} — PETAL assessment","",
                f"**TRL:** {project.trl}",
                f"**Functional unit:** {project.functional_unit or 'Not defined'}", ""]
        if project.description:
            report.extend([project.description,""])
        if project.core_function:
            report.extend(["## Reference product",project.core_function,""])
        if project.stakeholder_notes:
            report.extend(["## Stakeholders",project.stakeholder_notes,""])
        report.extend(["## Lifecycle stages"])
        for stage in project.lifecycle_stages:
            flag=" (expected to change)" if project.lifecycle_changed.get(stage,False) else ""
            report.append(f"- {stage}{flag}")
        report.extend(["","## Factors"])
        for cat in ("Environmental","Social","Economic"):
            report.append(f"- **{cat}:** "+", ".join(project.selected_factors.get(cat,[])))
        report.extend(["","## Assessment coverage",
                       f"- Scored: {scored_cells} / {total_cells}",
                       f"- Explicit knowledge-gap flags: {flagged_cells}",
                       f"- Stages with flags: {flagged_count} / {stage_count}",
                       "_Flags indicate missing knowledge, not its severity._", "",
                       "## Qualitative stage means"])
        for stage,value in avg_stage.items():
            report.append(f"- {stage}: {value:.2f}" if math.isfinite(value) else f"- {stage}: unscored")
        report.extend(["","## Factor means"])
        for factor,value in avg_factor.items():
            report.append(f"- {factor}: {value:.2f}")
        report.extend(["","## Explicit knowledge gaps"])
        rows=[(stage,factor,"To research" if fs.to_research else "I don't know",fs.note)
              for stage,facs in grid.items() for factor,fs in facs.items()
              if fs.to_research or fs.unknown]
        if rows:
            for stage,factor,status,note in rows:
                report.append(f"- **{stage} / {factor}:** {status}"+(f" — {note}" if note else ""))
        else:
            report.append("- No explicit flags")
        report.extend(["","## Assumptions"])
        report.extend([f"- {a}" for a in project.assumptions] or ["- None recorded"])
        if project.scoping_notes:
            report.extend(["","## Scope notes",project.scoping_notes])
        if project.tradeoff_notes:
            report.extend(["","## Trade-offs",project.tradeoff_notes])
        report.extend(["","_Scores are indicative ordinal judgments compared with a reference product; "
                       "means are discussion aids, not conclusive sustainability measurements._"])
        repname=project.name.replace(" ","_")
        cards=st.columns(3,gap="medium")
        with cards[0]:
            with st.container(border=True):
                st.markdown("**Project JSON**")
                st.caption("Save and reopen your work")
                st.download_button("Download project",json.dumps(asdict(project),indent=2),
                    file_name=f"{repname}.json",mime="application/json",use_container_width=True,
                    type="primary")
        with cards[1]:
            with st.container(border=True):
                st.markdown("**Results JSON**")
                st.caption("Structured analysis snapshot")
                st.download_button("Download results",json.dumps(safe_json(data),indent=2,allow_nan=False),
                    file_name=f"{repname}_results.json",mime="application/json",use_container_width=True)
        with cards[2]:
            with st.container(border=True):
                st.markdown("**Markdown report**")
                st.caption("Summary for documentation")
                st.download_button("Download report","\n".join(report),
                    file_name=f"{repname}_report.md",mime="text/markdown",use_container_width=True)
        with st.expander("Figure export quality"):
            st.checkbox("Export petal charts as SVG (instead of high-resolution PNG)",
                        key="petal_download_svg")
            st.caption("Use the chart toolbar to save figures.")

    bottom_nav()


# -------------------------------
# Footer
# -------------------------------
st.markdown('<div class="petal-footer-note">PETAL · Indicative qualitative assessment, not a substitute for LCA or S-LCA.</div>',unsafe_allow_html=True)
