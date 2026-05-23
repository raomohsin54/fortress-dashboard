"""
Personal Financial Intelligence Report — Version 8.0
Fortress Strategy v7.0 | Streamlit Cloud Edition
Premium dark theme with emerald/gold palette, mobile-first layout
"""

import os, io, json, warnings
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from scipy.stats import median_abs_deviation

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fortress Financial Intelligence",
    page_icon="🏰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────────────────────
# PREMIUM THEME — Deep navy + emerald + gold
# ─────────────────────────────────────────────────────────────────────────────
THEME = {
    "bg":       "#040d1a",
    "panel":    "#071224",
    "panel2":   "#0a1930",
    "card":     "#0d1f38",
    "card2":    "#0f2543",
    "border":   "#1a3a5c",
    "text":     "#e8f4fd",
    "muted":    "#7ba3c4",
    "dim":      "#4a6d8c",
    "gold":     "#d4af37",
    "gold2":    "#f0cc5a",
    "gold3":    "#a87d1a",
    "emerald":  "#10b981",
    "emerald2": "#34d399",
    "emerald3": "#064e35",
    "red":      "#f43f5e",
    "red2":     "#fda4af",
    "orange":   "#f97316",
    "yellow":   "#fbbf24",
    "blue":     "#3b82f6",
    "blue2":    "#93c5fd",
    "purple":   "#a78bfa",
    "teal":     "#22d3ee",
    "pink":     "#f472b6",
    "slate":    "#4a6d8c",
}

GOLD_SEQ = ["#d4af37","#f0cc5a","#10b981","#22d3ee","#3b82f6","#a78bfa","#f97316","#f43f5e","#fbbf24","#f472b6"]

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS — mobile-first, high contrast, no visibility issues
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

:root {{
  --bg:      {THEME['bg']};
  --panel:   {THEME['panel']};
  --card:    {THEME['card']};
  --text:    {THEME['text']};
  --muted:   {THEME['muted']};
  --gold:    {THEME['gold']};
  --emerald: {THEME['emerald']};
  --border:  {THEME['border']};
}}

html, body, .stApp {{
  background: linear-gradient(160deg, #030a14 0%, #040d1a 40%, #05101f 100%) !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
}}

.block-container {{
  padding: 0.8rem 1rem 2rem !important;
  max-width: 1400px !important;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, #040d1a 0%, #030810 100%) !important;
  border-right: 1px solid {THEME['border']} !important;
  min-width: 260px !important;
}}
section[data-testid="stSidebar"] * {{
  color: {THEME['text']} !important;
}}
section[data-testid="stSidebar"] .stNumberInput label,
section[data-testid="stSidebar"] .stRadio label,
section[data-testid="stSidebar"] .stCheckbox label {{
  color: {THEME['muted']} !important;
  font-size: 13px !important;
}}
section[data-testid="stSidebar"] input {{
  background: {THEME['card']} !important;
  color: {THEME['text']} !important;
  border: 1px solid {THEME['border']} !important;
}}

/* ── Metric cards ── */
div[data-testid="metric-container"] {{
  background: linear-gradient(145deg, {THEME['card']} 0%, {THEME['panel2']} 100%) !important;
  border: 1px solid {THEME['border']} !important;
  border-top: 2px solid {THEME['gold']}44 !important;
  box-shadow: 0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.03) !important;
  border-radius: 14px !important;
  padding: 18px 20px !important;
}}
div[data-testid="metric-container"] label {{
  color: {THEME['muted']} !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.06em !important;
}}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{
  color: {THEME['gold2']} !important;
  font-size: 1.6rem !important;
  font-weight: 800 !important;
  font-family: 'DM Mono', monospace !important;
}}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {{
  color: {THEME['muted']} !important;
  font-size: 12px !important;
}}

/* ── Charts ── */
.stPlotlyChart {{
  background: {THEME['panel']} !important;
  border: 1px solid {THEME['border']} !important;
  border-radius: 14px !important;
  padding: 8px 4px !important;
  box-shadow: 0 8px 32px rgba(0,0,0,0.35) !important;
}}
.js-plotly-plot .plotly, .plot-container {{ background: transparent !important; }}

/* ── Dataframe ── */
.stDataFrame, div[data-testid="stDataFrame"] {{
  background: {THEME['panel']} !important;
  border: 1px solid {THEME['border']} !important;
  border-radius: 12px !important;
  overflow: hidden !important;
}}
.stDataFrame table {{
  background: {THEME['panel']} !important;
  color: {THEME['text']} !important;
}}
.stDataFrame th {{
  background: {THEME['card']} !important;
  color: {THEME['gold2']} !important;
  border-bottom: 1px solid {THEME['border']} !important;
  font-size: 12px !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
}}
.stDataFrame td {{
  color: {THEME['text']} !important;
  border-color: {THEME['border']} !important;
  font-family: 'DM Mono', monospace !important;
  font-size: 13px !important;
}}
.stDataFrame tr:hover td {{
  background: {THEME['card2']} !important;
}}

/* ── Alerts ── */
.stAlert {{
  background: {THEME['card']} !important;
  color: {THEME['text']} !important;
  border: 1px solid {THEME['border']} !important;
  border-radius: 10px !important;
}}

/* ── Buttons ── */
button, .stButton button {{
  background: linear-gradient(135deg, {THEME['card']} 0%, {THEME['panel2']} 100%) !important;
  color: {THEME['gold2']} !important;
  border: 1px solid {THEME['gold3']} !important;
  border-radius: 8px !important;
  font-family: 'DM Sans', sans-serif !important;
  font-weight: 600 !important;
  transition: all 0.2s !important;
}}
button:hover {{ border-color: {THEME['gold']} !important; box-shadow: 0 0 12px {THEME['gold']}33 !important; }}

/* ── Inputs ── */
input, textarea, select {{
  color: {THEME['text']} !important;
  background: {THEME['card']} !important;
  border: 1px solid {THEME['border']} !important;
  border-radius: 8px !important;
}}
input:focus {{ border-color: {THEME['gold']}88 !important; box-shadow: 0 0 8px {THEME['gold']}22 !important; }}

/* ── Divider ── */
hr {{ border-color: {THEME['border']} !important; opacity: 0.5 !important; }}

/* ── Radio & checkbox ── */
[data-baseweb="radio"] div, [data-baseweb="checkbox"] div {{ color: {THEME['text']} !important; }}
[data-baseweb="radio"] [role="radio"] {{ border-color: {THEME['gold']}88 !important; }}

/* ── Expander ── */
details summary {{
  background: {THEME['card']} !important;
  color: {THEME['text']} !important;
  border: 1px solid {THEME['border']} !important;
  border-radius: 8px !important;
  padding: 10px 16px !important;
}}

/* ── Hide default chrome ── */
#MainMenu, footer, header {{ visibility: hidden !important; }}

