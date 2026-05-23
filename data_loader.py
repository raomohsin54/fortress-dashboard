import io
import json
import numpy as np
import pandas as pd
import streamlit as st

CATEGORY_BUCKET_MAP = {
    "HOUSING":"Essential","UTILITIES":"Essential","TRANSPORTATION":"Essential",
    "FOOD":"Essential","DAILY LIVING":"Essential","HEALTH & WELLNESS":"Essential",
    "DEBT & OBLIGATIONS":"Essential","SUBSCRIPTIONS":"Lifestyle","ENTERTAINMENT":"Lifestyle",
    "GIFTS & CHARITY":"Lifestyle","MISCELLANEOUS":"Lifestyle","SAVINGS & INVESTMENTS":"Wealth",
    "INCOME":"Income"
}
TRANSFER_KEYWORDS_INVEST = ["buy ","stocks","investment","invest","spus","spsk","slv","ivv","vas","ndq","etf","shares","spte","islm","skuk","hhif","gold","commsec","ibkr","interactive brokers","hejaz","stake","selfwealth","pearler"]
TRANSFER_KEYWORDS_GOAL = ["trip","travel","hotel","ticket","zakat","umrah","holiday","bangkok","savings goal","emergency","car fund","house fund","wedding"]
TRANSFER_KEYWORDS_SAVINGS = ["offset","savings account","high interest","hisa","ubank","ing ","macquarie savings","bonus saver","rabobank","move to savings"]


def normalize_cols(df):
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip().str.lower().str.replace(r"[^a-z0-9]+", "_", regex=True).str.strip("_")
    return df


def classify_bucket(category):
    return CATEGORY_BUCKET_MAP.get(str(category).strip().upper(), "Other")


def classify_transfer_type(description, subcategory="", category=""):
    desc = str(description).lower(); sub = str(subcategory).lower()
    if any(k in desc for k in TRANSFER_KEYWORDS_INVEST) or "stocks" in sub or "investment" in sub:
        return "Investment Transfer"
    if any(k in desc for k in TRANSFER_KEYWORDS_GOAL) or "savings goal" in sub or "zakat" in desc:
        return "Goal / Planned Drawdown"
    if any(k in desc for k in TRANSFER_KEYWORDS_SAVINGS) or "savings" in sub:
        return "Savings Account Transfer"
    return "Other Transfer"


