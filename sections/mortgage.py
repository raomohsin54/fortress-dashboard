import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from config import THEME, section_header, info_box, apply_layout, fmt_money, money_table

RATES_AND_INSURANCE = 400
MAINTENANCE_BUFFER = 400


def render_stress(df, monthly, salary_net_monthly, mortgage_repayment, dca_active):
    section_header("🏠", "§11 · Mortgage Reality & Surplus Stress Test", "Calculated against last 3 completed months of actual spending")
    completed = monthly[monthly["month_start"] < pd.Timestamp.today().to_period("M").to_timestamp()]
    last_3 = completed.tail(3)
    verified_income = last_3["income"].iloc[-1] if len(last_3) else salary_net_monthly
    non_housing = df[(df["transaction_type"]=="expense") & (df["subcategory"] != "Rent/Mortgage") & (df["month_start"] < pd.Timestamp.today().to_period("M").to_timestamp())]
    avg_lifestyle = non_housing.groupby("month_start")["amount"].sum().tail(3).mean()
    total_housing = mortgage_repayment + RATES_AND_INSURANCE + MAINTENANCE_BUFFER
    final_surplus = verified_income - avg_lifestyle - total_housing - dca_active

    c1, c2, c3 = st.columns(3)
    c1.metric("Verified Income", fmt_money(verified_income))
    c2.metric("Avg Lifestyle Spend (3m)", fmt_money(avg_lifestyle))
    c3.metric("Net Monthly Surplus", fmt_money(final_surplus), delta="✅ Above $1k floor" if final_surplus > 1000 else "⚠️ Below $1k floor")

    fig = go.Figure(go.Indicator(mode="gauge+number", value=final_surplus, title={"text":"Post-Mortgage Surplus ($/mo)", "font":{"size":16,"color":THEME["text"]}}, gauge={"axis":{"range":[-500,2500],"tickwidth":1},"bar":{"color":THEME["blue"]},"steps":[{"range":[-500,0],"color":THEME["red"]},{"range":[0,1000],"color":THEME["orange"]},{"range":[1000,2500],"color":THEME["green"]}]}))
    apply_layout(fig, "", 300); st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    info_box("Fortress Rule Check", f"Fortress requires <b>&gt;$1,000/mo</b> unallocated surplus post-mortgage. Current projection: <b>{fmt_money(final_surplus)}</b>. DCA dial is the first lever.", THEME["purple"])


