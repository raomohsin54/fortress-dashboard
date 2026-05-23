import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from config import THEME, GOLD_SEQUENCE, section_header, info_box, apply_layout, fmt_money, pct


def render(df, monthly_12m, latest_month, prior_month):
    section_header("📊", "§1-2 · Executive Diagnostic + Cash Flow Engine", "Latest month health check · income, expense, savings rate, transfer intelligence")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Income (Latest)", fmt_money(latest_month["income"]), delta=fmt_money(latest_month["income"]-prior_month["income"]))
    col2.metric("Expenses (Latest)", fmt_money(latest_month["expense"]), delta=fmt_money(latest_month["expense"]-prior_month["expense"]), delta_color="inverse")
    col3.metric("Savings Rate", pct(latest_month["savings_rate"]), delta=f"{latest_month['savings_rate']-prior_month['savings_rate']:.1f}pp")
    col4.metric("Surplus (Latest)", fmt_money(latest_month["savings"]), delta=fmt_money(latest_month["savings"]-prior_month["savings"]))

    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly_12m["Month_Label"], y=monthly_12m["income"], name="Income", marker_color=THEME["green"], opacity=.86))
    fig.add_trace(go.Bar(x=monthly_12m["Month_Label"], y=monthly_12m["expense"], name="Expense", marker_color=THEME["red"], opacity=.82))
    fig.add_trace(go.Scatter(x=monthly_12m["Month_Label"], y=monthly_12m["savings_3m_avg"], name="Savings 3m avg", mode="lines+markers", line=dict(color=THEME["gold2"], width=3)))
    apply_layout(fig, "Monthly Income vs Expense — 12 Months", 420)
    fig.update_yaxes(tickprefix="$", tickformat=",")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=monthly_12m["Month_Label"], y=monthly_12m["savings_rate"], mode="lines+markers", name="Savings Rate %", line=dict(color=THEME["teal"], width=3), fill="tozeroy", fillcolor="rgba(45,212,191,0.12)"))
    fig2.add_hline(y=20, line_dash="dash", line_color=THEME["soft"] if "soft" in THEME else THEME["slate"], annotation_text="20% benchmark")
    apply_layout(fig2, "Monthly Savings Rate %", 320)
    fig2.update_yaxes(ticksuffix="%")
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    section_header("🔄", "§2B · Transfer Intelligence", "Where money beyond expenses actually went")
    transfer_df = df[df["transfer_class"] != ""].groupby("transfer_class", as_index=False)["transfer_amount"].sum()
    if transfer_df.empty:
        info_box("No transfers detected", "No transfer rows were found in the workbook for this period.", THEME["orange"])
        return
    fig3 = px.pie(transfer_df, names="transfer_class", values="transfer_amount", hole=.58, color_discrete_sequence=GOLD_SEQUENCE)
    apply_layout(fig3, "Transfer Classification — Full Period", 360)
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
