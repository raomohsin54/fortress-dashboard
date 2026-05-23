"""Standalone printable HTML report export for Fortress.

This avoids Streamlit/browser print limitations by creating a normal HTML file
with static Plotly charts, page breaks, and explanations.
"""
from __future__ import annotations

import html
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.io import to_html

from config import GOLD_SEQUENCE, THEME, apply_layout, fmt_money, pct

SELL_WORDS = ("sell", "reduce", "avoid", "exit", "trim", "close", "closed")


def _chart_html(fig: go.Figure, title: str = "", height: int = 420) -> str:
    apply_layout(fig, title, height)
    fig.update_layout(width=None, autosize=True)
    return to_html(fig, include_plotlyjs=False, full_html=False, config={"displayModeBar": False, "responsive": True})


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def _money(value: Any) -> str:
    return _esc(fmt_money(value))


def _metric(label: str, value: Any, note: str = "") -> str:
    return f"""
    <div class="metric-card">
      <div class="metric-label">{_esc(label)}</div>
      <div class="metric-value">{_esc(value)}</div>
      <div class="metric-note">{_esc(note)}</div>
    </div>
    """


def _section(title: str, subtitle: str, body: str, page_break: bool = True) -> str:
    page_class = " page-break" if page_break else ""
    return f"""
    <section class="report-section{page_class}">
      <div class="section-title">{_esc(title)}</div>
      <div class="section-subtitle">{_esc(subtitle)}</div>
      {body}
    </section>
    """


def _note(title: str, text: str) -> str:
    return f"""
    <div class="chart-note">
      <b>{_esc(title)}</b><br>
      <span>{_esc(text)}</span>
    </div>
    """


def _table(df: pd.DataFrame, max_rows: int = 18) -> str:
    if df is None or df.empty:
        return "<div class='empty'>No table data available.</div>"
    shown = df.head(max_rows).copy()
    for col in shown.columns:
        if pd.api.types.is_numeric_dtype(shown[col]):
            shown[col] = shown[col].map(lambda x: f"${x:,.0f}" if abs(float(x)) > 20 else f"{x:,.1f}")
    return shown.to_html(index=False, classes="report-table", border=0, escape=True)


def _portfolio_frame(raw_portfolio: pd.DataFrame) -> pd.DataFrame:
    if raw_portfolio is None or raw_portfolio.empty:
        return pd.DataFrame()
    pf = raw_portfolio.copy()
    col_map = {}
    for col in pf.columns:
        cl = str(col).lower()
        if "ticker" in cl or "symbol" in cl:
            col_map[col] = "ticker"
        elif "unit" in cl or "qty" in cl or "shares" in cl:
            col_map[col] = "units"
        elif "cost" in cl or "avg" in cl or "price" in cl:
            col_map[col] = "avg_cost_aud"
        elif "curr" in cl:
            col_map[col] = "currency"
        elif any(word in cl for word in ["signal", "action", "recommend", "status", "decision", "stance"]):
            col_map[col] = "signal"
    pf = pf.rename(columns=col_map)
    if "ticker" not in pf.columns:
        return pd.DataFrame()
    pf["ticker"] = pf["ticker"].astype(str).str.strip()
    pf["units"] = pd.to_numeric(pf.get("units", 0), errors="coerce").fillna(0)
    pf["avg_cost_aud"] = pd.to_numeric(pf.get("avg_cost_aud", 0), errors="coerce").fillna(0)
    signal = pf.get("signal", pd.Series([""] * len(pf), index=pf.index)).astype(str).str.lower()
    pf["include_in_portfolio"] = (pf["units"] > 0) & ~signal.apply(lambda x: any(w in x for w in SELL_WORDS))
    pf["cost_aud"] = pf["units"] * pf["avg_cost_aud"]
    # Static report avoids live price dependency. This is intentionally marked as cost-based if no market value column exists.
    market_cols = [c for c in pf.columns if any(k in str(c).lower() for k in ["market", "value", "current_value"])]
    if market_cols:
        pf["report_value_aud"] = pd.to_numeric(pf[market_cols[0]], errors="coerce").fillna(pf["cost_aud"])
        pf["valuation_basis"] = "Workbook market value"
    else:
        pf["report_value_aud"] = pf["cost_aud"]
        pf["valuation_basis"] = "Cost basis only"
    return pf