def render_waterfall(df, salary_net_monthly, mortgage_repayment):
    section_header("🏡", "§12 · Future State: Post-House Monthly Waterfall", "Income → mortgage → expenses → stocks → surplus · 3 scenarios")
    non_housing = df[(df["transaction_type"]=="expense") & (~df["subcategory"].isin({"Rent/Mortgage"})) & (df["month_start"] < pd.Timestamp.today().to_period("M").to_timestamp())]
    avg_lifestyle = round(non_housing.groupby("month_start")["amount"].sum().tail(3).mean(), 0)
    provisions = RATES_AND_INSURANCE + MAINTENANCE_BUFFER

    def build(income, mortgage, provisions, lifestyle, dca):
        post_mortgage = income - mortgage - provisions; post_lifestyle = post_mortgage - lifestyle; surplus = post_lifestyle - dca
        return [("Gross Net Income", income), ("— Mortgage Repayment", -mortgage), ("— Ownership Provisions", -provisions), ("→ Post-Housing Surplus", post_mortgage), ("— Lifestyle Expenses", -lifestyle), ("→ Pre-Investment Surplus", post_lifestyle), ("— Stock DCA Investment", -dca), ("★ TAKE-HOME SURPLUS", surplus)], surplus

    scenarios = {
        "Base (DCA $450/mo — Phase 2)": build(salary_net_monthly, mortgage_repayment, provisions, avg_lifestyle, 450),
        "Scaled Up (DCA $1,000/mo — Phase 3)": build(salary_net_monthly, mortgage_repayment, provisions, avg_lifestyle, 1000),
        "Stress (Income -8%, Expenses +8%, DCA $450)": build(salary_net_monthly*.92, mortgage_repayment, provisions, avg_lifestyle*1.08, 450),
    }
    summary = [{"Scenario":k.split("(")[0].strip(), "SURPLUS":v[1]} for k,v in scenarios.items()]
    fig_s = go.Figure(go.Bar(x=[r["Scenario"] for r in summary], y=[r["SURPLUS"] for r in summary], marker_color=[THEME["green"] if r["SURPLUS"]>1000 else THEME["orange"] if r["SURPLUS"]>0 else THEME["red"] for r in summary], text=[fmt_money(r["SURPLUS"]) for r in summary], textposition="outside"))
    fig_s.add_hline(y=1000, line_dash="dash", line_color=THEME["slate"], annotation_text="$1,000 safety floor")
    apply_layout(fig_s, "Take-Home Surplus by Scenario", 360); fig_s.update_yaxes(tickprefix="$", tickformat=",")
    st.plotly_chart(fig_s, use_container_width=True, config={"displayModeBar": False})

    for name, (steps, surplus) in scenarios.items():
        with st.expander(f"📊 {name} — Surplus: {fmt_money(surplus)}/mo", expanded=surplus<1000):
            labels = [s[0] for s in steps]; values = [s[1] for s in steps]
            measures = ["absolute" if i==0 else ("total" if "Surplus" in labels[i] or "★" in labels[i] else "relative") for i in range(len(labels))]
            fig_w = go.Figure(go.Waterfall(orientation="v", measure=measures, x=labels, y=values, connector={"line":{"color":THEME["grid"]}}, increasing={"marker":{"color":THEME["green"]}}, decreasing={"marker":{"color":THEME["red"]}}, totals={"marker":{"color":THEME["blue"]}}, text=[fmt_money(abs(v)) for v in values], textposition="outside"))
            apply_layout(fig_w, "", 460); fig_w.update_xaxes(tickangle=-20); fig_w.update_yaxes(tickprefix="$", tickformat=",")
            st.plotly_chart(fig_w, use_container_width=True, config={"displayModeBar": False})


def render_lvr(df, salary_net_monthly, dca_active):
    section_header("📐", "§13 · LVR & Rate Sensitivity Modeller", "Repayment changes across rates and loan sizes")
    def monthly_rep(principal, annual_rate, n=360):
        r = annual_rate / 12
        return principal * (r*(1+r)**n) / ((1+r)**n - 1)
    rates = [0.0565,0.0615,0.0665,0.0715,0.0765,0.0815]; loans = [600000,625000,650000,655000,680000]
    rows = []
    for rate in rates:
        row = {"Rate":f"{rate*100:.2f}%"}
        for loan in loans: row[f"${loan//1000}k"] = monthly_rep(loan, rate)
        rows.append(row)
    sens_df = pd.DataFrame(rows); fmt_cols = {col:"${:,.0f}" for col in sens_df.columns if col != "Rate"}
    st.dataframe(money_table(sens_df, fmt_cols), use_container_width=True)

    base_loan = 654885; rate_range = np.linspace(.04, .10, 60); repayments = [monthly_rep(base_loan, r) for r in rate_range]
    non_h_exp = df[(df["transaction_type"]=="expense") & (~df["subcategory"].isin({"Rent/Mortgage"})) & (df["month_start"] < pd.Timestamp.today().to_period("M").to_timestamp())]
    avg_ls = round(non_h_exp.groupby("month_start")["amount"].sum().tail(3).mean(), 0)
    max_afford = salary_net_monthly - avg_ls - dca_active - 1000
    fig = go.Figure(); fig.add_trace(go.Scatter(x=rate_range*100, y=repayments, mode="lines", name="Monthly repayment", line=dict(color=THEME["blue"], width=3)))
    fig.add_vline(x=6.65, line_dash="dash", line_color=THEME["gold2"], annotation_text="Current 6.65%")
    fig.add_hline(y=max_afford, line_dash="dot", line_color=THEME["red"], annotation_text=f"Max for $1k surplus ({fmt_money(max_afford)})")
    apply_layout(fig, f"Repayment vs Rate — Loan ${base_loan/1000:.0f}k", 420); fig.update_xaxes(title="Annual Rate (%)", ticksuffix="%"); fig.update_yaxes(title="Monthly Repayment ($)", tickprefix="$", tickformat=",")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
