# app.py
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime
import math
import base64
from pathlib import Path

from src import config
from src.scenario import Scenario
from src.run_sim import simulate_many, evaluate_grid
import streamlit.components.v1 as components

Q_MIN = config.Q_MIN
Q_MAX = config.Q_MAX
MAX_GRID_POINTS = config.MAX_GRID_POINTS

# ============================================================
# Page config
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

        [data-testid="stHeader"] {{
            background: transparent;
        }}

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
        margin:14px 0 18px;
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
        GAME DAY MODE
      </div>
      <div style="color:#6B7280; font-weight:700; font-size:13px;">
        Choose your <span style="color:#D73A2F; font-weight:900;">Q</span> for the current game scenario.
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

        /* =========================
           METRICS
        ========================= */

        div[data-testid="metric-container"], .stMetric{
            background: rgba(255,255,255,0.92) !important;
            border: 1px solid rgba(224,227,235,0.9) !important;
            border-radius: 14px !important;
            padding: 14px !important;
            box-shadow: 0 8px 22px rgba(0,0,0,0.10);

            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;

            text-align: center !important;
        }

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

        /* Value */
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
# Altair Theme
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
    "price_per_dog", "cost_per_dog", "salvage_per_dog",
]

# ============================================================
# Initialize session state defaults
# ============================================================
if "temp_f" not in st.session_state:
    st.session_state["temp_f"] = IDEAL_TEMP_F

if "rain" not in st.session_state:
    st.session_state["rain"] = False

if "snow" not in st.session_state:
    st.session_state["snow"] = False

if "indoor" not in st.session_state:
    st.session_state["indoor"] = False

def handle_indoor_toggle():
    """Set weather inputs for an indoor stadium."""
    if st.session_state.get("indoor"):
        st.session_state["rain"] = False
        st.session_state["snow"] = False
        st.session_state["temp_f"] = IDEAL_TEMP_F


def reset_app():
    """Reset saved inputs and results."""
    for k in WIDGET_KEYS:
        if k in st.session_state:
            del st.session_state[k]
    st.session_state["last_run"] = None


def mean_ci_95(values) -> tuple[float | None, float | None, float | None, float | None]:
    """
    Returns:
        mean, standard_error, ci_low, ci_high
    using normal approx: mean ± 1.96 * SE
    """
    arr = np.asarray(values, dtype=float)
    n = arr.size
    if n == 0:
        return None, None, None, None

    mean_val = float(np.mean(arr))

    if n == 1:
        return mean_val, 0.0, mean_val, mean_val

    sd = float(np.std(arr, ddof=1))
    se = sd / np.sqrt(n)
    half_width = 1.96 * se
    return mean_val, se, mean_val - half_width, mean_val + half_width


def proportion_ci_95(p_hat: float, n: int) -> tuple[float | None, float | None]:
    """
    Wald-style 95% CI for a proportion.
    Returns:
        ci_low, ci_high
    """
    if n <= 0:
        return None, None

    se = np.sqrt((p_hat * (1.0 - p_hat)) / n)
    half_width = 1.96 * se
    lo = max(0.0, p_hat - half_width)
    hi = min(1.0, p_hat + half_width)
    return lo, hi


def expected_shortfall(values, alpha: float = 0.05) -> float | None:
    """
    Average of the worst alpha fraction of outcomes.
    For profit, this is a downside-risk metric.
    """
    arr = np.asarray(values, dtype=float)
    n = arr.size
    if n == 0:
        return None

    cutoff = np.quantile(arr, alpha)
    tail = arr[arr <= cutoff]

    if tail.size == 0:
        return float(cutoff)

    return float(np.mean(tail))


def paired_profit_analysis(values_a, values_b) -> dict[str, float | int | None]:
    a = np.asarray(values_a, dtype=float)
    b = np.asarray(values_b, dtype=float)

    if a.size == 0 or b.size == 0 or a.size != b.size:
        return {
            "n": None,
            "mean_diff": None,
            "se_diff": None,
            "ci_low": None,
            "ci_high": None,
            "z_stat": None,
            "p_value_two_sided": None,
        }

    diff = a - b
    n = int(diff.size)
    mean_diff = float(np.mean(diff))

    if n == 1:
        return {
            "n": n,
            "mean_diff": mean_diff,
            "se_diff": 0.0,
            "ci_low": mean_diff,
            "ci_high": mean_diff,
            "z_stat": None,
            "p_value_two_sided": None,
        }

    sd_diff = float(np.std(diff, ddof=1))
    se_diff = sd_diff / np.sqrt(n)
    half_width = 1.96 * se_diff

    if se_diff == 0.0:
        z_stat = None
        p_value = 0.0 if mean_diff != 0.0 else 1.0
    else:
        z_stat = mean_diff / se_diff
        p_value = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(z_stat) / np.sqrt(2.0))))

    return {
        "n": n,
        "mean_diff": mean_diff,
        "se_diff": se_diff,
        "ci_low": mean_diff - half_width,
        "ci_high": mean_diff + half_width,
        "z_stat": z_stat,
        "p_value_two_sided": p_value,
    }