def build_report_html(
    df: pd.DataFrame,
    monthly: pd.DataFrame,
    cat_month: pd.DataFrame,
    raw_portfolio: pd.DataFrame,
    *,
    total_liquid_cash: float,
    salary_net_monthly: float,
    purchase_price: float,
    mortgage_repayment: float,
    start_portfolio_value: float,
    dca_active: float,
    report_as_of: pd.Timestamp,
) -> str:
    monthly_12m = monthly.sort_values("month_start").tail(12).copy()
    latest = monthly_12m.iloc[-1]
    prior = monthly_12m.iloc[-2] if len(monthly_12m) > 1 else latest

    sections: list[str] = []
    hero_metrics = "".join([
        _metric("Latest income", fmt_money(latest["income"]), f"Change: {fmt_money(latest['income'] - prior['income'])}"),
        _metric("Latest expenses", fmt_money(latest["expense"]), f"Change: {fmt_money(latest['expense'] - prior['expense'])}"),
        _metric("Savings rate", pct(latest["savings_rate"]), "Income minus expenses"),
        _metric("Liquid cash", fmt_money(total_liquid_cash), "Sidebar input"),
    ])

    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly_12m["Month_Label"], y=monthly_12m["income"], name="Income", marker_color=THEME["green"]))
    fig.add_trace(go.Bar(x=monthly_12m["Month_Label"], y=monthly_12m["expense"], name="Expense", marker_color=THEME["red"]))
    fig.add_trace(go.Scatter(x=monthly_12m["Month_Label"], y=monthly_12m["savings_3m_avg"], name="Savings 3m avg", mode="lines+markers", line=dict(color=THEME["gold"], width=3)))
    cash_body = f"<div class='metrics'>{hero_metrics}</div>{_chart_html(fig, 'Monthly Income vs Expense — 12 Months', 430)}"
    cash_body += _note("Explanation", "This shows whether income is consistently covering expenses. The gold line smooths savings using a 3-month average so one-off spikes do not dominate the trend.")
    sections.append(_section("§1-2 Cash Flow Engine", "Income, expenses, savings and trend quality", cash_body, page_break=False))

    latest_cat = df[(df["transaction_type"] == "expense") & (df["month_start"] == latest["month_start"])].groupby("category", as_index=False)["amount"].sum().rename(columns={"amount": "latest"})
    avg_cat = cat_month[cat_month["month_start"] < latest["month_start"]].groupby("category", as_index=False)["amount"].mean().rename(columns={"amount": "avg_12m"})
    cat_compare = latest_cat.merge(avg_cat, on="category", how="left").sort_values("latest", ascending=False)
    fig = go.Figure()
    fig.add_trace(go.Bar(y=cat_compare["category"], x=cat_compare["avg_12m"], orientation="h", name="12m Avg", marker_color=THEME["slate"]))
    fig.add_trace(go.Bar(y=cat_compare["category"], x=cat_compare["latest"], orientation="h", name="Latest", marker_color=THEME["blue"]))
    fig.update_layout(barmode="overlay")
    spend_body = _chart_html(fig, "Category Spend: Latest vs Average", max(380, len(cat_compare) * 44))
    spend_body += _note("Explanation", "This highlights categories where the latest month is above or below normal run-rate. Big gaps deserve review before blaming the whole budget.")
    sections.append(_section("§3 Spend Analysis", "Category benchmarking and lifestyle creep detection", spend_body))

    cat_total = df[df["transaction_type"] == "expense"].groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
    if not cat_total.empty:
        cat_total["share_pct"] = cat_total["amount"] / cat_total["amount"].sum() * 100
        fig = px.bar(cat_total.head(10), x="category", y="share_pct", text=cat_total.head(10)["share_pct"].map(lambda x: f"{x:.1f}%"), color="share_pct", color_continuous_scale=[[0, "#172033"], [0.6, THEME["gold"]], [1, THEME["gold2"]]])
        anomaly_body = _chart_html(fig, "Expense Concentration — Top Categories", 410)
        anomaly_body += _note("Explanation", "This shows which spending categories dominate total expenses. If one category takes too much share, small improvements there can have a large cash-flow impact.")
    else:
        anomaly_body = "<div class='empty'>No expense data found.</div>"
    sections.append(_section("§4-7 Anomaly and Forecast", "Concentration, risk and forward run-rate", anomaly_body))

    pf = _portfolio_frame(raw_portfolio)
    if pf.empty:
        portfolio_body = "<div class='empty'>No Portfolio sheet found or ticker column unavailable.</div>"
    else:
        active_pf = pf[pf["include_in_portfolio"]].copy()
        excluded = pf[~pf["include_in_portfolio"]].copy()
        if active_pf.empty:
            portfolio_body = "<div class='empty'>No active buy/hold portfolio rows found after excluding sell/reduce/avoid/exit rows.</div>"
        else:
            total_value = active_pf["report_value_aud"].sum()
            active_pf["weight_pct"] = np.where(total_value > 0, active_pf["report_value_aud"] / total_value * 100, 0)
            metrics = "".join([
                _metric("Included portfolio value", fmt_money(total_value), "Excludes sell/reduce/avoid/exit rows"),
                _metric("Included tickers", len(active_pf), "Buy/hold rows only"),
                _metric("Excluded rows", len(excluded), "Not counted in totals"),
            ])
            fig1 = px.pie(active_pf, names="ticker", values="report_value_aud", hole=0.55, color_discrete_sequence=GOLD_SEQUENCE)
            fig2 = px.bar(active_pf.sort_values("weight_pct"), x="weight_pct", y="ticker", orientation="h", color="weight_pct", color_continuous_scale=[[0, THEME["blue"]], [1, THEME["gold2"]]])
            portfolio_body = f"<div class='metrics'>{metrics}</div>"
            portfolio_body += _chart_html(fig1, "Active Portfolio Allocation", 390)
            portfolio_body += _note("Explanation", "This allocation chart only includes rows treated as active holdings. Sell/reduce/avoid/exit/trim rows are shown as excluded and do not inflate the portfolio total.")
            portfolio_body += _chart_html(fig2, "Active Holding Weights", 390)
            portfolio_body += _table(active_pf[["ticker", "units", "avg_cost_aud", "report_value_aud", "weight_pct", "valuation_basis"]])
            if not excluded.empty:
                portfolio_body += "<h3>Excluded from portfolio totals</h3>" + _table(excluded[[c for c in ["ticker", "units", "avg_cost_aud", "signal"] if c in excluded.columns]])
    sections.append(_section("§8-9 Portfolio Performance + Technical Intelligence", "Active holdings only; sell/reduce rows excluded", portfolio_body))

    non_housing = df[(df["transaction_type"] == "expense") & (~df["subcategory"].isin({"Rent/Mortgage"}))]
    avg_lifestyle = non_housing.groupby("month_start")["amount"].sum().tail(3).mean() if not non_housing.empty else 0
    total_housing = mortgage_repayment + 800
    final_surplus = salary_net_monthly - avg_lifestyle - total_housing - dca_active
    stress_metrics = "".join([
        _metric("Net income", fmt_money(salary_net_monthly), "Sidebar input"),
        _metric("Lifestyle avg", fmt_money(avg_lifestyle), "Last 3 non-rent months"),
        _metric("Mortgage + ownership", fmt_money(total_housing), "Repayment + provisions"),
        _metric("Final surplus", fmt_money(final_surplus), "After active DCA"),
    ])
    fig = go.Figure(go.Indicator(mode="gauge+number", value=final_surplus, title={"text": "Post-Mortgage Surplus"}, gauge={"axis": {"range": [-500, 3000]}, "steps": [{"range": [-500, 0], "color": THEME["red"]}, {"range": [0, 1000], "color": THEME["orange"]}, {"range": [1000, 3000], "color": THEME["green"]}], "bar": {"color": THEME["blue"]}}))
    mortgage_body = f"<div class='metrics'>{stress_metrics}</div>{_chart_html(fig, 'Surplus Stress Gauge', 360)}"
    mortgage_body += _note("Explanation", "Fortress safety rule is to keep at least $1,000 per month unallocated after mortgage, lifestyle costs and DCA. If this falls below the floor, DCA is the first dial to reduce.")
    sections.append(_section("§11-13 Mortgage and Readiness", "Post-house stress testing and safety floor", mortgage_body))

    deposit_target, emergency_target, buffer_target = 130000, 30000, 8000
    total_targets = deposit_target + emergency_target + buffer_target
    readiness_pct = min(100, total_liquid_cash / total_targets * 100) if total_targets else 0
    ready_body = "<div class='metrics'>" + "".join([
        _metric("Readiness", f"{readiness_pct:.0f}%", "Deposit + emergency + buffer"),
        _metric("Target cash", fmt_money(total_targets), "Fortress bucket target"),
        _metric("Purchase price", fmt_money(purchase_price), "Sidebar input"),
        _metric("Starting portfolio", fmt_money(start_portfolio_value), "DCA model input"),
    ]) + "</div>"
    ready_body += _note("Explanation", "This section translates the cash balance into purchase readiness. A high cash balance is only safe if deposit, emergency fund and moving/buffer buckets are all protected.")
    sections.append(_section("§14-15 Purchase Readiness + DCA", "Cash buckets and long-term investing trajectory", ready_body))

    generated = datetime.now().strftime("%d %b %Y %H:%M")
    html_doc = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fortress Printable Report</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  @page {{ size: A4 landscape; margin: 10mm; }}
  * {{ box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  body {{ margin: 0; background: #05060A; color: #F8FAFC; font-family: Inter, Segoe UI, Arial, sans-serif; }}
  .report-wrap {{ max-width: 1220px; margin: 0 auto; padding: 28px; }}
  .hero {{ border: 1px solid rgba(242,201,76,.35); border-radius: 24px; padding: 28px; background: linear-gradient(135deg,#111827,#05060A 65%,rgba(242,201,76,.12)); margin-bottom: 24px; }}
  .hero h1 {{ margin: 0; font-size: 30px; color: #FFE08A; }}
  .hero p {{ color: #CBD5E1; margin: 8px 0 0; }}
  .report-section {{ border: 1px solid rgba(242,201,76,.25); border-radius: 22px; padding: 22px; margin: 22px 0; background: #0B0F17; break-inside: avoid; page-break-inside: avoid; }}
  .page-break {{ break-before: page; page-break-before: always; }}
  .section-title {{ font-size: 22px; font-weight: 900; color: #FFE08A; margin-bottom: 4px; }}
  .section-subtitle {{ font-size: 13px; color: #CBD5E1; margin-bottom: 16px; }}
  .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 12px 0 18px; }}
  .metric-card {{ background: #101621; border: 1px solid rgba(242,201,76,.25); border-radius: 16px; padding: 14px; }}
  .metric-label {{ color: #CBD5E1; font-size: 12px; font-weight: 800; }}
  .metric-value {{ color: #F2C94C; font-size: 22px; font-weight: 950; margin-top: 6px; }}
  .metric-note {{ color: #94A3B8; font-size: 11px; margin-top: 4px; }}
  .chart-note {{ border-left: 5px solid #F2C94C; background: rgba(242,201,76,.08); border-radius: 12px; padding: 12px 14px; margin: 12px 0 18px; color: #CBD5E1; line-height: 1.5; }}
  .chart-note b {{ color: #F8FAFC; }}
  .report-table {{ width: 100%; border-collapse: collapse; margin-top: 14px; font-size: 12px; }}
  .report-table th {{ background: #151B2A; color: #FFE08A; text-align: left; padding: 9px; border: 1px solid #2B3346; }}
  .report-table td {{ padding: 8px; border: 1px solid #2B3346; color: #F8FAFC; }}
  .empty {{ padding: 18px; border: 1px dashed #64748B; border-radius: 14px; color: #CBD5E1; }}
  @media print {{
    body {{ background: #05060A !important; }}
    .report-wrap {{ max-width: none; padding: 0; }}
    .report-section {{ box-shadow: none; }}
  }}
  @media (max-width: 800px) {{
    .report-wrap {{ padding: 12px; }}
    .metrics {{ grid-template-columns: 1fr; }}
    .hero h1 {{ font-size: 23px; }}
  }}
</style>
</head>
<body>
  <div class="report-wrap">
    <div class="hero">
      <h1>💼 Fortress Financial Intelligence — Printable Report</h1>
      <p>Generated {generated} · Reporting through {_esc(report_as_of.strftime('%B %Y'))} · Save this HTML as PDF from your browser.</p>
      <p><b>Print settings:</b> Ctrl/Cmd+P → Save as PDF → Landscape → Background graphics ON.</p>
    </div>
    {''.join(sections)}
  </div>
</body>
</html>"""
    return html_doc
