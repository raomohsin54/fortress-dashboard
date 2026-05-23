import streamlit as st
import pandas as pd

THEME = {
    "bg":"#05060A","panel":"#0B0F17","panel2":"#111827","card":"#101621","card2":"#151B2A",
    "grid":"#2B3346","text":"#F8FAFC","muted":"#CBD5E1","soft":"#94A3B8",
    "gold":"#F2C94C","gold2":"#FFE08A","green":"#34D399","red":"#FB7185",
    "orange":"#FDBA74","yellow":"#FDE68A","blue":"#60A5FA","purple":"#C084FC",
    "teal":"#2DD4BF","pink":"#F472B6","slate":"#64748B"
}
GOLD_SEQUENCE = ["#F2C94C","#FFE08A","#D4AF37","#60A5FA","#34D399","#C084FC","#FDBA74","#2DD4BF","#FB7185","#A78BFA"]
STATUS_COLORS = [THEME["green"], THEME["gold"], THEME["orange"], THEME["red"], THEME["blue"], THEME["purple"]]

PAGE_TITLE = "Fortress Financial Intelligence"
PAGE_ICON = "💼"


def fmt_money(x):
    try:
        return f"${float(x):,.0f}"
    except Exception:
        return str(x)


def pct(x):
    try:
        return f"{float(x):.1f}%"
    except Exception:
        return str(x)


def latest_n(arr, n=12):
    return arr.sort_values("month_start").tail(n).copy()


def inject_theme():
    st.markdown(f"""
<style>
:root {{
  --bg:{THEME['bg']}; --panel:{THEME['panel']}; --panel2:{THEME['panel2']}; --card:{THEME['card']};
  --text:{THEME['text']}; --muted:{THEME['muted']}; --soft:{THEME['soft']}; --gold:{THEME['gold']}; --grid:{THEME['grid']};
}}
html, body, .stApp {{
  background: radial-gradient(circle at 12% 0%, rgba(242,201,76,.18) 0%, rgba(11,15,23,.98) 32%, #05060A 100%) !important;
  color: var(--text) !important;
}}
.block-container {{ padding: 1rem 1.2rem 2rem; max-width: 1500px; }}
section[data-testid="stSidebar"] {{ background: linear-gradient(180deg,#090D14,#05060A) !important; border-right: 1px solid rgba(242,201,76,.22); }}
section[data-testid="stSidebar"] * {{ color: var(--text) !important; }}
h1,h2,h3,h4,h5,h6,p,span,label,div {{ color: inherit; }}
div[data-testid="metric-container"] {{
  background: linear-gradient(145deg, rgba(21,27,42,.98), rgba(11,15,23,.96)) !important;
  border: 1px solid rgba(242,201,76,.28) !important; border-radius: 18px; padding: 15px 16px;
  box-shadow: 0 14px 36px rgba(0,0,0,.34), inset 0 1px 0 rgba(255,255,255,.04);
}}
div[data-testid="metric-container"] label {{ color: var(--muted) !important; font-weight: 700 !important; }}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{ color: var(--gold) !important; font-size: clamp(1.25rem, 3.4vw, 1.7rem) !important; font-weight: 900 !important; }}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {{ color: var(--muted) !important; }}
.stPlotlyChart {{ background: linear-gradient(145deg,#0B0F17,#101621); border: 1px solid rgba(242,201,76,.22); border-radius: 18px; padding: 8px; box-shadow: 0 14px 38px rgba(0,0,0,.28); }}
.stDataFrame, div[data-testid="stDataFrame"] {{ background:#0B0F17 !important; border:1px solid rgba(242,201,76,.22); border-radius:16px; padding:6px; }}
.stAlert {{ background-color:#101621 !important; color:var(--text) !important; border:1px solid rgba(242,201,76,.25) !important; }}
button, .stButton button {{ background:#151B2A !important; color:var(--gold) !important; border:1px solid rgba(242,201,76,.55) !important; border-radius:12px !important; }}
input, textarea, select {{ color:var(--text) !important; background-color:#101621 !important; }}
[data-baseweb="radio"] div, [data-baseweb="checkbox"] div {{ color:var(--text) !important; }}
hr {{ border-color: rgba(242,201,76,.20); }}
#MainMenu, footer, header {{ visibility:hidden; }}
.fortress-hero {{ padding: 28px 32px; margin-bottom: 20px; border:1px solid rgba(242,201,76,.26); border-radius: 24px; background: linear-gradient(135deg,rgba(17,24,39,.94),rgba(5,6,10,.96) 62%,rgba(242,201,76,.10)); box-shadow: 0 22px 55px rgba(0,0,0,.33); }}
.fortress-kpis {{ display:grid; grid-template-columns:repeat(3,1fr); gap:10px; font-size:12px; color:var(--muted); }}
.fortress-section {{ margin:24px 0 12px; padding:18px 20px; border:1px solid rgba(242,201,76,.23); border-radius:18px; background:linear-gradient(135deg,#101621,#0B0F17); box-shadow:0 12px 32px rgba(0,0,0,.22); }}
.fortress-box {{ margin:10px 0 16px; padding:14px 16px; background:#101621; border-radius:14px; }}
@media (max-width: 768px) {{
  .block-container {{ padding-left:.65rem; padding-right:.65rem; }}
  .fortress-hero {{ padding:20px 16px; border-radius:18px; }}
  .fortress-hero h1 {{ font-size:1.35rem !important; }}
  .fortress-kpis {{ grid-template-columns:1fr; }}
  .fortress-section {{ padding:15px 14px; border-radius:16px; }}
  .stPlotlyChart {{ padding:4px; }}
}}
</style>
""", unsafe_allow_html=True)