def render_stat_card(label: str, value: str, height: int = 95):
    st.markdown(
        f"""
        <div style="
            background: rgba(255,255,255,0.92);
            border: 1px solid rgba(224,227,235,0.9);
            border-radius: 14px;
            padding: 12px 16px;
            box-shadow: 0 8px 22px rgba(0,0,0,0.10);
            min-height: {height}px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        ">
            <div style="
                font-weight: 800;
                color: #6B7280;
                font-size: 0.95rem;
                margin-bottom: 8px;
                line-height: 1.2;
            ">
                {label}
            </div>
            <div style="
                font-weight: 950;
                color: #111827;
                font-size: 1.45rem;
                line-height: 1.25;
                word-break: break-word;
                overflow-wrap: anywhere;
            ">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
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
    badges = []

    badges.append(_badge("🏟️ Indoor" if sc.indoor else "🌤️ Outdoor", "blue" if sc.indoor else "neutral"))
    badges.append(_badge(f"🧱 Capacity {int(sc.stadium_capacity):,}", "neutral"))

    if sc.indoor:
        badges.append(_badge(f"🌡️ {int(round(sc.temp_f))}F (fixed)", "neutral"))
    else:
        badges.append(_badge(f"🌡️ {int(round(sc.temp_f))}F", "neutral"))
        if sc.rain:
            badges.append(_badge("🌧️ Rain", "blue"))
        if sc.snow:
            badges.append(_badge("❄️ Snow", "blue"))

    badges.append(_badge("📣 Promotion" if sc.promo else "🚫 No Promo", "red" if sc.promo else "neutral"))
    badges.append(_badge("🏆 Playoff" if sc.playoff else "🗓️ Regular season", "gold" if sc.playoff else "neutral"))

    badges.append(_badge(f"🏠 Home {sc.team_wins}-{sc.team_losses}", "neutral"))
    badges.append(_badge(f"🚌 Away {sc.opp_wins}-{sc.opp_losses}", "neutral"))

    left_label = q_label
    left_value = "-" if best_q is None else f"{int(best_q):,}"

    right_label = "AVG PROFIT"
    right_value = "-" if avg_profit is None else f"${int(round(avg_profit)):,}"

    def fmt_rate(x: float | None) -> str:
        return "-" if x is None else f"{x:.1%}"

    def fmt_int(x: float | None) -> str:
        return "-" if x is None else f"{int(round(x)):,}"

    so = fmt_rate(stockout_rate)
    se = fmt_rate(sellout_rate)
    aa = fmt_int(avg_attendance)

    ticker = "".join(badges)
    ticker2 = ticker + ticker

    html = f"""
    <style>
        html, body {{
            margin: 0;
            padding: 0;
            background: transparent;
        }}
    </style>

    <div style="font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; display:flex; justify-content:center; padding:0;">

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

        .badge-ticker:hover .badge-track {{
        animation-play-state: paused;
        }}

        @keyframes badge-scroll {{
        0%   {{ transform: translateX(0); }}
        100% {{ transform: translateX(-50%); }}
        }}

        @media (max-width: 520px) {{
        .sb-top-row {{
            flex-wrap: wrap !important;
            gap: 10px !important;
        }}

        .sb-card {{
            max-width: none !important;
            flex: 1 1 100% !important;
        }}

        .sb-big-value {{
            white-space: nowrap !important;
            font-size: 28px !important;
            line-height: 1.05 !important;
        }}

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

        .sb-vs-line {{
            display: none !important;
        }}

        .badge-ticker {{
            padding: 8px 10px !important;
        }}
        }}
    </style>

    <div style="
        width: 100%;
        max-width: 980px;
        border: 1px solid #E0E3EB;
        border-radius: 18px;
        background: #FFFFFF;
        box-shadow: 0 10px 28px rgba(17,24,39,0.08);
        overflow: hidden;
    ">

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

        <div style="padding: 14px 14px 12px; background:#FFFFFF;">

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

        <div class="badge-ticker">
        <div class="badge-track">
            {ticker2}
        </div>
        </div>

    </div>
    </div>
    """

    components.html(html, height=292)


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
            lines.append("Stockouts are frequent - you’re leaving meaningful demand on the table.")
        elif stockout >= 0.08:
            lines.append("Stockouts are moderate - you’re balancing lost sales against waste.")
        else:
            lines.append("Stockouts are low - you’re prioritizing availability and fan satisfaction.")

    if waste is not None:
        if waste >= 0.25:
            lines.append("Waste is relatively high; consider lowering Q or improving salvage/secondary sales.")
        elif waste >= 0.10:
            lines.append("Waste looks manageable; there’s a healthy buffer for demand spikes.")
        else:
            lines.append("Waste is low; ordering is tight and efficient.")

    if sellout is not None:
        if sellout >= 0.25:
            lines.append("Sellouts happen often - packed-house games can drive right-tail demand spikes.")
        elif sellout >= 0.10:
            lines.append("Sellouts occur sometimes - expect occasional demand surges.")

    if mode == "grid":
        lines.append("“Best Q” is the top performer on your tested grid (tighten step size around the peak to refine).")

    return " ".join(lines)

# ============================================================
# Charts
# ============================================================
def plot_profit_vs_q_with_refs(results: list[dict], best_q: int):
    rows = []
    for r in results:
        n_games = int(r.get("n games", 0))
        sd_profit = float(r.get("sd_profit", 0.0))
        se_profit = (sd_profit / np.sqrt(n_games)) if n_games > 0 else 0.0
        rows.append({
            "Q": int(r["Q"]),
            "avg_profit": float(r["avg_profit"]),
            "ci_low": float(r["avg_profit"]) - 1.96 * se_profit,
            "ci_high": float(r["avg_profit"]) + 1.96 * se_profit,
        })

    chart_df = pd.DataFrame(rows).sort_values("Q")

    base = alt.Chart(chart_df).encode(
        x=alt.X("Q:Q", title="Order Quantity (Q)", axis=alt.Axis(format=",.0f")),
        y=alt.Y("avg_profit:Q", title="Average Profit ($)", axis=alt.Axis(format=",.0f")),
        tooltip=[
            alt.Tooltip("Q:Q", title="Q", format=","),
            alt.Tooltip("avg_profit:Q", title="Avg Profit", format=",.0f"),
            alt.Tooltip("ci_low:Q", title="95% CI Low", format=",.0f"),
            alt.Tooltip("ci_high:Q", title="95% CI High", format=",.0f"),
        ],
    )

    band = (
        alt.Chart(chart_df)
        .mark_area(color=MUSTARD, opacity=0.18)
        .encode(
            x=alt.X("Q:Q", title="Order Quantity (Q)", axis=alt.Axis(format=",.0f")),
            y=alt.Y("ci_low:Q", title="Average Profit ($)", axis=alt.Axis(format=",.0f")),
            y2="ci_high:Q",
        )
    )

    line = base.mark_line(color=KETCHUP, strokeWidth=3)
    pts = base.mark_point(filled=True, size=80, color=KETCHUP, stroke="white", strokeWidth=1)

    best_pt = alt.Chart(pd.DataFrame({"Q": [best_q]})).mark_rule(
        color=MUSTARD, strokeWidth=3, strokeDash=[8, 6]
    ).encode(x="Q:Q")

    zero = alt.Chart(pd.DataFrame({"avg_profit": [0]})).mark_rule(
        color=MUTED, strokeWidth=2, strokeDash=[6, 6], opacity=0.6
    ).encode(y="avg_profit:Q")

    chart = (
        (band + line + pts + best_pt + zero)
        .properties(height=380, padding={"left": 16, "right": 16, "top": 10, "bottom": 12})
    )

    st.altair_chart(chart, use_container_width=True)


def plot_inventory_flow(avg_sold: float, avg_leftover: float, avg_unmet: float, title: str):
    df = pd.DataFrame(
        [
            {"bucket": "Sold", "value": float(avg_sold), "color": KETCHUP},
            {"bucket": "Leftover", "value": float(avg_leftover), "color": MUSTARD},
            {"bucket": "Unmet Demand", "value": float(avg_unmet), "color": "#7F1D1D"},
        ]
    )

    domain = ["Sold", "Leftover", "Unmet Demand"]
    range_ = [KETCHUP, MUSTARD, "#7F1D1D"]
    max_value = max(float(df["value"].max()), 1.0)

    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusTopRight=8, cornerRadiusBottomRight=8)
        .encode(
            y=alt.Y("bucket:N", title=None, sort=domain),
            x=alt.X("value:Q", title="Average hot dogs", axis=alt.Axis(format=",.0f"), scale=alt.Scale(domain=[0, max_value * 1.12])),
            color=alt.Color("bucket:N", scale=alt.Scale(domain=domain, range=range_), legend=None),
            tooltip=[
                alt.Tooltip("bucket:N", title="Outcome"),
                alt.Tooltip("value:Q", title="Average hot dogs", format=",.0f"),
            ],
        )
        .properties(height=320)
    )

    st.altair_chart(
        chart.properties(
            title=title,
            padding={"left": 16, "right": 16, "top": 10, "bottom": 12},
        ),
        use_container_width=True,
    )


def plot_profit_tradeoff(results: list[dict], best_q: int):
    chart_df = pd.DataFrame(
        [
            {
                "Q": int(r["Q"]),
                "avg_profit": float(r["avg_profit"]),
                "stockout_rate": float(r["stockout_rate"]),
                "avg_leftover": float(r["avg_leftover"]),
                "is_best": int(r["Q"]) == int(best_q),
            }
            for r in results
        ]
    )
    other_points = (
        alt.Chart(chart_df)
        .transform_filter("datum.is_best == false")
        .mark_circle(opacity=0.45, color=MUTED)
        .encode(
            x=alt.X("stockout_rate:Q", title="Stockout Rate", axis=alt.Axis(format=".0%")),
            y=alt.Y("avg_profit:Q", title="Average Profit ($)", axis=alt.Axis(format=",.0f")),
            size=alt.Size("avg_leftover:Q", title="Avg Leftover", scale=alt.Scale(range=[40, 420])),
            tooltip=[
                alt.Tooltip("Q:Q", title="Q", format=","),
                alt.Tooltip("avg_profit:Q", title="Avg Profit", format=",.0f"),
                alt.Tooltip("stockout_rate:Q", title="Stockout Rate", format=".1%"),
                alt.Tooltip("avg_leftover:Q", title="Avg Leftover", format=",.0f"),
            ],
        )
    )

    best_point = (
        alt.Chart(chart_df)
        .transform_filter("datum.is_best == true")
        .mark_circle(opacity=1.0, color=KETCHUP, stroke="white", strokeWidth=2)
        .encode(
            x=alt.X("stockout_rate:Q", title="Stockout Rate", axis=alt.Axis(format=".0%")),
            y=alt.Y("avg_profit:Q", title="Average Profit ($)", axis=alt.Axis(format=",.0f")),
            size=alt.Size("avg_leftover:Q", title="Avg Leftover", scale=alt.Scale(range=[40, 420])),
            tooltip=[
                alt.Tooltip("Q:Q", title="Q", format=","),
                alt.Tooltip("avg_profit:Q", title="Avg Profit", format=",.0f"),
                alt.Tooltip("stockout_rate:Q", title="Stockout Rate", format=".1%"),
                alt.Tooltip("avg_leftover:Q", title="Avg Leftover", format=",.0f"),
            ],
        )
    )

    chart = (
        (other_points + best_point)
        .properties(height=320, padding={"left": 16, "right": 16, "top": 10, "bottom": 12})
    )

    st.altair_chart(chart, use_container_width=True)


def plot_hist_numeric_eps(eps_values, step: float = 0.02):
    df = pd.DataFrame({"eps": np.asarray(eps_values, dtype=float)})

    bars = (
        alt.Chart(df)
        .mark_bar(color=KETCHUP, opacity=0.70)
        .encode(
            x=alt.X("eps:Q", bin=alt.Bin(step=step), title="epsilon (demand multiplier)", axis=alt.Axis(format=".2f")),
            y=alt.Y("count():Q", title="Simulated games"),
            tooltip=[alt.Tooltip("count():Q", title="Games")],
        )
        .properties(height=300)
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
            "Temperature (F)",
            min_value=int(config.TEMP_MIN_F),
            max_value=int(config.TEMP_MAX_F),
            key="temp_f",
            step=1,
            disabled=indoor,
        )

        col_w1, col_w2 = st.columns(2)
        with col_w1:
            rain_ui = st.checkbox("Rain", key="rain", value=bool(st.session_state.get("rain", False)), disabled=indoor)
        with col_w2:
            snow_ui = st.checkbox("Snow", key="snow", value=bool(st.session_state.get("snow", False)), disabled=indoor)

        if indoor:
            st.caption(f"Indoor stadium: weather + temperature are ignored.")

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
                    "Q": q_ran,
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
                        runner_up = top10[1] if len(top10) > 1 else None
                        runner_up_trace = (
                            simulate_many(Q=int(runner_up["Q"]), sc=sc, return_traces=True)
                            if runner_up is not None else None
                        )

                        st.session_state.last_run = {
                            "mode": "grid",
                            "scenario": sc,
                            "results": results,
                            "best": best,
                            "top10": top10,
                            "best_trace": best_trace,
                            "runner_up": runner_up,
                            "runner_up_trace": runner_up_trace,
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
        traces = summary.get("traces")

        sellout_rate: float | None = None
        avg_attendance: float | None = None

        if traces:
            att = np.asarray(traces["attendance"], dtype=float)
            avg_attendance = float(np.mean(att))
            sellout_rate = float(np.mean(att >= stadium_capacity))

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
            st.caption(
                f"Last run: {meta.get('ran_at','')} • Seed: {meta.get('seed','')} • Replications: {meta.get('replications','')}"
            )

        traces = summary.get("traces")
        p05_profit = None
        waste_rate = None
        hotdogs_per_1k = None
        efficiency = None
        avg_unmet = None

        profit_se = None
        profit_ci_low = None
        profit_ci_high = None
        stockout_ci_low = None
        stockout_ci_high = None
        expected_shortfall_5 = None

        if traces:
            att = np.asarray(traces["attendance"], dtype=float)
            profit = np.asarray(traces["profit"], dtype=float)
            demand = np.asarray(traces["demand"], dtype=float)

            Q_used = int(last["Q"])
            sold_est = np.minimum(Q_used, demand)
            leftover_est = np.maximum(Q_used - demand, 0)
            unmet_est = np.maximum(demand - Q_used, 0)

            sellout_rate = float(np.mean(att >= stadium_capacity))
            p05_profit = float(np.percentile(profit, 5))
            waste_rate = float(np.mean(leftover_est / max(Q_used, 1)))
            efficiency = float(np.mean(sold_est / max(Q_used, 1)))
            avg_unmet = float(np.mean(unmet_est))

            denom = np.maximum(att, 1.0)
            hotdogs_per_1k = float(np.mean((sold_est / denom) * 1000.0))

            n_games = profit.size
            _, profit_se, profit_ci_low, profit_ci_high = mean_ci_95(profit)
            stockout_ci_low, stockout_ci_high = proportion_ci_95(
                float(summary["stockout_rate"]),
                n_games,
            )
            expected_shortfall_5 = expected_shortfall(profit, alpha=0.05)

        st.subheader("Summary")

        c1, c2, c3 = st.columns(3)
        c1.metric("SE Profit", "N/A" if profit_se is None else f"${profit_se:,.0f}")
        c2.metric("SD Profit", f"${int(round(summary['sd_profit'])):,}")
        c3.metric("Avg Demand", f"{int(round(summary['avg_demand'])):,}")

        st.subheader("Statistical analysis")

        c5, c6 = st.columns(2)
        with c5:
            render_stat_card(
                "95% CI: Expected Avg Profit",
                "N/A" if profit_ci_low is None or profit_ci_high is None
                else f"[${profit_ci_low:,.0f}, ${profit_ci_high:,.0f}]",
                height=140,
            )
        with c6:
            render_stat_card(
                "95% CI: Stockout Rate",
                "N/A" if stockout_ci_low is None or stockout_ci_high is None
                else f"[{stockout_ci_low:.1%}, {stockout_ci_high:.1%}]",
                height=140,
            )

        if traces:
            plot_hist_numeric(traces["profit"], title="", x_title="Profit per game ($)", bins=30, x_format=",.0f")

        st.subheader("Operational tradeoffs")

        m1, m2, m3 = st.columns(3)
        m1.metric("Downside Profit (5th %ile)", "N/A" if p05_profit is None else f"${int(round(p05_profit)):,}")
        m2.metric("Expected Shortfall (5%)", "N/A" if expected_shortfall_5 is None else f"${int(round(expected_shortfall_5)):,}")
        m3.metric("Sellout Rate", "N/A" if sellout_rate is None else f"{sellout_rate:.1%}")

        m4, m5, m6 = st.columns(3)
        m4.metric("Waste Rate", "N/A" if waste_rate is None else f"{waste_rate:.1%}")
        m5.metric("Order Efficiency", "N/A" if efficiency is None else f"{efficiency:.1%}")
        m6.metric("Hot Dogs / 1,000 Fans", "N/A" if hotdogs_per_1k is None else f"{int(round(hotdogs_per_1k)):,}")

        if avg_unmet is not None:
            plot_inventory_flow(
                float(summary["avg_sold"]),
                float(summary["avg_leftover"]),
                float(avg_unmet),
                title="Average inventory flow per game",
            )

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
            st.subheader("Distribution views")
            plot_hist_numeric(traces["demand"], title="", x_title="Hot dogs demanded", bins=30, x_format=",.0f")

            with st.expander("Attendance + Noise Distributions", expanded=True):
                st.markdown("**Attendance (A)**")
                plot_hist_numeric(traces["attendance"], title="", x_title="Fans in attendance", bins=30, x_format=",.0f")

                st.markdown("**Multiplicative Noise (epsilon)**")
                plot_hist_numeric(traces["eps"], title="", x_title="epsilon (demand multiplier)", bins=30, x_format=".2f")

    else:
        best = last["best"]
        top10 = last["top10"]
        results = last["results"]
        best_trace = last.get("best_trace")
        runner_up = last.get("runner_up")
        runner_up_trace = last.get("runner_up_trace")

        sellout_rate: float | None = None
        avg_attendance: float | None = None

        if best_trace and best_trace.get("traces"):
            att = np.asarray(best_trace["traces"]["attendance"], dtype=float)
            avg_attendance = float(np.mean(att))
            sellout_rate = float(np.mean(att >= stadium_capacity))

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
            st.caption(
                f"Last run: {meta.get('ran_at','')} • Seed: {meta.get('seed','')} • Replications: {meta.get('replications','')}"
            )

        p05_profit = None
        waste_rate = None
        hotdogs_per_1k = None
        efficiency = None
        avg_unmet = None

        profit_se = None
        profit_ci_low = None
        profit_ci_high = None
        stockout_ci_low = None
        stockout_ci_high = None
        expected_shortfall_5 = None
        paired_vs_runner = None

        if best_trace and best_trace.get("traces"):
            traces = best_trace["traces"]
            att = np.asarray(traces["attendance"], dtype=float)
            profit = np.asarray(traces["profit"], dtype=float)
            demand = np.asarray(traces["demand"], dtype=float)

            Q_used = int(best["Q"])
            sold_est = np.minimum(Q_used, demand)
            leftover_est = np.maximum(Q_used - demand, 0)
            unmet_est = np.maximum(demand - Q_used, 0)

            p05_profit = float(np.percentile(profit, 5))
            waste_rate = float(np.mean(leftover_est / max(Q_used, 1)))
            efficiency = float(np.mean(sold_est / max(Q_used, 1)))
            avg_unmet = float(np.mean(unmet_est))

            denom = np.maximum(att, 1.0)
            hotdogs_per_1k = float(np.mean((sold_est / denom) * 1000.0))

            n_games = profit.size
            _, profit_se, profit_ci_low, profit_ci_high = mean_ci_95(profit)
            stockout_ci_low, stockout_ci_high = proportion_ci_95(
                float(best["stockout_rate"]),
                n_games,
            )
            expected_shortfall_5 = expected_shortfall(profit, alpha=0.05)

            if runner_up_trace and runner_up_trace.get("traces"):
                paired_vs_runner = paired_profit_analysis(
                    traces["profit"],
                    runner_up_trace["traces"]["profit"],
                )

        st.subheader("Summary")

        r1c1, r1c2, r1c3 = st.columns(3)
        r1c1.metric("SE Profit", "N/A" if profit_se is None else f"${profit_se:,.0f}")
        r1c2.metric("Avg Demand", f"{int(round(best['avg_demand'])):,}")
        r1c3.metric("Avg Leftover", f"{int(round(best['avg_leftover'])):,}")

        st.subheader("Statistical analysis")

        c7, c8 = st.columns(2)
        with c7:
            render_stat_card(
                "95% CI: Expected Avg Profit",
                "N/A" if profit_ci_low is None or profit_ci_high is None
                else f"[${profit_ci_low:,.0f}, ${profit_ci_high:,.0f}]",
                height=95,
            )
        with c8:
            render_stat_card(
                "95% CI: Stockout Rate",
                "N/A" if stockout_ci_low is None or stockout_ci_high is None
                else f"[{stockout_ci_low:.1%}, {stockout_ci_high:.1%}]",
                height=95,
            )

        st.subheader("Best Q vs Runner-up")

        if runner_up is None:
            st.info("A comparison test needs at least two Q values in the grid.")
        else:
            cmp1, cmp2, cmp3 = st.columns(3)
            cmp1.metric("Runner-up Q", f"{int(runner_up['Q']):,}")
            cmp2.metric(
                "Mean Profit Gap",
                "N/A" if paired_vs_runner is None or paired_vs_runner["mean_diff"] is None
                else f"${paired_vs_runner['mean_diff']:,.0f}",
            )
            cmp3.metric(
                "Two-sided p-value",
                "N/A" if paired_vs_runner is None or paired_vs_runner["p_value_two_sided"] is None
                else f"{paired_vs_runner['p_value_two_sided']:.4f}",
            )

            cmp4, cmp5 = st.columns(2)
            with cmp4:
                render_stat_card(
                    "95% CI: Profit Gap",
                    "N/A" if paired_vs_runner is None or paired_vs_runner["ci_low"] is None or paired_vs_runner["ci_high"] is None
                    else f"[${paired_vs_runner['ci_low']:,.0f}, ${paired_vs_runner['ci_high']:,.0f}]",
                    height=95,
                )
            with cmp5:
                verdict = "N/A"
                if paired_vs_runner is not None and paired_vs_runner["ci_low"] is not None and paired_vs_runner["ci_high"] is not None:
                    if paired_vs_runner["ci_low"] > 0:
                        verdict = "Best Q is statistically higher"
                    elif paired_vs_runner["ci_high"] < 0:
                        verdict = "Runner-up is statistically higher"
                    else:
                        verdict = "Difference is not statistically clear"
                render_stat_card("Comparison Verdict", verdict, height=95)

        plot_profit_vs_q_with_refs(results, best_q=int(best["Q"]))

        st.subheader("Operational tradeoffs")

        m1, m2, m3 = st.columns(3)
        m1.metric("Downside Profit (5th %ile)", "N/A" if p05_profit is None else f"${int(round(p05_profit)):,}")
        m2.metric("Expected Shortfall (5%)", "N/A" if expected_shortfall_5 is None else f"${int(round(expected_shortfall_5)):,}")
        m3.metric("Sellout Rate", "N/A" if sellout_rate is None else f"{sellout_rate:.1%}")

        m4, m5, m6 = st.columns(3)
        m4.metric("Waste Rate", "N/A" if waste_rate is None else f"{waste_rate:.1%}")
        m5.metric("Order Efficiency", "N/A" if efficiency is None else f"{efficiency:.1%}")
        m6.metric("Hot Dogs / 1,000 Fans", "N/A" if hotdogs_per_1k is None else f"{int(round(hotdogs_per_1k)):,}")

        if avg_unmet is not None:
            left_col, right_col = st.columns(2)
            with left_col:
                plot_inventory_flow(
                    float(best["avg_sold"]),
                    float(best["avg_leftover"]),
                    float(avg_unmet),
                    title="Average inventory flow at best Q",
                )
            with right_col:
                plot_profit_tradeoff(results, best_q=int(best["Q"]))
                st.caption(f"Best Q highlighted: {int(best['Q']):,}. Higher is better. Farther left means fewer stockouts.")

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

        st.subheader("Grid summary")
        st.dataframe(df, use_container_width=True)

        if best_trace and best_trace.get("traces"):
            traces = best_trace["traces"]

            st.subheader("Distribution views")
            plot_hist_numeric(traces["profit"], title="", x_title="Profit per game ($)", bins=30, x_format=",.0f")

            plot_hist_numeric(traces["demand"], title="", x_title="Hot dogs demanded", bins=30, x_format=",.0f")

            with st.expander("Attendance + Noise Distributions (Best Q)", expanded=True):
                st.markdown("**Attendance (A)**")
                plot_hist_numeric(traces["attendance"], title="", x_title="Fans in attendance", bins=30, x_format=",.0f")

                st.markdown("**Multiplicative Noise (epsilon)**")
                plot_hist_numeric_eps(traces["eps"])

        st.subheader("Best Q details")
        st.write(best)

# -------------------------
# Explanation tab
# -------------------------
with tab_explain:
    st.subheader("How to read this dashboard")

    st.markdown(
        """
**What you're deciding:** the order quantity **Q**.  

**What the simulator models:** game-to-game uncertainty in attendance and demand.  

**What "best Q" means:** the tested Q with the highest estimated average profit under the current scenario.
"""
    )

    with st.expander("Demand model: what each piece means", expanded=False):
        st.markdown(
            r"""
### Core demand equation

We model game demand as:

$$
D = \mathrm{round}(A \cdot r \cdot \varepsilon)
$$

**Where:**

- **A (Attendance)** = how many fans show up  
- **r (Hot dogs per attendee)** = fixed baseline purchase rate  
- **ε (Epsilon noise)** = multiplicative residual randomness

### Why multiplicative noise?

We use multiplicative noise so demand variability scales with crowd size:

- Big crowds -> bigger swings in absolute demand  
- Small crowds -> smaller swings  

### Rounding / integer demand

Hot dogs are discrete units, so simulated demand is rounded to an integer.
"""
        )

    with st.expander("Attendance (A): how scenario inputs affect demand", expanded=False):
        st.markdown(
            r"""
### Attendance model

Attendance is the main scenario-driven part of the demand model.

The code:

1. Starts with a baseline mean tied to stadium capacity  
2. Adjusts that mean using multipliers for promotions, playoffs, weather, and team quality  
3. Samples attendance from a Normal distribution  
4. Caps attendance at stadium capacity

### Capacity capping and sellouts

Attendance is bounded by:

$$
0 \le A \le \text{Stadium Capacity}
$$

If simulated attendance exceeds capacity, it is capped. That creates visible mass at capacity in the attendance distribution, representing sellout games.

### Indoor stadium behavior

When **Indoor stadium** is enabled:

- Rain and snow are ignored  
- Temperature is fixed at the ideal level  

This prevents outdoor weather effects from changing indoor attendance.
"""
        )

    with st.expander("Purchase rate (r): fixed consumption assumption", expanded=False):
        st.markdown(
            """
### Fixed baseline rate

The purchase rate **r** is the expected number of hot dogs purchased per attendee.

In the current implementation, this rate is fixed:

$$
r = r_0 = 0.30
$$

Scenario inputs do **not** directly change `r` in the current code. They affect demand through attendance instead.

### Why keep r fixed?

- It keeps the model simple and interpretable  
- It avoids double-counting effects already captured in attendance  
- It makes the demand decomposition clearer: attendance drives scale, epsilon drives residual variation
"""
        )

    with st.expander("Noise term epsilon: randomness and uncertainty", expanded=False):
        st.markdown(
            r"""
### Why lognormal noise?

The epsilon term is modeled using a Lognormal distribution:

- Always positive  
- Allows occasional unusually high-demand games  
- Produces realistic right-skewed behavior

### Mean near 1

We set:

$$
E[\varepsilon] \approx 1
$$

This lets epsilon add variability without systematically pushing demand up or down.
"""
        )

    with st.expander("Profit model: Newsvendor formulation", expanded=False):
        st.markdown(
            r"""
### Profit per game

$$
\Pi(Q,D)
=
p\min(Q,D)
-
cQ
+
s\max(Q-D,0)
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
- Leftover = Q - D  
- Salvage recovers part of the leftover cost

This is the classic single-period newsvendor setup.
"""
        )

    with st.expander("What 'optimal Q' means in this simulation", expanded=False):
        st.markdown(
            r"""
### Monte Carlo estimation

Expected profit is estimated using simulation:

$$
\widehat{E[\Pi(Q)]}
=
\frac{1}{N}
\sum_{i=1}^{N} \Pi(Q, D_i)
$$

Because this is simulation-based:

- Results depend on random seed  
- More replications improve stability  

### Grid search interpretation

In grid-search mode, the app evaluates a set of candidate Q values and selects the one with the highest estimated average profit.

That means the reported best Q is the best among the tested grid points, not the exact continuous optimum.

Smaller step sizes provide a more refined search.
"""
        )

    with st.expander("Metric definitions", expanded=False):
        st.markdown(
            r"""
### Stockout rate

$$
P(D > Q)
$$

Fraction of games where demand exceeds supply.

### Sellout rate

$$
P(A \ge \text{Capacity})
$$

Fraction of games where attendance reaches stadium capacity.

### Statistical precision metrics

**SE Profit** shows the standard error of estimated average profit across simulation replications.

**95% CI: Expected Avg Profit** gives an approximate confidence interval for the expected average profit under the current scenario.

**95% CI: Stockout Rate** gives an approximate confidence interval for the estimated stockout probability.

**Expected Shortfall (5%)** averages the worst 5% of simulated profit outcomes and highlights downside risk more clearly than a single percentile cutoff.

**Best Q vs Runner-up** compares the top two Q values using paired simulation output from the same random stream. The profit-gap confidence interval and p-value show whether the selected best Q meaningfully outperforms the next-best option.

**Profit vs Q** shows the average-profit curve across tested order quantities, with a 95% confidence band around each estimate.

**Average inventory flow** breaks the typical game into sold hot dogs, leftovers, and unmet demand.

**Risk-return map** shows the tradeoff between average profit and stockout risk across the tested Q values.

### Distributions

- Demand -> customer uncertainty  
- Profit -> business risk  
- Attendance -> crowd variability  
- epsilon -> unexplained randomness
"""
        )

    with st.expander("Model assumptions and limitations", expanded=False):
        st.markdown(
            """
This model is intentionally simplified and designed for decision support rather than exact forecasting.

### Key assumptions

- Single-period decision  
- No mid-game replenishment  
- No dynamic pricing  
- No product substitution  
- One product focus  
- Fixed per-fan baseline purchase rate  
- Parameters treated as stable within a scenario  

### Implication

The model emphasizes interpretability, scenario analysis, and inventory tradeoffs.
It is well-suited for classroom analysis and for illustrating how uncertainty affects the recommended order quantity.
"""
        )

# ============================================================
# Photo credit (footer)
# ============================================================
st.markdown(
    """
    <style>
      .photo-credit {
        text-align:center;
        font-size:12px;
        color:#6B7280;
        margin-top:30px;
        padding-bottom:10px;
      }
      .photo-credit a {
        color:#374151;
        text-decoration: underline;
        text-underline-offset: 2px;
        font-weight: 700;
      }
      .photo-credit a:hover {
        color:#111827;
        text-decoration-thickness: 2px;
      }
    </style>

    <div class="photo-credit">
      Background photo by
      <a href="https://unsplash.com/@jessicaloaizar" target="_blank" rel="noopener noreferrer">
        Jessica Loaiza
      </a>
      on
      <a href="https://unsplash.com/photos/hotdog-sandwich-on-white-plate-glqTtszXfM0" target="_blank" rel="noopener noreferrer">
        Unsplash
      </a>
    </div>
    """,
    unsafe_allow_html=True
)

