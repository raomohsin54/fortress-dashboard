import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from scipy.stats import median_abs_deviation
from config import THEME, section_header, info_box, apply_layout, fmt_money


def render(df, monthly_12m, cat_month):
    section_header("⚠️", "§4-7 · Anomaly Engine, Concentration & Forecast", "Statistical anomaly detection · run-rate · 3-month forward projection")
    cat_total = df[df["transaction_type"]=="expense"].groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
    total_exp = cat_total["amount"].sum()
    cat_total["share_pct"] = np.where(total_exp != 0, cat_total["amount"] / total_exp * 100, 0)
    fig = px.bar(cat_total.head(10), x="category", y="share_pct", color="share_pct", color_continuous_scale=[[0,"#1E293B"],[.55,THEME["gold"]],[1,THEME["gold2"]]], text=cat_total.head(10)["share_pct"].apply(lambda x:f"{x:.1f}%"))
    apply_layout(fig, "Expense Concentration — Full Period (Top 10 Categories)", 380)
    fig.update_yaxes(title="Share %", ticksuffix="%")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    rows = []
    for cat, grp in cat_month.groupby("category"):
        amounts = grp["amount"].values
        if len(amounts) < 3:
            continue
        med = np.median(amounts); mad = median_abs_deviation(amounts)
        latest_amt = grp.sort_values("month_start").iloc[-1]["amount"]
        z = (latest_amt - med) / (mad * 1.4826 + 1e-9)
        rows.append({"Category":cat,"Latest":latest_amt,"Median":med,"MAD-Z":z})
    anom_df = pd.DataFrame(rows).sort_values("MAD-Z", ascending=False) if rows else pd.DataFrame()
    flagged = anom_df[anom_df["MAD-Z"] > 2].head(5) if not anom_df.empty else pd.DataFrame()
    if flagged.empty:
        info_box("✅ No Anomalies", "All categories are within normal statistical ranges this month.", THEME["green"])
    else:
        info_box("🚨 Anomaly Flags", "Categories running >2 MAD above their median: " + ", ".join(f"<b>{r['Category']}</b> ({fmt_money(r['Latest'])})" for _, r in flagged.iterrows()), THEME["red"])

    section_header("🔮", "§7 · 3-Month Forward Forecast", "Run-rate projection based on trailing 3m average")
    run_rate_income = monthly_12m["income"].tail(3).mean(); run_rate_expense = monthly_12m["expense"].tail(3).mean(); run_rate_surplus = run_rate_income - run_rate_expense
    c1, c2, c3 = st.columns(3)
    c1.metric("Projected Monthly Income", fmt_money(run_rate_income))
    c2.metric("Projected Monthly Expense", fmt_money(run_rate_expense))
    c3.metric("Projected Monthly Surplus", fmt_money(run_rate_surplus), delta="vs $1,000 floor" if run_rate_surplus > 1000 else "⚠️ Below $1k floor")
