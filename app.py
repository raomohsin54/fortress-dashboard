"""
Personal Financial Intelligence Report — Fortress modular Streamlit app.
Run with: streamlit run app.py
"""
import io
import warnings
from datetime import datetime

import pandas as pd
import streamlit as st

from config import PAGE_ICON, PAGE_TITLE, THEME, banner, inject_theme, latest_n
from data_loader import get_workbook_from_ui, load_and_process, setup_guide
from sections import anomaly, cashflow, dca, mortgage, portfolio, readiness, spend

warnings.filterwarnings("ignore")

st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide", initial_sidebar_state="expanded")
inject_theme()

with st.sidebar:
    st.markdown(f"""
    <div style="padding:14px 0 8px;">
      <div style="font-size:23px;font-weight:900;color:{THEME['text']};">💼 Fortress</div>
      <div style="font-size:12px;color:{THEME['muted']};margin-top:4px;">Personal Financial Intelligence</div>
    </div>""", unsafe_allow_html=True)
    st.divider()
    st.markdown("**📊 Live Parameters**")
    total_liquid_cash = st.number_input("Total Liquid Cash ($)", value=168000, step=1000)
    salary_net_monthly = st.number_input("Net Monthly Income ($)", value=9684, step=100)
    purchase_price = st.number_input("House Target ($)", value=730000, step=5000)
    mortgage_repayment = st.number_input("Monthly Repayment ($)", value=4205, step=50)
    start_portfolio_value = st.number_input("Current IBKR Portfolio ($)", value=15000, step=1000)
    st.divider()
    st.markdown("**📈 DCA Phase**")
    dca_phase = st.radio("Active DCA Phase", ["Phase 1 ($950/mo)", "Phase 2 ($450/mo)", "Phase 3 ($1,000/mo)"], index=1)
    dca_active = {"Phase 1 ($950/mo)":950, "Phase 2 ($450/mo)":450, "Phase 3 ($1,000/mo)":1000}[dca_phase]
    st.divider()
    st.markdown("**👁 Show Sections**")
    show_cashflow = st.checkbox("§1-2 · Cash Flow Engine", value=True)
    show_spend = st.checkbox("§3-3D · Spend Analysis", value=True)
    show_anomaly = st.checkbox("§4-7 · Anomaly & Forecast", value=True)
    show_portfolio = st.checkbox("§8-9 · Portfolio & Technical", value=True)
    show_action = st.checkbox("§10 · Action Board", value=True)
    show_mortgage = st.checkbox("§11 · Mortgage Stress Test", value=True)
    show_waterfall = st.checkbox("§12 · Post-House Waterfall", value=True)
    show_lvr = st.checkbox("§13 · LVR Sensitivity", value=True)
    show_readiness = st.checkbox("§14 · Purchase Readiness", value=True)
    show_dca = st.checkbox("§15 · DCA Engine & $1.7M", value=True)
    st.divider()
    st.caption(f"Last refreshed: {datetime.now().strftime('%d %b %Y %H:%M')}")

banner()
workbook_buffer = get_workbook_from_ui()
setup_guide(expanded=(workbook_buffer is None))

if workbook_buffer is None:
    st.info("⬆️ Load your workbook above to see the dashboard.")
    st.stop()

report_today = pd.Timestamp.today().normalize()
report_as_of = (report_today - pd.offsets.MonthBegin(1)).normalize() if report_today.day < 12 else report_today
buffer_bytes = workbook_buffer.read() if hasattr(workbook_buffer, "read") else workbook_buffer

try:
    df, monthly, cat_month, raw_portfolio = load_and_process(buffer_bytes, str(report_as_of.date()))
except Exception as exc:
    st.error(f"❌ Could not process workbook: {exc}")
    st.info("Required Sheet1 columns: transaction_date, category, subcategory, description, amount, transaction_type.")
    st.stop()

monthly_12m = latest_n(monthly, 12)
latest_month = monthly_12m.iloc[-1]
prior_month = monthly_12m.iloc[-2] if len(monthly_12m) >= 2 else latest_month
st.success(f"✅ {len(df):,} transactions loaded · Reporting through {report_as_of.strftime('%B %Y')}")

if show_cashflow:
    cashflow.render(df, monthly_12m, latest_month, prior_month)
if show_spend:
    spend.render(df, monthly, monthly_12m, cat_month, latest_month, mortgage_repayment)
if show_anomaly:
    anomaly.render(df, monthly_12m, cat_month)
if show_portfolio:
    portfolio.render(raw_portfolio)
if show_action:
    readiness.render_action(df, monthly_12m, latest_month, salary_net_monthly, mortgage_repayment, dca_active)
if show_mortgage:
    mortgage.render_stress(df, monthly, salary_net_monthly, mortgage_repayment, dca_active)
if show_waterfall:
    mortgage.render_waterfall(df, salary_net_monthly, mortgage_repayment)
if show_lvr:
    mortgage.render_lvr(df, salary_net_monthly, dca_active)
if show_readiness:
    readiness.render_readiness(total_liquid_cash, purchase_price, mortgage_repayment)
if show_dca:
    dca.render(start_portfolio_value)

st.markdown(f"""
<div style="margin:40px 0 0;padding:20px 24px;background:{THEME['panel']};border:1px solid rgba(242,201,76,.22);border-radius:18px;text-align:center;">
  <div style="font-size:16px;font-weight:900;color:{THEME['text']};">Personal Financial Intelligence Report — Modular Fortress Edition</div>
  <div style="font-size:12px;color:{THEME['muted']};margin-top:6px;">Source: Google Drive workbook · Auto-refresh: 5 min · Future edits isolated by section module</div>
</div>
""", unsafe_allow_html=True)