/* ── Success/Info/Warning ── */
div[data-testid="stSuccessMessage"] {{ background: {THEME['emerald3']}66 !important; border: 1px solid {THEME['emerald']}44 !important; border-radius: 10px !important; }}
div[data-testid="stInfoMessage"]    {{ background: {THEME['card']} !important; border: 1px solid {THEME['blue']}44 !important; border-radius: 10px !important; }}
div[data-testid="stWarningMessage"] {{ background: #291500 !important; border: 1px solid {THEME['orange']}44 !important; border-radius: 10px !important; }}
div[data-testid="stErrorMessage"]   {{ background: #1f0010 !important; border: 1px solid {THEME['red']}44 !important; border-radius: 10px !important; }}
div[data-testid="stSuccessMessage"] p,
div[data-testid="stInfoMessage"] p,
div[data-testid="stWarningMessage"] p,
div[data-testid="stErrorMessage"] p {{ color: {THEME['text']} !important; }}

/* ── Selectbox / number_input ── */
div[data-baseweb="select"] > div {{
  background: {THEME['card']} !important;
  border: 1px solid {THEME['border']} !important;
  border-radius: 8px !important;
  color: {THEME['text']} !important;
}}
div[data-baseweb="select"] span {{ color: {THEME['text']} !important; }}
div[data-baseweb="popover"] {{ background: {THEME['card2']} !important; border: 1px solid {THEME['border']} !important; }}

/* ── Mobile tweaks ── */
@media (max-width: 768px) {{
  .block-container {{ padding: 0.5rem 0.5rem 2rem !important; }}
  div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{ font-size: 1.3rem !important; }}
  div[data-testid="column"] {{ min-width: 140px !important; }}
  h1 {{ font-size: 1.4rem !important; }}
  h2 {{ font-size: 1.1rem !important; }}
}}

/* ── Tabs ── */
button[data-baseweb="tab"] {{
  color: {THEME['muted']} !important;
  background: transparent !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  font-weight: 600 !important;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
  color: {THEME['gold2']} !important;
  border-bottom: 2px solid {THEME['gold']} !important;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def fmt_money(x):
    try: return f"${float(x):,.0f}"
    except: return str(x)

def pct(x):
    try: return f"{float(x):.1f}%"
    except: return str(x)

def section_header(icon, title, subtitle=""):
    st.markdown(f"""
    <div style="margin:28px 0 16px; padding:18px 22px;
                border:1px solid {THEME['border']}; border-radius:14px;
                background:linear-gradient(135deg,{THEME['panel']} 0%,{THEME['card']} 100%);
                box-shadow:0 4px 20px rgba(0,0,0,0.3);">
      <div style="display:flex; align-items:center; gap:14px;">
        <div style="font-size:26px; width:42px; height:42px; display:flex; align-items:center;
                    justify-content:center; background:{THEME['card2']};
                    border-radius:10px; border:1px solid {THEME['border']};">{icon}</div>
        <div>
          <div style="font-size:18px; font-weight:800; color:{THEME['text']};
                      font-family:'DM Sans',sans-serif; letter-spacing:-0.02em;">{title}</div>
          {f'<div style="font-size:12px; color:{THEME["muted"]}; margin-top:3px; font-weight:400;">{subtitle}</div>' if subtitle else ''}
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

def info_box(title, body, accent=None):
    accent = accent or THEME["blue"]
    st.markdown(f"""
    <div style="margin:10px 0 16px; padding:14px 18px;
                background:linear-gradient(135deg,{THEME['panel']} 0%,{THEME['card']} 100%);
                border-left:4px solid {accent}; border-radius:10px;
                box-shadow:0 2px 12px rgba(0,0,0,0.2);">
      <div style="font-weight:700; margin-bottom:6px; color:{THEME['text']};
                  font-family:'DM Sans',sans-serif;">{title}</div>
      <div style="color:{THEME['muted']}; line-height:1.6; font-size:13.5px;">{body}</div>
    </div>""", unsafe_allow_html=True)

def kpi_card(label, value, sub="", color=None):
    color = color or THEME["gold"]
    st.markdown(f"""
    <div style="background:linear-gradient(145deg,{THEME['card']} 0%,{THEME['panel2']} 100%);
                border:1px solid {THEME['border']}; border-top:2px solid {color}55;
                border-radius:14px; padding:18px 20px; text-align:center;
                box-shadow:0 4px 20px rgba(0,0,0,0.35);">
      <div style="font-size:11px; font-weight:700; color:{THEME['muted']};
                  text-transform:uppercase; letter-spacing:0.07em; margin-bottom:8px;">{label}</div>
      <div style="font-size:1.55rem; font-weight:800; color:{color};
                  font-family:'DM Mono',monospace;">{value}</div>
      {f'<div style="font-size:12px; color:{THEME["dim"]}; margin-top:5px;">{sub}</div>' if sub else ''}
    </div>""", unsafe_allow_html=True)

def apply_layout(fig, title="", height=420):
    fig.update_layout(
        title=dict(
            text=title, x=0.015, y=0.97,
            font=dict(size=15, color=THEME["gold2"], family="DM Sans")
        ),
        paper_bgcolor=THEME["panel"],
        plot_bgcolor=THEME["panel"],
        font=dict(color=THEME["text"], size=12, family="DM Sans"),
        xaxis=dict(
            showgrid=False, color=THEME["muted"], linecolor=THEME["border"],
            tickfont=dict(color=THEME["text"], size=11)
        ),
        yaxis=dict(
            showgrid=True, gridcolor=THEME["border"]+"66", zeroline=False,
            color=THEME["muted"], tickfont=dict(color=THEME["text"], size=11)
        ),
        margin=dict(l=40, r=40, t=55, b=40),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=THEME["card2"], font_color=THEME["text"],
            bordercolor=THEME["border"], font_size=12
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01, x=0,
            font=dict(color=THEME["text"], size=11),
            bgcolor="rgba(0,0,0,0)"
        ),
        height=height,
    )
    try:
        fig.update_layout(scene=dict(
            bgcolor=THEME["panel"],
            xaxis=dict(backgroundcolor=THEME["panel"], gridcolor=THEME["border"], color=THEME["text"]),
            yaxis=dict(backgroundcolor=THEME["panel"], gridcolor=THEME["border"], color=THEME["text"]),
            zaxis=dict(backgroundcolor=THEME["panel"], gridcolor=THEME["border"], color=THEME["text"]),
        ))
    except Exception:
        pass
    return fig

def safe_plotly(fig, title="", height=420):
    try:
        apply_layout(fig, title, height)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    except Exception as e:
        info_box(f"Chart skipped: {title}", str(e), THEME["orange"])

def money_table(df, formatter="${:,.0f}"):
    return (df.style
        .format(formatter)
        .set_properties(**{
            "background-color": THEME["panel"],
            "color": THEME["text"],
            "border-color": THEME["border"],
            "font-family": "DM Mono, monospace",
            "font-size": "13px",
        })
        .set_table_styles([
            {"selector": "th", "props": [
                ("background-color", THEME["card"]),
                ("color", THEME["gold2"]),
                ("border-color", THEME["border"]),
                ("font-family", "DM Sans, sans-serif"),
                ("font-size", "11px"),
                ("text-transform", "uppercase"),
                ("letter-spacing", "0.05em"),
            ]},
            {"selector": "td", "props": [("border-color", THEME["border"])]},
            {"selector": "tr:hover td", "props": [("background-color", THEME["card2"])]},
        ]))

def normalize_cols(df):
    df = df.copy()
    df.columns = (
        df.columns.astype(str).str.strip().str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True).str.strip("_")
    )
    return df

def latest_n(arr, n=12):
    return arr.sort_values("month_start").tail(n).copy()

CATEGORY_BUCKET_MAP = {
    "HOUSING":"Essential","UTILITIES":"Essential","TRANSPORTATION":"Essential",
    "FOOD":"Essential","DAILY LIVING":"Essential","HEALTH & WELLNESS":"Essential",
    "DEBT & OBLIGATIONS":"Essential","SUBSCRIPTIONS":"Lifestyle","ENTERTAINMENT":"Lifestyle",
    "GIFTS & CHARITY":"Lifestyle","MISCELLANEOUS":"Lifestyle","SAVINGS & INVESTMENTS":"Wealth",
    "INCOME":"Income"
}

def classify_bucket(category):
    return CATEGORY_BUCKET_MAP.get(str(category).strip().upper(), "Other")

TRANSFER_KEYWORDS_INVEST = ["buy ","stocks","investment","invest","spus","spsk","slv","ivv",
    "vas","ndq","etf","shares","spte","islm","skuk","hhif","gold","commsec","ibkr",
    "interactive brokers","hejaz","stake","selfwealth","pearler"]
TRANSFER_KEYWORDS_GOAL = ["trip","travel","hotel","ticket","zakat","umrah","holiday",
    "bangkok","savings goal","emergency","car fund","house fund","wedding"]
TRANSFER_KEYWORDS_SAVINGS = ["offset","savings account","high interest","hisa","ubank","ing ",
    "macquarie savings","bonus saver","rabobank","move to savings"]

def classify_transfer_type(description, subcategory="", category=""):
    desc = str(description).lower(); sub = str(subcategory).lower()
    if any(k in desc for k in TRANSFER_KEYWORDS_INVEST) or "stocks" in sub or "investment" in sub:
        return "Investment Transfer"
    if any(k in desc for k in TRANSFER_KEYWORDS_GOAL) or "savings goal" in sub or "zakat" in desc:
        return "Goal / Planned Drawdown"
    if any(k in desc for k in TRANSFER_KEYWORDS_SAVINGS) or "savings" in sub:
        return "Savings Account Transfer"
    return "Other Transfer"

# ─────────────────────────────────────────────────────────────────────────────
# GOOGLE DRIVE LOADER
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner="📡 Syncing from Google Drive…")
def load_from_google_drive(file_id: str, credentials_json: str):
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    creds_dict = json.loads(credentials_json)
    scopes = ["https://www.googleapis.com/auth/drive.readonly"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    service = build("drive", "v3", credentials=creds, cache_discovery=False)
    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    buffer.seek(0)
    return buffer

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:16px 4px 8px; font-family:'DM Sans',sans-serif;">
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
        <span style="font-size:24px;">🏰</span>
        <div>
          <div style="font-size:18px; font-weight:800; color:{THEME['text']}; letter-spacing:-0.02em;">Fortress v7.0</div>
          <div style="font-size:11px; color:{THEME['muted']}; font-weight:400;">Financial Intelligence</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)
    st.divider()

    st.markdown(f"<div style='font-weight:700;color:{THEME['gold2']};font-size:12px;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px;'>📊 Live Parameters</div>", unsafe_allow_html=True)
    TOTAL_LIQUID_CASH     = st.number_input("Total Liquid Cash ($)", value=168000, step=1000)
    SALARY_NET_MONTHLY    = st.number_input("Net Monthly Income ($)", value=9684, step=100)
    PURCHASE_PRICE        = st.number_input("House Target ($)", value=730000, step=5000)
    MORTGAGE_REPAYMENT    = st.number_input("Monthly Repayment ($)", value=4205, step=50)
    START_PORTFOLIO_VALUE = st.number_input("Current Portfolio ($)", value=15000, step=1000)
    st.divider()

    st.markdown(f"<div style='font-weight:700;color:{THEME['gold2']};font-size:12px;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px;'>📈 DCA Phase</div>", unsafe_allow_html=True)
    dca_phase = st.radio("Active DCA Phase", ["Phase 1 ($950/mo)", "Phase 2 ($450/mo)", "Phase 3 ($1,000/mo)"], index=1)
    DCA_ACTIVE = {"Phase 1 ($950/mo)":950,"Phase 2 ($450/mo)":450,"Phase 3 ($1,000/mo)":1000}[dca_phase]
    st.divider()

    st.markdown(f"<div style='font-weight:700;color:{THEME['gold2']};font-size:12px;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px;'>👁 Sections</div>", unsafe_allow_html=True)
    show_cashflow  = st.checkbox("§1-2 · Cash Flow Engine",      value=True)
    show_spend     = st.checkbox("§3-3D · Spend Analysis",       value=True)
    show_anomaly   = st.checkbox("§4-7 · Anomaly & Forecast",    value=True)
    show_portfolio = st.checkbox("§8-9 · Portfolio & Technical", value=True)
    show_action    = st.checkbox("§10 · Action Board",           value=True)
    show_mortgage  = st.checkbox("§11 · Mortgage Stress Test",   value=True)
    show_waterfall = st.checkbox("§12 · Post-House Waterfall",   value=True)
    show_lvr       = st.checkbox("§13 · LVR Sensitivity",        value=True)
    show_readiness = st.checkbox("§14 · Purchase Readiness",     value=True)
    show_dca       = st.checkbox("§15 · DCA Engine & $1.7M",     value=True)
    st.divider()
    st.markdown(f"<div style='font-size:11px;color:{THEME['dim']};'>🕐 {datetime.now().strftime('%d %b %Y %H:%M')}</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TITLE BANNER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(135deg,{THEME['panel']} 0%,{THEME['card']} 60%,{THEME['panel']} 100%);
            border:1px solid {THEME['border']}; border-radius:18px; padding:24px 28px; margin-bottom:20px;
            box-shadow:0 8px 40px rgba(0,0,0,0.5);">
  <div style="display:flex; align-items:center; gap:18px; margin-bottom:16px; flex-wrap:wrap;">
    <div style="width:52px;height:52px;background:linear-gradient(135deg,{THEME['gold3']},{THEME['gold']});
                border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:26px;
                box-shadow:0 4px 16px {THEME['gold']}44;flex-shrink:0;">🏰</div>
    <div>
      <h1 style="margin:0; font-size:clamp(18px,4vw,26px); font-weight:800; color:{THEME['text']};
                 letter-spacing:-0.03em; font-family:'DM Sans',sans-serif;">
        Personal Financial Intelligence
      </h1>
      <p style="margin:4px 0 0; font-size:13px; color:{THEME['muted']}; font-weight:400;">
        Fortress Strategy v7.0 · Perth, WA · v8.0 Dashboard
      </p>
    </div>
  </div>
  <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:8px; font-size:12px;">
    <div style="background:{THEME['card2']}; border:1px solid {THEME['border']}; border-radius:8px;
                padding:8px 12px; color:{THEME['muted']};">📂 Google Drive · auto-sync</div>
    <div style="background:{THEME['card2']}; border:1px solid {THEME['border']}; border-radius:8px;
                padding:8px 12px; color:{THEME['muted']};">🏠 Target: $730k · Hejaz Ijarah</div>
    <div style="background:{THEME['card2']}; border:1px solid {THEME['border']}; border-radius:8px;
                padding:8px 12px; color:{THEME['muted']};">📈 Goal: $1.7M net worth · 2056</div>
    <div style="background:{THEME['card2']}; border:1px solid {THEME['border']}; border-radius:8px;
                padding:8px 12px; color:{THEME['muted']};">🔄 Auto-refresh: 5 minutes</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATA SOURCE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"<div style='font-size:12px;color:{THEME['muted']};margin-bottom:6px;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;'>📂 Data Source</div>", unsafe_allow_html=True)
data_source = st.radio("Load data from", ["Google Drive (auto-sync)", "Upload Excel manually"],
                        horizontal=True, label_visibility="collapsed")
workbook_buffer = None

if data_source == "Google Drive (auto-sync)":
    try:
        creds_json = json.dumps(dict(st.secrets["gcp_service_account"]))
        file_id    = st.secrets["gdrive_file_id"]
        workbook_buffer = load_from_google_drive(file_id, creds_json)
        st.success("✅ Loaded from Google Drive")
    except Exception as e:
        st.warning(f"⚠️ Google Drive not configured yet. ({e})")
        st.info("Switch to 'Upload Excel manually' to test your data now.")
else:
    uploaded = st.file_uploader("Upload your 'Transactions budget.xlsx'", type=["xlsx"])
    if uploaded:
        workbook_buffer = uploaded
        st.success("✅ File loaded")

with st.expander("📋 One-time Setup Guide", expanded=(workbook_buffer is None)):
    st.markdown(f"""
<div style="font-family:'DM Sans',sans-serif; color:{THEME['text']}; line-height:1.7; font-size:14px;">

### Step 1 — GitHub
Create a public repo `fortress-dashboard`, add `app.py` and `requirements.txt`.

### Step 2 — Streamlit Cloud
Deploy at share.streamlit.io → your app URL is permanent.

### Step 3 — Google Drive API
1. console.cloud.google.com → New Project → Enable **Google Drive API**
2. IAM → Service Accounts → Create → download JSON key
3. Share your Excel with the service account email
4. In Streamlit Cloud → Edit Secrets → add `gdrive_file_id` and `[gcp_service_account]`

### Step 4 — Done
Edit Excel anywhere → open dashboard → live update.
</div>""", unsafe_allow_html=True)

if workbook_buffer is None:
    st.info("⬆️ Load your workbook above to unlock all 15 sections.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# LOAD & PROCESS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner="🔄 Processing transactions…")
def load_and_process(buffer_bytes: bytes, report_as_of_str: str):
    raw_tx = pd.read_excel(io.BytesIO(buffer_bytes), sheet_name="Sheet1")
    raw_tx = normalize_cols(raw_tx)
    raw_tx = raw_tx[[c for c in raw_tx.columns if not str(c).startswith("unnamed_")]]

    try:
        raw_portfolio_sheet = pd.read_excel(io.BytesIO(buffer_bytes), sheet_name="Portfolio")
        raw_portfolio_sheet = normalize_cols(raw_portfolio_sheet)
        raw_portfolio_sheet = raw_portfolio_sheet[[c for c in raw_portfolio_sheet.columns if not str(c).startswith("unnamed_")]]
    except Exception:
        raw_portfolio_sheet = pd.DataFrame()

    # ── Also try to read a trade log / transactions sheet for portfolio ──────
    # We look for columns: trade_date / asset_ticker / transaction_type / units / price / currency
    trade_df = pd.DataFrame()
    for sheet_try in ["Trades", "Trade Log", "Portfolio Trades", "Sheet2"]:
        try:
            _t = pd.read_excel(io.BytesIO(buffer_bytes), sheet_name=sheet_try)
            _t = normalize_cols(_t)
            trade_df = _t
            break
        except Exception:
            pass

    # If no dedicated trades sheet, check Sheet1 itself for trade columns
    if trade_df.empty:
        cols_lower = [c.lower() for c in raw_tx.columns]
        if any("trade" in c or "ticker" in c or "asset" in c for c in cols_lower):
            trade_df = raw_tx.copy()

    required = ["transaction_date","category","subcategory","description","amount","transaction_type"]
    missing = [c for c in required if c not in raw_tx.columns]
    if missing:
        raise KeyError(f"Missing columns: {missing}")

    df = raw_tx.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce", dayfirst=True)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df = df.dropna(subset=["transaction_date"]).copy()
    df["category"]         = df["category"].astype(str).str.strip()
    df["subcategory"]      = df["subcategory"].astype(str).str.strip()
    df["description"]      = df["description"].astype(str).fillna("").str.strip()
    df["transaction_type"] = df["transaction_type"].astype(str).str.strip().str.lower()

    report_as_of = pd.Timestamp(report_as_of_str)
    cutoff = report_as_of.to_period("M").to_timestamp("M")
    df = df[df["transaction_date"] <= cutoff].copy()

    df["month_start"]  = df["transaction_date"].dt.to_period("M").dt.to_timestamp()
    df["month_year"]   = df["transaction_date"].dt.to_period("M").astype(str)
    df["month_label"]  = df["transaction_date"].dt.strftime("%b %Y")
    df["Month_Label"]  = df["month_label"]
    df["quarter"]      = "Q" + df["transaction_date"].dt.quarter.astype(str) + " " + df["transaction_date"].dt.year.astype(str)
    df["year"]         = df["transaction_date"].dt.year
    df["bucket"]       = df["category"].map(classify_bucket)

    transfer_mask = df["transaction_type"].eq("transfer")
    df["transfer_class"] = np.where(
        transfer_mask,
        df.apply(lambda r: classify_transfer_type(r.get("description",""), r.get("subcategory",""), r.get("category","")), axis=1),
        ""
    )
    df["income_amount"]   = np.where(df["transaction_type"].eq("income"),   df["amount"].abs(), 0)
    df["expense_amount"]  = np.where(df["transaction_type"].eq("expense"),  df["amount"].abs(), 0)
    df["transfer_amount"] = np.where(df["transaction_type"].eq("transfer"), df["amount"].abs(), 0)
    df["investment_transfer_amount"] = np.where(df["transfer_class"].eq("Investment Transfer"), df["transfer_amount"], 0)
    df["goal_transfer_amount"]       = np.where(df["transfer_class"].eq("Goal / Planned Drawdown"), df["transfer_amount"], 0)
    df["savings_transfer_amount"]    = np.where(df["transfer_class"].eq("Savings Account Transfer"), df["transfer_amount"], 0)

    monthly = (
        df.groupby(["month_start","month_year"], as_index=False)
          .agg(
              income=("income_amount","sum"),
              expense=("expense_amount","sum"),
              transfer_total=("transfer_amount","sum"),
              investment_transfer=("investment_transfer_amount","sum"),
              goal_transfer=("goal_transfer_amount","sum"),
              savings_transfer=("savings_transfer_amount","sum"),
              rows=("amount","size")
          ).sort_values("month_start").reset_index(drop=True)
    )
    monthly["Month_Label"]    = monthly["month_start"].dt.strftime("%b %Y")
    monthly["savings"]        = monthly["income"] - monthly["expense"]
    monthly["actual_savings"] = monthly["savings"] - monthly["transfer_total"]
    monthly["savings_rate"]   = np.where(monthly["income"]!=0, monthly["savings"]/monthly["income"]*100, np.nan)
    monthly["expense_ratio"]  = np.where(monthly["income"]!=0, monthly["expense"]/monthly["income"]*100, np.nan)
    monthly["income_3m_avg"]  = monthly["income"].rolling(3,min_periods=1).mean()
    monthly["expense_3m_avg"] = monthly["expense"].rolling(3,min_periods=1).mean()
    monthly["savings_3m_avg"] = monthly["savings"].rolling(3,min_periods=1).mean()

    cat_month = (
        df[df["transaction_type"].eq("expense")]
        .groupby(["month_start","month_year","category"], as_index=False)["amount"].sum()
        .sort_values(["month_start","amount"], ascending=[True,False])
    )

    return df, monthly, cat_month, raw_portfolio_sheet, trade_df

_today = pd.Timestamp.today().normalize()
REPORT_AS_OF = (_today - pd.offsets.MonthBegin(1)).normalize() if _today.day < 12 else _today

buffer_bytes = workbook_buffer.read() if hasattr(workbook_buffer, "read") else workbook_buffer

try:
    df, monthly, cat_month, raw_portfolio, trade_df = load_and_process(buffer_bytes, str(REPORT_AS_OF.date()))
except Exception as e:
    st.error(f"❌ Could not process workbook: {e}")
    st.stop()

monthly_12m  = latest_n(monthly, 12)
latest_month = monthly_12m.iloc[-1]
prior_month  = monthly_12m.iloc[-2] if len(monthly_12m) >= 2 else latest_month

st.success(f"✅ {len(df):,} transactions loaded · Reporting through {REPORT_AS_OF.strftime('%B %Y')}")

# ─────────────────────────────────────────────────────────────────────────────
# §1-2  EXECUTIVE DIAGNOSTIC + CASH FLOW ENGINE
# ─────────────────────────────────────────────────────────────────────────────
if show_cashflow:
    section_header("📊","§1-2 · Executive Diagnostic + Cash Flow Engine",
                   "Latest month health check · income, expense, savings rate, transfer intelligence")

    col1,col2,col3,col4 = st.columns(4)
    with col1: st.metric("Income (Latest)", fmt_money(latest_month["income"]),
                         delta=fmt_money(latest_month["income"]-prior_month["income"]))
    with col2: st.metric("Expenses (Latest)", fmt_money(latest_month["expense"]),
                         delta=fmt_money(latest_month["expense"]-prior_month["expense"]), delta_color="inverse")
    with col3: st.metric("Savings Rate", pct(latest_month["savings_rate"]),
                         delta=f"{latest_month['savings_rate']-prior_month['savings_rate']:.1f}pp")
    with col4: st.metric("Surplus (Latest)", fmt_money(latest_month["savings"]),
                         delta=fmt_money(latest_month["savings"]-prior_month["savings"]))

    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly_12m["Month_Label"], y=monthly_12m["income"],
                         name="Income", marker_color=THEME["emerald"], opacity=0.85))
    fig.add_trace(go.Bar(x=monthly_12m["Month_Label"], y=monthly_12m["expense"],
                         name="Expense", marker_color=THEME["red"], opacity=0.85))
    fig.add_trace(go.Scatter(x=monthly_12m["Month_Label"], y=monthly_12m["savings_3m_avg"],
                             name="Savings 3m avg", mode="lines+markers",
                             line=dict(color=THEME["gold"], width=2.5),
                             marker=dict(size=6, color=THEME["gold"])))
    safe_plotly(fig, "Monthly Income vs Expense — 12 Months", 420)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=monthly_12m["Month_Label"], y=monthly_12m["savings_rate"],
        mode="lines+markers", name="Savings Rate %",
        line=dict(color=THEME["teal"], width=3),
        fill="tozeroy", fillcolor=THEME["teal"]+"18",
        marker=dict(size=7, color=THEME["teal"])
    ))
    fig2.add_hline(y=20, line_dash="dash", line_color=THEME["border"], line_width=1.5,
                   annotation_text="20% benchmark", annotation_font_color=THEME["muted"])
    safe_plotly(fig2, "Monthly Savings Rate %", 300)
    fig2.update_yaxes(ticksuffix="%")

    section_header("🔄","§2B · Transfer Intelligence","Where the money beyond expenses actually went")
    transfer_df = df[df["transfer_class"] != ""].groupby("transfer_class")["transfer_amount"].sum().reset_index()
    if not transfer_df.empty:
        fig3 = px.pie(transfer_df, names="transfer_class", values="transfer_amount", hole=0.52,
                      color_discrete_sequence=GOLD_SEQ)
        fig3.update_traces(textfont_color=THEME["text"], textfont_size=13,
                           marker=dict(line=dict(color=THEME["panel"], width=2)))
        safe_plotly(fig3, "Transfer Classification — Full Period", 360)

# ─────────────────────────────────────────────────────────────────────────────
# §3-3D  SPEND ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
if show_spend:
    section_header("🛒","§3 · Spend Benchmarking + §3C-3D Portable Cost Base",
                   "Category breakdown · excl. rent · your true carry-forward costs")

    latest_cat = (
        df[(df["transaction_type"]=="expense") & (df["month_start"]==latest_month["month_start"])]
        .groupby("category")["amount"].sum().reset_index().rename(columns={"amount":"latest"})
    )
    avg_cat = (
        cat_month[cat_month["month_start"] < latest_month["month_start"]]
        .groupby("category")["amount"].mean().reset_index().rename(columns={"amount":"avg_12m"})
    )
    cat_compare = latest_cat.merge(avg_cat, on="category", how="left").sort_values("latest", ascending=False)
    cat_compare["variance_$"] = cat_compare["latest"] - cat_compare["avg_12m"]

    fig = go.Figure()
    fig.add_trace(go.Bar(y=cat_compare["category"], x=cat_compare["avg_12m"],
                         orientation="h", name="12m Avg",
                         marker_color=THEME["slate"]+"aa", opacity=0.8))
    fig.add_trace(go.Bar(y=cat_compare["category"], x=cat_compare["latest"],
                         orientation="h", name="Latest Month",
                         marker_color=THEME["blue"], opacity=0.9))
    safe_plotly(fig, "Category Spend: Latest vs 12m Average", max(360, len(cat_compare)*44))
    fig.update_layout(barmode="overlay")
    fig.update_xaxes(tickprefix="$", tickformat=",")

    section_header("🧮","§3C · Portable Cost Base — Expenses Excl. Rent",
                   "These are the costs that survive the house purchase")

    portable_df = df[(df["transaction_type"]=="expense") & (~df["subcategory"].isin({"Rent/Mortgage"}))].copy()
    portable_monthly = (
        portable_df.groupby(["month_start","Month_Label"], as_index=False)["amount"].sum()
        .rename(columns={"amount":"portable_expenses"}).sort_values("month_start")
    )
    portable_monthly = portable_monthly.merge(monthly[["month_start","income"]], on="month_start", how="left")
    portable_monthly["portable_pct_income"] = np.where(
        portable_monthly["income"]>0, portable_monthly["portable_expenses"]/portable_monthly["income"]*100, np.nan)
    portable_monthly["portable_3m_avg"] = portable_monthly["portable_expenses"].rolling(3,min_periods=1).mean()
    portable_12m = portable_monthly.sort_values("month_start").tail(12)

    col1,col2,col3 = st.columns(3)
    with col1: st.metric("Latest Month (excl. rent)", fmt_money(portable_12m["portable_expenses"].iloc[-1]))
    with col2: st.metric("12-Month Average", fmt_money(portable_12m["portable_expenses"].mean()))
    with col3: st.metric("Avg % of Income", pct(portable_12m["portable_pct_income"].mean()))

    fig_p = go.Figure()
    fig_p.add_trace(go.Bar(x=portable_12m["Month_Label"], y=portable_12m["portable_expenses"],
                           name="Monthly (excl. rent)", marker_color=THEME["blue"], opacity=0.85))
    fig_p.add_trace(go.Scatter(x=portable_12m["Month_Label"], y=portable_12m["portable_3m_avg"],
                               mode="lines+markers", name="3m rolling avg",
                               line=dict(color=THEME["gold"], width=3),
                               marker=dict(size=6, color=THEME["gold"])))
    safe_plotly(fig_p, "Monthly Expenses Excl. Rent & Transfers", 420)
    fig_p.update_yaxes(tickprefix="$", tickformat=",")

    avg_portable = portable_12m["portable_expenses"].mean()
    info_box("Portable Cost Base Verdict",
             f"Your average portable cost base: <b>{fmt_money(avg_portable)}/mo</b>. "
             f"Stacks on your ${MORTGAGE_REPAYMENT:,}/mo mortgage.",
             THEME["teal"])

    section_header("📋","§3D · Monthly Expense Tracker (Excl. Rent)",
                   "Month-by-month category matrix — spot lifestyle creep")
    portable_pivot = (
        portable_df[portable_df["month_start"].isin(portable_12m["month_start"])]
        .assign(amount_abs=lambda x: x["amount"].abs())
        .groupby(["Month_Label","category"], as_index=False)["amount_abs"].sum()
        .pivot_table(index="Month_Label", columns="category", values="amount_abs", aggfunc="sum", fill_value=0)
    )
    if not portable_pivot.empty:
        month_order = [m for m in portable_12m["Month_Label"].tolist() if m in portable_pivot.index]
        portable_pivot = portable_pivot.loc[month_order]
        portable_pivot["TOTAL"] = portable_pivot.sum(axis=1)
        st.dataframe(money_table(portable_pivot), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# §4-7  ANOMALY ENGINE + FORECAST
# ─────────────────────────────────────────────────────────────────────────────
if show_anomaly:
    section_header("⚠️","§4-7 · Anomaly Engine, Concentration & Forecast",
                   "Statistical anomaly detection · concentration · 3-month forward projection")

    cat_total = (
        df[df["transaction_type"]=="expense"]
        .groupby("category", as_index=False)["amount"].sum()
        .sort_values("amount", ascending=False)
    )
    total_exp = cat_total["amount"].sum()
    cat_total["share_pct"] = cat_total["amount"] / total_exp * 100

    fig = px.bar(cat_total.head(10), x="category", y="share_pct",
                 color="share_pct",
                 color_continuous_scale=[[0, THEME["card"]], [0.5, THEME["gold3"]], [1, THEME["gold2"]]],
                 text=cat_total.head(10)["share_pct"].apply(lambda x: f"{x:.1f}%"))
    fig.update_traces(textfont_color=THEME["text"], textposition="outside")
    safe_plotly(fig, "Expense Concentration — Full Period (Top 10 Categories)", 380)
    fig.update_yaxes(title="Share %", ticksuffix="%")

    anom_results = []
    for cat, grp in cat_month.groupby("category"):
        amounts = grp["amount"].values
        if len(amounts) < 3: continue
        med = np.median(amounts)
        mad = median_abs_deviation(amounts)
        latest_amt = grp.sort_values("month_start").iloc[-1]["amount"]
        z = (latest_amt - med) / (mad * 1.4826 + 1e-9)
        anom_results.append({"Category":cat,"Latest":latest_amt,"Median":med,"MAD-Z":z})

    anom_df = pd.DataFrame(anom_results).sort_values("MAD-Z", ascending=False)
    flagged  = anom_df[anom_df["MAD-Z"] > 2].head(5)
    if not flagged.empty:
        info_box("🚨 Anomaly Flags",
                 "Categories running >2 MAD above their own median this month: " +
                 ", ".join(f"<b>{r['Category']}</b> ({fmt_money(r['Latest'])})" for _,r in flagged.iterrows()),
                 THEME["red"])
    else:
        info_box("✅ No Anomalies","All categories within normal statistical ranges this month.", THEME["emerald"])

    section_header("🔮","§7 · 3-Month Forward Forecast","Run-rate projection based on trailing 3m average")
    run_rate_income  = monthly_12m["income"].tail(3).mean()
    run_rate_expense = monthly_12m["expense"].tail(3).mean()
    run_rate_surplus = run_rate_income - run_rate_expense

    col1,col2,col3 = st.columns(3)
    with col1: st.metric("Projected Monthly Income",  fmt_money(run_rate_income))
    with col2: st.metric("Projected Monthly Expense", fmt_money(run_rate_expense))
    with col3: st.metric("Projected Monthly Surplus", fmt_money(run_rate_surplus),
                         delta="✅ Above $1k floor" if run_rate_surplus > 1000 else "⚠️ Below $1k floor")

# ─────────────────────────────────────────────────────────────────────────────
# §8-9  PORTFOLIO + TECHNICAL INTELLIGENCE
# Reads directly from the transactions data (BUY trades only — no hardcoding)
# ─────────────────────────────────────────────────────────────────────────────
if show_portfolio:
    section_header("📈","§8-9 · Portfolio Performance + Technical Intelligence",
                   "Derived from your transaction data · BUY positions only · live prices via yfinance")

    # ── Step 1: Build holdings from trade data ────────────────────────────────
    # Look for trade columns: trade_date / asset_ticker / transaction_type / units / price / currency / application
    holdings_df = pd.DataFrame()
    data_source_used = ""

    # Try trade_df first (dedicated trades sheet or Sheet1 with trade columns)
    for tdf_candidate in [trade_df, df]:
        cols = set(tdf_candidate.columns.tolist())
        has_ticker = any(c in cols for c in ["asset_ticker","ticker","symbol"])
        has_units  = any(c in cols for c in ["units","qty","quantity","shares"])
        has_price  = any(c in cols for c in ["price","avg_cost","avg_cost_aud","cost"])
        if has_ticker and has_units:
            _t = tdf_candidate.copy()
            # Rename to standard names
            for src, dst in [("asset_ticker","ticker"),("symbol","ticker"),
                              ("qty","units"),("quantity","units"),("shares","units"),
                              ("avg_cost","price"),("avg_cost_aud","price"),("cost","price")]:
                if src in _t.columns and dst not in _t.columns:
                    _t = _t.rename(columns={src: dst})
            # Detect transaction_type column (may be named differently)
            tt_col = None
            for c in ["transaction_type","type","trade_type","action"]:
                if c in _t.columns:
                    tt_col = c; break
            if tt_col:
                _t[tt_col] = _t[tt_col].astype(str).str.strip().str.lower()
                buys = _t[_t[tt_col].str.contains("buy", na=False)].copy()
                sells = _t[_t[tt_col].str.contains("sell", na=False)].copy()
            else:
                buys = _t.copy(); sells = pd.DataFrame()

            buys["units"]  = pd.to_numeric(buys.get("units",  0), errors="coerce").fillna(0)
            buys["price"]  = pd.to_numeric(buys.get("price",  0), errors="coerce").fillna(0)
            buys["ticker"] = buys["ticker"].astype(str).str.strip().str.upper()

            if not sells.empty:
                sells["units"]  = pd.to_numeric(sells.get("units",  0), errors="coerce").fillna(0)
                sells["ticker"] = sells["ticker"].astype(str).str.strip().str.upper()

            if buys.empty or "ticker" not in buys.columns:
                continue

            # Aggregate net units (buys minus sells)
            buy_agg = buys.groupby("ticker").agg(
                buy_units=("units","sum"),
                total_cost=("price", lambda x: (x * buys.loc[x.index,"units"]).sum())
            ).reset_index()

            if not sells.empty and "ticker" in sells.columns:
                sell_agg = sells.groupby("ticker")["units"].sum().reset_index().rename(columns={"units":"sell_units"})
                buy_agg  = buy_agg.merge(sell_agg, on="ticker", how="left")
                buy_agg["sell_units"] = buy_agg["sell_units"].fillna(0)
                buy_agg["net_units"]  = buy_agg["buy_units"] - buy_agg["sell_units"]
            else:
                buy_agg["net_units"] = buy_agg["buy_units"]

            buy_agg = buy_agg[buy_agg["net_units"] > 0].copy()
            buy_agg["avg_cost"] = np.where(buy_agg["buy_units"]>0,
                                           buy_agg["total_cost"]/buy_agg["buy_units"], 0)

            # Try to get currency per ticker
            if "currency" in buys.columns:
                ccy = buys.groupby("ticker")["currency"].last().reset_index()
                buy_agg = buy_agg.merge(ccy, on="ticker", how="left")
                buy_agg["currency"] = buy_agg["currency"].fillna("AUD").str.upper()
            else:
                buy_agg["currency"] = "AUD"

            holdings_df = buy_agg
            data_source_used = "transactions"
            break

    # Fallback: dedicated Portfolio sheet
    if holdings_df.empty and not raw_portfolio.empty:
        pf = raw_portfolio.copy()
        col_map = {}
        for col in pf.columns:
            cl = col.lower()
            if "ticker" in cl or "symbol" in cl: col_map[col] = "ticker"
            elif "unit" in cl or "qty" in cl or "shares" in cl: col_map[col] = "net_units"
            elif "cost" in cl or "avg" in cl or "price" in cl: col_map[col] = "avg_cost"
            elif "curr" in cl: col_map[col] = "currency"
        pf = pf.rename(columns=col_map)
        if "ticker" in pf.columns and "net_units" in pf.columns:
            pf["ticker"]   = pf["ticker"].astype(str).str.strip().str.upper()
            pf["net_units"]= pd.to_numeric(pf.get("net_units",0), errors="coerce").fillna(0)
            pf["avg_cost"] = pd.to_numeric(pf.get("avg_cost",0),  errors="coerce").fillna(0)
            pf["currency"] = pf.get("currency","AUD").fillna("AUD").str.upper()
            holdings_df = pf[pf["net_units"]>0].copy()
            data_source_used = "Portfolio sheet"

    if holdings_df.empty:
        info_box("Portfolio Data Unavailable",
                 "No trade data found. Add a sheet named 'Trades' with columns: "
                 "trade_date, asset_ticker, transaction_type, units, price, currency. "
                 "Or add a 'Portfolio' sheet with: ticker, units, avg_cost, currency.",
                 THEME["slate"])
    else:
        st.caption(f"📂 Portfolio derived from: **{data_source_used}** · {len(holdings_df)} positions (BUY only)")

        try:
            import yfinance as yf

            # FX
            try:
                from forex_python.converter import CurrencyRates
                audusd = CurrencyRates().get_rate("AUD","USD")
            except Exception:
                try:
                    _fx = yf.Ticker("AUDUSD=X").fast_info
                    audusd = float(_fx.last_price)
                except Exception:
                    audusd = 0.645

            rows = []
            for _, row in holdings_df.iterrows():
                ticker  = str(row["ticker"]).strip().upper()
                units   = float(row["net_units"])
                avg_cst = float(row.get("avg_cost", 0))
                curr    = str(row.get("currency","AUD")).upper()
                lookup  = ticker + ".AX" if curr=="AUD" and not ticker.endswith(".AX") else ticker
                try:
                    td   = yf.Ticker(lookup)
                    live = td.info.get("regularMarketPrice") or td.fast_info.last_price
                    price_aud = live / audusd if curr=="USD" else float(live)
                except Exception:
                    price_aud = avg_cst
                cost_aud   = units * avg_cst
                market_v   = units * price_aud
                rows.append({
                    "Ticker": ticker, "Units": units,
                    "Avg Cost": avg_cst, "Live Price": price_aud,
                    "Cost (AUD)": cost_aud, "Value (AUD)": market_v,
                    "Gain (AUD)": market_v - cost_aud,
                    "Gain %": (market_v-cost_aud)/cost_aud*100 if cost_aud else 0,
                    "Currency": curr,
                })

            hdf = pd.DataFrame(rows)
            total_mv   = hdf["Value (AUD)"].sum()
            total_cost = hdf["Cost (AUD)"].sum()
            total_gain = total_mv - total_cost
            roi_pct    = total_gain / total_cost * 100 if total_cost else 0
            hdf["Weight %"] = hdf["Value (AUD)"] / total_mv * 100

            # KPI metrics
            col1,col2,col3,col4 = st.columns(4)
            with col1: st.metric("Portfolio Value", fmt_money(total_mv), delta=f"vs cost {fmt_money(total_cost)}")
            with col2: st.metric("Total Gain / Loss", fmt_money(total_gain))
            with col3: st.metric("ROI", f"{roi_pct:.1f}%")
            with col4: st.metric("Positions", f"{len(hdf)}")

            # ── Allocation donut + Gain/loss bar ─────────────────────────────
            c1, c2 = st.columns([1,1])
            with c1:
                fig_pie = px.pie(hdf, names="Ticker", values="Value (AUD)", hole=0.54,
                                 color_discrete_sequence=GOLD_SEQ)
                fig_pie.update_traces(
                    textfont_color=THEME["text"], textfont_size=13,
                    marker=dict(line=dict(color=THEME["panel"], width=3))
                )
                safe_plotly(fig_pie, "Portfolio Allocation by Value", 380)

            with c2:
                bar_colors = [THEME["emerald"] if g >= 0 else THEME["red"] for g in hdf.sort_values("Gain %")["Gain %"]]
                fig_gain = go.Figure(go.Bar(
                    x=hdf.sort_values("Gain %")["Ticker"],
                    y=hdf.sort_values("Gain %")["Gain %"],
                    marker_color=bar_colors,
                    text=hdf.sort_values("Gain %")["Gain %"].apply(lambda x: f"{x:+.1f}%"),
                    textposition="outside",
                    textfont=dict(color=THEME["text"], size=11)
                ))
                fig_gain.add_hline(y=0, line_color=THEME["text"], line_width=1.5)
                safe_plotly(fig_gain, "Gain / Loss % by Ticker", 380)
                fig_gain.update_yaxes(ticksuffix="%")

            # ── Holdings table ────────────────────────────────────────────────
            st.markdown(f"<div style='margin:12px 0 6px;font-size:13px;font-weight:700;color:{THEME['muted']};'>Holdings Summary</div>", unsafe_allow_html=True)
            display_cols = ["Ticker","Units","Avg Cost","Live Price","Cost (AUD)","Value (AUD)","Gain (AUD)","Gain %","Weight %"]
            disp_df = hdf[display_cols].set_index("Ticker")
            st.dataframe(
                disp_df.style.format({
                    "Units": "{:,.0f}", "Avg Cost": "${:,.3f}", "Live Price": "${:,.3f}",
                    "Cost (AUD)": "${:,.0f}", "Value (AUD)": "${:,.0f}",
                    "Gain (AUD)": "${:+,.0f}", "Gain %": "{:+.1f}%", "Weight %": "{:.1f}%"
                }).background_gradient(subset=["Gain %"], cmap="RdYlGn", vmin=-20, vmax=20),
                use_container_width=True
            )

            # ── §9 Technical Intelligence ─────────────────────────────────────
            section_header("🔍","§9 · Technical Intelligence","200-DMA value gap · RSI(14) momentum signal")

            tech_results = []
            for _, row in hdf.iterrows():
                ticker = row["Ticker"]
                curr   = row["Currency"]
                lookup = ticker + ".AX" if curr=="AUD" and "." not in ticker else ticker
                try:
                    hist = yf.download(lookup, period="18mo", interval="1d", progress=False, auto_adjust=True)
                    if hist.empty or len(hist) < 14: continue
                    if isinstance(hist.columns, pd.MultiIndex):
                        hist.columns = hist.columns.get_level_values(0)
                    close = hist["Close"].squeeze().dropna()
                    price = float(close.iloc[-1])
                    if len(close) >= 200:
                        sma = float(close.rolling(200).mean().iloc[-1]); sma_label = "200-DMA"
                    elif len(close) >= 50:
                        sma = float(close.rolling(50).mean().iloc[-1]); sma_label = "50-DMA*"
                    else:
                        sma = float(close.mean()); sma_label = "Mean*"
                    gap = (price - sma) / sma * 100
                    delta_ = close.diff()
                    gain_  = delta_.clip(lower=0).rolling(14).mean()
                    loss_  = (-delta_.clip(upper=0)).rolling(14).mean()
                    lg, ll = float(gain_.iloc[-1]), float(loss_.iloc[-1])
                    rsi = 100.0 if ll==0 and lg>0 else (50.0 if ll==0 else float(100-(100/(1+lg/ll))))
                    rsi_sig = "Overbought" if rsi>=70 else "Oversold" if rsi<=30 else "Neutral"
                    tech_results.append({"Ticker":ticker,"Price":price,"MA":sma,
                                         "MA Label":sma_label,"Value Gap %":gap,
                                         "RSI(14)":rsi,"Signal":rsi_sig})
                except Exception:
                    continue

            if tech_results:
                tech_df = pd.DataFrame(tech_results).sort_values("Value Gap %")

                c1, c2 = st.columns(2)
                with c1:
                    gap_colors = [THEME["emerald"] if x<0 else THEME["blue"] for x in tech_df["Value Gap %"]]
                    fig_vg = go.Figure(go.Bar(
                        x=tech_df["Ticker"], y=tech_df["Value Gap %"],
                        marker_color=gap_colors,
                        text=tech_df["Value Gap %"].apply(lambda x: f"{x:+.1f}%"),
                        textposition="outside",
                        textfont=dict(color=THEME["text"], size=11)
                    ))
                    fig_vg.add_hline(y=0, line_color=THEME["text"], line_width=1.5)
                    fig_vg.add_hrect(y0=-25, y1=0, fillcolor=THEME["emerald"], opacity=0.06,
                                     annotation_text="BUY ZONE", annotation_font_color=THEME["emerald"])
                    safe_plotly(fig_vg, "Value Gap from Moving Average", 380)
                    fig_vg.update_yaxes(ticksuffix="%")

                with c2:
                    rsi_colors = [THEME["red"] if r>=70 else THEME["emerald"] if r<=30 else THEME["blue"]
                                  for r in tech_df["RSI(14)"]]
                    fig_rsi = go.Figure(go.Bar(
                        x=tech_df["Ticker"], y=tech_df["RSI(14)"],
                        marker_color=rsi_colors,
                        text=tech_df["RSI(14)"].apply(lambda x: f"{x:.0f}"),
                        textposition="outside",
                        textfont=dict(color=THEME["text"], size=11)
                    ))
                    fig_rsi.add_hline(y=70, line_dash="dash", line_color=THEME["red"],
                                      annotation_text="Overbought (70)", annotation_font_color=THEME["red"])
                    fig_rsi.add_hline(y=30, line_dash="dash", line_color=THEME["emerald"],
                                      annotation_text="Oversold (30)", annotation_font_color=THEME["emerald"])
                    safe_plotly(fig_rsi, "RSI(14) Momentum Signal", 380)
                    fig_rsi.update_yaxes(range=[0,105])

                # ── Summary table ──────────────────────────────────────────────
                tech_display = tech_df[["Ticker","Price","MA","MA Label","Value Gap %","RSI(14)","Signal"]].set_index("Ticker")
                st.dataframe(
                    tech_display.style.format({
                        "Price":"${:,.3f}","MA":"${:,.3f}",
                        "Value Gap %":"{:+.1f}%","RSI(14)":"{:.0f}"
                    }).applymap(lambda v: f"color:{THEME['emerald']}" if isinstance(v,str) and v=="Oversold"
                                else (f"color:{THEME['red']}" if isinstance(v,str) and v=="Overbought"
                                      else f"color:{THEME['text']}"), subset=["Signal"]),
                    use_container_width=True
                )

                # Golden Override
                deepest = tech_df.iloc[0]
                if deepest["Value Gap %"] < -5:
                    info_box("🔔 Golden Override Candidate",
                             f"<b>{deepest['Ticker']}</b> is {deepest['Value Gap %']:+.1f}% below its {deepest['MA Label']}. "
                             f"RSI: {deepest['RSI(14)']:.0f} ({deepest['Signal']}). "
                             f"Watch for a 3%+ intraday S&P drop as the trigger. Max 1 purchase/month.",
                             THEME["purple"])

        except ImportError:
            info_box("yfinance not available", "Add `yfinance` to requirements.txt", THEME["orange"])
        except Exception as e:
            info_box("Portfolio Error", str(e), THEME["red"])

# ─────────────────────────────────────────────────────────────────────────────
# §10  ACTION BOARD
# ─────────────────────────────────────────────────────────────────────────────
if show_action:
    section_header("✅","§10 · Strategic Action Board","Turn the analysis into concrete priorities")

    actions = []
    avg_sr = monthly_12m["savings_rate"].mean()
    if latest_month["savings_rate"] < avg_sr:
        actions.append(("📉 Lift Monthly Surplus",
                        f"Latest savings rate {pct(latest_month['savings_rate'])} below 12m avg {pct(avg_sr)}"))
    portable_latest = df[
        (df["transaction_type"]=="expense") & (~df["subcategory"].isin({"Rent/Mortgage"})) &
        (df["month_start"]==latest_month["month_start"])]["amount"].sum()
    if portable_latest > 5000:
        actions.append(("🛒 Review Portable Spend",
                        f"Lifestyle spend (excl. rent) hit {fmt_money(portable_latest)} this month"))
    run_surplus = SALARY_NET_MONTHLY - portable_latest - MORTGAGE_REPAYMENT - DCA_ACTIVE
    if run_surplus < 1000:
        actions.append(("⚠️ Surplus Below $1,000 Floor",
                        f"Post-mortgage surplus is {fmt_money(run_surplus)} — dial down DCA first"))
    if not actions:
        actions.append(("✅ Maintain Course","All metrics within target ranges. Focus on DCA consistency."))

    for priority, why in actions:
        st.markdown(f"""
        <div style="margin:8px 0; padding:14px 18px;
                    background:linear-gradient(135deg,{THEME['panel']} 0%,{THEME['card']} 100%);
                    border-left:4px solid {THEME['blue']}; border-radius:10px;
                    box-shadow:0 2px 12px rgba(0,0,0,0.2);">
          <div style="font-weight:700; color:{THEME['text']}; font-size:15px;">{priority}</div>
          <div style="color:{THEME['muted']}; font-size:13px; margin-top:5px; line-height:1.5;">{why}</div>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# §11  MORTGAGE REALITY
# ─────────────────────────────────────────────────────────────────────────────
if show_mortgage:
    section_header("🏠","§11 · Mortgage Reality & Surplus Stress Test",
                   "Calculated against last 3 completed months of actual spending")

    RATES_AND_INSURANCE = 400
    MAINTENANCE_BUFFER  = 400
    WA_STAMP_DUTY       = 27855

    completed_months = monthly[monthly["month_start"] < pd.Timestamp.today().to_period("M").to_timestamp()]
    last_3 = completed_months.tail(3)
    verified_income = last_3["income"].iloc[-1] if len(last_3) else SALARY_NET_MONTHLY

    non_housing_exp = df[
        (df["transaction_type"]=="expense") &
        (df["subcategory"] != "Rent/Mortgage") &
        (df["month_start"] < pd.Timestamp.today().to_period("M").to_timestamp())
    ]
    avg_lifestyle = non_housing_exp.groupby("month_start")["amount"].sum().tail(3).mean()

    total_housing_outflow = MORTGAGE_REPAYMENT + RATES_AND_INSURANCE + MAINTENANCE_BUFFER
    surplus_pre_stocks    = verified_income - avg_lifestyle - total_housing_outflow
    final_net_surplus     = surplus_pre_stocks - DCA_ACTIVE

    col1,col2,col3 = st.columns(3)
    with col1: st.metric("Verified Income (Last Full Month)", fmt_money(verified_income))
    with col2: st.metric("Avg Lifestyle Spend (3m)", fmt_money(avg_lifestyle))
    with col3: st.metric("Net Monthly Surplus", fmt_money(final_net_surplus),
                         delta="✅ Above $1k floor" if final_net_surplus > 1000 else "⚠️ Below floor")

    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=final_net_surplus,
        title={"text":"Post-Mortgage Surplus ($/mo)", "font":{"size":15,"color":THEME["text"]}},
        number={"prefix":"$", "font":{"color":THEME["gold2"],"size":36,"family":"DM Mono"}},
        gauge={
            "axis":  {"range":[-500,3000],"tickwidth":1,"tickcolor":THEME["muted"],"tickfont":{"color":THEME["muted"]}},
            "bar":   {"color":THEME["blue"],"thickness":0.3},
            "bgcolor": THEME["panel"],
            "borderwidth": 0,
            "steps":[
                {"range":[-500,0],    "color":THEME["red"]+"33"},
                {"range":[0,1000],    "color":THEME["orange"]+"33"},
                {"range":[1000,3000], "color":THEME["emerald"]+"22"}
            ],
            "threshold":{"line":{"color":THEME["gold"],"width":3},"thickness":0.8,"value":1000}
        }
    ))
    apply_layout(fig, "", 320)
    fig.update_layout(paper_bgcolor=THEME["panel"])
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    info_box("Fortress Rule Check",
             f"Fortress v7.0 requires <b>&gt;$1,000/mo</b> unallocated surplus post-mortgage. "
             f"Projection: <b>{fmt_money(final_net_surplus)}</b>. "
             f"DCA (currently <b>${DCA_ACTIVE}/mo</b>) is the first lever.",
             THEME["purple"])

# ─────────────────────────────────────────────────────────────────────────────
# §12  POST-HOUSE WATERFALL
# ─────────────────────────────────────────────────────────────────────────────
if show_waterfall:
    section_header("🏡","§12 · Future State: Post-House Monthly Waterfall",
                   "Income → mortgage → expenses → stocks → surplus · 3 scenarios")

    RATES_AND_INSURANCE = 400; MAINTENANCE_BUFFER = 400
    DCA_PHASE_2 = 450; DCA_PHASE_3 = 1000

    non_housing_exp = df[
        (df["transaction_type"]=="expense") & (~df["subcategory"].isin({"Rent/Mortgage"})) &
        (df["month_start"] < pd.Timestamp.today().to_period("M").to_timestamp())
    ]
    avg_lifestyle_actual = round(non_housing_exp.groupby("month_start")["amount"].sum().tail(3).mean(), 0)

    scenarios = {
        "Conservative (avg spend)": avg_lifestyle_actual,
        "Optimistic (−10%)":        round(avg_lifestyle_actual * 0.90, 0),
        "Stress (+15%)":            round(avg_lifestyle_actual * 1.15, 0),
    }

    cols = st.columns(len(scenarios))
    for i, (label, lifestyle) in enumerate(scenarios.items()):
        surplus_p2 = SALARY_NET_MONTHLY - MORTGAGE_REPAYMENT - RATES_AND_INSURANCE - MAINTENANCE_BUFFER - lifestyle - DCA_PHASE_2
        surplus_p3 = SALARY_NET_MONTHLY - MORTGAGE_REPAYMENT - RATES_AND_INSURANCE - MAINTENANCE_BUFFER - lifestyle - DCA_PHASE_3
        color = THEME["emerald"] if surplus_p2 > 1000 else THEME["orange"] if surplus_p2 > 0 else THEME["red"]
        with cols[i]:
            st.markdown(f"""
            <div style="background:linear-gradient(145deg,{THEME['card']} 0%,{THEME['panel2']} 100%);
                        border:1px solid {THEME['border']}; border-top:2px solid {color}; border-radius:14px;
                        padding:18px; box-shadow:0 4px 20px rgba(0,0,0,0.3);">
              <div style="font-size:12px; font-weight:700; color:{THEME['muted']};
                          text-transform:uppercase; letter-spacing:0.05em; margin-bottom:12px;">{label}</div>
              <div style="font-size:13px; color:{THEME['muted']}; line-height:2.2;">
                <div>Income: <b style="color:{THEME['text']};">{fmt_money(SALARY_NET_MONTHLY)}</b></div>
                <div>Mortgage: <b style="color:{THEME['text']};"> −{fmt_money(MORTGAGE_REPAYMENT+RATES_AND_INSURANCE+MAINTENANCE_BUFFER)}</b></div>
                <div>Lifestyle: <b style="color:{THEME['text']};"> −{fmt_money(lifestyle)}</b></div>
                <div>DCA Ph2: <b style="color:{THEME['text']};"> −{fmt_money(DCA_PHASE_2)}</b></div>
                <div style="border-top:1px solid {THEME['border']}; margin-top:8px; padding-top:8px;">
                  Surplus: <b style="color:{color}; font-size:16px; font-family:DM Mono,monospace;">{fmt_money(surplus_p2)}</b>
                </div>
                <div>DCA Ph3: <b style="color:{THEME['text']};"> −{fmt_money(DCA_PHASE_3)}</b></div>
                <div>Ph3 Surplus: <b style="color:{THEME['emerald'] if surplus_p3>1000 else THEME['orange']};">{fmt_money(surplus_p3)}</b></div>
              </div>
            </div>""", unsafe_allow_html=True)

    info_box("Waterfall Interpretation",
             f"Using your actual 3m avg lifestyle spend of <b>{fmt_money(avg_lifestyle_actual)}/mo</b>. "
             f"Phase 2 DCA ($450/mo) is the transition gear — Phase 3 ($1,000/mo) is the wealth-building engine. "
             f"Never go below $1,000/mo unallocated.",
             THEME["gold"])

# ─────────────────────────────────────────────────────────────────────────────
# §13  LVR SENSITIVITY
# ─────────────────────────────────────────────────────────────────────────────
if show_lvr:
    section_header("📐","§13 · LVR Sensitivity & Stamp Duty Analysis","Perth WA · Hejaz Ijarah structure")

    WA_STAMP_DUTY = 27855
    prices = [650000, 680000, 700000, 720000, 730000, 750000, 780000, 800000]
    deposit_pool = TOTAL_LIQUID_CASH * 0.55
    lvr_rows = []
    for p in prices:
        net_dep = deposit_pool - WA_STAMP_DUTY
        lvr = (p - net_dep) / p * 100
        lvr_rows.append({"Purchase Price": p, "Net Deposit": net_dep, "LVR %": lvr,
                          "LMI Risk": "⚠️ LMI" if lvr > 90 else ("🔍 Watch" if lvr > 80 else "✅ Safe")})
    lvr_df = pd.DataFrame(lvr_rows)

    fig = go.Figure()
    colors = [THEME["red"] if r>90 else THEME["orange"] if r>80 else THEME["emerald"] for r in lvr_df["LVR %"]]
    fig.add_trace(go.Bar(
        x=lvr_df["Purchase Price"].apply(lambda x: f"${x/1000:.0f}k"),
        y=lvr_df["LVR %"], marker_color=colors,
        text=lvr_df["LVR %"].apply(lambda x: f"{x:.1f}%"),
        textposition="outside", textfont=dict(color=THEME["text"])
    ))
    fig.add_hline(y=90, line_dash="dash", line_color=THEME["red"], annotation_text="LMI Threshold (90%)")
    fig.add_hline(y=80, line_dash="dash", line_color=THEME["orange"], annotation_text="80% Ideal")
    safe_plotly(fig, "LVR by Purchase Price (WA Stamp Duty Applied)", 380)
    fig.update_yaxes(ticksuffix="%", range=[0, 110])
    st.dataframe(lvr_df.style.format({"Purchase Price":"${:,.0f}","Net Deposit":"${:,.0f}","LVR %":"{:.1f}%"}),
                 use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# §14  PURCHASE READINESS
# ─────────────────────────────────────────────────────────────────────────────
if show_readiness:
    section_header("🎯","§14 · Purchase Readiness Dashboard","Fortress capital stack · Hejaz Ijarah")

    PURCHASE_PRICE_14 = PURCHASE_PRICE
    WA_STAMP_DUTY = 27855
    DEPOSIT_TARGET     = 130000
    EMERGENCY_FUND_TARGET = 30000
    BUFFER_TARGET      = 15000
    total_target       = DEPOSIT_TARGET + EMERGENCY_FUND_TARGET + BUFFER_TARGET

    DEPOSIT_CURRENT   = TOTAL_LIQUID_CASH * 0.55
    EMERGENCY_CURRENT = TOTAL_LIQUID_CASH * 0.18
    BUFFER_CURRENT    = TOTAL_LIQUID_CASH * 0.09
    UNALLOCATED       = TOTAL_LIQUID_CASH - DEPOSIT_CURRENT - EMERGENCY_CURRENT - BUFFER_CURRENT
    MORTGAGE_14       = MORTGAGE_REPAYMENT
    total_gap         = max(0, total_target - TOTAL_LIQUID_CASH)

    col1,col2,col3 = st.columns(3)
    with col1: st.metric("Total Capital Pool",  fmt_money(TOTAL_LIQUID_CASH),
                         delta=f"Target {fmt_money(total_target)}")
    with col2: st.metric("Capital Gap",  fmt_money(total_gap),
                         delta="✅ Ready" if total_gap==0 else f"${total_gap:,.0f} to go")
    with col3:
        cov_months = EMERGENCY_CURRENT / MORTGAGE_14
        st.metric("Emergency Cover", f"{cov_months:.1f} months",
                  delta="✅ 7m+ fortress" if cov_months>=7 else "⚠️ Below fortress floor")

    col1, col2 = st.columns(2)
    with col1:
        for label, current, target, color in [
            ("Deposit + Stamp Duty",  DEPOSIT_CURRENT,   DEPOSIT_TARGET,        THEME["blue"]),
            ("Emergency Fund",        EMERGENCY_CURRENT, EMERGENCY_FUND_TARGET, THEME["emerald"]),
            ("Moving/Baby/Buffer",    BUFFER_CURRENT,    BUFFER_TARGET,         THEME["orange"]),
        ]:
            pct_fill = min(100, current / target * 100)
            st.markdown(f"""
            <div style="margin:10px 0;">
              <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:6px;">
                <span style="color:{THEME['text']}; font-weight:600;">{label}</span>
                <span style="color:{THEME['muted']};">${current:,.0f} / ${target:,.0f} ({pct_fill:.0f}%)</span>
              </div>
              <div style="background:{THEME['card2']}; border-radius:8px; height:12px; overflow:hidden;
                          border:1px solid {THEME['border']};">
                <div style="width:{pct_fill}%; background:linear-gradient(90deg,{color}cc,{color});
                             height:100%; border-radius:8px; transition:width 0.5s;"></div>
              </div>
            </div>""", unsafe_allow_html=True)

    with col2:
        pie_data = pd.DataFrame({
            "Bucket": ["Deposit Pool","Emergency Fund","Buffer","Unallocated"],
            "Amount": [DEPOSIT_CURRENT, EMERGENCY_CURRENT, BUFFER_CURRENT, max(UNALLOCATED,0)]
        }).query("Amount > 0")
        fig_d = px.pie(pie_data, names="Bucket", values="Amount", hole=0.55,
                       color_discrete_sequence=GOLD_SEQ)
        fig_d.update_traces(marker=dict(line=dict(color=THEME["panel"], width=2)))
        safe_plotly(fig_d, f"Capital Allocation — {fmt_money(TOTAL_LIQUID_CASH)}", 340)

    net_dep = DEPOSIT_CURRENT - WA_STAMP_DUTY
    lvr     = (PURCHASE_PRICE_14 - net_dep) / PURCHASE_PRICE_14 * 100
    info_box("LVR Check",
             f"Deposit pool <b>{fmt_money(DEPOSIT_CURRENT)}</b> minus stamp duty <b>${WA_STAMP_DUTY:,}</b> = "
             f"net deposit <b>{fmt_money(net_dep)}</b>. On {fmt_money(PURCHASE_PRICE_14)}: "
             f"LVR = <b>{lvr:.1f}%</b>. "
             f"{'✅ Below 90% — no LMI under Hejaz Ijarah.' if lvr<90 else '⚠️ Above 90% — check LMI.'}",
             THEME["emerald"] if lvr < 90 else THEME["red"])

# ─────────────────────────────────────────────────────────────────────────────
# §15  DCA ENGINE & $1.7M PROJECTION
# ─────────────────────────────────────────────────────────────────────────────
if show_dca:
    section_header("📈","§15 · DCA Engine: Cycle Tracker & $1.7M Portfolio Projection",
                   "Phase-aware DCA schedule · 8% CAGR model · milestone tracker")

    today = pd.Timestamp.today()
    phases = [
        ("Phase 1 — Pre-house DCA",    pd.Timestamp("2026-02-01"), pd.Timestamp("2026-06-30"),  950),
        ("Phase 2 — House transition", pd.Timestamp("2026-07-01"), pd.Timestamp("2027-07-31"),  450),
        ("Phase 3 — Growth mode",      pd.Timestamp("2027-08-01"), pd.Timestamp("2056-12-31"), 1000),
    ]
    schedule = []
    for phase_name, start, end, amount in phases:
        months = pd.date_range(start=start, end=min(end, pd.Timestamp("2056-12-01")), freq="MS")
        for m in months:
            schedule.append({"month":m,"phase":phase_name,"dca_amount":amount})
    sched_df = pd.DataFrame(schedule)

    next_24 = sched_df[sched_df["month"] >= today].head(24).copy()
    next_24["Month_Label"] = next_24["month"].dt.strftime("%b %Y")
    phase_colors = {
        "Phase 1 — Pre-house DCA": THEME["emerald"],
        "Phase 2 — House transition": THEME["orange"],
        "Phase 3 — Growth mode": THEME["blue"],
    }
    fig_dca = go.Figure(go.Bar(
        x=next_24["Month_Label"], y=next_24["dca_amount"],
        marker_color=[phase_colors.get(p, THEME["blue"]) for p in next_24["phase"]],
        text=[fmt_money(v) for v in next_24["dca_amount"]],
        textposition="outside", textfont=dict(color=THEME["text"], size=10)
    ))
    safe_plotly(fig_dca, "Monthly DCA Contributions — Next 24 Months", 400)
    fig_dca.update_yaxes(tickprefix="$", tickformat=",")
    fig_dca.update_xaxes(tickangle=-45)

    CAGR = 0.08
    portfolio_value = START_PORTFOLIO_VALUE
    projection = []
    for _, row in sched_df.iterrows():
        monthly_return = (1 + CAGR) ** (1/12) - 1
        portfolio_value = portfolio_value * (1 + monthly_return) + row["dca_amount"]
        projection.append({"month":row["month"],"phase":row["phase"],"portfolio_value":portfolio_value})

    proj_df    = pd.DataFrame(projection)
    annual_proj = proj_df[proj_df["month"].dt.month == 12].copy()
    annual_proj["Year"] = annual_proj["month"].dt.year

    fig_proj = go.Figure()
    fig_proj.add_trace(go.Scatter(
        x=annual_proj["Year"], y=annual_proj["portfolio_value"],
        mode="lines+markers", name="Portfolio Value (8% CAGR)",
        line=dict(color=THEME["emerald"], width=3),
        fill="tozeroy", fillcolor=THEME["emerald"]+"18",
        marker=dict(size=6, color=THEME["emerald"])
    ))
    fig_proj.add_hline(y=1700000, line_dash="dash", line_color=THEME["gold"],
                       annotation_text="$1.7M Target", annotation_font_color=THEME["gold"])
    fig_proj.add_vrect(x0=2026, x1=2027.5, fillcolor=THEME["orange"], opacity=0.05,
                       annotation_text="Ph2", annotation_font_color=THEME["orange"])
    fig_proj.add_vrect(x0=2027.5, x1=2057, fillcolor=THEME["blue"], opacity=0.03,
                       annotation_text="Ph3", annotation_font_color=THEME["blue"])
    safe_plotly(fig_proj, "Portfolio Growth Projection to 2056 — 8% CAGR", 500)
    fig_proj.update_yaxes(tickprefix="$", tickformat=",")

    milestone_years = [2030, 2035, 2040, 2045, 2050, 2056]
    milestones = annual_proj[annual_proj["Year"].isin(milestone_years)][["Year","portfolio_value"]].copy()
    milestones.columns = ["Year","Projected Value"]
    milestones["vs $1.7M Target"] = milestones["Projected Value"] - 1700000
    st.dataframe(milestones.style.format({
        "Projected Value": "${:,.0f}", "vs $1.7M Target": "${:+,.0f}"
    }), use_container_width=True)

    hit_row = proj_df[proj_df["portfolio_value"] >= 1700000]
    if not hit_row.empty:
        hit_date = hit_row.iloc[0]["month"]
        info_box("🎯 $1.7M Target Milestone",
                 f"At 8% CAGR starting from <b>{fmt_money(START_PORTFOLIO_VALUE)}</b>, "
                 f"$1.7M is reached around <b>{hit_date.strftime('%B %Y')}</b> — "
                 f"<b>{hit_date.year - today.year} years</b> from today. "
                 f"Phase 3 ramp-up ($1,000/mo from Aug 2027) is the critical driver.",
                 THEME["emerald"])
    else:
        info_box("Projection Note",
                 "Increase DCA Phase 3 or starting portfolio to reach $1.7M within the model window.",
                 THEME["orange"])

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin:48px 0 0; padding:24px 28px;
            background:linear-gradient(135deg,{THEME['panel']} 0%,{THEME['card']} 100%);
            border:1px solid {THEME['border']}; border-radius:16px;
            text-align:center; font-family:'DM Sans',sans-serif;
            box-shadow:0 4px 24px rgba(0,0,0,0.4);">
  <div style="font-size:22px; margin-bottom:8px;">🏰</div>
  <div style="font-size:16px; font-weight:800; color:{THEME['text']}; letter-spacing:-0.02em;">
    Personal Financial Intelligence — v8.0
  </div>
  <div style="font-size:12px; color:{THEME['muted']}; margin-top:6px; line-height:1.6;">
    Fortress Strategy v7.0 · Perth, WA · Sections §1–§15 active
    <br>Source: Google Drive workbook · Auto-refresh: 5 min · {datetime.now().strftime('%d %b %Y %H:%M')}
  </div>
</div>
""", unsafe_allow_html=True)