def section_header(icon, title, subtitle):
    st.markdown(f"""
    <div class="fortress-section">
      <div style="display:flex;align-items:center;gap:12px;">
        <div style="font-size:28px;">{icon}</div>
        <div>
          <div style="font-size:20px;font-weight:850;color:{THEME['text']};">{title}</div>
          <div style="font-size:13px;color:{THEME['muted']};margin-top:3px;">{subtitle}</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)


def info_box(title, body, accent=None):
    accent = accent or THEME["blue"]
    st.markdown(f"""
    <div class="fortress-box" style="border-left:5px solid {accent};">
      <div style="font-weight:800;margin-bottom:6px;color:{THEME['text']};">{title}</div>
      <div style="color:{THEME['muted']};line-height:1.55;">{body}</div>
    </div>""", unsafe_allow_html=True)


def apply_layout(fig, title="", height=420):
    fig.update_layout(
        title=dict(text=title, x=0.01, font=dict(size=17, color=THEME["gold2"], family="Arial Black")),
        paper_bgcolor=THEME["panel"], plot_bgcolor=THEME["panel"], font=dict(color=THEME["text"], size=12),
        xaxis=dict(showgrid=False, color=THEME["muted"], linecolor=THEME["grid"], tickfont=dict(color=THEME["text"])),
        yaxis=dict(showgrid=True, gridcolor=THEME["grid"], zeroline=False, color=THEME["muted"], tickfont=dict(color=THEME["text"])),
        margin=dict(l=35, r=25, t=58, b=35), hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, font=dict(color=THEME["text"])), height=height,
    )
    fig.update_layout(scene=dict(bgcolor=THEME["panel"], xaxis=dict(backgroundcolor=THEME["panel"], gridcolor=THEME["grid"], color=THEME["text"]), yaxis=dict(backgroundcolor=THEME["panel"], gridcolor=THEME["grid"], color=THEME["text"]), zaxis=dict(backgroundcolor=THEME["panel"], gridcolor=THEME["grid"], color=THEME["text"])))
    return fig


def safe_plotly(fig, title="Chart", height=420):
    try:
        apply_layout(fig, title, height)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False, "responsive": True})
    except Exception as e:
        info_box(f"Chart skipped: {title}", f"Reason: {e}", THEME["orange"])


def money_table(df, formatter="${:,.0f}"):
    return (df.style.format(formatter).set_properties(**{"background-color":"#0B0F17","color":THEME["text"],"border-color":THEME["grid"]}).set_table_styles([
        {"selector":"th","props":[("background-color","#151B2A"),("color",THEME["gold2"]),("border-color",THEME["grid"])]},
        {"selector":"td","props":[("border-color",THEME["grid"])]},
    ]))


def banner():
    st.markdown(f"""
<div class="fortress-hero">
  <div style="display:flex;align-items:center;gap:16px;margin-bottom:14px;">
    <span style="font-size:40px;">💼</span>
    <div>
      <h1 style="margin:0;font-size:28px;font-weight:900;color:{THEME['text']};">Personal Financial Intelligence Report</h1>
      <p style="margin:4px 0 0;font-size:13px;color:{THEME['muted']};">Fortress Strategy v6.4 · Streamlit Cloud Edition · modular refactor</p>
    </div>
  </div>
  <div class="fortress-kpis">
    <div>📂 Source: Google Drive Excel workbook or manual upload</div><div>🏠 Target: house-readiness and mortgage stress engine</div><div>📈 Portfolio: excludes sell/reduce rows from totals</div>
    <div>🧠 Transfer intelligence active</div><div>📱 Mobile-friendly cards and chart spacing</div><div>🔄 Auto-refreshes every 5 minutes</div>
  </div>
</div>""", unsafe_allow_html=True)