@st.cache_data(ttl=300, show_spinner="📡 Syncing from Google Drive…")
def load_from_google_drive(file_id: str, credentials_json: str):
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    creds_dict = json.loads(credentials_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/drive.readonly"])
    service = build("drive", "v3", credentials=creds, cache_discovery=False)
    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO(); downloader = MediaIoBaseDownload(buffer, request); done = False
    while not done:
        _, done = downloader.next_chunk()
    buffer.seek(0)
    return buffer


def get_workbook_from_ui():
    st.markdown("<div style='font-size:13px;color:#CBD5E1;margin-bottom:8px;'>📂 Data source</div>", unsafe_allow_html=True)
    data_source = st.radio("Load data from", ["Google Drive (auto-sync)", "Upload Excel manually"], horizontal=True, label_visibility="collapsed")
    workbook_buffer = None
    if data_source == "Google Drive (auto-sync)":
        try:
            creds_json = json.dumps(dict(st.secrets["gcp_service_account"]))
            file_id = st.secrets["gdrive_file_id"]
            workbook_buffer = load_from_google_drive(file_id, creds_json)
            st.success("✅ Loaded from Google Drive")
        except Exception as e:
            st.warning(f"⚠️ Google Drive not configured yet. ({e})")
            st.info("Switch to manual upload while secrets are being configured.")
    else:
        uploaded = st.file_uploader("Upload your 'Transactions budget.xlsx'", type=["xlsx"])
        if uploaded:
            workbook_buffer = uploaded
            st.success("✅ File loaded")
    return workbook_buffer


def setup_guide(expanded=False):
    with st.expander("📋 One-time Setup Guide — Google Drive + Streamlit", expanded=expanded):
        st.markdown("""
1. Create a GitHub repo and upload this `fortress/` folder.
2. Deploy with Streamlit Cloud using `fortress/app.py` as the entry file.
3. Enable Google Drive API, create a service account, and share the workbook with that service account email.
4. Add `gdrive_file_id` and `[gcp_service_account]` to Streamlit secrets.

After that: edit Excel in Google Drive → open the dashboard → it refreshes automatically.
""")


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
    for c in ["category","subcategory","description","transaction_type"]:
        df[c] = df[c].astype(str).str.strip()
    df["transaction_type"] = df["transaction_type"].str.lower()

    report_as_of = pd.Timestamp(report_as_of_str)
    cutoff = report_as_of.to_period("M").to_timestamp("M")
    df = df[df["transaction_date"] <= cutoff].copy()
    df["month_start"] = df["transaction_date"].dt.to_period("M").dt.to_timestamp()
    df["month_year"] = df["transaction_date"].dt.to_period("M").astype(str)
    df["month_label"] = df["transaction_date"].dt.strftime("%b %Y")
    df["Month_Label"] = df["month_label"]
    df["quarter"] = "Q" + df["transaction_date"].dt.quarter.astype(str) + " " + df["transaction_date"].dt.year.astype(str)
    df["year"] = df["transaction_date"].dt.year
    df["bucket"] = df["category"].map(classify_bucket)

    transfer_mask = df["transaction_type"].eq("transfer")
    df["transfer_class"] = np.where(transfer_mask, df.apply(lambda r: classify_transfer_type(r.get("description",""), r.get("subcategory",""), r.get("category","")), axis=1), "")
    df["income_amount"] = np.where(df["transaction_type"].eq("income"), df["amount"].abs(), 0)
    df["expense_amount"] = np.where(df["transaction_type"].eq("expense"), df["amount"].abs(), 0)
    df["transfer_amount"] = np.where(df["transaction_type"].eq("transfer"), df["amount"].abs(), 0)
    df["investment_transfer_amount"] = np.where(df["transfer_class"].eq("Investment Transfer"), df["transfer_amount"], 0)
    df["goal_transfer_amount"] = np.where(df["transfer_class"].eq("Goal / Planned Drawdown"), df["transfer_amount"], 0)
    df["savings_transfer_amount"] = np.where(df["transfer_class"].eq("Savings Account Transfer"), df["transfer_amount"], 0)

    monthly = df.groupby(["month_start","month_year"], as_index=False).agg(
        income=("income_amount","sum"), expense=("expense_amount","sum"), transfer_total=("transfer_amount","sum"),
        investment_transfer=("investment_transfer_amount","sum"), goal_transfer=("goal_transfer_amount","sum"),
        savings_transfer=("savings_transfer_amount","sum"), rows=("amount","size")
    ).sort_values("month_start").reset_index(drop=True)
    monthly["Month_Label"] = monthly["month_start"].dt.strftime("%b %Y")
    monthly["savings"] = monthly["income"] - monthly["expense"]
    monthly["actual_savings"] = monthly["savings"] - monthly["transfer_total"]
    monthly["savings_rate"] = np.where(monthly["income"] != 0, monthly["savings"] / monthly["income"] * 100, np.nan)
    monthly["expense_ratio"] = np.where(monthly["income"] != 0, monthly["expense"] / monthly["income"] * 100, np.nan)
    monthly["income_3m_avg"] = monthly["income"].rolling(3, min_periods=1).mean()
    monthly["expense_3m_avg"] = monthly["expense"].rolling(3, min_periods=1).mean()
    monthly["savings_3m_avg"] = monthly["savings"].rolling(3, min_periods=1).mean()

    cat_month = df[df["transaction_type"].eq("expense")].groupby(["month_start","month_year","category"], as_index=False)["amount"].sum().sort_values(["month_start","amount"], ascending=[True,False])
    return df, monthly, cat_month, raw_portfolio
