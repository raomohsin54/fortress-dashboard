import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from config import THEME, section_header, info_box, apply_layout, fmt_money, money_table


def render(start_portfolio_value):
    section_header("📈", "§15 · DCA Engine: Cycle Tracker & $1.7M Portfolio Projection", "Phase-aware DCA schedule · 8% CAGR model · milestone tracker")
    today = pd.Timestamp.today()
    phases = [("Phase 1 — Pre-house DCA", pd.Timestamp("2026-02-01"), pd.Timestamp("2026-06-30"), 950),("Phase 2 — House transition", pd.Timestamp("2026-07-01"), pd.Timestamp("2027-07-31"), 450),("Phase 3 — Growth mode", pd.Timestamp("2027-08-01"), pd.Timestamp("2056-12-31"), 1000)]
    schedule = []
    for name, start, end, amount in phases:
        for m in pd.date_range(start=start, end=min(end, pd.Timestamp("2056-12-01")), freq="MS"):
            schedule.append({"month":m,"phase":name,"dca_amount":amount})
    sched = pd.DataFrame(schedule)
    next_24 = sched[sched["month"] >= today].head(24).copy(); next_24["Month_Label"] = next_24["month"].dt.strftime("%b %Y")
    phase_colours = {"Phase 1 — Pre-house DCA":THEME["green"],"Phase 2 — House transition":THEME["orange"],"Phase 3 — Growth mode":THEME["blue"]}
    fig = go.Figure(go.Bar(x=next_24["Month_Label"], y=next_24["dca_amount"], marker_color=[phase_colours.get(p, THEME["blue"]) for p in next_24["phase"]], text=[fmt_money(v) for v in next_24["dca_amount"]], textposition="outside"))
    apply_layout(fig, "Monthly DCA Contributions — Next 24 Months", 420); fig.update_yaxes(tickprefix="$", tickformat=","); fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    cagr = .08; value = start_portfolio_value; projection = []
    monthly_return = (1+cagr)**(1/12)-1
    for _, row in sched.iterrows():
        value = value * (1 + monthly_return) + row["dca_amount"]
        projection.append({"month":row["month"],"phase":row["phase"],"portfolio_value":value})
    proj = pd.DataFrame(projection); annual = proj[proj["month"].dt.month == 12].copy(); annual["Year"] = annual["month"].dt.year
    fig2 = go.Figure(go.Scatter(x=annual["Year"], y=annual["portfolio_value"], mode="lines+markers", name="Portfolio Value (8% CAGR)", line=dict(color=THEME["green"], width=3), fill="tozeroy", fillcolor="rgba(52,211,153,.10)"))
    fig2.add_hline(y=1700000, line_dash="dash", line_color=THEME["gold2"], annotation_text="$1.7M Target by 2056")
    fig2.add_vrect(x0=2026, x1=2027.5, fillcolor=THEME["orange"], opacity=.07, annotation_text="Phase 2")
    fig2.add_vrect(x0=2027.5, x1=2057, fillcolor=THEME["blue"], opacity=.04, annotation_text="Phase 3")
    apply_layout(fig2, "Portfolio Growth Projection to 2056 — 8% CAGR", 520); fig2.update_yaxes(tickprefix="$", tickformat=","); fig2.update_xaxes(title="Year")
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    milestones = annual[annual["Year"].isin([2030,2035,2040,2045,2050,2056])][["Year","portfolio_value"]].copy()
    milestones.columns = ["Year","Projected Portfolio Value"]; milestones["vs $1.7M Target"] = milestones["Projected Portfolio Value"] - 1700000
    st.dataframe(milestones.style.format({"Projected Portfolio Value":"${:,.0f}","vs $1.7M Target":"${:+,.0f}"}), use_container_width=True)
    hit = proj[proj["portfolio_value"] >= 1700000]
    if not hit.empty:
        hit_date = hit.iloc[0]["month"]
        info_box("🎯 $1.7M Target Milestone", f"At 8% CAGR with the Fortress DCA schedule, the $1.7M target is reached around <b>{hit_date.strftime('%B %Y')}</b>.", THEME["green"])
    else:
        info_box("Projection Note", "Increase Phase 3 DCA or starting portfolio value to reach $1.7M within the model window.", THEME["orange"])
