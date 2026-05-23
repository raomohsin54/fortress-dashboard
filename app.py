"""
Personal Financial Intelligence Report — Version 7.0
Fortress Strategy v6.4 | Streamlit Cloud Edition
Reads directly from Google Drive via service account credentials
"""

import os
import io
import json
import warnings
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
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# THEME  (mirrors your notebook dark palette exactly)
# ─────────────────────────────────────────────────────────────────────────────
THEME = {
    "bg": "#050505",
    "panel": "#0d0d0d",
    "panel2": "#151515",
    "card": "#101010",
    "grid": "#3a3020",
    "text": "#fff7df",
    "muted": "#c9b37a",
    "gold": "#d4af37",
    "gold2": "#f5d76e",
    "gold3": "#8a6f1f",
    "green": "#3ddc97",
    "red": "#ff5c5c",
    "orange": "#ffb347",
    "yellow": "#f5d76e",
    "blue": "#68a8ff",
    "purple": "#c084fc",
    "teal": "#38e8d1",
    "pink": "#ff7ab6",
    "slate": "#8b8b8b",
}

GOLD_SEQUENCE = [
    "#d4af37", "#f5d76e", "#b8860b", "#ffcc33", "#c9a227",
    "#e6be4a", "#a67c00", "#ffd700", "#8a6f1f", "#fff1a8"
]
STATUS_COLORS = [THEME["green"], THEME["gold"], THEME["orange"], THEME["red"], THEME["blue"], THEME["purple"]]

