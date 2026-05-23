import numpy as np
import streamlit as st
import plotly.graph_objects as go
from config import THEME, section_header, info_box, apply_layout, fmt_money, pct, money_table


def render(df, monthly, monthly_12m, cat_month, latest_month, mortgage_repayment):
    section_header("🛒", "§3 · Spend Benchmarking + §3C-3D Portable Cost Base", "Category breakdown · excl. rent · true carry-forward costs")
    latest_cat = df[(df["transaction_type"]=="expense") & (df["month_start"]==latest_month["month_start"])].groupby("category", as_index=False)["amount"].sum().rename(columns={"amount":"latest"})
    avg_cat = cat_month[cat_month["month_start"] < latest_month["month_start"]].groupby("category", as_index=False)["amount"].mean().rename(columns={"amount":"avg_12m"})
    cat_compare = latest_cat.merge(avg_cat, on="category", how="left").sort_values("latest", ascending=False)
    cat_compare["variance_$"] = cat_compare["latest"] - cat_compare["avg_12m"]

    fig = go.Figure()
    fig.add_trace(go.Bar(y=cat_compare["category"], x=cat_compare["avg_12m"], orientation="h", name="12m Avg", marker_color=THEME["slate"], opacity=.70))
    fig.add_trace(go.Bar(y=cat_compare["category"], x=cat_compare["latest"], orientation="h", name="Latest Month", marker_color=THEME["blue"]))
    apply_layout(fig, "Category Spend: Latest vs 12m Average", max(360, len(cat_compare)*45))
    fig.update_layout(barmode="overlay"); fig.update_xaxes(tickprefix="$", tickformat=",")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    section_header("🧮", "§3C · Portable Cost Base — Expenses Excl. Rent & Transfers", "The costs that survive the house purchase")
    portable_df = df[(df["transaction_type"]=="expense") & (~df["subcategory"].isin({"Rent/Mortgage"}))].copy()
    portable_monthly = portable_df.groupby(["month_start","Month_Label"], as_index=False)["amount"].sum().rename(columns={"amount":"portable_expenses"}).sort_values("month_start")
    portable_monthly = portable_monthly.merge(monthly[["month_start","income"]], on="month_start", how="left")
    portable_monthly["portable_pct_income"] = np.where(portable_monthly["income"]>0, portable_monthly["portable_expenses"]/portable_monthly["income"]*100, np.nan)
    portable_monthly["portable_3m_avg"] = portable_monthly["portable_expenses"].rolling(3, min_periods=1).mean()
    portable_12m = portable_monthly.tail(12)

    c1, c2, c3 = st.columns(3)
    c1.metric("Latest Month (excl. rent)", fmt_money(portable_12m["portable_expenses"].iloc[-1]))
    c2.metric("12-Month Average", fmt_money(portable_12m["portable_expenses"].mean()))
    c3.metric("Avg % of Income", pct(portable_12m["portable_pct_income"].mean()))

    fig_p = go.Figure()
    fig_p.add_trace(go.Bar(x=portable_12m["Month_Label"], y=portable_12m["portable_expenses"], name="Monthly (excl. rent)", marker_color=THEME["blue"], opacity=.85))
    fig_p.add_trace(go.Scatter(x=portable_12m["Month_Label"], y=portable_12m["portable_3m_avg"], mode="lines+markers", name="3m rolling avg", line=dict(color=THEME["gold2"], width=3)))
    apply_layout(fig_p, "Monthly Expenses Excl. Rent & Transfers", 420)
    fig_p.update_yaxes(tickprefix="$", tickformat=",")
    st.plotly_chart(fig_p, use_container_width=True, config={"displayModeBar": False})

    avg_portable = portable_12m["portable_expenses"].mean()
    info_box("Portable Cost Base Verdict", f"Average portable cost base is <b>{fmt_money(avg_portable)}/mo</b>. This stacks on top of your <b>{fmt_money(mortgage_repayment)}/mo</b> mortgage repayment.", THEME["teal"])

    section_header("📋", "§3D · Monthly Expense Tracker (Excl. Rent)", "Month-by-month category matrix — spot lifestyle creep")
    portable_pivot = portable_df[portable_df["month_start"].isin(portable_12m["month_start"])].assign(amount_abs=lambda x: x["amount"].abs()).groupby(["Month_Label","category"], as_index=False)["amount_abs"].sum().pivot_table(index="Month_Label", columns="category", values="amount_abs", aggfunc="sum", fill_value=0)
    if portable_pivot.empty:
        info_box("No portable expense data", "No non-rent expense rows were found for the selected period.", THEME["orange"])
    else:
        portable_pivot = portable_pivot.loc[[m for m in portable_12m["Month_Label"].tolist() if m in portable_pivot.index]]
        portable_pivot["TOTAL"] = portable_pivot.sum(axis=1)
        st.dataframe(money_table(portable_pivot), use_container_width=True)
