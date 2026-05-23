import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from config import THEME, GOLD_SEQUENCE, section_header, info_box, apply_layout, fmt_money, money_table

EXCLUDE_SIGNALS = ("sell", "reduce", "avoid", "exit", "trim", "close")
INCLUDE_SIGNALS = ("buy", "hold", "accumulate", "core", "own", "owned", "keep")


def _find_col(df, names):
    for c in df.columns:
        cl = str(c).lower()
        if any(n in cl for n in names):
            return c
    return None


def _normalise_portfolio(raw):
    pf = raw.copy()
    mapping = {}
    for col in pf.columns:
        cl = str(col).lower()
        if "ticker" in cl or "symbol" in cl or cl == "code": mapping[col] = "ticker"
        elif "unit" in cl or "qty" in cl or "quantity" in cl or "shares" in cl: mapping[col] = "units"
        elif "avg" in cl or "average" in cl or "cost" in cl or "wacb" in cl: mapping[col] = "avg_cost_aud"
        elif "curr" in cl: mapping[col] = "currency"
        elif any(x in cl for x in ["signal","recommend","action","rating","decision","status"]): mapping[col] = "signal"
        elif "target" in cl and "price" in cl: mapping[col] = "target_price"
    pf = pf.rename(columns=mapping)
    if "ticker" not in pf.columns:
        return pd.DataFrame()
    pf["ticker"] = pf["ticker"].astype(str).str.strip()
    pf = pf[pf["ticker"].ne("") & pf["ticker"].str.lower().ne("nan")].copy()
    pf["units"] = pd.to_numeric(pf.get("units", 0), errors="coerce").fillna(0)
    pf["avg_cost_aud"] = pd.to_numeric(pf.get("avg_cost_aud", 0), errors="coerce").fillna(0)
    pf["currency"] = pf.get("currency", "AUD").astype(str).str.upper().str.strip() if "currency" in pf.columns else "AUD"
    pf["signal"] = pf.get("signal", "BUY").astype(str).str.lower().str.strip() if "signal" in pf.columns else "buy"
    pf["portfolio_include"] = ~pf["signal"].str.contains("|".join(EXCLUDE_SIGNALS), case=False, na=False)
    pf.loc[pf["units"].le(0), "portfolio_include"] = False
    return pf


def _fx_audusd():
    try:
        from forex_python.converter import CurrencyRates
        return CurrencyRates().get_rate("AUD", "USD")
    except Exception:
        return 0.645


def _live_price_aud(ticker, currency, fallback):
    try:
        import yfinance as yf
        lookup = ticker + ".AX" if currency == "AUD" and "." not in ticker else ticker
        data = yf.Ticker(lookup)
        price = data.info.get("regularMarketPrice") or data.fast_info.last_price
        return float(price) / _fx_audusd() if currency == "USD" else float(price)
    except Exception:
        return float(fallback or 0)