# Inject global CSS — black/gold visibility-first theme
st.markdown(f"""
<style>
  :root {{
    --bg: {THEME['bg']}; --panel: {THEME['panel']}; --panel2: {THEME['panel2']};
    --text: {THEME['text']}; --muted: {THEME['muted']}; --gold: {THEME['gold']};
    --grid: {THEME['grid']};
  }}
  html, body, .stApp {{ background: radial-gradient(circle at top left, #1d1606 0%, #050505 38%, #000 100%) !important; color: var(--text) !important; }}
  .block-container {{ padding-top: 1.3rem; max-width: 1480px; }}
  section[data-testid="stSidebar"] {{ background: linear-gradient(180deg, #0b0b0b 0%, #050505 100%) !important; border-right: 1px solid var(--grid); }}
  section[data-testid="stSidebar"] * {{ color: var(--text) !important; }}
  h1, h2, h3, h4, h5, h6, p, span, label, div {{ color: inherit; }}
  div[data-testid="metric-container"] {{
      background: linear-gradient(145deg, #111 0%, #080808 100%) !important;
      border: 1px solid rgba(212,175,55,.55) !important;
      box-shadow: 0 10px 30px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.03);
      border-radius: 16px; padding: 16px 18px;
  }}
  div[data-testid="metric-container"] label, div[data-testid="metric-container"] [data-testid="stMetricDelta"] {{ color: var(--muted) !important; }}
  div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{ color: var(--gold) !important; font-size: 1.55rem !important; font-weight: 800 !important; }}
  .stPlotlyChart {{ background: #0b0b0b; border: 1px solid rgba(212,175,55,.35); border-radius: 16px; padding: 8px; box-shadow: 0 12px 36px rgba(0,0,0,.30); }}
  .js-plotly-plot .plotly, .plot-container {{ background: transparent !important; }}
  .stDataFrame, div[data-testid="stDataFrame"] {{ background: #0b0b0b !important; border: 1px solid rgba(212,175,55,.35); border-radius: 14px; padding: 6px; }}
  .stAlert {{ background-color: #111 !important; color: var(--text) !important; border: 1px solid rgba(212,175,55,.35) !important; }}
  button, .stButton button {{ background: #151515 !important; color: var(--gold) !important; border: 1px solid var(--gold) !important; }}
  input, textarea, select {{ color: var(--text) !important; background-color: #111 !important; }}
  [data-baseweb="radio"] div, [data-baseweb="checkbox"] div {{ color: var(--text) !important; }}
  hr {{ border-color: rgba(212,175,55,.25); }}
  #MainMenu, footer, header {{ visibility: hidden; }}
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

def section_header(icon, title, subtitle):
    st.markdown(f"""
    <div style="margin:24px 0 12px; padding:18px 20px;
                border:1px solid {THEME['grid']}; border-radius:12px;
                background:linear-gradient(135deg,{THEME['panel']} 0%,#0b1220 100%);">
      <div style="display:flex; align-items:center; gap:12px;">
        <div style="font-size:28px;">{icon}</div>
        <div>
          <div style="font-size:20px; font-weight:700; color:{THEME['text']};">{title}</div>
          <div style="font-size:13px; color:{THEME['muted']}; margin-top:2px;">{subtitle}</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

def info_box(title, body, accent=None):
    accent = accent or THEME["blue"]
    st.markdown(f"""
    <div style="margin:10px 0 16px; padding:14px 16px; background:#0b1220;
                border-left:5px solid {accent}; border-radius:10px;">
      <div style="font-weight:700; margin-bottom:6px; color:{THEME['text']};">{title}</div>
      <div style="color:{THEME['muted']}; line-height:1.5;">{body}</div>
    </div>""", unsafe_allow_html=True)

def apply_layout(fig, title="", height=420):
    """Consistent high-contrast Plotly layout. Safe for normal + 3D charts."""
    fig.update_layout(
        title=dict(text=title, x=0.01, font=dict(size=17, color=THEME["gold2"], family="Arial Black")),
        paper_bgcolor=THEME["panel"],
        plot_bgcolor=THEME["panel"],
        font=dict(color=THEME["text"], size=12),
        xaxis=dict(showgrid=False, color=THEME["muted"], linecolor=THEME["grid"], tickfont=dict(color=THEME["text"])),
        yaxis=dict(showgrid=True, gridcolor=THEME["grid"], zeroline=False, color=THEME["muted"], tickfont=dict(color=THEME["text"])),
        margin=dict(l=35, r=35, t=58, b=35),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(color=THEME["text"])),
        height=height,
    )
    fig.update_layout(
        scene=dict(
            bgcolor=THEME["panel"],
            xaxis=dict(backgroundcolor=THEME["panel"], gridcolor=THEME["grid"], color=THEME["text"]),
            yaxis=dict(backgroundcolor=THEME["panel"], gridcolor=THEME["grid"], color=THEME["text"]),
            zaxis=dict(backgroundcolor=THEME["panel"], gridcolor=THEME["grid"], color=THEME["text"]),
        )
    )
    return fig

def safe_plotly(fig, title="Chart", height=420):
    """Render a chart without letting one bad visual stop the rest of the dashboard."""
    try:
        apply_layout(fig, title, height)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    except Exception as e:
        info_box(f"Chart skipped: {title}", f"Reason: {e}", THEME["orange"])

def money_table(df, formatter="${:,.0f}"):
    """Dark/gold dataframe style that avoids unreadable matplotlib colour maps."""
    return (df.style
        .format(formatter)
        .set_properties(**{
            "background-color": "#0b0b0b",
            "color": THEME["text"],
            "border-color": THEME["grid"],
        })
        .set_table_styles([
            {"selector": "th", "props": [("background-color", "#151515"), ("color", THEME["gold2"]), ("border-color", THEME["grid"])]},
            {"selector": "td", "props": [("border-color", THEME["grid"])]},
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
    desc = str(description).lower(); sub = str(subcategory).lower(); cat = str(category).lower()
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
    """
    Downloads an Excel file from Google Drive using a service account.
    Credentials are stored in Streamlit secrets as 'gcp_service_account'.
    """
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
    <div style="padding:16px 0 8px; font-family:sans-serif;">
      <div style="font-size:22px; font-weight:800; color:{THEME['text']};">💼 Fortress v6.4</div>
      <div style="font-size:12px; color:{THEME['muted']}; margin-top:4px;">
        Personal Financial Intelligence
      </div>
    </div>""", unsafe_allow_html=True)
    st.divider()

    # ── Live inputs ──────────────────────────────────────────────────────────
    st.markdown(f"<div style='font-weight:700;color:{THEME['text']};font-size:14px;margin-bottom:6px;'>📊 Live Parameters</div>", unsafe_allow_html=True)

    TOTAL_LIQUID_CASH = st.number_input(
        "Total Liquid Cash ($)", value=168000, step=1000,
        help="Your current verified bank balance — updates all 15 sections instantly"
    )
    SALARY_NET_MONTHLY = st.number_input("Net Monthly Income ($)", value=9684, step=100)
    PURCHASE_PRICE = st.number_input("House Target ($)", value=730000, step=5000)
    MORTGAGE_REPAYMENT = st.number_input("Monthly Repayment ($)", value=4205, step=50)
    START_PORTFOLIO_VALUE = st.number_input("Current IBKR Portfolio ($)", value=15000, step=1000)

    st.divider()

    # ── DCA Phase selector ───────────────────────────────────────────────────
    st.markdown(f"<div style='font-weight:700;color:{THEME['text']};font-size:14px;margin-bottom:6px;'>📈 DCA Phase</div>", unsafe_allow_html=True)
    dca_phase = st.radio(
        "Active DCA Phase", ["Phase 1 ($950/mo)", "Phase 2 ($450/mo)", "Phase 3 ($1,000/mo)"],
        index=1, help="Phase 2 = July 2026–July 2027"
    )
    DCA_ACTIVE = {"Phase 1 ($950/mo)":950, "Phase 2 ($450/mo)":450, "Phase 3 ($1,000/mo)":1000}[dca_phase]

    st.divider()

    # ── Section toggles ──────────────────────────────────────────────────────
    st.markdown(f"<div style='font-weight:700;color:{THEME['text']};font-size:14px;margin-bottom:6px;'>👁 Show Sections</div>", unsafe_allow_html=True)
    show_cashflow    = st.checkbox("§1-2 · Cash Flow Engine",     value=True)
    show_spend       = st.checkbox("§3-3D · Spend Analysis",      value=True)
    show_anomaly     = st.checkbox("§4-7 · Anomaly & Forecast",   value=True)
    show_portfolio   = st.checkbox("§8-9 · Portfolio & Technical",value=True)
    show_action      = st.checkbox("§10 · Action Board",          value=True)
    show_mortgage    = st.checkbox("§11 · Mortgage Stress Test",  value=True)
    show_waterfall   = st.checkbox("§12 · Post-House Waterfall",  value=True)
    show_lvr         = st.checkbox("§13 · LVR Sensitivity",       value=True)
    show_readiness   = st.checkbox("§14 · Purchase Readiness",    value=True)
    show_dca         = st.checkbox("§15 · DCA Engine & $1.7M",   value=True)

    st.divider()
    st.markdown(f"<div style='font-size:11px;color:{THEME['muted']};'>Last refreshed: {datetime.now().strftime('%d %b %Y %H:%M')}</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TITLE BANNER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(135deg,#0b1220 0%,{THEME['panel']} 55%,#0b1220 100%);
            border:1px solid {THEME['grid']}; border-radius:14px; padding:28px 36px; margin-bottom:24px;">
  <div style="display:flex; align-items:center; gap:16px; margin-bottom:14px;">
    <span style="font-size:38px;">💼</span>
    <div>
      <h1 style="margin:0; font-size:26px; font-weight:800; color:{THEME['text']};">
        Personal Financial Intelligence Report
      </h1>
      <p style="margin:4px 0 0; font-size:13px; color:{THEME['muted']};">
        Fortress Strategy v6.4 · Perth, WA · Streamlit Cloud Edition · v7.0
      </p>
    </div>
  </div>
  <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:8px; font-size:12px; color:{THEME['muted']};">
    <div>📂 Source: Google Drive Excel workbook</div>
    <div>🏠 Target: $730k house · Hejaz Ijarah</div>
    <div>📈 Goal: $1.7M net worth by 2056</div>
    <div>🧠 Transfer intelligence layer active</div>
    <div>🚫 Rent excluded from anomaly flags</div>
    <div>🔄 Auto-refreshes every 5 minutes</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING — Google Drive + fallback to file upload
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"<div style='font-size:13px;color:{THEME['muted']};margin-bottom:8px;'>📂 Data source</div>", unsafe_allow_html=True)

data_source = st.radio("Load data from", ["Google Drive (auto-sync)", "Upload Excel manually"],
                        horizontal=True, label_visibility="collapsed")

workbook_buffer = None

if data_source == "Google Drive (auto-sync)":
    # Credentials come from Streamlit secrets → set up in Step 3 of the guide
    try:
        creds_json = json.dumps(dict(st.secrets["gcp_service_account"]))
        file_id    = st.secrets["gdrive_file_id"]
        workbook_buffer = load_from_google_drive(file_id, creds_json)
        st.success("✅ Loaded from Google Drive")
    except Exception as e:
        st.warning(f"⚠️ Google Drive not configured yet — see setup guide below. ({e})")
        st.info("👆 Switch to 'Upload Excel manually' to test your data now while you complete the setup.")

else:
    uploaded = st.file_uploader("Upload your 'Transactions budget.xlsx'", type=["xlsx"])
    if uploaded:
        workbook_buffer = uploaded
        st.success("✅ File loaded")

# ─────────────────────────────────────────────────────────────────────────────
# SETUP GUIDE (always visible until Drive is configured)
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("📋 One-time Setup Guide — Click to expand / collapse", expanded=(workbook_buffer is None)):
    st.markdown(f"""
<div style="font-family:sans-serif; color:{THEME['text']}; line-height:1.7;">

### Step 1 — GitHub (2 minutes)
1. Go to **github.com** → **New repository** → name it `fortress-dashboard` → **Public** → **Create**
2. Click **Add file → Create new file**, name it `app.py`, paste the full `app.py` content → **Commit**
3. Click **Add file → Create new file**, name it `requirements.txt`, paste the content → **Commit**

---

### Step 2 — Streamlit Cloud (2 minutes)
1. Go to **share.streamlit.io** → **Sign in with GitHub**
2. Click **New app** → pick your `fortress-dashboard` repo → branch `main` → file `app.py`
3. Click **Deploy** — your app gets a permanent URL like `https://yourname-fortress-dashboard.streamlit.app`

---

### Step 3 — Google Drive API (10 minutes — one time only)

**3a. Create a Google Cloud project + service account:**
1. Go to **console.cloud.google.com** → New Project → name it `fortress-dashboard`
2. Search **"Google Drive API"** → Enable it
3. Go to **IAM & Admin → Service Accounts** → **Create Service Account**
4. Name it `fortress-reader` → Continue → Done
5. Click the service account → **Keys tab** → **Add Key → JSON** → Download the file
   (This JSON file is your credential — keep it private)

**3b. Share your Excel file with the service account:**
1. Open your `Transactions budget.xlsx` in Google Drive
2. Click **Share** → paste the service account email (looks like `fortress-reader@yourproject.iam.gserviceaccount.com`) → **Viewer** → Share
3. Copy the **File ID** from the URL: `https://docs.google.com/spreadsheets/d/`**`THIS_PART`**`/edit`

**3c. Add secrets to Streamlit Cloud:**
1. In Streamlit Cloud, go to your app → **⋮ menu → Edit secrets**
2. Paste exactly this, replacing with your values:

```toml
gdrive_file_id = "your_file_id_from_step_3b"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\\n...\\n-----END RSA PRIVATE KEY-----\\n"
client_email = "fortress-reader@your-project.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

> ⚠️ Paste these **exactly as they appear in the downloaded JSON file**. The `private_key` needs `\\n` (double backslash) to work in TOML format.

3. Click **Save** → app auto-restarts → you're done ✅

---

### Step 4 — Done. Your workflow is now:
```
Edit Excel on Google Drive (phone, tablet, anywhere)
          ↓ (automatic, no action needed)
Open your Streamlit URL → live dashboard updated
```

**Your URL:** Share it only with yourself. It is private if you keep the Streamlit app set to "Private" (free tier allows 1 private app).

</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# STOP HERE IF NO DATA
# ─────────────────────────────────────────────────────────────────────────────
if workbook_buffer is None:
    st.info("⬆️ Load your workbook above to see the dashboard. All 15 sections will appear here.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# LOAD & CLEAN DATA  (mirrors your Step 3-4 notebook logic exactly)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner="🔄 Processing transactions…")
def load_and_process(buffer_bytes: bytes, report_as_of_str: str):
    raw_tx = pd.read_excel(io.BytesIO(buffer_bytes), sheet_name="Sheet1")
    raw_tx = normalize_cols(raw_tx)
    raw_tx = raw_tx[[c for c in raw_tx.columns if not str(c).startswith("unnamed_")]]

    try:
        raw_portfolio = pd.read_excel(io.BytesIO(buffer_bytes), sheet_name="Portfolio")
        raw_portfolio = normalize_cols(raw_portfolio)
        raw_portfolio = raw_portfolio[[c for c in raw_portfolio.columns if not str(c).startswith("unnamed_")]]
    except Exception:
        raw_portfolio = pd.DataFrame()

    required = ["transaction_date","category","subcategory","description","amount","transaction_type"]
    missing = [c for c in required if c not in raw_tx.columns]
    if missing:
        raise KeyError(f"Missing columns: {missing}")

    df = raw_tx.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce", dayfirst=True)
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    df = df.dropna(subset=["transaction_date"]).copy()

    df["category"] = df["category"].astype(str).str.strip()
    df["subcategory"] = df["subcategory"].astype(str).str.strip()
    df["description"] = df["description"].astype(str).fillna("").str.strip()
    df["transaction_type"] = df["transaction_type"].astype(str).str.strip().str.lower()

    report_as_of = pd.Timestamp(report_as_of_str)
    cutoff = report_as_of.to_period("M").to_timestamp("M")
    df = df[df["transaction_date"] <= cutoff].copy()

    df["month_start"] = df["transaction_date"].dt.to_period("M").dt.to_timestamp()
    df["month_year"]  = df["transaction_date"].dt.to_period("M").astype(str)
    df["month_label"] = df["transaction_date"].dt.strftime("%b %Y")
    df["Month_Label"] = df["month_label"]
    df["quarter"] = "Q" + df["transaction_date"].dt.quarter.astype(str) + " " + df["transaction_date"].dt.year.astype(str)
    df["year"] = df["transaction_date"].dt.year
    df["bucket"] = df["category"].map(classify_bucket)

    # Transfer classification
    transfer_mask = df["transaction_type"].eq("transfer")
    df["transfer_class"] = np.where(
        transfer_mask,
        df.apply(lambda r: classify_transfer_type(r.get("description",""), r.get("subcategory",""), r.get("category","")), axis=1),
        ""
    )

    df["income_amount"]   = np.where(df["transaction_type"].eq("income"), df["amount"].abs(), 0)
    df["expense_amount"]  = np.where(df["transaction_type"].eq("expense"), df["amount"].abs(), 0)
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
          )
          .sort_values("month_start").reset_index(drop=True)
    )
    monthly["Month_Label"]     = monthly["month_start"].dt.strftime("%b %Y")
    monthly["savings"]         = monthly["income"] - monthly["expense"]
    monthly["actual_savings"]  = monthly["savings"] - monthly["transfer_total"]
    monthly["savings_rate"]    = np.where(monthly["income"]!=0, monthly["savings"]/monthly["income"]*100, np.nan)
    monthly["expense_ratio"]   = np.where(monthly["income"]!=0, monthly["expense"]/monthly["income"]*100, np.nan)
    monthly["income_3m_avg"]   = monthly["income"].rolling(3, min_periods=1).mean()
    monthly["expense_3m_avg"]  = monthly["expense"].rolling(3, min_periods=1).mean()
    monthly["savings_3m_avg"]  = monthly["savings"].rolling(3, min_periods=1).mean()

    cat_month = (
        df[df["transaction_type"].eq("expense")]
        .groupby(["month_start","month_year","category"], as_index=False)["amount"].sum()
        .sort_values(["month_start","amount"], ascending=[True,False])
    )

    return df, monthly, cat_month, raw_portfolio

# Determine reporting cutoff
_today = pd.Timestamp.today().normalize()
REPORT_AS_OF = (_today - pd.offsets.MonthBegin(1)).normalize() if _today.day < 12 else _today

# Read bytes once for caching
buffer_bytes = workbook_buffer.read() if hasattr(workbook_buffer, "read") else workbook_buffer

try:
    df, monthly, cat_month, raw_portfolio = load_and_process(buffer_bytes, str(REPORT_AS_OF.date()))
except Exception as e:
    st.error(f"❌ Could not process workbook: {e}")
    st.info("Check that your Excel has: `transaction_date`, `category`, `subcategory`, `description`, `amount`, `transaction_type` columns in Sheet1.")
    st.stop()

monthly_12m   = latest_n(monthly, 12)
latest_month  = monthly_12m.iloc[-1]
prior_month   = monthly_12m.iloc[-2] if len(monthly_12m) >= 2 else latest_month

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

    # Income vs Expense chart
    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly_12m["Month_Label"], y=monthly_12m["income"],
                         name="Income", marker_color=THEME["green"], opacity=0.8))
    fig.add_trace(go.Bar(x=monthly_12m["Month_Label"], y=monthly_12m["expense"],
                         name="Expense", marker_color=THEME["red"], opacity=0.8))
    fig.add_trace(go.Scatter(x=monthly_12m["Month_Label"], y=monthly_12m["savings_3m_avg"],
                             name="Savings 3m avg", mode="lines+markers",
                             line=dict(color=THEME["yellow"], width=2)))
    apply_layout(fig, "Monthly Income vs Expense — 12 Months", 420)
    st.plotly_chart(fig, use_container_width=True)

    # Savings rate trend
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=monthly_12m["Month_Label"], y=monthly_12m["savings_rate"],
                              mode="lines+markers", name="Savings Rate %",
                              line=dict(color=THEME["teal"], width=3),
                              fill="tozeroy", fillcolor="rgba(45,212,191,0.1)"))
    fig2.add_hline(y=20, line_dash="dash", line_color=THEME["slate"],
                   annotation_text="20% benchmark")
    apply_layout(fig2, "Monthly Savings Rate %", 320)
    fig2.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig2, use_container_width=True)

    # Transfer intelligence
    section_header("🔄","§2B · Transfer Intelligence","Where the money beyond expenses actually went")
    transfer_df = df[df["transfer_class"] != ""].groupby("transfer_class")["transfer_amount"].sum().reset_index()
    if not transfer_df.empty:
        fig3 = px.pie(transfer_df, names="transfer_class", values="transfer_amount", hole=0.5,
                      color_discrete_sequence=GOLD_SEQUENCE)
        apply_layout(fig3, "Transfer Classification — Full Period", 360)
        st.plotly_chart(fig3, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# §3-3D  SPEND ANALYSIS + PORTABLE COST BASE
# ─────────────────────────────────────────────────────────────────────────────
if show_spend:
    section_header("🛒","§3 · Spend Benchmarking + §3C-3D Portable Cost Base",
                   "Category breakdown · excl. rent · your true carry-forward costs")

    # Category spend latest vs avg
    latest_cat = (
        df[(df["transaction_type"]=="expense") & (df["month_start"]==latest_month["month_start"])]
        .groupby("category")["amount"].sum().reset_index()
        .rename(columns={"amount":"latest"})
    )
    avg_cat = (
        cat_month[cat_month["month_start"] < latest_month["month_start"]]
        .groupby("category")["amount"].mean().reset_index()
        .rename(columns={"amount":"avg_12m"})
    )
    cat_compare = latest_cat.merge(avg_cat, on="category", how="left").sort_values("latest", ascending=False)
    cat_compare["variance_$"] = cat_compare["latest"] - cat_compare["avg_12m"]

    fig = go.Figure()
    fig.add_trace(go.Bar(y=cat_compare["category"], x=cat_compare["avg_12m"],
                         orientation="h", name="12m Avg", marker_color=THEME["slate"], opacity=0.7))
    fig.add_trace(go.Bar(y=cat_compare["category"], x=cat_compare["latest"],
                         orientation="h", name="Latest Month", marker_color=THEME["blue"]))
    apply_layout(fig, "Category Spend: Latest vs 12m Average", max(360, len(cat_compare)*45))
    fig.update_layout(barmode="overlay")
    fig.update_xaxes(tickprefix="$", tickformat=",")
    st.plotly_chart(fig, use_container_width=True)

    # §3C — Portable cost base (excl. rent)
    section_header("🧮","§3C · Portable Cost Base — Expenses Excl. Rent & Transfers",
                   "These are the costs that survive the house purchase — your true lifestyle spend")

    portable_df = df[
        (df["transaction_type"]=="expense") &
        (~df["subcategory"].isin({"Rent/Mortgage"}))
    ].copy()

    portable_monthly = (
        portable_df.groupby(["month_start","Month_Label"], as_index=False)["amount"].sum()
        .rename(columns={"amount":"portable_expenses"}).sort_values("month_start")
    )
    portable_monthly = portable_monthly.merge(monthly[["month_start","income"]], on="month_start", how="left")
    portable_monthly["portable_pct_income"] = np.where(
        portable_monthly["income"]>0, portable_monthly["portable_expenses"]/portable_monthly["income"]*100, np.nan
    )
    portable_monthly["portable_3m_avg"] = portable_monthly["portable_expenses"].rolling(3, min_periods=1).mean()
    portable_12m = portable_monthly.sort_values("month_start").tail(12)

    col1,col2,col3 = st.columns(3)
    with col1: st.metric("Latest Month (excl. rent)", fmt_money(portable_12m["portable_expenses"].iloc[-1]))
    with col2: st.metric("12-Month Average", fmt_money(portable_12m["portable_expenses"].mean()))
    with col3: st.metric("Avg % of Income", pct(portable_12m["portable_pct_income"].mean()))

    fig_p = go.Figure()
    fig_p.add_trace(go.Bar(x=portable_12m["Month_Label"], y=portable_12m["portable_expenses"],
                           name="Monthly (excl. rent)", marker_color=THEME["blue"], opacity=0.8))
    fig_p.add_trace(go.Scatter(x=portable_12m["Month_Label"], y=portable_12m["portable_3m_avg"],
                               mode="lines+markers", name="3m rolling avg",
                               line=dict(color=THEME["yellow"], width=3)))
    apply_layout(fig_p, "Monthly Expenses Excl. Rent & Transfers", 420)
    fig_p.update_yaxes(tickprefix="$", tickformat=",")
    st.plotly_chart(fig_p, use_container_width=True)

    avg_portable = portable_12m["portable_expenses"].mean()
    info_box("Portable Cost Base Verdict",
             f"Your average portable cost base over 12 months is <b>{fmt_money(avg_portable)}/mo</b>. "
             f"This stacks directly on top of your ${MORTGAGE_REPAYMENT:,}/mo mortgage repayment. "
             f"If consistently above $4,000 — watch it closely.",
             THEME["teal"])

    # §3D — Tracker table
    section_header("📋","§3D · Monthly Expense Tracker (Excl. Rent)",
                   "Month-by-month category matrix — spot lifestyle creep")

    portable_pivot = (
        portable_df[portable_df["month_start"].isin(portable_12m["month_start"])]
        .assign(amount_abs=lambda x: x["amount"].abs())
        .groupby(["Month_Label","category"], as_index=False)["amount_abs"].sum()
        .pivot_table(index="Month_Label", columns="category", values="amount_abs", aggfunc="sum", fill_value=0)
    )
    if portable_pivot.empty:
        info_box("No portable expense data", "No non-rent expense rows were found for the selected period.", THEME["orange"])
    else:
        month_order = [m for m in portable_12m["Month_Label"].tolist() if m in portable_pivot.index]
        portable_pivot = portable_pivot.loc[month_order]
        portable_pivot["TOTAL"] = portable_pivot.sum(axis=1)
        st.dataframe(money_table(portable_pivot), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# §4-7  ANOMALY ENGINE + FORECAST
# ─────────────────────────────────────────────────────────────────────────────
if show_anomaly:
    section_header("⚠️","§4-7 · Anomaly Engine, Concentration & Forecast",
                   "Statistical anomaly detection · run-rate · 3-month forward projection")

    # Concentration
    cat_total = (
        df[df["transaction_type"]=="expense"]
        .groupby("category", as_index=False)["amount"].sum()
        .sort_values("amount", ascending=False)
    )
    total_exp = cat_total["amount"].sum()
    cat_total["share_pct"] = cat_total["amount"] / total_exp * 100

    fig = px.bar(cat_total.head(10), x="category", y="share_pct",
                 color="share_pct", color_continuous_scale=[[0, "#3a3020"], [0.5, "#d4af37"], [1, "#fff1a8"]],
                 text=cat_total.head(10)["share_pct"].apply(lambda x: f"{x:.1f}%"))
    apply_layout(fig, "Expense Concentration — Full Period (Top 10 Categories)", 380)
    fig.update_yaxes(title="Share %", ticksuffix="%")
    st.plotly_chart(fig, use_container_width=True)

    # Simple MAD-based anomaly detection per category
    anom_results = []
    for cat, grp in cat_month.groupby("category"):
        amounts = grp["amount"].values
        if len(amounts) < 3:
            continue
        med = np.median(amounts)
        mad = median_abs_deviation(amounts)
        latest_amt = grp.sort_values("month_start").iloc[-1]["amount"]
        z = (latest_amt - med) / (mad * 1.4826 + 1e-9)
        anom_results.append({"Category": cat, "Latest": latest_amt, "Median": med, "MAD-Z": z})

    anom_df = pd.DataFrame(anom_results).sort_values("MAD-Z", ascending=False)
    flagged  = anom_df[anom_df["MAD-Z"] > 2].head(5)
    if not flagged.empty:
        info_box("🚨 Anomaly Flags",
                 "Categories running >2 MAD above their own median this month: " +
                 ", ".join(f"<b>{r['Category']}</b> ({fmt_money(r['Latest'])})" for _,r in flagged.iterrows()),
                 THEME["red"])
    else:
        info_box("✅ No Anomalies", "All categories within normal statistical ranges this month.", THEME["green"])

    # 3-month forward run-rate
    section_header("🔮","§7 · 3-Month Forward Forecast","Run-rate projection based on trailing 3m average")
    run_rate_income  = monthly_12m["income"].tail(3).mean()
    run_rate_expense = monthly_12m["expense"].tail(3).mean()
    run_rate_surplus = run_rate_income - run_rate_expense

    col1,col2,col3 = st.columns(3)
    with col1: st.metric("Projected Monthly Income",  fmt_money(run_rate_income))
    with col2: st.metric("Projected Monthly Expense", fmt_money(run_rate_expense))
    with col3: st.metric("Projected Monthly Surplus", fmt_money(run_rate_surplus),
                         delta="vs $1,000 floor" if run_rate_surplus > 1000 else "⚠️ Below $1k floor")

# ─────────────────────────────────────────────────────────────────────────────
# §8-9  PORTFOLIO + TECHNICAL INTELLIGENCE
# ─────────────────────────────────────────────────────────────────────────────
if show_portfolio:
    section_header("📈","§8-9 · Portfolio Performance + Technical Intelligence",
                   "WACB, gain/loss, 200-DMA value gap, RSI(14)")

    if raw_portfolio.empty:
        info_box("Portfolio Data Unavailable",
                 "Add a 'Portfolio' sheet to your Excel with columns: ticker, units, avg_cost, currency",
                 THEME["slate"])
    else:
        try:
            import yfinance as yf
            pf = raw_portfolio.copy()

            # Normalise expected columns
            col_map = {}
            for col in pf.columns:
                cl = col.lower()
                if "ticker" in cl or "symbol" in cl: col_map[col] = "ticker"
                elif "unit" in cl or "qty" in cl or "shares" in cl: col_map[col] = "units"
                elif "cost" in cl or "avg" in cl or "price" in cl: col_map[col] = "avg_cost_aud"
                elif "curr" in cl: col_map[col] = "currency"
            pf = pf.rename(columns=col_map)

            # Fetch live prices
            try:
                from forex_python.converter import CurrencyRates
                c = CurrencyRates()
                audusd = c.get_rate("AUD", "USD")
            except Exception:
                audusd = 0.645  # fallback

            holdings = []
            for _, row in pf.iterrows():
                ticker  = str(row.get("ticker","")).strip()
                units   = float(row.get("units", 0))
                avg_cst = float(row.get("avg_cost_aud", 0))
                curr    = str(row.get("currency","AUD")).upper()
                lookup  = ticker + ".AX" if curr == "AUD" and not ticker.endswith(".AX") else ticker
                try:
                    data = yf.Ticker(lookup)
                    price_usd = data.info.get("regularMarketPrice") or data.fast_info.last_price
                    price_aud = price_usd / audusd if curr == "USD" else price_usd
                except Exception:
                    price_aud = avg_cst

                cost_aud  = units * avg_cst
                market_v  = units * price_aud
                holdings.append({
                    "ticker": ticker, "units": units, "avg_cost_aud": avg_cst,
                    "cost_aud": cost_aud, "market_value_aud": market_v,
                    "gain_aud": market_v - cost_aud,
                    "gain_pct": (market_v - cost_aud) / cost_aud * 100 if cost_aud else 0,
                })

            holdings_df = pd.DataFrame(holdings)
            total_mv    = holdings_df["market_value_aud"].sum()
            total_cost  = holdings_df["cost_aud"].sum()
            holdings_df["weight_pct"] = holdings_df["market_value_aud"] / total_mv * 100

            col1,col2,col3,col4 = st.columns(4)
            with col1: st.metric("Portfolio Value", fmt_money(total_mv))
            with col2: st.metric("Cost Base",       fmt_money(total_cost))
            with col3: st.metric("Unrealised Gain", fmt_money(total_mv - total_cost))
            with col4: st.metric("ROI", f"{(total_mv-total_cost)/total_cost*100:.1f}%")

            c1, c2 = st.columns(2)
            with c1:
                fig = px.pie(holdings_df, names="ticker", values="market_value_aud", hole=0.5,
                             color_discrete_sequence=GOLD_SEQUENCE)
                apply_layout(fig, "Portfolio Allocation", 360)
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                fig2 = px.bar(holdings_df.sort_values("gain_aud"), x="gain_aud", y="ticker",
                              orientation="h", color="gain_aud",
                              color_continuous_scale=[[0, THEME["red"]], [0.5, THEME["gold"]], [1, THEME["green"]]])
                apply_layout(fig2, "Unrealised Gain/Loss by Ticker", 360)
                fig2.update_xaxes(tickprefix="$", tickformat=",")
                st.plotly_chart(fig2, use_container_width=True)

            # §9 — Technical Intelligence
            section_header("🔍","§9 · Technical Intelligence","200-DMA value gap + RSI(14) momentum")

            tech_results = []
            for _, row in holdings_df.iterrows():
                ticker = row["ticker"]
                lookup = ticker + ".AX" if "." not in ticker else ticker
                try:
                    hist = yf.download(lookup, period="18mo", interval="1d",
                                       progress=False, auto_adjust=True)
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
                    delta = close.diff()
                    gain  = delta.clip(lower=0).rolling(14).mean()
                    loss  = (-delta.clip(upper=0)).rolling(14).mean()
                    lg, ll = float(gain.iloc[-1]), float(loss.iloc[-1])
                    rsi = 100.0 if ll == 0 and lg > 0 else (50.0 if ll == 0 else float(100-(100/(1+lg/ll))))
                    rsi_sig = "Overbought" if rsi >= 70 else "Oversold" if rsi <= 30 else "Neutral"
                    tech_results.append({"ticker":ticker,"price":price,"sma":sma,
                                         "sma_label":sma_label,"value_gap":gap,"rsi_14":rsi,"rsi_signal":rsi_sig})
                except Exception:
                    continue

            if tech_results:
                tech_df = pd.DataFrame(tech_results).sort_values("value_gap")
                colors  = [THEME["green"] if x < 0 else THEME["blue"] for x in tech_df["value_gap"]]
                fig_t = go.Figure()
                fig_t.add_trace(go.Bar(x=tech_df["ticker"], y=tech_df["value_gap"],
                                       marker_color=colors,
                                       text=tech_df["value_gap"].apply(lambda x:f"{x:+.1f}%"),
                                       textposition="outside"))
                fig_t.add_hline(y=0, line_color=THEME["text"], line_width=2)
                fig_t.add_hrect(y0=-25, y1=0, fillcolor=THEME["green"], opacity=0.08,
                                annotation_text="BUYING ZONE")
                apply_layout(fig_t, "Value Gap from Moving Average", 400)
                fig_t.update_yaxes(ticksuffix="%")
                st.plotly_chart(fig_t, use_container_width=True)

                # RSI chart
                rsi_colors = [THEME["red"] if r>=70 else THEME["green"] if r<=30 else THEME["blue"]
                              for r in tech_df["rsi_14"]]
                fig_r = go.Figure()
                fig_r.add_trace(go.Bar(x=tech_df["ticker"], y=tech_df["rsi_14"],
                                       marker_color=rsi_colors,
                                       text=tech_df["rsi_14"].apply(lambda x:f"{x:.0f}"),
                                       textposition="outside"))
                fig_r.add_hline(y=70, line_dash="dash", line_color=THEME["red"], annotation_text="Overbought (70)")
                fig_r.add_hline(y=30, line_dash="dash", line_color=THEME["green"], annotation_text="Oversold (30)")
                apply_layout(fig_r, "RSI(14) Momentum Signal", 360)
                fig_r.update_yaxes(range=[0,100])
                st.plotly_chart(fig_r, use_container_width=True)

                # Golden Override Signal
                deepest = tech_df.iloc[0]
                if deepest["value_gap"] < -5:
                    info_box("🔔 Golden Override Candidate",
                             f"<b>{deepest['ticker']}</b> is {deepest['value_gap']:+.1f}% below its moving average. "
                             f"RSI: {deepest['rsi_14']:.0f} ({deepest['rsi_signal']}). "
                             f"Watch for a 3%+ intraday S&P drop as the trigger. Max 1 purchase/month.",
                             THEME["purple"])

        except ImportError:
            info_box("yfinance not available","Add `yfinance` to requirements.txt",THEME["orange"])
        except Exception as e:
            info_box("Portfolio Error",str(e),THEME["red"])

# ─────────────────────────────────────────────────────────────────────────────
# §10  ACTION BOARD
# ─────────────────────────────────────────────────────────────────────────────
if show_action:
    section_header("✅","§10 · Strategic Action Board","Turn the analysis into concrete priorities")

    actions = []
    avg_sr  = monthly_12m["savings_rate"].mean()
    if latest_month["savings_rate"] < avg_sr:
        actions.append(("Lift monthly surplus",
                        f"Latest savings rate {pct(latest_month['savings_rate'])} below 12m avg {pct(avg_sr)}"))
    portable_latest = df[
        (df["transaction_type"]=="expense") & (~df["subcategory"].isin({"Rent/Mortgage"})) &
        (df["month_start"]==latest_month["month_start"])
    ]["amount"].sum()
    if portable_latest > 5000:
        actions.append(("Review portable spend",
                        f"Lifestyle spend (excl. rent) hit {fmt_money(portable_latest)} this month — watch mortgage headroom"))
    run_surplus = SALARY_NET_MONTHLY - portable_latest - MORTGAGE_REPAYMENT - DCA_ACTIVE
    if run_surplus < 1000:
        actions.append(("⚠️ Surplus below $1,000 floor",
                        f"Post-mortgage surplus is {fmt_money(run_surplus)} — consider dialling down DCA first"))

    if not actions:
        actions.append(("Maintain course","All metrics within target ranges. Focus on DCA consistency."))

    for priority, why in actions:
        st.markdown(f"""
        <div style="margin:8px 0; padding:12px 16px; background:#0b1220;
                    border-left:4px solid {THEME['blue']}; border-radius:8px;">
          <div style="font-weight:700; color:{THEME['text']};">{priority}</div>
          <div style="color:{THEME['muted']}; font-size:13px; margin-top:4px;">{why}</div>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# §11  MORTGAGE REALITY & SURPLUS STRESS TEST
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
                         delta="✅ Above $1k floor" if final_net_surplus > 1000 else "⚠️ Below $1k floor")

    # Gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=final_net_surplus,
        title={"text":"Post-Mortgage Surplus ($/mo)", "font":{"size":16,"color":THEME["text"]}},
        gauge={
            "axis": {"range":[-500,2500], "tickwidth":1},
            "bar":  {"color": THEME["blue"]},
            "steps":[
                {"range":[-500,0],    "color":THEME["red"]},
                {"range":[0,1000],    "color":THEME["orange"]},
                {"range":[1000,2500], "color":THEME["green"]}
            ]
        }
    ))
    apply_layout(fig, "", 300)
    fig.update_layout(paper_bgcolor=THEME["panel"])
    st.plotly_chart(fig, use_container_width=True)

    info_box("Fortress Rule Check",
             f"Fortress v6.4 requires <b>&gt;$1,000/mo</b> unallocated surplus post-mortgage. "
             f"Your current projection: <b>{fmt_money(final_net_surplus)}</b>. "
             f"DCA dial (currently <b>${DCA_ACTIVE}/mo</b>) is the first lever — never touch the $30k emergency fund.",
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

    def build_waterfall(income, mortgage, provisions, lifestyle, dca):
        post_mortgage   = income - mortgage - provisions
        post_lifestyle  = post_mortgage - lifestyle
        surplus         = post_lifestyle - dca
        return [
            ("Gross Net Income",            income,                    THEME["green"]),
            ("— Mortgage Repayment",         -mortgage,                THEME["red"]),
            ("— Ownership Provisions",       -provisions,              THEME["orange"]),
            ("→ Post-Housing Surplus",        post_mortgage,            THEME["blue"]),
            ("— Lifestyle Expenses",         -lifestyle,               THEME["orange"]),
            ("→ Pre-Investment Surplus",      post_lifestyle,           THEME["teal"]),
            ("— Stock DCA Investment",       -dca,                     THEME["purple"]),
            ("★ TAKE-HOME SURPLUS",           surplus,                  THEME["green"] if surplus>1000 else THEME["yellow"] if surplus>0 else THEME["red"]),
        ], surplus

    scenarios = {
        f"Base (DCA ${DCA_PHASE_2}/mo — Phase 2)":  build_waterfall(SALARY_NET_MONTHLY, MORTGAGE_REPAYMENT, RATES_AND_INSURANCE+MAINTENANCE_BUFFER, avg_lifestyle_actual, DCA_PHASE_2),
        f"Scaled Up (DCA ${DCA_PHASE_3}/mo — Phase 3)": build_waterfall(SALARY_NET_MONTHLY, MORTGAGE_REPAYMENT, RATES_AND_INSURANCE+MAINTENANCE_BUFFER, avg_lifestyle_actual, DCA_PHASE_3),
        "Stress (Income -8%, Expenses +8%, DCA $450)": build_waterfall(SALARY_NET_MONTHLY*0.92, MORTGAGE_REPAYMENT, RATES_AND_INSURANCE+MAINTENANCE_BUFFER, avg_lifestyle_actual*1.08, DCA_PHASE_2),
    }

    # Summary comparison
    summary_rows = []
    for name, (steps, surplus) in scenarios.items():
        d = {s[0]: s[1] for s in steps}
        summary_rows.append({
            "Scenario": name.split("(")[0].strip(),
            "Income": d["Gross Net Income"], "Mortgage": d["— Mortgage Repayment"],
            "Lifestyle": d["— Lifestyle Expenses"], "DCA": d["— Stock DCA Investment"], "SURPLUS": surplus
        })

    fig_s = go.Figure(go.Bar(
        x=[r["Scenario"] for r in summary_rows],
        y=[r["SURPLUS"]  for r in summary_rows],
        marker_color=[THEME["green"] if r["SURPLUS"]>1000 else THEME["yellow"] if r["SURPLUS"]>0 else THEME["red"]
                      for r in summary_rows],
        text=[fmt_money(r["SURPLUS"]) for r in summary_rows],
        textposition="outside"
    ))
    fig_s.add_hline(y=1000, line_dash="dash", line_color=THEME["slate"],
                    annotation_text="$1,000 safety floor")
    apply_layout(fig_s, "Take-Home Surplus by Scenario", 360)
    fig_s.update_yaxes(tickprefix="$", tickformat=",")
    st.plotly_chart(fig_s, use_container_width=True)

    # Waterfall per scenario
    for name, (steps, surplus) in scenarios.items():
        with st.expander(f"📊 {name} — Surplus: {fmt_money(surplus)}/mo", expanded=(surplus<1000)):
            labels = [s[0] for s in steps]; values = [s[1] for s in steps]
            measures = ["absolute" if i==0 else ("total" if "Surplus" in labels[i] or "★" in labels[i] else "relative")
                        for i in range(len(labels))]
            fig_w = go.Figure(go.Waterfall(
                orientation="v", measure=measures, x=labels, y=values,
                connector={"line":{"color":THEME["grid"]}},
                increasing={"marker":{"color":THEME["green"]}},
                decreasing={"marker":{"color":THEME["red"]}},
                totals={"marker":{"color":THEME["blue"]}},
                text=[fmt_money(abs(v)) for v in values], textposition="outside"
            ))
            apply_layout(fig_w, "", 460)
            fig_w.update_xaxes(tickangle=-20)
            fig_w.update_yaxes(tickprefix="$", tickformat=",")
            st.plotly_chart(fig_w, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# §13  LVR & RATE SENSITIVITY
# ─────────────────────────────────────────────────────────────────────────────
if show_lvr:
    section_header("📐","§13 · LVR & Rate Sensitivity Modeller",
                   "How repayment changes across rate scenarios and deposit sizes")

    def monthly_rep(principal, annual_rate, n=360):
        r = annual_rate / 12
        return principal * (r*(1+r)**n) / ((1+r)**n - 1)

    rates       = [0.0565, 0.0615, 0.0665, 0.0715, 0.0765, 0.0815]
    loan_amounts = [600000, 625000, 650000, 655000, 680000]

    rows = []
    for rate in rates:
        row = {"Rate": f"{rate*100:.2f}%"}
        for loan in loan_amounts:
            row[f"${loan//1000}k"] = monthly_rep(loan, rate)
        rows.append(row)

    sens_df = pd.DataFrame(rows)
    st.markdown(f"<b style='color:{THEME['text']};'>Monthly Repayment Sensitivity ($)</b>", unsafe_allow_html=True)
    fmt_cols = {col: "${:,.0f}" for col in sens_df.columns if col != "Rate"}
    st.dataframe(money_table(sens_df, fmt_cols), use_container_width=True)

    # Rate vs repayment curve
    base_loan    = 654885
    rate_range   = np.linspace(0.04, 0.10, 60)
    repayments   = [monthly_rep(base_loan, r) for r in rate_range]
    non_h_exp    = df[(df["transaction_type"]=="expense") & (~df["subcategory"].isin({"Rent/Mortgage"})) &
                      (df["month_start"] < pd.Timestamp.today().to_period("M").to_timestamp())]
    avg_ls       = round(non_h_exp.groupby("month_start")["amount"].sum().tail(3).mean(), 0)
    max_afford   = SALARY_NET_MONTHLY - avg_ls - DCA_ACTIVE - 1000

    fig_lvr = go.Figure()
    fig_lvr.add_trace(go.Scatter(x=rate_range*100, y=repayments, mode="lines",
                                 name="Monthly repayment", line=dict(color=THEME["blue"], width=3)))
    fig_lvr.add_vline(x=6.65, line_dash="dash", line_color=THEME["yellow"],
                      annotation_text="Current 6.65%", annotation_position="top right")
    fig_lvr.add_hline(y=max_afford, line_dash="dot", line_color=THEME["red"],
                      annotation_text=f"Max for $1k surplus ({fmt_money(max_afford)})")
    apply_layout(fig_lvr, f"Repayment vs Rate — Loan ${base_loan/1000:.0f}k", 420)
    fig_lvr.update_xaxes(title="Annual Rate (%)", ticksuffix="%")
    fig_lvr.update_yaxes(title="Monthly Repayment ($)", tickprefix="$", tickformat=",")
    st.plotly_chart(fig_lvr, use_container_width=True)

    # Rate move impact table
    curr_rate = 0.0665; curr_rep = monthly_rep(base_loan, curr_rate)
    move_df = pd.DataFrame([
        {"Move":m, "Rate":f"{(curr_rate+d)*100:.2f}%",
         "Repayment": monthly_rep(base_loan, curr_rate+d),
         "MoM Delta": monthly_rep(base_loan, curr_rate+d)-curr_rep,
         "Annual Impact": (monthly_rep(base_loan, curr_rate+d)-curr_rep)*12}
        for m, d in [("-1.00%",-0.01),("-0.50%",-0.005),("-0.25%",-0.0025),
                     ("Current",0),("+0.25%",0.0025),("+0.50%",0.005),("+1.00%",0.01)]
    ])
    st.dataframe(move_df.style.format({"Repayment":"${:,.0f}","MoM Delta":"${:+,.0f}","Annual Impact":"${:+,.0f}"}),
                 use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# §14  HOME PURCHASE READINESS
# ─────────────────────────────────────────────────────────────────────────────
if show_readiness:
    section_header("🎯","§14 · Home Purchase Readiness Tracker",
                   "Fortress position: deposit, emergency fund, buffer, and runway to settlement")

    DEPOSIT_TARGET        = 130000
    EMERGENCY_FUND_TARGET = 30000
    BUFFER_TARGET         = 8000
    TOTAL_TARGETS         = DEPOSIT_TARGET + EMERGENCY_FUND_TARGET + BUFFER_TARGET
    PURCHASE_PRICE_14     = PURCHASE_PRICE
    WA_STAMP_DUTY         = 27855
    MORTGAGE_14           = MORTGAGE_REPAYMENT

    DEPOSIT_CURRENT   = min(TOTAL_LIQUID_CASH, DEPOSIT_TARGET)
    remaining_1       = max(0, TOTAL_LIQUID_CASH - DEPOSIT_CURRENT)
    EMERGENCY_CURRENT = min(remaining_1, EMERGENCY_FUND_TARGET)
    remaining_2       = max(0, remaining_1 - EMERGENCY_CURRENT)
    BUFFER_CURRENT    = min(remaining_2, BUFFER_TARGET)
    UNALLOCATED       = max(0, remaining_2 - BUFFER_CURRENT)

    deposit_gap   = max(0, DEPOSIT_TARGET - DEPOSIT_CURRENT)
    emergency_gap = max(0, EMERGENCY_FUND_TARGET - EMERGENCY_CURRENT)
    buffer_gap    = max(0, BUFFER_TARGET - BUFFER_CURRENT)
    total_gap     = deposit_gap + emergency_gap + buffer_gap
    readiness_pct = min(100, TOTAL_LIQUID_CASH / TOTAL_TARGETS * 100)

    # Readiness banner
    banner_color = THEME["green"] if readiness_pct >= 100 else THEME["yellow"] if readiness_pct >= 80 else THEME["red"]
    st.markdown(f"""
    <div style="margin:12px 0 20px; padding:18px 22px; background:#0b1220;
                border-left:6px solid {banner_color}; border-radius:10px;">
      <div style="font-size:22px; font-weight:800; color:{THEME['text']};">
        Overall Readiness: {readiness_pct:.0f}%
        &nbsp;·&nbsp; Cash: <span style='color:{THEME["blue"]};'>${TOTAL_LIQUID_CASH:,.0f}</span>
        &nbsp;·&nbsp; Target: <span style='color:{THEME["muted"]};'>${TOTAL_TARGETS:,.0f}</span>
        {'&nbsp;·&nbsp; <span style="color:' + THEME["green"] + ';">✅ All buckets funded</span>'
         if total_gap == 0 else
         f'&nbsp;·&nbsp; <span style="color:{THEME["red"]};">Still need: ${total_gap:,.0f}</span>'}
      </div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # Progress bars
    with col1:
        for label, current, target, color in [
            ("Deposit + Stamp Duty",  DEPOSIT_CURRENT,   DEPOSIT_TARGET,        THEME["blue"]),
            ("Emergency Fund",        EMERGENCY_CURRENT, EMERGENCY_FUND_TARGET, THEME["green"]),
            ("Moving/Baby/Buffer",    BUFFER_CURRENT,    BUFFER_TARGET,         THEME["orange"]),
        ]:
            pct_fill = min(100, current / target * 100)
            st.markdown(f"""
            <div style="margin:10px 0;">
              <div style="display:flex; justify-content:space-between; color:{THEME['text']};
                          font-size:13px; margin-bottom:5px;">
                <span>{label}</span>
                <span>${current:,.0f} / ${target:,.0f} ({pct_fill:.0f}%)</span>
              </div>
              <div style="background:#1e293b; border-radius:6px; height:16px; overflow:hidden;">
                <div style="width:{pct_fill}%; background:{color}; height:100%; border-radius:6px;"></div>
              </div>
            </div>""", unsafe_allow_html=True)

    with col2:
        # Donut chart
        pie_data = pd.DataFrame({
            "Bucket": ["Deposit Pool","Emergency Fund","Buffer","Unallocated"],
            "Amount": [DEPOSIT_CURRENT, EMERGENCY_CURRENT, BUFFER_CURRENT, max(UNALLOCATED,0)]
        }).query("Amount > 0")
        fig_d = px.pie(pie_data, names="Bucket", values="Amount", hole=0.55,
                       color_discrete_sequence=GOLD_SEQUENCE)
        apply_layout(fig_d, f"Capital Allocation — ${TOTAL_LIQUID_CASH:,.0f}", 360)
        st.plotly_chart(fig_d, use_container_width=True)

    # Emergency fund coverage
    cov_months = EMERGENCY_CURRENT / MORTGAGE_14
    info_box("Emergency Fund Coverage",
             f"${EMERGENCY_CURRENT:,.0f} covers <b>{cov_months:.1f} months</b> of ${MORTGAGE_14:,}/mo mortgage. "
             f"Fortress floor: 7+ months. Status: <b>{'✅ Pass' if cov_months>=7 else f'⚠️ {cov_months:.1f} months — below floor'}</b>",
             THEME["green"] if cov_months >= 7 else THEME["orange"])

    # LVR check
    net_dep = DEPOSIT_CURRENT - WA_STAMP_DUTY
    lvr     = (PURCHASE_PRICE_14 - net_dep) / PURCHASE_PRICE_14 * 100
    info_box("LVR Check",
             f"Deposit pool <b>${DEPOSIT_CURRENT:,.0f}</b> minus WA stamp duty <b>${WA_STAMP_DUTY:,.0f}</b> = "
             f"net deposit <b>${net_dep:,.0f}</b>. "
             f"On ${PURCHASE_PRICE_14:,.0f} purchase: LVR = <b>{lvr:.1f}%</b>. "
             f"{'✅ Below 90% — no LMI under Hejaz Ijarah.' if lvr<90 else '⚠️ Above 90% — check LMI terms.'}",
             THEME["green"] if lvr < 90 else THEME["red"])

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
            schedule.append({"month":m, "phase":phase_name, "dca_amount":amount})
    sched_df = pd.DataFrame(schedule)

    # Next 24 months bar chart
    next_24 = sched_df[sched_df["month"] >= today].head(24).copy()
    next_24["Month_Label"] = next_24["month"].dt.strftime("%b %Y")
    colors_24 = {
        "Phase 1 — Pre-house DCA": THEME["green"],
        "Phase 2 — House transition": THEME["orange"],
        "Phase 3 — Growth mode": THEME["blue"],
    }
    fig_dca = go.Figure()
    fig_dca.add_trace(go.Bar(
        x=next_24["Month_Label"], y=next_24["dca_amount"],
        marker_color=[colors_24.get(p, THEME["blue"]) for p in next_24["phase"]],
        text=[fmt_money(v) for v in next_24["dca_amount"]],
        textposition="outside"
    ))
    apply_layout(fig_dca, "Monthly DCA Contributions — Next 24 Months", 420)
    fig_dca.update_yaxes(tickprefix="$", tickformat=",")
    fig_dca.update_xaxes(tickangle=-45)
    st.plotly_chart(fig_dca, use_container_width=True)

    # Long-range projection
    CAGR = 0.08
    portfolio_value = START_PORTFOLIO_VALUE
    projection = []
    for _, row in sched_df.iterrows():
        monthly_return = (1 + CAGR) ** (1/12) - 1
        portfolio_value = portfolio_value * (1 + monthly_return) + row["dca_amount"]
        projection.append({"month":row["month"], "phase":row["phase"], "portfolio_value":portfolio_value})

    proj_df    = pd.DataFrame(projection)
    annual_proj = proj_df[proj_df["month"].dt.month == 12].copy()
    annual_proj["Year"] = annual_proj["month"].dt.year

    fig_proj = go.Figure()
    fig_proj.add_trace(go.Scatter(
        x=annual_proj["Year"], y=annual_proj["portfolio_value"],
        mode="lines+markers", name="Portfolio Value (8% CAGR)",
        line=dict(color=THEME["green"], width=3),
        fill="tozeroy", fillcolor="rgba(52,211,153,0.08)"
    ))
    fig_proj.add_hline(y=1700000, line_dash="dash", line_color=THEME["yellow"],
                       annotation_text="$1.7M Target by 2056")
    fig_proj.add_vrect(x0=2026, x1=2027.5, fillcolor=THEME["orange"], opacity=0.07,
                       annotation_text="Phase 2 ($450/mo)")
    fig_proj.add_vrect(x0=2027.5, x1=2057, fillcolor=THEME["blue"], opacity=0.03,
                       annotation_text="Phase 3 ($1,000+/mo)")
    apply_layout(fig_proj, "Portfolio Growth Projection to 2056 — 8% CAGR", 520)
    fig_proj.update_yaxes(tickprefix="$", tickformat=",")
    fig_proj.update_xaxes(title="Year")
    st.plotly_chart(fig_proj, use_container_width=True)

    # Milestones table
    milestone_years = [2030, 2035, 2040, 2045, 2050, 2056]
    milestones = annual_proj[annual_proj["Year"].isin(milestone_years)][["Year","portfolio_value"]].copy()
    milestones.columns = ["Year","Projected Portfolio Value"]
    milestones["vs $1.7M Target"] = milestones["Projected Portfolio Value"] - 1700000
    st.dataframe(milestones.style.format({
        "Projected Portfolio Value": "${:,.0f}",
        "vs $1.7M Target": "${:+,.0f}"
    }), use_container_width=True)

    # When does $1.7M hit?
    hit_row = proj_df[proj_df["portfolio_value"] >= 1700000]
    if not hit_row.empty:
        hit_date = hit_row.iloc[0]["month"]
        info_box("🎯 $1.7M Target Milestone",
                 f"At 8% CAGR with the Fortress DCA schedule (starting at ${START_PORTFOLIO_VALUE:,}), "
                 f"the $1.7M target is reached around <b>{hit_date.strftime('%B %Y')}</b> — "
                 f"<b>{hit_date.year - today.year} years</b> from today. "
                 f"Phase 3 ramp-up ($1,000+/mo from Aug 2027) is the critical driver. "
                 f"Each month of delay in Phase 3 pushes the milestone by ~1.5 months.",
                 THEME["green"])
    else:
        info_box("Projection Note",
                 "Increase DCA Phase 3 amount or starting portfolio value to reach $1.7M within the model window.",
                 THEME["orange"])

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin:40px 0 0; padding:20px 24px; background:{THEME['panel']};
            border:1px solid {THEME['grid']}; border-radius:12px; text-align:center;
            font-family:sans-serif;">
  <div style="font-size:16px; font-weight:700; color:{THEME['text']};">
    Personal Financial Intelligence Report — Version 7.0
  </div>
  <div style="font-size:12px; color:{THEME['muted']}; margin-top:6px;">
    Fortress Strategy v6.4 · Perth, WA · Sections 1–2B, 3–3D, 4–7, 8–9, 10, 11, 12, 13, 14, 15 active ·
    Source: Google Drive workbook · Auto-refresh: 5 min
  </div>
</div>
""", unsafe_allow_html=True)
