import pandas as pd
import streamlit as st
import plotly.express as px
from config import THEME, GOLD_SEQUENCE, section_header, info_box, apply_layout, fmt_money


def render_action(df, monthly_12m, latest_month, salary_net_monthly, mortgage_repayment, dca_active):
    section_header("✅", "§10 · Strategic Action Board", "Turn the analysis into concrete priorities")
    actions = []
    avg_sr = monthly_12m["savings_rate"].mean()
    if latest_month["savings_rate"] < avg_sr:
        actions.append(("Lift monthly surplus", f"Latest savings rate is {latest_month['savings_rate']:.1f}% vs 12m average {avg_sr:.1f}%."))
    portable_latest = df[(df["transaction_type"]=="expense") & (~df["subcategory"].isin({"Rent/Mortgage"})) & (df["month_start"]==latest_month["month_start"] )]["amount"].sum()
    if portable_latest > 5000:
        actions.append(("Review portable spend", f"Lifestyle spend excluding rent hit {fmt_money(portable_latest)} this month."))
    run_surplus = salary_net_monthly - portable_latest - mortgage_repayment - dca_active
    if run_surplus < 1000:
        actions.append(("⚠️ Surplus below $1,000 floor", f"Post-mortgage surplus is {fmt_money(run_surplus)}. Consider reducing DCA before touching emergency funds."))
    if not actions:
        actions.append(("Maintain course", "All tracked metrics are inside the target range. Keep DCA consistency."))
    for title, why in actions:
        st.markdown(f"""<div class='fortress-box' style='border-left:4px solid {THEME['blue']};'><div style='font-weight:800;color:{THEME['text']};'>{title}</div><div style='color:{THEME['muted']};font-size:13px;margin-top:4px;'>{why}</div></div>""", unsafe_allow_html=True)


def render_readiness(total_liquid_cash, purchase_price, mortgage_repayment):
    section_header("🎯", "§14 · Home Purchase Readiness Tracker", "Deposit, emergency fund, buffer, and settlement runway")
    deposit_target = 130000; emergency_target = 30000; buffer_target = 8000; total_targets = deposit_target + emergency_target + buffer_target; wa_stamp_duty = 27855
    deposit_current = min(total_liquid_cash, deposit_target); rem1 = max(0, total_liquid_cash - deposit_current)
    emergency_current = min(rem1, emergency_target); rem2 = max(0, rem1 - emergency_current)
    buffer_current = min(rem2, buffer_target); unallocated = max(0, rem2 - buffer_current)
    total_gap = max(0, deposit_target-deposit_current) + max(0, emergency_target-emergency_current) + max(0, buffer_target-buffer_current)
    readiness_pct = min(100, total_liquid_cash / total_targets * 100)
    banner_color = THEME["green"] if readiness_pct >= 100 else THEME["yellow"] if readiness_pct >= 80 else THEME["red"]
    st.markdown(f"""<div class='fortress-box' style='border-left:6px solid {banner_color};'><div style='font-size:22px;font-weight:900;color:{THEME['text']};'>Overall Readiness: {readiness_pct:.0f}% · Cash: <span style='color:{THEME['blue']};'>{fmt_money(total_liquid_cash)}</span> · Target: <span style='color:{THEME['muted']};'>{fmt_money(total_targets)}</span> {' · <span style="color:'+THEME['green']+';">✅ All buckets funded</span>' if total_gap == 0 else ' · <span style="color:'+THEME['red']+';">Still need: '+fmt_money(total_gap)+'</span>'}</div></div>""", unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        for label, current, target, color in [("Deposit + Stamp Duty", deposit_current, deposit_target, THEME["blue"]),("Emergency Fund", emergency_current, emergency_target, THEME["green"]),("Moving/Baby/Buffer", buffer_current, buffer_target, THEME["orange"] )]:
            fill = min(100, current/target*100)
            st.markdown(f"""<div style='margin:11px 0;'><div style='display:flex;justify-content:space-between;color:{THEME['text']};font-size:13px;margin-bottom:5px;'><span>{label}</span><span>{fmt_money(current)} / {fmt_money(target)} ({fill:.0f}%)</span></div><div style='background:#1E293B;border-radius:8px;height:18px;overflow:hidden;'><div style='width:{fill}%;background:{color};height:100%;border-radius:8px;'></div></div></div>""", unsafe_allow_html=True)
    with right:
        pie_data = pd.DataFrame({"Bucket":["Deposit Pool","Emergency Fund","Buffer","Unallocated"],"Amount":[deposit_current, emergency_current, buffer_current, unallocated]}).query("Amount > 0")
        fig = px.pie(pie_data, names="Bucket", values="Amount", hole=.58, color_discrete_sequence=GOLD_SEQUENCE)
        apply_layout(fig, f"Capital Allocation — {fmt_money(total_liquid_cash)}", 360); st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    cov_months = emergency_current / mortgage_repayment if mortgage_repayment else 0
    info_box("Emergency Fund Coverage", f"{fmt_money(emergency_current)} covers <b>{cov_months:.1f} months</b> of {fmt_money(mortgage_repayment)}/mo mortgage. Fortress floor: 7+ months.", THEME["green"] if cov_months >= 7 else THEME["orange"])
    net_dep = deposit_current - wa_stamp_duty; lvr = (purchase_price - net_dep) / purchase_price * 100 if purchase_price else 0
    info_box("LVR Check", f"Deposit pool <b>{fmt_money(deposit_current)}</b> minus WA stamp duty <b>{fmt_money(wa_stamp_duty)}</b> = net deposit <b>{fmt_money(net_dep)}</b>. On {fmt_money(purchase_price)} purchase: LVR = <b>{lvr:.1f}%</b>.", THEME["green"] if lvr < 90 else THEME["red"])