def render(raw_portfolio):
    section_header("📈", "§8-9 · Portfolio Performance + Technical Intelligence", "Data-driven holdings only · sell/reduce rows excluded from totals and allocation")
    if raw_portfolio.empty:
        info_box("Portfolio Data Unavailable", "Add a 'Portfolio' sheet with ticker/symbol, units, avg cost, currency, and optional signal/action/recommendation columns.", THEME["slate"])
        return
    try:
        pf = _normalise_portfolio(raw_portfolio)
        if pf.empty:
            info_box("Portfolio sheet found, but no ticker column detected", "Use a column like ticker, symbol, or code.", THEME["orange"])
            return
        excluded = pf[~pf["portfolio_include"]].copy()
        active_pf = pf[pf["portfolio_include"]].copy()
        if active_pf.empty:
            info_box("No active holdings to total", "Rows marked sell/reduce/avoid/exit/trim, or rows with zero units, were excluded from portfolio totals.", THEME["orange"])
            if not excluded.empty:
                st.dataframe(excluded[[c for c in ["ticker","signal","units","avg_cost_aud"] if c in excluded.columns]], use_container_width=True)
            return

        holdings = []
        for _, row in active_pf.iterrows():
            ticker = str(row["ticker"]).strip(); units = float(row["units"]); avg_cst = float(row["avg_cost_aud"]); curr = str(row.get("currency","AUD")).upper()
            price_aud = _live_price_aud(ticker, curr, avg_cst)
            cost_aud = units * avg_cst; market_v = units * price_aud
            holdings.append({"ticker":ticker,"signal":row.get("signal","buy"),"units":units,"avg_cost_aud":avg_cst,"last_price_aud":price_aud,"cost_aud":cost_aud,"market_value_aud":market_v,"gain_aud":market_v-cost_aud,"gain_pct":((market_v-cost_aud)/cost_aud*100 if cost_aud else 0)})
        holdings_df = pd.DataFrame(holdings)
        total_mv = holdings_df["market_value_aud"].sum(); total_cost = holdings_df["cost_aud"].sum()
        holdings_df["weight_pct"] = np.where(total_mv > 0, holdings_df["market_value_aud"] / total_mv * 100, 0)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Included Portfolio Value", fmt_money(total_mv))
        c2.metric("Included Cost Base", fmt_money(total_cost))
        c3.metric("Unrealised Gain", fmt_money(total_mv-total_cost))
        c4.metric("ROI", f"{((total_mv-total_cost)/total_cost*100 if total_cost else 0):.1f}%")

        if not excluded.empty:
            info_box("Sell/reduce rows excluded", f"Excluded from totals/graphs: <b>{', '.join(excluded['ticker'].astype(str).tolist())}</b>. This is driven by the Portfolio sheet signal/action/recommendation/status column, not hardcoded.", THEME["orange"])

        left, right = st.columns(2)
        with left:
            fig = px.pie(holdings_df, names="ticker", values="market_value_aud", hole=.58, color_discrete_sequence=GOLD_SEQUENCE)
            apply_layout(fig, "Active Portfolio Allocation", 360); st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        with right:
            fig2 = px.bar(holdings_df.sort_values("gain_aud"), x="gain_aud", y="ticker", orientation="h", color="gain_aud", color_continuous_scale=[[0,THEME["red"]],[.5,THEME["gold"]],[1,THEME["green"]]])
            apply_layout(fig2, "Unrealised Gain/Loss by Included Ticker", 360); fig2.update_xaxes(tickprefix="$", tickformat=",")
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        st.dataframe(money_table(holdings_df.set_index("ticker")[["units","avg_cost_aud","last_price_aud","cost_aud","market_value_aud","gain_aud","gain_pct","weight_pct"]], {"units":"{:,.2f}","avg_cost_aud":"${:,.2f}","last_price_aud":"${:,.2f}","cost_aud":"${:,.0f}","market_value_aud":"${:,.0f}","gain_aud":"${:+,.0f}","gain_pct":"{:+.1f}%","weight_pct":"{:.1f}%"}), use_container_width=True)

        section_header("🔍", "§9 · Technical Intelligence", "Moving-average value gap + RSI(14) — calculated from included active rows")
        tech_results = []
        try:
            import yfinance as yf
            for _, row in holdings_df.iterrows():
                ticker = row["ticker"]; lookup = ticker + ".AX" if "." not in ticker else ticker
                hist = yf.download(lookup, period="18mo", interval="1d", progress=False, auto_adjust=True)
                if hist.empty or len(hist) < 14: continue
                if isinstance(hist.columns, pd.MultiIndex): hist.columns = hist.columns.get_level_values(0)
                close = hist["Close"].squeeze().dropna(); price = float(close.iloc[-1])
                if len(close) >= 200: sma = float(close.rolling(200).mean().iloc[-1]); label = "200-DMA"
                elif len(close) >= 50: sma = float(close.rolling(50).mean().iloc[-1]); label = "50-DMA*"
                else: sma = float(close.mean()); label = "Mean*"
                gap = (price - sma) / sma * 100
                delta = close.diff(); gain = delta.clip(lower=0).rolling(14).mean(); loss = (-delta.clip(upper=0)).rolling(14).mean()
                lg, ll = float(gain.iloc[-1]), float(loss.iloc[-1]); rsi = 100.0 if ll == 0 and lg > 0 else (50.0 if ll == 0 else float(100-(100/(1+lg/ll))))
                signal = "Overbought" if rsi >= 70 else "Oversold" if rsi <= 30 else "Neutral"
                tech_results.append({"ticker":ticker,"price":price,"sma":sma,"sma_label":label,"value_gap":gap,"rsi_14":rsi,"rsi_signal":signal})
        except ImportError:
            info_box("yfinance not available", "Add `yfinance` to requirements.txt for live technical charts.", THEME["orange"])

        if tech_results:
            tech_df = pd.DataFrame(tech_results).sort_values("value_gap")
            colors = [THEME["green"] if x < 0 else THEME["blue"] for x in tech_df["value_gap"]]
            fig_t = go.Figure(go.Bar(x=tech_df["ticker"], y=tech_df["value_gap"], marker_color=colors, text=tech_df["value_gap"].apply(lambda x:f"{x:+.1f}%"), textposition="outside"))
            fig_t.add_hline(y=0, line_color=THEME["text"], line_width=2)
            fig_t.add_hrect(y0=-25, y1=0, fillcolor=THEME["green"], opacity=.08, annotation_text="VALUE ZONE")
            apply_layout(fig_t, "Value Gap from Moving Average", 400); fig_t.update_yaxes(ticksuffix="%")
            st.plotly_chart(fig_t, use_container_width=True, config={"displayModeBar": False})

            rsi_colors = [THEME["red"] if r>=70 else THEME["green"] if r<=30 else THEME["blue"] for r in tech_df["rsi_14"]]
            fig_r = go.Figure(go.Bar(x=tech_df["ticker"], y=tech_df["rsi_14"], marker_color=rsi_colors, text=tech_df["rsi_14"].apply(lambda x:f"{x:.0f}"), textposition="outside"))
            fig_r.add_hline(y=70, line_dash="dash", line_color=THEME["red"], annotation_text="Overbought")
            fig_r.add_hline(y=30, line_dash="dash", line_color=THEME["green"], annotation_text="Oversold")
            apply_layout(fig_r, "RSI(14) Momentum Signal", 360); fig_r.update_yaxes(range=[0,100])
            st.plotly_chart(fig_r, use_container_width=True, config={"displayModeBar": False})

            deepest = tech_df.iloc[0]
            if deepest["value_gap"] < -5:
                info_box("🔔 Golden Override Candidate", f"<b>{deepest['ticker']}</b> is {deepest['value_gap']:+.1f}% below its moving average. RSI: {deepest['rsi_14']:.0f} ({deepest['rsi_signal']}).", THEME["purple"])
        else:
            info_box("Technical data unavailable", "Portfolio totals still work. Live technical charts require internet access from Streamlit Cloud plus yfinance.", THEME["orange"])
    except Exception as e:
        info_box("Portfolio Error", str(e), THEME["red"])
