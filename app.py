# app.py
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime
import textwrap
import base64
from pathlib import Path

from src import config
from src.scenario import Scenario
from src.run_sim import simulate_many, evaluate_grid
import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval

Q_MIN = config.Q_MIN
Q_MAX = config.Q_MAX
MAX_GRID_POINTS = config.MAX_GRID_POINTS

# ============================================================
# Page config (must be first Streamlit call)
# ============================================================
st.set_page_config(
    page_title="Hot Dog Newsvendor Simulator",
    layout="wide",
    initial_sidebar_state="expanded",
)

def set_bg(image_path: str):
    img = Path(image_path).read_bytes()
    encoded = base64.b64encode(img).decode()

    st.markdown(
        f"""
        <style>

        /* =========================
           PAGE BACKDROP
        ========================= */
        [data-testid="stAppViewContainer"] {{
            background:
              linear-gradient(rgba(0,0,0,0.15), rgba(0,0,0,0.35)),
              url("data:image/jpeg;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }}

        /* =========================
           MAIN CONTENT PANEL
        ========================= */
        [data-testid="stMainBlockContainer"] {{
            background: rgba(255, 255, 255, 0.92);
            border-radius: 20px;
            padding: 36px 36px;
            margin-top: 24px;
            box-shadow: 0 18px 50px rgba(0,0,0,0.25);
            backdrop-filter: blur(6px);
        }}

        /* =========================
           SIDEBAR PANEL
        ========================= */
        [data-testid="stSidebar"] > div:first-child {{
            background: rgba(255, 255, 255, 0.95);
            border-right: 1px solid rgba(0,0,0,0.06);
        }}

        /* Remove header clash */
        [data-testid="stHeader"] {{
            background: transparent;
        }}

        /* Constrain width for cleaner layout */
        .block-container {{
            max-width: 1200px;
        }}

        /* =========================
           HERO TITLE SECTION
        ========================= */

        .hero-title {{
            text-align: center;
            margin-top: 10px;
            margin-bottom: 28px;
            animation: fadeUp .6s ease-out;
        }}

        .hero-title h1 {{
            font-family: "Inter", "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 2.9rem;
            font-weight: 900;
            letter-spacing: -0.02em;
            margin-bottom: 10px;

            /* Clean professional gradient text */
            background: linear-gradient(90deg, #D73A2F, #F4B400);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .hero-title p {{
            font-family: "Inter", "Segoe UI", sans-serif;
            font-size: 1.15rem;
            font-weight: 600;
            color: #374151;
            letter-spacing: 0.02em;
        }}

        @keyframes fadeUp {{
            from {{
                opacity: 0;
                transform: translateY(12px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

set_bg("pics/hotdog_1.jpg")

st.markdown(
    """
    <div class="hero-title">
        <h1>Hot Dog Newsvendor Simulator</h1>
        <p>Game-day demand & profit simulation for choosing the optimal hot dog order quantity (Q)</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        margin:14px 0 18px;   /* <-- key: pushes it down below the header */
        border:1px solid #E0E3EB;
        border-radius:16px;
        padding:12px 14px;
        background:
          linear-gradient(90deg, rgba(215,58,47,0.35), rgba(244,180,0,0.35)),
          repeating-linear-gradient(
            90deg,
            rgba(17,24,39,0.03) 0px,
            rgba(17,24,39,0.03) 10px,
            rgba(17,24,39,0.00) 10px,
            rgba(17,24,39,0.00) 22px
          );
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:10px;
    ">
      <div style="font-weight:900; letter-spacing:.08em; color:#111827;">
        🌭🏈 GAME DAY MODE
      </div>
      <div style="color:#6B7280; font-weight:700; font-size:13px;">
        Pick your <span style="color:#D73A2F; font-weight:900;">Q</span> like a coach calls plays.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Theme / CSS
# ============================================================
def apply_theme_css():
    st.markdown(
        """
        <style>
        :root{
            --bg: #FFFFFF;
            --sidebar: #F6F7FB;
            --card: #FFFFFF;
            --border: #E0E3EB;
            --muted: #6B7280;
            --text: #111827;

            --ketchup: #D73A2F;
            --ketchupDark: #B92B23;
            --mustard: #F4B400;
            --pill: #F3F4F6;
        }

        .stApp { background: var(--bg) !important; color: var(--text) !important; }

        header[data-testid="stHeader"] {
            background: var(--bg) !important;
            border-bottom: 1px solid var(--border) !important;
        }
        header[data-testid="stHeader"]::before { background: none !important; }
        div[data-testid="stToolbar"] { background: var(--bg) !important; }

        .block-container { padding-top: 3.2rem !important; padding-bottom: 2.5rem; }

        h1,h2,h3,h4,h5,h6,p,li,span,label,div { color: var(--text); }
        .stCaption, small { color: var(--muted) !important; }

        section[data-testid="stSidebar"] > div {
            background: var(--sidebar) !important;
            border-right: 1px solid var(--border) !important;
        }

        /* ===== Cardify column blocks ===== */
        div[data-testid="column"]{
            background: rgba(255,255,255,0.92);
            border: 1px solid rgba(224,227,235,0.9);
            border-radius: 14px;
            padding: 14px 14px 16px 14px;
            box-shadow: 0 8px 22px rgba(0,0,0,0.10);
        }

        /* =========================
           METRICS (FIX: centered + bold)
        ========================= */

        /* The card itself */
        div[data-testid="metric-container"], .stMetric{
            background: rgba(255,255,255,0.92) !important;
            border: 1px solid rgba(224,227,235,0.9) !important;
            border-radius: 14px !important;
            padding: 14px !important;
            box-shadow: 0 8px 22px rgba(0,0,0,0.10);
            
            /* force layout */
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;

            text-align: center !important;
        }

        /* Streamlit nests a couple wrapper divs — center those too */
        div[data-testid="metric-container"] > div,
        .stMetric > div{
            width: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
        }

        /* Label */
        div[data-testid="metric-container"] [data-testid="stMetricLabel"],
        div[data-testid="metric-container"] [data-testid="stMetricLabel"] *,
        .stMetric [data-testid="stMetricLabel"],
        .stMetric [data-testid="stMetricLabel"] *{
            width: 100% !important;
            display: block !important;
            text-align: center !important;
            font-weight: 800 !important;
            color: var(--muted) !important;
        }

        /* Value (big number) */
        div[data-testid="metric-container"] [data-testid="stMetricValue"],
        div[data-testid="metric-container"] [data-testid="stMetricValue"] *,
        .stMetric [data-testid="stMetricValue"],
        .stMetric [data-testid="stMetricValue"] *{
            width: 100% !important;
            display: block !important;
            text-align: center !important;
            font-weight: 950 !important;
            color: var(--text) !important;
        }

        /* Delta (if any) */
        div[data-testid="metric-container"] [data-testid="stMetricDelta"],
        .stMetric [data-testid="stMetricDelta"]{
            width: 100% !important;
            text-align: center !important;
            justify-content: center !important;
        }

        /* =========================
           Buttons
        ========================= */
        div.stButton > button[kind="primary"]{
            background: var(--ketchup) !important;
            color: #FFFFFF !important;
            border: 1px solid var(--ketchup) !important;
            border-radius: 12px !important;
            padding: 0.60rem 1.15rem !important;
            font-weight: 800 !important;
        }
        div.stButton > button[kind="primary"]:hover{
            background: var(--ketchupDark) !important;
            border-color: var(--ketchupDark) !important;
        }

        button:focus, button:focus-visible{
            outline: none !important;
            box-shadow: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

apply_theme_css()

# ============================================================
# Altair Theme (ketchup/mustard + clean spacing)
# ============================================================
KETCHUP = "#D73A2F"
MUSTARD = "#F4B400"
INK     = "#111827"
MUTED   = "#6B7280"
BORDER  = "#E0E3EB"
PANEL   = "#FFFFFF"

def register_altair_theme():
    def _theme():
        return {
            "config": {
                "background": "transparent",
                "view": {"stroke": "transparent"},
                "axis": {
                    "labelFont": "Inter",
                    "titleFont": "Inter",
                    "labelColor": MUTED,
                    "titleColor": INK,
                    "labelFontSize": 12,
                    "titleFontSize": 13,
                    "titleFontWeight": 800,
                    "labelPadding": 6,
                    "titlePadding": 10,
                    "grid": True,
                    "gridColor": BORDER,
                    "gridOpacity": 0.55,
                    "domain": False,
                    "tickColor": BORDER,
                },
                "legend": {
                    "labelFont": "Inter",
                    "titleFont": "Inter",
                    "labelColor": MUTED,
                    "titleColor": INK,
                    "titleFontWeight": 800,
                    "labelFontSize": 12,
                    "titleFontSize": 12,
                },
                "title": {
                    "font": "Inter",
                    "fontSize": 16,
                    "fontWeight": 900,
                    "color": INK,
                    "anchor": "start",
                },
                "mark": {
                    "color": KETCHUP,
                    "stroke": KETCHUP,
                    "strokeWidth": 2,
                },
            }
        }

    alt.themes.register("hotdog_theme", _theme)
    alt.themes.enable("hotdog_theme")

register_altair_theme()

st.markdown(
    """
    <div style="height:3px; border-radius:999px; margin:10px 0 18px;
                background: linear-gradient(90deg, rgba(229,57,53,0.0), rgba(229,57,53,0.65), rgba(229,57,53,0.0));">
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Helpers / constants
# ============================================================
IDEAL_TEMP_F = int(getattr(config, "TEMP_IDEAL_F", getattr(config, "TEMP_DEFAULT_F", 70)))

WIDGET_KEYS = [
    "mode",
    "Q_single", "Qmin", "Qmax", "step",
    "seed", "replications",
    "stadium_capacity", "indoor",
    "temp_f", "rain", "snow",
    "promo", "playoff",
    "team_wins", "team_losses", "opp_wins", "opp_losses",
    # NEW
    "price_per_dog", "cost_per_dog", "salvage_per_dog",
]

def handle_indoor_toggle():
    """If indoor turned on, clear weather + set temp to ideal (UI + logic)."""
    if st.session_state.get("indoor"):
        st.session_state["rain"] = False
        st.session_state["snow"] = False
        st.session_state["temp_f"] = IDEAL_TEMP_F

def reset_app():
    """Hard reset UI + results."""
    for k in WIDGET_KEYS:
        if k in st.session_state:
            del st.session_state[k]
    st.session_state["last_run"] = None

# ============================================================
# Scoreboard + narrative helpers
# ============================================================
def _badge(text: str, kind: str = "neutral") -> str:
    colors = {
        "neutral": ("#F3F4F6", "#111827", "#E0E3EB"),
        "red":     ("#FDE8E7", "#7F1D1D", "#FCA5A5"),
        "gold":    ("#FFF7D6", "#854D0E", "#FDE68A"),
        "blue":    ("#E8F1FF", "#1E3A8A", "#BFDBFE"),
    }
    bg, fg, border = colors.get(kind, colors["neutral"])
    return (
        f'<span style="display:inline-block; padding:4px 10px; margin-right:0px; '
        f'border-radius:999px; border:1px solid {border}; background:{bg}; color:{fg}; '
        f'font-size:12px; line-height:1; white-space:nowrap; font-weight:700;">{text}</span>'
    )


def render_scoreboard(
    sc: Scenario,
    *,
    best_q: int | None = None,
    q_label: str = "BEST Q",
    avg_profit: float | None = None,
    stockout_rate: float | None = None,
    sellout_rate: float | None = None,
    avg_attendance: float | None = None,
) -> None:
    # ---------- badges ----------
    badges = []

    # stadium / weather
    badges.append(_badge("🏟️ Indoor" if sc.indoor else "🌤️ Outdoor", "blue" if sc.indoor else "neutral"))
    badges.append(_badge(f"🧱 Capacity {int(sc.stadium_capacity):,}", "neutral"))

    if sc.indoor:
        badges.append(_badge(f"🌡️ {int(round(sc.temp_f))}°F (fixed)", "neutral"))
    else:
        badges.append(_badge(f"🌡️ {int(round(sc.temp_f))}°F", "neutral"))
        if sc.rain:
            badges.append(_badge("🌧️ Rain", "blue"))
        if sc.snow:
            badges.append(_badge("❄️ Snow", "blue"))

    # game context
    badges.append(_badge("📣 Promotion" if sc.promo else "🚫 No Promo", "red" if sc.promo else "neutral"))
    badges.append(_badge("🏆 Playoff" if sc.playoff else "🗓️ Regular season", "gold" if sc.playoff else "neutral"))

    # records
    badges.append(_badge(f"🏠 Home {sc.team_wins}-{sc.team_losses}", "neutral"))
    badges.append(_badge(f"🚌 Away {sc.opp_wins}-{sc.opp_losses}", "neutral"))

    # ---------- headline values ----------
    left_label = q_label
    left_value = "—" if best_q is None else f"{int(best_q):,}"

    right_label = "AVG PROFIT"
    right_value = "—" if avg_profit is None else f"${int(round(avg_profit)):,}"

    # ---------- subscores ----------
    def fmt_rate(x: float | None) -> str:
        return "—" if x is None else f"{x:.1%}"

    def fmt_int(x: float | None) -> str:
        return "—" if x is None else f"{int(round(x)):,}"

    so = fmt_rate(stockout_rate)
    se = fmt_rate(sellout_rate)
    aa = fmt_int(avg_attendance)

    ticker = "".join(badges)
    ticker2 = ticker + ticker  # duplicate for seamless loop

    html = f"""
    <div style="font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; display:flex; justify-content:center;">

    <!-- IMPORTANT: CSS must be INSIDE this iframe -->
    <style>
        .badge-ticker {{
        position: relative;
        overflow: hidden;
        background: #F8FAFF;
        border-top: 1px solid #E0E3EB;
        padding: 10px 12px;
        white-space: nowrap;
        }}

        .badge-track {{
        display: inline-flex;
        gap: 10px;
        width: max-content;
        will-change: transform;
        animation: badge-scroll 18s linear infinite;
        }}

        /* optional: pause on hover */
        .badge-ticker:hover .badge-track {{
        animation-play-state: paused;
        }}

        @keyframes badge-scroll {{
        0%   {{ transform: translateX(0); }}
        100% {{ transform: translateX(-50%); }}
        }}

        /* =========================
        MOBILE-ONLY SCOREBOARD FIX
        (Desktop unchanged)
        ========================= */
        @media (max-width: 520px) {{
        .sb-top-row {{
            flex-wrap: wrap !important;
            gap: 10px !important;
        }}

        /* Cards stack full-width on narrow screens */
        .sb-card {{
            max-width: none !important;
            flex: 1 1 100% !important;
        }}

        /* Prevent value breaking like "$65,90" */
        .sb-big-value {{
            white-space: nowrap !important;
            font-size: 28px !important; /* slightly smaller on mobile */
            line-height: 1.05 !important;
        }}

        /* Make VS a clean divider row:  —— VS ——  */
        .sb-vs {{
            flex: 1 1 100% !important;
            min-width: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            flex-direction: row !important;
            gap: 10px !important;
            padding: 4px 0 !important;
            opacity: 0.55;
        }}

        .sb-vs::before,
        .sb-vs::after {{
            content: "";
            height: 2px;
            background: #E0E3EB;
            border-radius: 999px;
            flex: 1 1 auto;
            max-width: 140px;
        }}

        /* Hide the old little line block */
        .sb-vs-line {{
            display: none !important;
        }}

        /* Slightly tighten ticker padding on mobile (helps a bit) */
        .badge-ticker {{
            padding: 8px 10px !important;
        }}
        }}
    </style>

    <!-- OUTER SCOREBOARD (the mounted unit) -->
    <div style="
        width: 100%;
        max-width: 980px;
        border: 1px solid #E0E3EB;
        border-radius: 18px;
        background: #FFFFFF;
        box-shadow: 0 10px 28px rgba(17,24,39,0.08);
        overflow: hidden;
    ">

        <!-- HEADER BAR -->
        <div style="
        padding: 10px 14px;
        background: linear-gradient(180deg, #FAFBFF, #FFFFFF);
        border-bottom: 1px solid #E0E3EB;
        display:flex;
        align-items:center;
        justify-content:center;
        gap:10px;
        ">
        <div style="font-weight:900; letter-spacing:0.14em; color:#6B7280; font-size:12px;">
            GAME DAY SCOREBOARD
        </div>
        </div>

        <!-- INNER "SCREEN" AREA -->
        <div style="padding: 14px 14px 12px; background:#FFFFFF;">

        <!-- Big cards row -->
        <div style="
            background:#FAFBFF;
            border:1px solid #E0E3EB;
            border-radius: 16px;
            padding: 12px;
        ">

            <div class="sb-top-row" style="display:flex; gap:14px; align-items:stretch; justify-content:center;">
            <div class="sb-card" style="flex:1; max-width:420px; padding:14px 16px; border-radius:14px; background:#FFFFFF; border:1px solid #E0E3EB; text-align:center;">
                <div style="font-size:12px; letter-spacing:0.12em; color:#6B7280; font-weight:800;">{left_label}</div>
                <div class="sb-big-value" style="font-size:30px; font-weight:950; color:#111827; margin-top:2px;">{left_value}</div>
            </div>

            <div class="sb-vs" style="min-width:66px; display:flex; align-items:center; justify-content:center; flex-direction:column;">
                <div style="font-size:12px; letter-spacing:0.16em; color:#9CA3AF; font-weight:900; text-align:center;">VS</div>
                <div class="sb-vs-line" style="margin-top:4px; width:36px; height:2px; border-radius:999px; background:#E0E3EB;"></div>
            </div>

            <div class="sb-card" style="flex:1; max-width:420px; padding:14px 16px; border-radius:14px; background:#FFFFFF; border:1px solid #E0E3EB; text-align:center;">
                <div style="font-size:12px; letter-spacing:0.12em; color:#6B7280; font-weight:800;">{right_label}</div>
                <div class="sb-big-value" style="font-size:30px; font-weight:950; color:#111827; margin-top:2px;">{right_value}</div>
            </div>
            </div>

            <!-- Subscores row -->
            <div style="display:flex; gap:10px; justify-content:center; margin-top:10px;">
            <div style="flex:1; max-width:270px; padding:10px 12px; border-radius:12px; background:#FFFFFF; border:1px solid #E0E3EB;">
                <div style="font-size:12px; color:#6B7280; font-weight:700; text-align:center;">Stockout Rate</div>
                <div style="font-size:18px; font-weight:900; color:#111827; text-align:center;">{so}</div>
            </div>
            <div style="flex:1; max-width:270px; padding:10px 12px; border-radius:12px; background:#FFFFFF; border:1px solid #E0E3EB;">
                <div style="font-size:12px; color:#6B7280; font-weight:700; text-align:center;">Sellout Rate</div>
                <div style="font-size:18px; font-weight:900; color:#111827; text-align:center;">{se}</div>
            </div>
            <div style="flex:1; max-width:270px; padding:10px 12px; border-radius:12px; background:#FFFFFF; border:1px solid #E0E3EB;">
                <div style="font-size:12px; color:#6B7280; font-weight:700; text-align:center;">Avg Attendance</div>
                <div style="font-size:18px; font-weight:900; color:#111827; text-align:center;">{aa}</div>
            </div>
            </div>

        </div>
        </div>

        <!-- BADGE TICKER STRIP (looping) -->
        <div class="badge-ticker">
        <div class="badge-track">
            {ticker2}
        </div>
        </div>

    </div>
    </div>
    """

    # --- mobile-only iframe height (prevents badge bar clipping on phones) ---
    vw = streamlit_js_eval(
        js_expressions="window.innerWidth",
        key="vw_scoreboard",
        want_output=True,
    )

    # desktop stays tight; mobile gets extra room for stacked layout
    height = 520 if (vw is not None and int(vw) < 520) else 320

    components.html(html, height=height)

def make_game_script(sc: Scenario, out: dict, mode: str) -> str:
    lines = []
    ctx = []
    if sc.playoff:
        ctx.append("playoff intensity")
    if sc.promo:
        ctx.append("promotion uplift")
    if sc.indoor:
        ctx.append("indoor conditions (weather-neutral)")
    else:
        if sc.rain and sc.snow:
            ctx.append("rain + snow headwinds")
        elif sc.rain:
            ctx.append("rain headwinds")
        elif sc.snow:
            ctx.append("snow headwinds")
    if ctx:
        lines.append(f"Scenario notes: {', '.join(ctx)}.")

    avg_profit = out.get("avg_profit")
    stockout = out.get("stockout_rate")
    sellout = out.get("sellout_rate")
    waste = out.get("waste_rate")

    if avg_profit is not None:
        lines.append(f"Expected profit is about ${int(round(avg_profit)):,} per game.")

    if stockout is not None:
        if stockout >= 0.20:
            lines.append("Stockouts are frequent — you’re leaving meaningful demand on the table.")
        elif stockout >= 0.08:
            lines.append("Stockouts are moderate — you’re balancing lost sales against waste.")
        else:
            lines.append("Stockouts are low — you’re prioritizing availability and fan satisfaction.")

    if waste is not None:
        if waste >= 0.25:
            lines.append("Waste is relatively high; consider lowering Q or improving salvage/secondary sales.")
        elif waste >= 0.10:
            lines.append("Waste looks manageable; there’s a healthy buffer for demand spikes.")
        else:
            lines.append("Waste is low; ordering is tight and efficient.")

    if sellout is not None:
        if sellout >= 0.25:
            lines.append("Sellouts happen often — packed-house games can drive right-tail demand spikes.")
        elif sellout >= 0.10:
            lines.append("Sellouts occur sometimes — expect occasional demand surges.")

    if mode == "grid":
        lines.append("“Best Q” is the top performer on your tested grid (tighten step size around the peak to refine).")

    return " ".join(lines)

# ============================================================
# Charts
# ============================================================
def plot_profit_vs_q_with_refs(results: list[dict], best_q: int):
    chart_df = (
        pd.DataFrame([{"Q": int(r["Q"]), "avg_profit": float(r["avg_profit"])} for r in results])
        .sort_values("Q")
    )

    base = alt.Chart(chart_df).encode(
        x=alt.X("Q:Q", title="Order Quantity (Q)", axis=alt.Axis(format=",.0f")),
        y=alt.Y("avg_profit:Q", title="Average Profit ($)", axis=alt.Axis(format=",.0f")),
        tooltip=[
            alt.Tooltip("Q:Q", title="Q", format=","),
            alt.Tooltip("avg_profit:Q", title="Avg Profit", format=",.0f"),
        ],
    )

    line = base.mark_line(color=KETCHUP, strokeWidth=3)
    pts  = base.mark_point(filled=True, size=80, color=KETCHUP, stroke="white", strokeWidth=1)

    # Best Q highlight (mustard)
    best_pt = alt.Chart(pd.DataFrame({"Q":[best_q]})).mark_rule(
        color=MUSTARD, strokeWidth=3, strokeDash=[8, 6]
    ).encode(x="Q:Q")

    # $0 reference line (muted)
    zero = alt.Chart(pd.DataFrame({"avg_profit":[0]})).mark_rule(
        color=MUTED, strokeWidth=2, strokeDash=[6, 6], opacity=0.6
    ).encode(y="avg_profit:Q")

    chart = (
        (line + pts + best_pt + zero)
        .properties(height=380, padding={"left": 16, "right": 16, "top": 10, "bottom": 12})
    )

    st.altair_chart(chart, use_container_width=True)


def plot_hist_numeric_eps(eps_values, step: float = 0.02):
    df = pd.DataFrame({"eps": np.asarray(eps_values, dtype=float)})

    bars = (
        alt.Chart(df)
        .mark_bar(color=KETCHUP, opacity=0.70)
        .encode(
            x=alt.X("eps:Q", bin=alt.Bin(step=step), title="ε (demand multiplier)", axis=alt.Axis(format=".2f")),
            y=alt.Y("count():Q", title="Simulated games"),
            tooltip=[alt.Tooltip("count():Q", title="Games")],
        )
        .properties(height=300)  # <-- NO padding here
    )

    mean_line = (
        alt.Chart(pd.DataFrame({"eps": [1.0]}))
        .mark_rule(color=MUSTARD, strokeWidth=4)
        .encode(x="eps:Q")
    )

    chart = (bars + mean_line).properties(
        padding={"left": 16, "right": 16, "top": 10, "bottom": 12}
    )

    st.altair_chart(chart, use_container_width=True)

def plot_hist_numeric(values, title: str, x_title: str, bins: int = 30, x_format: str = ".2f"):
    df = pd.DataFrame({"x": np.asarray(values, dtype=float)})

    chart = (
        alt.Chart(df)
        .mark_bar(color=KETCHUP, opacity=0.72)
        .encode(
            x=alt.X("x:Q", bin=alt.Bin(maxbins=bins), title=x_title, axis=alt.Axis(format=x_format)),
            y=alt.Y("count():Q", title="Simulated games"),
            tooltip=[alt.Tooltip("count():Q", title="Games")],
        )
        .properties(height=300, padding={"left": 16, "right": 16, "top": 10, "bottom": 12})
    )

    # only add a title if you actually provided one
    if title and str(title).strip():
        chart = chart.properties(title=title)

    st.altair_chart(chart, use_container_width=True)

# ============================================================
# Top buttons
# ============================================================
c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
with c2:
    run_btn = st.button("Run Simulation", type="primary")
with c4:
    st.button("Reset", on_click=reset_app)

# ============================================================
# Session state
# ============================================================
if "last_run" not in st.session_state:
    st.session_state.last_run = None

# ============================================================
# Sidebar inputs
# ============================================================
with st.sidebar:
    st.header("Scenario Inputs")

    with st.expander("Decision Variable: Q", expanded=True):
        mode = st.radio(
            "Run mode",
            ["Find optimal Q (grid search)", "Evaluate a single Q"],
            index=0,
            key="mode",
        )

        if mode == "Evaluate a single Q":
            Q_single = st.number_input(
                "Order quantity Q",
                min_value=Q_MIN,
                max_value=Q_MAX,
                value=20000,
                step=500,
                key="Q_single",
            )
        else:
            Qmin = st.number_input(
                "Q min",
                min_value=Q_MIN,
                max_value=Q_MAX,
                value=15000,
                step=500,
                key="Qmin",
            )

            Qmax = st.number_input(
                "Q max",
                min_value=Q_MIN,
                max_value=Q_MAX,
                value=30000,
                step=500,
                key="Qmax",
            )
            step = st.number_input("Step", min_value=1, value=500, step=50, key="step")
            Q_single = None

    with st.expander("Simulation Controls", expanded=True):
        seed = st.number_input("Random seed", value=123, step=1, key="seed")

        replications = st.slider(
            "Replications (simulated games)",
            min_value=config.REPS_MIN,
            max_value=config.REPS_MAX,
            value=config.REPS_DEFAULT,
            step=config.REPS_STEP,
            key="replications",
        )

    with st.expander("Economics (Newsvendor)", expanded=True):
        # Use config defaults if present, else sensible fallbacks
        price_per_dog = st.slider(
            "Price per hot dog ($)",
            min_value=0.00,
            max_value=10.00,
            value=float(getattr(config, "P_DEFAULT", 6.00)),
            step=0.10,
            key="price_per_dog",
        )

        cost_per_dog = st.slider(
            "Cost per hot dog ($)",
            min_value=0.00,
            max_value=5.00,
            value=float(getattr(config, "C_DEFAULT", 1.50)),
            step=0.05,
            key="cost_per_dog",
        )

        salvage_per_dog = st.slider(
            "Salvage value per leftover ($)",
            min_value=0.00,
            max_value=2.00,
            value=float(getattr(config, "S_DEFAULT", 0.25)),
            step=0.05,
            key="salvage_per_dog",
        )

        # Optional: quick sanity warning (not blocking)
        if salvage_per_dog > cost_per_dog:
            st.caption("⚠️ Salvage > Cost means leftovers are 'profitable' to over-order (unusual).")
        if price_per_dog <= cost_per_dog:
            st.caption("⚠️ Price ≤ Cost means each sale loses money unless salvage/fixed costs change.")

    with st.expander("Stadium", expanded=True):
        stadium_capacity = st.slider(
            "Stadium capacity",
            min_value=config.CAPACITY_MIN,
            max_value=config.CAPACITY_MAX,
            value=config.CAPACITY_DEFAULT,
            step=config.CAPACITY_STEP,
            key="stadium_capacity",
        )

        indoor = st.checkbox(
            "Indoor stadium",
            key="indoor",
            value=bool(st.session_state.get("indoor", False)),
            on_change=handle_indoor_toggle,
        )
        indoor = bool(st.session_state.get("indoor", False))

    with st.expander("Weather", expanded=True):
        temp_f_ui = st.slider(
            "Temperature (°F)",
            min_value=int(config.TEMP_MIN_F),
            max_value=int(config.TEMP_MAX_F),
            key="temp_f",
            value=int(st.session_state.get("temp_f", int(getattr(config, "TEMP_DEFAULT_F", IDEAL_TEMP_F)))),
            step=1,
            disabled=indoor,
        )

        col_w1, col_w2 = st.columns(2)
        with col_w1:
            rain_ui = st.checkbox("Rain", key="rain", value=bool(st.session_state.get("rain", False)), disabled=indoor)
        with col_w2:
            snow_ui = st.checkbox("Snow", key="snow", value=bool(st.session_state.get("snow", False)), disabled=indoor)

        if indoor:
            st.caption(f"Indoor stadium: weather + temperature are ignored (temperature fixed at {IDEAL_TEMP_F}°F).")

        temp_f = float(IDEAL_TEMP_F if indoor else temp_f_ui)
        rain = False if indoor else bool(rain_ui)
        snow = False if indoor else bool(snow_ui)

    with st.expander("Game Context", expanded=True):
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            promo = st.checkbox("Promotion", key="promo", value=bool(st.session_state.get("promo", False)))
        with col_g2:
            playoff = st.checkbox("Playoff game", key="playoff", value=bool(st.session_state.get("playoff", False)))

    with st.expander("Team record (Wins / Losses)", expanded=True):
        season_games = config.SEASON_GAMES
        team_wins = st.slider("Team wins", 0, season_games, 9, key="team_wins")
        team_losses = st.slider("Team losses", 0, season_games, 8, key="team_losses")
        st.divider()
        opp_wins = st.slider("Opponent wins", 0, season_games, 9, key="opp_wins")
        opp_losses = st.slider("Opponent losses", 0, season_games, 8, key="opp_losses")

# ============================================================
# Build Scenario
# ============================================================
sc = Scenario(
    seed=int(seed),
    replications=int(replications),
    stadium_capacity=int(stadium_capacity),
    temp_f=float(temp_f),
    indoor=bool(indoor),
    team_wins=int(team_wins),
    team_losses=int(team_losses),
    opp_wins=int(opp_wins),
    opp_losses=int(opp_losses),
    rain=bool(rain),
    snow=bool(snow),
    promo=bool(promo),
    playoff=bool(playoff),

    # NEW economics
    price=float(price_per_dog),
    cost=float(cost_per_dog),
    salvage=float(salvage_per_dog),
)

# ============================================================
# Tabs
# ============================================================
tab_results, tab_explain, tab_debug = st.tabs(["Results", "Explanation", "Debug"])

with tab_debug:
    st.subheader("Scenario (what will be simulated)")
    st.code(str(sc))

# ============================================================
# Run on click
# ============================================================
if run_btn:
    try:
        sc.validate()
    except Exception as e:
        st.session_state.last_run = {"error": f"Scenario validation failed: {e}", "scenario": sc}
    else:
        with st.spinner("Running simulation..."):
            run_meta = {
                "ran_at": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
                "seed": int(seed),
                "replications": int(replications),
            }

            if mode == "Evaluate a single Q":
                q_ran = int(Q_single)
                summary = simulate_many(Q=q_ran, sc=sc, return_traces=True)
                st.session_state.last_run = {
                    "mode": "single",
                    "scenario": sc,
                    "Q": q_ran,                 # <--- add
                    "summary": summary,
                    "meta": run_meta,
                }
            else:
                if int(Qmax) < int(Qmin):
                    st.session_state.last_run = {
                        "error": "Q max must be >= Q min.",
                        "scenario": sc
                    }

                else:
                    # ============================
                    # Grid size safety check
                    # ============================
                    n_points = (int(Qmax) - int(Qmin)) // int(step) + 1

                    if n_points > MAX_GRID_POINTS:
                        st.session_state.last_run = {
                            "error": (
                                f"Grid too large: {n_points:,} values "
                                f"(max allowed: {MAX_GRID_POINTS}). "
                                "Increase step size or reduce range."
                            ),
                            "scenario": sc,
                        }

                    else:
                        Q_values = list(range(int(Qmin), int(Qmax) + 1, int(step)))
                        results = evaluate_grid(Q_values, sc=sc)

                        best = max(results, key=lambda r: r["avg_profit"])
                        top10 = sorted(results, key=lambda r: r["avg_profit"], reverse=True)[:10]
                        best_trace = simulate_many(Q=int(best["Q"]), sc=sc, return_traces=True)

                        st.session_state.last_run = {
                            "mode": "grid",
                            "scenario": sc,
                            "results": results,
                            "best": best,
                            "top10": top10,
                            "best_trace": best_trace,
                            "grid": {
                                "Qmin": int(Qmin),
                                "Qmax": int(Qmax),
                                "step": int(step),
                            },
                            "meta": run_meta,
                        }
# ============================================================
# Results tab
# ============================================================
with tab_results:
    last = st.session_state.last_run

    if last is None:
        st.warning("Set inputs on the left sidebar, then click Run Simulation.")
    elif "error" in last:
        st.error(last["error"])
        st.subheader("Scenario used")
        st.code(str(last.get("scenario")))
    elif last.get("mode") == "single":
        summary = last["summary"]


        # ---- compute values needed for scoreboard FIRST ----
        traces = summary.get("traces")

        sellout_rate: float | None = None
        avg_attendance: float | None = None

        if traces:
            att = np.asarray(traces["attendance"], dtype=float)
            avg_attendance = float(np.mean(att))
            sellout_rate = float(np.mean(att >= stadium_capacity))

        # ---- now render scoreboard ----
        render_scoreboard(
            last["scenario"],
            best_q=int(last["Q"]),
            q_label="Q (Your Input)", 
            avg_profit=float(summary["avg_profit"]),
            stockout_rate=float(summary["stockout_rate"]),
            sellout_rate=sellout_rate,
            avg_attendance=avg_attendance,
        )

        meta = last.get("meta", {})
        if meta:
            st.caption(f"Last run: {meta.get('ran_at','')} • Seed: {meta.get('seed','')} • Replications: {meta.get('replications','')}")

        st.subheader("Single Q results")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Avg Profit", f"${int(round(summary['avg_profit'])):,}")
        c2.metric("SD Profit", f"${int(round(summary['sd_profit'])):,}")
        c3.metric("Stockout Rate", f"{summary['stockout_rate']:.1%}")
        c4.metric("Avg Demand", f"{int(round(summary['avg_demand'])):,}")

        traces = summary.get("traces")
        p05_profit = None
        waste_rate = None
        hotdogs_per_1k = None
        efficiency = None

        if traces:
            att = np.asarray(traces["attendance"], dtype=float)
            profit = np.asarray(traces["profit"], dtype=float)
            demand = np.asarray(traces["demand"], dtype=float)

            Q_used = int(last["Q"])
            sold_est = np.minimum(Q_used, demand)
            leftover_est = np.maximum(Q_used - demand, 0)

            sellout_rate = float(np.mean(att >= stadium_capacity))
            p05_profit = float(np.percentile(profit, 5))
            waste_rate = float(np.mean(leftover_est / max(Q_used, 1)))
            efficiency = float(np.mean(sold_est / max(Q_used, 1)))

            denom = np.maximum(att, 1.0)
            hotdogs_per_1k = float(np.mean((sold_est / denom) * 1000.0))

        st.subheader("Concessions performance")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Downside Profit (5th %ile)", "N/A" if p05_profit is None else f"${int(round(p05_profit)):,}")
        m2.metric("Sellout Rate", "N/A" if sellout_rate is None else f"{sellout_rate:.1%}")
        m3.metric("Waste Rate", "N/A" if waste_rate is None else f"{waste_rate:.1%}")
        m4.metric("Order Efficiency", "N/A" if efficiency is None else f"{efficiency:.1%}")
        m5.metric("Hot Dogs / 1,000 Fans", "N/A" if hotdogs_per_1k is None else f"{int(round(hotdogs_per_1k)):,}")

        script = make_game_script(
            last["scenario"],
            {
                "avg_profit": summary.get("avg_profit"),
                "stockout_rate": summary.get("stockout_rate"),
                "sellout_rate": sellout_rate,
                "waste_rate": waste_rate,
            },
            mode="single",
        )
        st.info(script)

        if traces:
            st.subheader("Profit Distribution (this Q)")
            plot_hist_numeric(traces["profit"], title="", x_title="Profit per game ($)", bins=30, x_format=",.0f")

            st.subheader("Demand distribution (this Q)")
            plot_hist_numeric(traces["demand"], title="", x_title="Hot dogs demanded", bins=30, x_format=",.0f")

            with st.expander("Optional: Attendance + Noise Distributions", expanded=True):
                st.markdown("**Attendance (A)**")
                plot_hist_numeric(traces["attendance"], title="", x_title="Fans in attendance", bins=30, x_format=",.0f")

                st.markdown("**Multiplicative Noise (ε)**")
                plot_hist_numeric(traces["eps"], title="", x_title="ε (demand multiplier)", bins=30, x_format=".2f")

    else:
        best = last["best"]
        top10 = last["top10"]
        results = last["results"]
        best_trace = last.get("best_trace")


        # ---- compute values needed for scoreboard FIRST ----
        sellout_rate: float | None = None
        avg_attendance: float | None = None

        if best_trace and best_trace.get("traces"):
            att = np.asarray(best_trace["traces"]["attendance"], dtype=float)
            avg_attendance = float(np.mean(att))
            sellout_rate = float(np.mean(att >= stadium_capacity))

        # ---- now render scoreboard ----
        render_scoreboard(
            last["scenario"],
            best_q=int(best["Q"]),
            avg_profit=float(best["avg_profit"]),
            stockout_rate=float(best["stockout_rate"]),
            sellout_rate=sellout_rate,
            avg_attendance=avg_attendance,
        )

        meta = last.get("meta", {})
        if meta:
            st.caption(f"Last run: {meta.get('ran_at','')} • Seed: {meta.get('seed','')} • Replications: {meta.get('replications','')}")

        st.subheader("Best Q (by avg_profit)")

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Best Q", f"{int(best['Q']):,}")
        c2.metric("Avg Profit", f"${int(round(best['avg_profit'])):,}")
        c3.metric("Stockout Rate", f"{best['stockout_rate']:.1%}")
        c4.metric("Sellout Rate", "N/A" if sellout_rate is None else f"{sellout_rate:.1%}")
        c5.metric("Avg Attendance", "N/A" if avg_attendance is None else f"{int(round(avg_attendance)):,}")

        p05_profit = None
        waste_rate = None
        hotdogs_per_1k = None
        efficiency = None

        if best_trace and best_trace.get("traces"):
            traces = best_trace["traces"]
            att = np.asarray(traces["attendance"], dtype=float)
            profit = np.asarray(traces["profit"], dtype=float)
            demand = np.asarray(traces["demand"], dtype=float)

            Q_used = int(best["Q"])
            sold_est = np.minimum(Q_used, demand)
            leftover_est = np.maximum(Q_used - demand, 0)

            p05_profit = float(np.percentile(profit, 5))
            waste_rate = float(np.mean(leftover_est / max(Q_used, 1)))
            efficiency = float(np.mean(sold_est / max(Q_used, 1)))

            denom = np.maximum(att, 1.0)
            hotdogs_per_1k = float(np.mean((sold_est / denom) * 1000.0))

        st.subheader("Concessions performance (Best Q)")
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Downside Profit (5th %ile)", "N/A" if p05_profit is None else f"${int(round(p05_profit)):,}")
        m2.metric("Sellout Rate", "N/A" if sellout_rate is None else f"{sellout_rate:.1%}")
        m3.metric("Waste Rate", "N/A" if waste_rate is None else f"{waste_rate:.1%}")
        m4.metric("Order Efficiency", "N/A" if efficiency is None else f"{efficiency:.1%}")
        m5.metric("Hot Dogs / 1,000 Fans", "N/A" if hotdogs_per_1k is None else f"{int(round(hotdogs_per_1k)):,}")

        script = make_game_script(
            last["scenario"],
            {
                "avg_profit": best.get("avg_profit"),
                "stockout_rate": best.get("stockout_rate"),
                "sellout_rate": sellout_rate,
                "waste_rate": waste_rate,
            },
            mode="grid",
        )
        st.info(script)

        st.subheader("Top 10 Q values")
        df = pd.DataFrame(top10).copy()

        INT_COLS = [
            "Q",
            "n_games",
            "seed",
            "min_profit",
            "max_profit",
            "avg_attendance",
            "avg_demand",
            "avg_sold",
            "avg_leftover",
        ]
        for col in INT_COLS:
            if col in df.columns:
                df[col] = df[col].round(0).astype(int).map("{:,}".format)

        MONEY_COLS = ["avg_profit", "sd_profit"]
        for col in MONEY_COLS:
            if col in df.columns:
                df[col] = df[col].round(0).astype(int).map("${:,}".format)

        RATE_COLS = ["stockout_rate"]
        for col in RATE_COLS:
            if col in df.columns:
                df[col] = (df[col] * 100).round(1).astype(str) + "%"

        st.dataframe(df, use_container_width=True)

        st.subheader("Profit vs Q (grid)")
        plot_profit_vs_q_with_refs(results, best_q=int(best["Q"]))

        if best_trace and best_trace.get("traces"):
            traces = best_trace["traces"]

            st.subheader("Profit Distribution (Best Q)")
            plot_hist_numeric(traces["profit"], title="", x_title="Profit per game ($)", bins=30, x_format=",.0f")

            st.subheader("Demand Distribution (Best Q)")
            plot_hist_numeric(traces["demand"], title="", x_title="Hot dogs demanded", bins=30, x_format=",.0f")

            with st.expander("Optional: Attendance + Noise Distributions (Best Q)", expanded=True):
                st.markdown("**Attendance (A)**")
                plot_hist_numeric(traces["attendance"], title="", x_title="Fans in attendance", bins=30, x_format=",.0f")

                st.markdown("**Multiplicative Noise (ε)**")
                plot_hist_numeric_eps(traces["eps"])

        st.subheader("Best Q details")
        st.write(best)

        
# -------------------------
# Explanation tab (storytelling)
# -------------------------
with tab_explain:
    st.subheader("How to read this dashboard")

    st.markdown(
        """
**What you’re deciding:** the order quantity **Q** (how many hot dogs to stock).  

**What the simulator models:** game-to-game uncertainty in attendance and buying behavior.  

**What “best Q” means:** the Q that maximizes **average profit** on your tested grid, given the current scenario.
"""
    )

    with st.expander("Demand model: what each piece means", expanded=False):
        st.markdown(
            """
### Core demand equation

We model game demand as:

$$
D = \\mathrm{round}(A \\cdot r \\cdot \\varepsilon)
$$

**Where:**

- **A (Attendance)** = how many fans show up  
- **r (Hot dogs per attendee)** = baseline purchase rate (expected hot dogs per fan)  
- **ε (Epsilon noise)** = multiplicative randomness capturing “everything else”  
  (appetite, lines, demographics, vendor placement, etc.)

### Why multiplicative noise?

We use multiplicative noise because crowds tend to scale demand:

- Big crowds → bigger swings in absolute demand  
- Small crowds → smaller swings  

### Rounding / integer demand

Hot dogs are discrete units, so we round demand to an integer.  
This adds a small amount of discretization error, but makes the simulation realistic.
"""
        )

    with st.expander("Attendance (A): capacity, sellouts, and indoor stadium behavior", expanded=False):
        st.markdown(
            """
### Capacity capping and sellouts

Attendance is bounded:

$$
0 \\le A \\le \\text{Stadium Capacity}
$$

If the simulated attendance exceeds capacity, it is capped.

This creates visible “spikes” at capacity in the histogram, representing sellout games.

### Indoor stadium behavior

When **Indoor stadium** is enabled:

- Rain and snow are ignored  
- Temperature is fixed at the ideal level  

This prevents weather effects from being double-counted.
"""
        )

    with st.expander("Purchase rate (r): how scenario inputs affect demand", expanded=False):
        st.markdown(
            """
### Baseline rate and multipliers

The baseline purchase rate **r** represents expected hot dogs per fan.

Scenario factors modify this rate using multipliers:

$$
r_{\\text{effective}}
=
r_0
\\times m_{\\text{promo}}
\\times m_{\\text{playoff}}
\\times m_{\\text{weather}}
\\times m_{\\text{record}}
$$

**Interpretation:**

- Promotions increase buying behavior  
- Playoffs increase excitement  
- Team records influence fan engagement  
- Weather affects comfort and concessions usage  

This keeps the model interpretable and easy to calibrate.
"""
        )

    with st.expander("Noise term ε: randomness and uncertainty", expanded=False):
        st.markdown(
            """
### Why lognormal noise?

The ε term is modeled using a Lognormal distribution:

- Always positive  
- Allows occasional unusually high-demand games  
- Produces realistic right-skewed behavior

### Mean near 1

We set:

$$
E[\\varepsilon] \\approx 1
$$

This ensures randomness adds variability without biasing demand upward or downward.
"""
        )

    with st.expander("Profit model: Newsvendor formulation", expanded=False):
        st.markdown(
            """
### Profit per game

$$
\\Pi(Q,D)
=
p\\min(Q,D)
-
cQ
+
s\\max(Q-D,0)
-
F
$$

**Where:**

- **p** = selling price per hot dog  
- **c** = cost per hot dog  
- **s** = salvage value of leftovers  
- **F** = fixed operating cost  

### Key cases

**1) Stockout (D > Q):**

- Sold = Q  
- Leftover = 0  
- Lost sales occur  

**2) Leftovers (D < Q):**

- Sold = D  
- Leftover = Q − D  
- Salvage recovers partial cost  

This matches the classic single-period newsvendor setting.
"""
        )

    with st.expander("What “optimal Q” means in this simulation", expanded=False):
        st.markdown(
            """
### Monte Carlo estimation

Expected profit is estimated using simulation:

$$
\\widehat{E[\\Pi(Q)]}
=
\\frac{1}{N}
\\sum_{i=1}^{N} \\Pi(Q, D_i)
$$

Because this is simulation-based:

- Results depend on random seed  
- More replications improve stability  

### Grid search limitation

Q is optimized only over tested grid values.

Smaller step sizes provide more precise estimates.
"""
        )

    with st.expander("Metric definitions", expanded=False):
        st.markdown(
            """
### Stockout rate

$$
P(D > Q)
$$

Fraction of games where demand exceeds supply.

### Sellout rate

$$
P(A \\ge \\text{Capacity})
$$

Fraction of games where attendance reaches capacity.

### Distributions

- Demand → customer uncertainty  
- Profit → business risk  
- Attendance → crowd variability  
- ε → unexplained randomness
"""
        )

    with st.expander("Model assumptions and limitations", expanded=False):
        st.markdown(
            """
This model is intentionally simplified.

### Key assumptions

- No dynamic pricing  
- No mid-game replenishment  
- No product substitution  
- Single-item focus  
- Parameters assumed stable  

### Implication

The model emphasizes interpretability and decision support rather than exact prediction.
It is well-suited for strategic inventory planning and classroom analysis.
"""
        )